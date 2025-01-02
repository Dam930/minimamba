import json
from pathlib import Path

from artificonfig.core import constants as c
from artificonfig.core.constants import ConfigType
from artificonfig.core.models import BaseConfig, BaseSimpleConfig
from artificonfig.core.utils import (
    get_file_from_config_link,
    is_field_a_config_link,
    is_field_a_config_node,
)
from artificonfig.utils.dynamic_importer import DynamicImporter
from artificonfig.utils.exceptions import ConfigurationError


class ConfigReader:
    def __init__(self, path_file: Path) -> None:
        if not path_file.exists():
            raise ConfigurationError(f"Config file {path_file} does not exist")

        self._root_config: Path = self._find_config_root(path_file)

        self._config: BaseConfig = self._read_config_from_file(path_file)

    def _find_config_root(self, path_file: Path) -> Path:
        found = False
        curr_path = path_file
        while not found:
            if curr_path.name == "":
                raise ConfigurationError(
                    f"Could not find config root for file {path_file}."
                    + "\nThe config file must be placed in a folder named 'configs' or "
                    + "in a subfolder of it."
                )
            if curr_path.is_dir() and curr_path.name == "configs":
                found = True
            else:
                curr_path = curr_path.parent

        return curr_path

    def _read_config_from_file(self, path_file) -> BaseConfig:
        with open(path_file, "rt", encoding="utf-8") as json_file:
            dict_config = json.load(json_file)

        return self._parse_config_node(dict_config)

    def _create_config_from_dict(self, config_dict: dict) -> BaseConfig:
        config_class = config_dict[c.KEY_CONFIG_CLASS]

        index_split = config_class.rfind(".")
        module = config_class[:index_split]
        class_name = config_class[index_split + 1 :]

        return DynamicImporter(module, class_name).get_instance(**config_dict)

    def _parse_config_node(self, dict_config_node: dict) -> BaseConfig:
        # The config dict must be flattened and its parameters parsed
        # to be converted into a config object
        config_type = ConfigType(list(dict_config_node.keys())[0])

        dict_meta: dict = dict_config_node[config_type.value]
        dict_convertible = self._parse_dict(dict_meta[c.KEY_PARAMS])
        dict_convertible[c.KEY_CONFIG_TYPE] = config_type
        # Add the remaining key to the convertible dict parameters
        dict_meta.pop(c.KEY_PARAMS)
        for k, v in dict_meta.items():
            dict_convertible[k] = v

        return self._create_config_from_dict(dict_convertible)

    def _parse_dict(self, dict_field: dict) -> dict:
        for key in dict_field:
            val_field = dict_field[key]

            # Field is a config node
            if is_field_a_config_node(val_field):
                config_node = self._parse_config_node(val_field)
                dict_field[key] = config_node
            # Field is a config link
            elif is_field_a_config_link(val_field):
                config_node = self._parse_config_link(val_field)
                dict_field[key] = config_node
            # Field is a list (could contain nodes and/or links)
            elif isinstance(val_field, list):
                dict_field[key] = self._parse_list(val_field)
            # Field is a dict that could contain config nodes/and or links
            elif isinstance(val_field, dict):
                dict_field[key] = self._parse_dict(val_field)

        return dict_field

    def _parse_config_link(self, link_field: dict) -> BaseSimpleConfig:
        config_link = link_field[c.KEY_CONFIG_LINK]

        path_node_file = get_file_from_config_link(config_link, self._root_config)
        if not path_node_file.exists():
            raise ConfigurationError(f"Linked file {path_node_file} does not exists")

        config_node: BaseSimpleConfig = self._read_config_from_file(path_node_file)

        # Save the link that generated the config object to facilitate serialization
        config_node.config_link = config_link

        return config_node

    def _parse_list(self, list_field: list) -> list:
        parsed_list = []
        for el in list_field:
            if is_field_a_config_node(el):
                config_node = self._parse_config_node(el)
                parsed_list.append(config_node)
            elif is_field_a_config_link(el):
                config_node = self._parse_config_link(el)
                parsed_list.append(config_node)
            # Field is a list (could contain nodes and/or links)
            elif isinstance(el, list):
                parsed_list.append(self._parse_list(el))
            # Field is a dict that could contain config nodes/and or links
            elif isinstance(el, dict):
                parsed_list.append(self._parse_dict(el))
            # Simple value
            else:
                parsed_list.append(el)

        return parsed_list

    def get_config(self) -> BaseConfig:
        return self._config
