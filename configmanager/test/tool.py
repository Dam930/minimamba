from configmanager.configs.models import ToolConfig


class Tool:
    def __init__(self, config: ToolConfig) -> None:
        self._param_1: str = config.param_1
        self._param_2: int = config.param_2

    def get_param_1(self) -> str:
        return self._param_1

    def get_param_2(self) -> int:
        return self._param_2
