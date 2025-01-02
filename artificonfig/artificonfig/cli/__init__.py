from argparse import ArgumentParser, RawDescriptionHelpFormatter
from importlib import import_module, metadata
from pathlib import Path
from typing import Optional

from artificonfig.configs.models import GlobalContextConfig
from artificonfig.core.constants import ConfigType
from artificonfig.core.models import BaseCommandConfig
from artificonfig.core.reader import ConfigReader
from artificonfig.core.writer import ConfigWriter
from artificonfig.utils.global_context import GlobalContextManager


class Callback:
    def __init__(self, module: str):
        self.module = module

    def __call__(self, config: BaseCommandConfig):
        command = import_module(self.module)
        command.main(config)


def main(prog: Optional[str] = None) -> None:
    """Entry point of `artificonfig`.

    It creates an argument parser and automatically adds all the available commands.
    It registers the callbacks corresponding to each command.

    Parameters
    ----------
    prog : `Optional[str]`
        Name of the program
    """
    parser = ArgumentParser(
        description="PYTHON TEMPLATE\n" "Artificialy SA - https://www.artificialy.ch/",
        formatter_class=RawDescriptionHelpFormatter,
        prog=prog,
    )
    _create_subparsers(parser)

    args = parser.parse_args()
    if hasattr(args, "callback"):
        # A sub-command has been called: setup the global context
        _create_global_context(args.global_config, args.command_name)

        # Read and serialize the command configuration
        command_config: BaseCommandConfig = ConfigReader(Path(args.config)).get_config()
        writer: ConfigWriter = ConfigWriter()
        writer.write(
            command_config,
            GlobalContextManager().get_global_context().path_serialization_dir,
        )

        # Run the command
        args.callback(command_config)
    else:
        # display help when there are no args
        parser.print_help()


def _create_subparsers(parser: ArgumentParser):
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=metadata.version("artificonfig"),
    )
    parser.add_argument(
        "-g",
        "--global-config",
        default=None,
        help="Path to global config file.",
        type=str,
    )
    subparsers = parser.add_subparsers(title="Commands")

    # each file in "artificonfig/cli" defines a CLI entry-point for a command
    for filepath in Path(__file__).parent.iterdir():
        # skip files that begins with an underscore
        if filepath.name[0] == "_":
            continue

        _add_subparser_from_file(filepath, subparsers)


def _add_subparser_from_file(filepath: Path, subparsers: list):
    # create subparser
    cli_command_name = filepath.stem.replace("_", "-")
    subparser = subparsers.add_parser(cli_command_name)

    # register subparser callback as the 'main' function of 'callback_module'
    callback_module = f"artificonfig.commands.{filepath.stem}"
    subparser.set_defaults(callback=Callback(callback_module), command_name=filepath.stem)
    subparser.add_argument(
        "-c",
        "--config",
        help="Path to configuration file for the command",
        type=str,
        required=True,
    )

    # customize (description and arguments) of this subparser
    package = import_module(f"{__name__}.{filepath.stem}")
    package.customize_subparser(subparser)

    # create help string from description
    help_str = subparser.description.split("\n")[0]
    choice_action = subparsers._ChoicesPseudoAction(cli_command_name, (), help_str)
    subparsers._choices_actions.append(choice_action)


def _create_global_context(path_global_config: Optional[str], command_name: str):
    global_config: GlobalContextConfig
    if path_global_config is not None:
        global_config = ConfigReader(
            Path(path_global_config), "artificonfig.configs.models"
        ).get_config()
    else:
        global_config = GlobalContextConfig(
            __config_class=".".join(
                [GlobalContextConfig.__module__, GlobalContextConfig.__name__]
            ),
            __config_type=ConfigType.CONFIG_SIMPLE,
        )
    gcm: GlobalContextManager = GlobalContextManager()
    gcm.setup_global_context(global_config, command_name=command_name)
