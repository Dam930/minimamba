import logging
import torch
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning.callbacks import ModelCheckpoint
from configmanager.core.utils import create_obj_from_config
import torch.utils
import torch.utils.data

from minimamba.configs.models import TrainCommandConfig
from minimamba.models.nn_model import NNModel

logger = logging.getLogger(__name__)


def main(config: TrainCommandConfig):
    """Train Mamba.

    A command must receive a single config object as argument.

    Args:
        config (TrainCommandConfig): config object
        defined into minimamba.config.models and that
        inherits from BaseCommandConfig
    """
    logger.info("Running %s", __name__)

    logger.info("Load datasets")

    # Create the Datasets
    dataset_train: torch.utils.data.Dataset = create_obj_from_config(
        config.train_config
    )
    dataset_val: torch.utils.data.Dataset = create_obj_from_config(config.val_config)
    dataloader_train = torch.utils.data.DataLoader(
        dataset_train,
        config.batch_size,
        num_workers=config.num_workers,
        persistent_workers=True,
    )
    dataloader_val = torch.utils.data.DataLoader(
        dataset_val,
        config.batch_size,
        num_workers=config.num_workers,
        persistent_workers=True,
    )

    # Create the NN
    logger.info("Create NN")
    nn_model: NNModel = create_obj_from_config(config.nn_config)

    # Train
    wandb_logger = WandbLogger(log_model="all")
    checkpoint_callback = ModelCheckpoint(
        monitor="val_loss",
        mode="min",
        dirpath="models",
        filename="checkpoint-{epoch:02d}",
        every_n_epochs=1,
    )
    trainer = Trainer(
        max_epochs=config.num_epochs,
        log_every_n_steps=config.batch_size,
        logger=wandb_logger,
        callbacks=[checkpoint_callback],
    )
    trainer.fit(nn_model, dataloader_train, dataloader_val)

    logger.info("Done")
