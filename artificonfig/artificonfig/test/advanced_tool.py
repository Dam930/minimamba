from artificonfig.configs.models import AdvancedToolConfig
from artificonfig.test.tool import Tool


class AdvancedTool(Tool):
    def __init__(self, config: AdvancedToolConfig) -> None:
        super().__init__(config)
        self._param_advanced = config.param_advanced

    def get_param_advanced(self) -> str:
        return self._param_advanced
