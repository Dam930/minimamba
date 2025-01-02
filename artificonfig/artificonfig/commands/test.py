import logging

from artificonfig.configs.models import TestCommandConfig

logger = logging.getLogger(__name__)


def main(config: TestCommandConfig):
    """Test command.

    Intended only for development purposes.

    Args:
        config (TestConfig): config object
    """
    logger.info("Running %s", __name__)

    logger.info("Config: %s", config)

    logger.info("Done")
