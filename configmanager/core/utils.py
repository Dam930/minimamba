from pathlib import Path
from typing import Any

from configmanager.core import constants as c
from configmanager.core.constants import ConfigType
from configmanager.core.models import BaseObjectConfig
from configmanager.utils.dynamic_importer import DynamicImporter


def create_obj_from_config(config: BaseObjectConfig) -> object:
    index_split = config.target_class.rfind(".")
    module = config.target_class[:index_split]
    class_name = config.target_class[index_split + 1 :]

    return DynamicImporter(module, class_name).get_instance(**{"config": config})


def get_target_class_from_config(config: BaseObjectConfig) -> type:
    index_split = config.target_class.rfind(".")
    module = config.target_class[:index_split]
    class_name = config.target_class[index_split + 1 :]

    return DynamicImporter(module, class_name).get_class()


def is_field_a_config_link(val: Any) -> bool:
    # Config nodes are dictionaries containing the field KEY_NODE
    if isinstance(val, dict) and set(val.keys()) == set([c.KEY_CONFIG_LINK]):
        return True

    return False


def is_field_a_config_node(val: Any) -> bool:
    # Config nodes are dictionaries containing a single key with the config type
    if isinstance(val, dict):
        list_keys = list(val.keys())
        if len(list_keys) == 1 and list_keys[0] in [t.value for t in ConfigType]:
            return True

    return False


def get_file_from_config_link(config_link: str, root_config: Path):
    splits = config_link.split(".")

    path_dir = root_config
    for split in splits[:-1]:
        path_dir = path_dir / split

    path_config = path_dir / f"{splits[-1]}.json"

    return path_config
