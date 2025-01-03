####################################
# DO NOT DELETE
# ----------------------------------
# Add here your custom config models
#####################################

from pathlib import Path

from typing import List, Optional
from configmanager.core.models import BaseConfig, BaseObjectConfig, BaseCommandConfig
from pydantic import StrictStr, StrictInt, StrictFloat


# DO NOT DELETE
# Contains information about the current execution not related to a specific command
# (e.g. serialization dir, debug settings, etc.)
class GlobalContextConfig(BaseConfig):
    working_dir: Path = Path.home() / ".minimamba"


class NNConfig(BaseObjectConfig):
    pass


class MiniMambaBlockConfig(BaseConfig):
    layer_input: StrictInt
    expansion: StrictInt
    conv_kernel: StrictInt
    state_dim: StrictInt
    fraction_d: StrictInt
    layer_out: Optional[StrictInt] = None


class MiniMambaConfig(NNConfig):
    blocks: List[MiniMambaBlockConfig]
    lr: StrictFloat
    embedding_dim: StrictInt
    vocab_size: StrictInt


class DatasetConfig(BaseObjectConfig):
    data_path: StrictStr
    block_size: StrictInt
    epoch_length: StrictInt


class TrainCommandConfig(BaseCommandConfig):
    batch_size: StrictInt
    num_epochs: StrictInt
    nn_config: NNConfig
    train_config: DatasetConfig
    val_config: DatasetConfig


class GenerateCommandConfig(BaseCommandConfig):
    nn_config: NNConfig
    path_pretrained: StrictStr
