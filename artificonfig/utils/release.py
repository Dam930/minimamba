import argparse
import fileinput
import os
import re
import sys
from enum import Enum
from subprocess import call, check_output

try:
    import tomllib  # python >= 3.11
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib  # python < 3.11


class UpgradeType(str, Enum):
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"
    BETA = "beta"
    STABLE = "stable"


def replace_version_in_toml(
    new_major: str, new_minor: str, new_patch: str, new_stability: str
):
    file_toml = "pyproject.toml"
    current_section = None
    for line in fileinput.input(file_toml, inplace=True):
        section_match = re.match(r"\[(.+)\]", line)
        if section_match:
            current_section = section_match.group(1)
        if current_section == "project":
            line = re.sub(
                r"version = \"([0-9]+).([0-9]+).([0-9]+[ab])\"",
                f'version = "{new_major}.{new_minor}.{new_patch}{new_stability}"',
                line,
            )
        sys.stdout.write(line)


def get_current_version() -> tuple[str, str, str, str]:
    with open("pyproject.toml", "rt") as f:
        file_content = f.read()
    config_toml: dict = tomllib.loads(file_content)

    curr_version = config_toml["project"]["version"]
    version_splits = curr_version.split(".")
    curr_major, curr_minor, curr_patch = version_splits
    if curr_patch[-1] in ["a", "b"]:
        curr_stability = curr_patch[-1]
        curr_patch = curr_patch[:-1]
    else:
        curr_stability = ""

    return curr_major, curr_minor, curr_patch, curr_stability


def get_new_version_from_upgrade_type(
    upgrade_type: UpgradeType, curr_version: tuple[str, str, str, str]
) -> tuple[str, str, str, str]:
    curr_major, curr_minor, curr_patch, curr_stability = curr_version
    new_major, new_minor, new_patch, new_stability = curr_version

    # When a numerical version update is done
    # an alpha version is created by default
    if upgrade_type == UpgradeType.PATCH:
        new_patch = str(int(curr_patch) + 1)
        new_stability = "a"
    elif upgrade_type == UpgradeType.MINOR:
        new_minor = str(int(curr_minor) + 1)
        new_patch = "0"
        new_stability = "a"
    elif upgrade_type == UpgradeType.MAJOR:
        new_major = str(int(curr_major) + 1)
        new_minor = "0"
        new_patch = "0"
        new_stability = "a"
    elif upgrade_type == UpgradeType.BETA:
        if curr_stability == "b":
            raise ValueError("Cannot upgrade: current version is already a beta version")
        new_stability = "b"
    elif upgrade_type == UpgradeType.STABLE:
        if curr_stability == "b":
            raise ValueError(
                "Cannot upgrade: current version is already a stable version"
            )
        new_stability = ""

    return new_major, new_minor, new_patch, new_stability


def is_upgrade_feasible(upgrade_type: UpgradeType) -> bool:
    branch = check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode()
    print("active branch:", branch)
    if upgrade_type in [UpgradeType.MAJOR, UpgradeType.MINOR, UpgradeType.PATCH]:
        if branch != "development":
            print("to upgrade version, you should be on 'development' branch")
            print("change branch and try again")
            return False

        ret = call(["git", "diff", "--staged", "--quiet"])
        if ret != 0:
            print("to upgrade version, there must be no staged file")
            print("clear stage and try again")
            return False

        print("updating development branch using 'git pull'")
        ret = call(["git", "pull"])
        if ret != 0:
            print("git pull did not run successfully, aborting")
            return False
    elif upgrade_type in [UpgradeType.BETA, UpgradeType.STABLE]:
        if not os.environ.get("GITLAB_CI", False):
            print("beta and stable upgrade can be done only from a CI pipeline")
            return False

    return True


def main(upgrade_type: UpgradeType):
    if not is_upgrade_feasible(upgrade_type):
        exit(1)
    old_major, old_minor, old_patch, old_stability = get_current_version()
    new_major, new_minor, new_patch, new_stability = get_new_version_from_upgrade_type(
        upgrade_type=upgrade_type,
        curr_version=(old_major, old_minor, old_patch, old_stability),
    )

    new_version = ".".join([new_major, new_minor, new_patch]) + new_stability

    tmp_branch_name = f"bump-{new_version}"

    local_branches = (
        check_output(["git", "branch", "--format=%(refname:short)"])
        .strip()
        .decode()
        .split("\n")
    )

    if tmp_branch_name in local_branches:
        print(
            f"upgrade script has to create branch '{tmp_branch_name}', but already exists"
        )
        exit(1)

    # Ask confirmation only when doing manual upgrading
    if upgrade_type in [UpgradeType.PATCH, UpgradeType.MAJOR, UpgradeType.MINOR]:
        proceed = None
        while proceed not in {"y", "n", ""}:
            proceed = input(
                f"Upgrading to version {new_version}. Do you wish to proceed? [y/N]"
            )
            proceed = proceed.lower()
    else:
        proceed = "y"

    if proceed == "y":
        ret = call(["git", "checkout", "-b", tmp_branch_name])
        if ret != 0:
            print(f"cannot checkout to new branch {tmp_branch_name}")
            return

        print("Replacing version in .toml")
        replace_version_in_toml(
            new_major=new_major,
            new_minor=new_minor,
            new_patch=new_patch,
            new_stability=new_stability,
        )
        print(get_current_version())

        call(["git", "add", "pyproject.toml"])
        ret = call(["git", "commit", "-m", f"chg: bump version to {new_version}"])
        if ret != 0:
            print("git commit failed")
            print("rolling back to previous version in pyproject.toml")
            replace_version_in_toml(
                new_major=old_major,
                new_minor=old_minor,
                new_patch=old_patch,
                new_stability=old_stability,
            )
            call(["git", "add", "pyproject.toml"])
            print("aborting")
            exit(1)

        print("version bump committed")
        ret = call(["git", "push", "--set-upstream", "origin", tmp_branch_name])
        if ret != 0:
            print("git push failed, try to push again manually")
            exit(1)

        print("version bump pushed")
        if upgrade_type not in [UpgradeType.BETA, UpgradeType.STABLE]:
            print("remember to open MR: a new tag will be registered after merge")
    else:
        print("upgrade interrupted")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "upgrade",
        type=str,
        choices=[t.value for t in UpgradeType],
        help="upgrate type to perform",
    )

    args = parser.parse_args()
    upgrade_type = args.upgrade
    main(upgrade_type)
