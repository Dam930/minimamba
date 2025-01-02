import pytorch_lightning as pl
from minimamba.configs.models import NNConfig


class NNModel(pl.LightningModule):
    """Abstract Class of a NN Model

    Args:
        config (NNConfig): config of the NN Model
    """

    def __init__(self, config: NNConfig) -> None:
        super().__init__()
