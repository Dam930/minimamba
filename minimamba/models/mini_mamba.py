import torch
from torch import nn
import torch.nn.functional as F

from minimamba.configs.models import MiniMambaConfig, MiniMambaBlockConfig
from minimamba.models.nn_model import NNModel
from minimamba.models.utils.rmsnorm import RMSNorm


class MiniMamba(NNModel):
    """Implementation of Minimal Mamba Model

    Args:
        config (MiniMambaConfig): config of the Mini Mamba Model
    """

    def __init__(self, config: MiniMambaConfig) -> None:
        super().__init__(config)
        # Define input embeddings and projection
        self._input_embed = nn.Embedding(config.vocab_size, config.embedding_dim)
        self._proj = nn.Linear(config.embedding_dim, config.blocks[0].layer_input)
        # Define Blocks
        self._layers = torch.nn.ModuleList([MambaBlock(conf) for conf in config.blocks])
        # Define output embeddings
        layer_output_dim: int = (
            config.blocks[-1].layer_out
            if config.blocks[-1].layer_out
            else config.blocks[-1].layer_input
        )
        self._head = torch.nn.Linear(layer_output_dim, config.vocab_size)
        self._lr = config.lr

    def forward(self, x: torch.tensor) -> torch.tensor:
        # Get the embeddings and projection
        x = self._input_embed(x)
        x = self._proj(x)

        # Execute layers
        for layer in self._layers:
            x = layer(x)

        # Head
        x = self._head(x)

        return x

    def training_step(self, batch: tuple[torch.tensor, torch.tensor], batch_idx: int):
        x, y = batch
        logits = self(x)
        loss = F.cross_entropy(
            logits.view(-1, logits.size(-1)), y.view(-1), ignore_index=-1
        )
        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch: tuple[torch.tensor, torch.tensor], batch_idx: int):
        x, y = batch
        logits = self(x)
        loss = F.cross_entropy(
            logits.view(-1, logits.size(-1)), y.view(-1), ignore_index=-1
        )
        self.log("val_loss", loss)

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self._lr)


class MambaBlock(nn.Module):
    """Implementation of Mamba Block Model

    Args:
        config (MiniMambaBlockConfig): config of the Mini Mamba Block
    """

    def __init__(self, config: MiniMambaBlockConfig) -> None:
        super().__init__()
        working_dim = config.layer_input * config.expansion
        # Input norm
        self._norm = RMSNorm(config.layer_input)
        # Projection for expansion block, x2 for gatedMLP
        self._in_projection = nn.Linear(config.layer_input, working_dim * 2)

        # Projection output
        self._out_projection = nn.Linear(
            working_dim,
            config.layer_out if config.layer_out is not None else config.layer_input,
        )

        # Conv
        self._conv = nn.Conv1d(
            working_dim,
            working_dim,
            config.conv_kernel,
            padding=config.conv_kernel - 1,
            groups=working_dim,
        )

        # SSM
        self._ssm = SelectiveStateSpaceModel(
            working_dim, config.state_dim, config.fraction_d
        )

    def forward(self, x: torch.tensor) -> torch.tensor:
        residual = x
        # X shape: B, T, D
        x = self._norm(x)

        # Expansion and separation between gated and main branch
        x, g = self._in_projection(x).chunk(2, -1)

        #######################
        ##### Main Branch #####
        #######################
        # Conv
        origin_T = x.shape[1]
        x = x.transpose(1, 2)
        x = self._conv(x)[..., :origin_T]
        x = x.transpose(1, 2)

        # Activation
        x = F.silu(x)

        # SSM
        x = self._ssm(x)

        #########################
        ##### Gated Branch ######
        #########################
        g = F.silu(g)

        #######################
        ##### Projection ######
        #######################
        x = g * x

        x = self._out_projection(x)

        if x.shape == residual.shape:
            x = x + residual

        return x


class SelectiveStateSpaceModel(nn.Module):
    """Implementation of Selective Space Model Operation

    Args:
        working_dim (int): feature dimension of the element
        state_dim (int): dimension of the state space
        fraction_d (int): fraction of working dim for delta
    """

    def __init__(self, working_dim: int, state_dim: int, fraction_d: int) -> None:
        super().__init__()

        # S4D real initialization https://github.com/state-spaces/mamba/issues/167
        A = torch.arange(1, state_dim + 1, dtype=torch.float32).repeat(working_dim, 1)
        self._A_log = nn.Parameter(torch.log(A))
        self._A_log._no_weight_decay = True
        self._DBC_proj = nn.Linear(
            working_dim, state_dim * 2 + working_dim // fraction_d
        )
        self._delta_up_rank = nn.Linear(working_dim // fraction_d, working_dim)
        self._working_dim: int = working_dim
        self._state_dim: int = state_dim
        self._fraction_d: int = fraction_d

    def forward(self, x: torch.tensor) -> torch.tensor:
        # Get A from parameters
        A = -torch.exp(self._A_log.float())

        # Get Delta, B and C from the projection of x (section 3.2)
        delta, B, C = self._DBC_proj(x).split(
            [
                self._working_dim // self._fraction_d,
                self._state_dim,
                self._state_dim,
            ],
            -1,
        )
        # Go back after the low rank (look paper, section 3.2 and 3.6)
        delta = F.softplus(self._delta_up_rank(delta))

        # Look at "Discretization" in the section 2
        A_discrete = torch.exp(delta.unsqueeze(-1) * A)
        B_discrete = delta.unsqueeze(-1) * B.unsqueeze(2)

        # State Update
        B_x = B_discrete * (x.unsqueeze(-1))
        h_list = []
        h = torch.zeros(x.shape[0], self._working_dim, self._state_dim, device=x.device)
        # This can be parallalized in CUDA:
        # https://developer.nvidia.com/gpugems/gpugems3/
        # /part-vi-gpu-computing/chapter-39-parallel-prefix-sum-scan-cuda
        for t in range(x.shape[1]):
            h = A_discrete[:, t] * h + B_x[:, t]
            h_list.append(h)

        h_list = torch.stack(h_list, 1)

        # output update Y = C*H
        y = (h_list @ C.unsqueeze(-1)).squeeze(3)

        return y
