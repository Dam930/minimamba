import argparse


def customize_subparser(subparser: argparse.ArgumentParser):
    """Customize the subparser by adding a description to this command.

    Parameters
    ----------
    subparser : `argparse.ArgumentParser`
        The subparser to customize.
    """
    subparser.description = "Test command.\n\nIntended only for development purposes."
