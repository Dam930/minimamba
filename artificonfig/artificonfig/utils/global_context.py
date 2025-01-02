import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from artificonfig.configs.models import GlobalContextConfig
from artificonfig.utils.exceptions import OperationNotAllowed
from artificonfig.utils.logging import generate_log_name
from artificonfig.utils.singleton import singleton

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GlobalContext:
    """Container for application-scope information
    Add fields as needed and handle them inside the
    _handle_additional_context_fields() method of the GlobalContextManager
    """

    path_serialization_dir: Path


@singleton
class GlobalContextManager:
    def __init__(self) -> None:
        self._global_context: GlobalContext
        self._config: GlobalContextConfig
        self._path_serialization_dir: Path
        self._initialized: bool = False

    def get_global_context(self) -> GlobalContext:
        return self._global_context

    def setup_global_context(self, config: GlobalContextConfig, command_name: str):
        if self._initialized:
            raise OperationNotAllowed("The GlobalContext is already initialized")

        self._config = config

        # Setup a local serialization dir
        self._path_serialization_dir = self._setup_serialization_dir(
            command_name=command_name
        )

        self._setup_logger()

        self._handle_additional_context_fields()

        self._initialized = True

    def _handle_additional_context_fields(self):
        # Add here the code to handle additional configurations
        # (accessible through self._config) and information to be
        # stored in the GlobalContext

        # Initialize the global context
        self._global_context = GlobalContext(
            path_serialization_dir=self._path_serialization_dir
        )

    def _setup_serialization_dir(self, command_name: str) -> Path:
        os.makedirs(self._config.working_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        path_serialization_dir = self._config.working_dir / f"{command_name}-{timestamp}"
        logger.debug("Creating local output folder `%s`", path_serialization_dir)
        if path_serialization_dir.exists():
            raise OperationNotAllowed(
                f"Serialization directory {path_serialization_dir} already exists."
            )
        path_serialization_dir.mkdir(parents=True)

        return path_serialization_dir

    def _setup_logger(self):
        loglevel = os.environ.get("LOGLEVEL", "INFO").upper()
        log_name = generate_log_name()
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%m/%d/%Y %H:%M:%S",
            level=loglevel,
            handlers=[
                logging.FileHandler(
                    os.path.join(self._path_serialization_dir, log_name), delay=True
                ),
                logging.StreamHandler(),
            ],
        )
