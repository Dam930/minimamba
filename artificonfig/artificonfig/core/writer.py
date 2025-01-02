import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from artificonfig.core import constants as c
from artificonfig.core.constants import ConfigType
from artificonfig.core.models import BaseConfig


class ConfigWriter:
    def __init__(self) -> None:
        self._path_root_config: Path
        self._complete_config: dict

    def write(self, config: BaseConfig, path_out_dir: Path):
        dict_config = config.model_dump(mode="json", by_alias=True)

        dict_config = self._adapt_dumped_node(dict_config)

        with open(path_out_dir / "config.json", "w") as outfile:
            json.dump(dict_config, outfile, indent=4)

    def _adapt_dumped_node(self, dict_config: dict) -> dict:
        # Remove config links information
        # (configuration is stored a single config file)
        if c.KEY_CONFIG_LINK in dict_config:
            dict_config.pop(c.KEY_CONFIG_LINK)

        # Adapt all subconfigs recursively
        for field_name, field_value in dict_config.items():
            if self._is_field_a_config_node(field_value):
                # Config node fields are config objects converted to dict
                adapted_config_node = self._adapt_dumped_node(field_value)
                dict_config[field_name] = adapted_config_node
            elif isinstance(field_value, list):
                dict_config[field_name] = self._adapt_dumped_list(field_value)
            # Field is a dict that could contain config nodes/and or links
            elif isinstance(field_value, dict):
                dict_config[field_name] = self._adapt_dumped_dict(field_value)

        return self._organize_metadata(dict_config)

    def _adapt_dumped_list(self, dumped_list: list) -> list:
        adapted_list = []
        for element in dumped_list:
            if self._is_field_a_config_node(element):
                adapted_list.append(self._adapt_dumped_node(element))
            elif isinstance(element, dict):
                adapted_list.append(self._adapt_dumped_dict(element))
            elif isinstance(element, list):
                adapted_list.append(self._adapt_dumped_list(element))
            # Simple field
            else:
                adapted_list.append(element)

        return adapted_list

    def _adapt_dumped_dict(self, dumped_dict: dict) -> dict:
        dumped_dict = deepcopy(dumped_dict)
        for field_name, field_value in dumped_dict.items():
            if self._is_field_a_config_node(field_value):
                dumped_dict[field_name] = self._adapt_dumped_node(field_value)
            elif isinstance(field_value, list):
                dumped_dict[field_name] = self._adapt_dumped_list(field_value)
            elif isinstance(field_value, dict):
                dumped_dict[field_name] = self._adapt_dumped_dict(field_value)

        return dumped_dict

    def _organize_metadata(self, dict_config: dict):
        # Move the config type, class and target class to the metadata level
        config_type = dict_config[c.KEY_CONFIG_TYPE]
        config_class = dict_config[c.KEY_CONFIG_CLASS]
        dict_config.pop(c.KEY_CONFIG_TYPE)
        dict_config.pop(c.KEY_CONFIG_CLASS)
        if config_type == ConfigType.CONFIG_OBJECT.value:
            target_class = dict_config[c.KEY_TARGET_CLASS]
            dict_config.pop(c.KEY_TARGET_CLASS)
        else:
            target_class = None

        dict_config = {
            config_type: {
                c.KEY_CONFIG_CLASS: config_class,
                c.KEY_PARAMS: dict_config,
            }
        }

        if target_class is not None:
            dict_config[config_type][c.KEY_TARGET_CLASS] = target_class

        return dict_config

    def _is_field_a_config_node(self, field_val: Any):
        if (
            isinstance(field_val, dict)
            and c.KEY_CONFIG_TYPE in field_val
            and c.KEY_CONFIG_CLASS in field_val
        ):
            return True

        return False
