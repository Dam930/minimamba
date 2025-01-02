import torch
import numpy as np
from minimamba.configs.models import DatasetConfig


class Dataset(torch.utils.data.Dataset):
    """Load dataset from a bin file

    Args:
        config (DatasetConfig): configuration of the dataset
    """

    def __init__(self, config: DatasetConfig) -> None:
        super().__init__()
        # Define input embeddings
        self._data = np.memmap(config.data_path, dtype=np.uint16, mode="r")
        self._block_size: int = config.block_size
        self._epoch_length: int = config.epoch_length

    def __len__(self) -> int:
        return self._epoch_length

    def __getitem__(self, idx: int) -> tuple[torch.tensor, torch.tensor]:
        i = np.random.randint(len(self._data) - self._block_size)
        x = torch.from_numpy((self._data[i : i + self._block_size]).astype(np.int64))

        y = torch.from_numpy(
            (self._data[i + 1 : i + 1 + self._block_size]).astype(np.int64)
        )
        return x, y
