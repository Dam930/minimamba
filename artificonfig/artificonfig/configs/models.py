from pathlib import Path
from typing import List

from pydantic import HttpUrl, SerializeAsAny, StrictFloat, StrictInt, StrictStr

from artificonfig.core.models import BaseCommandConfig, BaseConfig, BaseObjectConfig


class GlobalContextConfig(BaseConfig):
    working_dir: Path = Path.home() / ".artificonfig"


class ToolConfig(BaseObjectConfig):
    param_1: StrictStr
    param_2: StrictInt


class AdvancedToolConfig(ToolConfig):
    param_advanced: StrictFloat


class TestCommandConfig(BaseCommandConfig):
    param_1: StrictFloat
    tools: SerializeAsAny[List[ToolConfig]]
    url: HttpUrl
