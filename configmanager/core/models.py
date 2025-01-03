from typing import Optional

from pydantic import BaseModel, Field, StrictStr

from configmanager.core.constants import (
    KEY_CONFIG_CLASS,
    KEY_CONFIG_LINK,
    KEY_CONFIG_TYPE,
    KEY_TARGET_CLASS,
    ConfigType,
)


class BaseConfig(BaseModel):
    config_type: ConfigType = Field(alias=KEY_CONFIG_TYPE)
    config_class: StrictStr = Field(alias=KEY_CONFIG_CLASS)


# Extend BaseCommandConfig to configure entry points of the application
class BaseCommandConfig(BaseConfig):
    pass


class BaseSimpleConfig(BaseConfig):
    config_link: Optional[StrictStr] = Field(alias=KEY_CONFIG_LINK, default=None)


# Extend BaseObjConfig to configure instantiable objects
class BaseObjectConfig(BaseSimpleConfig):
    target_class: StrictStr = Field(alias=KEY_TARGET_CLASS)
