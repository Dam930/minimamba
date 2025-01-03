from enum import Enum


class ConfigType(str, Enum):
    CONFIG_SIMPLE = "@SIMPLE_CONFIG"
    CONFIG_COMMAND = "@COMMAND_CONFIG"
    CONFIG_OBJECT = "@OBJECT_CONFIG"


KEY_CONFIG_TYPE = "__config_type"
KEY_PARAMS = "__config_params"
KEY_CONFIG_CLASS = "__config_class"
KEY_TARGET_CLASS = "__target_class"
KEY_CONFIG_LINK = "@CONFIG_LINK"
