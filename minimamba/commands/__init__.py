import argparse
import ast
import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from importlib import import_module, metadata
from importlib.util import find_spec
from pathlib import Path
from typing import Optional

from minimamba.utils.exceptions import CommandFormatError, UnexpectedFileError

try:
    import tomllib  # python >= 3.11
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib  # python < 3.11

from artificonfig.core.constants import ConfigType
from artificonfig.core.models import BaseCommandConfig
from artificonfig.core.reader import ConfigReader
from artificonfig.core.writer import ConfigWriter

from minimamba.configs.models import GlobalContextConfig
from minimamba.utils.global_context import GlobalContextManager


class Callback:
    def __init__(self, module: str):
        self.module = module

    def __call__(self, config: BaseCommandConfig):
        command = import_module(self.module)
        command.main(config)

    def get_description(self) -> str:
        """Read the command description from the docstring of the main function.

        Returns:
            str: Description of the command

        """
        # use ast to avoid unnecessary import_module (that can be slow)
        spec = find_spec(self.module)

        if spec is None or spec.origin is None:
            raise CommandFormatError(f"Module {self.module} not found")

        with open(spec.origin) as f:  # type: ignore[arg-type, union-attr]
            file_tree = ast.parse(f.read())

        # find main function and its docstring
        doc = None
        for node in ast.walk(file_tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                body = node.body
                doc = ""  # empty string as default
                if (
                    body
                    and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                ):
                    doc = node.body[0].value.s  # type: ignore[attr-defined]
                    break

        if doc is None:
            raise CommandFormatError(f"Module {self.module} has no main function")

        return doc.split("\n\n")[0].strip()


def main(prog: Optional[str] = None) -> None:
    """Entry point of `minimamba`.

    It creates an argument parser and automatically adds all the available commands.
    It registers the callbacks corresponding to each command.

    Parameters:
    ----------
    prog : `Optional[str]`
        Name of the program

    """
    parser = ArgumentParser(
        description="MINIMAMBA\n" "Artificialy SA - https://www.artificialy.ch/",
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
    version = "unknown"
    try:
        version = metadata.version("models_proxy")  # get installed version
    except metadata.PackageNotFoundError:
        try:
            with open("pyproject.toml", "rt") as file:
                file_content = file.read()
            toml: dict = tomllib.loads(file_content)
            version = toml["project"]["version"]
        except FileNotFoundError:
            pass
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=version,
    )
    parser.add_argument(
        "-g",
        "--global-config",
        default=None,
        help="Path to global config file.",
        type=str,
    )
    subparsers = parser.add_subparsers(title="Commands")

    # each file in "minimamba/commands" defines a CLI entry-point for a command
    for filepath in Path(__file__).parent.iterdir():
        # skip files that begins with an underscore
        if filepath.name[0] in {"_", "."}:
            continue

        # only Python files for commands are allowed
        if filepath.is_dir() or "py" not in filepath.suffix:
            commands_dir = filepath.parent.relative_to(os.getcwd())
            raise UnexpectedFileError(
                f"{commands_dir} should contain only Python files for CLI commands, "
                f"please place '{filepath.name}' somewhere else"
            )

        _add_subparser_from_file(filepath, subparsers)


def _add_subparser_from_file(filepath: Path, subparsers: argparse._SubParsersAction):
    # create subparser
    cli_command_name = filepath.stem.replace("_", "-")
    subparser = subparsers.add_parser(cli_command_name)

    # register subparser callback as the 'main' function of 'callback_module'
    callback_module = f"minimamba.commands.{filepath.stem}"
    callback = Callback(callback_module)
    subparser.set_defaults(callback=callback, command_name=filepath.stem)
    subparser.add_argument(
        "-c",
        "--config",
        help="Path to configuration file for the command",
        type=str,
        required=True,
    )

    # create help string from command docstring
    help_str = callback.get_description()
    choice_action = subparsers._ChoicesPseudoAction(cli_command_name, (), help_str)
    subparsers._choices_actions.append(choice_action)


def _create_global_context(path_global_config: Optional[str], command_name: str):
    global_config: GlobalContextConfig
    if path_global_config is not None:
        global_config = ConfigReader(Path(path_global_config)).get_config()
    else:
        global_config = GlobalContextConfig(
            __config_class=".".join(
                [GlobalContextConfig.__module__, GlobalContextConfig.__name__]
            ),
            __config_type=ConfigType.CONFIG_SIMPLE,
        )
    gcm: GlobalContextManager = GlobalContextManager()
    gcm.setup_global_context(global_config, command_name=command_name)
