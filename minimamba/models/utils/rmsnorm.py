import torch
import torch.nn as nn


class RMSNorm(nn.Module):
    """Implementation of RMSNorm, look at the paper for details

    Args:
        dimension (int): size of the layer to be normalized
        eps (float): epsilon for avoiding division by zero
    """

    def __init__(self, dimension: int, eps: float = 1e-5) -> None:
        super().__init__()
        self._scale = nn.Parameter(torch.ones(dimension))
        self._eps: float = eps

    def forward(self, x: torch.tensor) -> torch.tensor:
        y = (
            x
            * torch.rsqrt(torch.mean(x**2, -1).unsqueeze(-1) + self._eps)
            * self._scale
        )
        return y
