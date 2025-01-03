import logging
import torch
from configmanager.core.utils import get_target_class_from_config
import torch.utils
import torch.utils.data
import os
import requests

from minimamba.configs.models import GenerateCommandConfig
from minimamba.models.nn_model import NNModel

logger = logging.getLogger(__name__)


def main(config: GenerateCommandConfig):
    """Generate some sample data with Mamba.

    A command must receive a single config object as argument.

    Args:
        config (GenerateCommandConfig): config object
        defined into minimamba.config.models and that
        inherits from BaseCommandConfig
    """
    logger.info("Running %s", __name__)

    # Create the NN
    logger.info("Create NN")
    nn_model: NNModel = get_target_class_from_config(
        config.nn_config
    ).load_from_checkpoint(config.path_pretrained, config=config.nn_config)
    nn_model = nn_model.eval()

    input_file_path = "/tmp/file.txt"
    if not os.path.exists(input_file_path):
        data_url = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
        with open(input_file_path, "w") as f:
            f.write(requests.get(data_url).text)

    with open(input_file_path, "r") as f:
        data = f.read()

    # get all the unique characters that occur in this text
    chars = sorted(list(set(data)))

    # create a mapping from characters to integers
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}

    def encode(s):
        return [stoi[c] for c in s]  # encoder: take a string, output a list of integers

    def decode(l):
        return "".join(
            [itos[i] for i in l]
        )  # decoder: take a list of integers, output a string

    input_str = "Hello,"
    input_idx = torch.tensor(encode(input_str)).unsqueeze(0).to(nn_model.device)

    for i in range(50):
        out = nn_model(input_idx)
        next_token_idx = out[0, -1].argmax().item()
        input_idx = torch.cat(
            [
                input_idx,
                torch.tensor([next_token_idx]).unsqueeze(0).to(input_idx.device),
            ],
            -1,
        )
    output_str = decode(input_idx[0].tolist())
    logger.info("Produced the following string: %s", output_str)

    logger.info("Done")
