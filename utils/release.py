import argparse
import fileinput
import re
import sys
from subprocess import call, check_output

try:
    import tomllib  # python >= 3.11
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib  # python < 3.11


def replace_version_in_toml(new_major: str, new_minor: str, new_patch: str):
    file_toml = "pyproject.toml"
    current_section = None
    for line in fileinput.input(file_toml, inplace=True):
        section_match = re.match(r"\[(.+)\]", line)
        if section_match:
            current_section = section_match.group(1)
        if current_section == "project":
            line = re.sub(
                r"version = \"([0-9]+).([0-9]+).([0-9]+)\"",
                f'version = "{new_major}.{new_minor}.{new_patch}"',
                line,
            )
        sys.stdout.write(line)


def main(upgrade: str):  # noqa: C901
    branch = check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode()
    print("active branch:", branch)
    if branch != "development":
        print("to upgrade version, you should be on 'development' branch")
        print("change branch and try again")
        return

    ret = call(["git", "diff", "--staged", "--quiet"])
    if ret != 0:
        print("to upgrade version, there must be no staged file")
        print("clear stage and try again")
        return

    print("updating development branch using 'git pull'")
    ret = call(["git", "pull"])
    if ret != 0:
        print("git pull did not run successfully, aborting")
        return

    with open("pyproject.toml", "rt") as f:
        file_content = f.read()
    config_toml: dict = tomllib.loads(file_content)

    curr_version = config_toml["project"]["version"]
    version_splits = curr_version.split(".")
    old_major, old_minor, old_patch = version_splits
    new_major, new_minor, new_patch = version_splits

    if upgrade == "patch":
        new_patch = str(int(old_patch) + 1)
    elif upgrade == "minor":
        new_minor = str(int(old_minor) + 1)
        new_patch = "0"
    elif upgrade == "major":
        new_major = str(int(old_major) + 1)
        new_minor = "0"
        new_patch = "0"
    else:
        raise ValueError("The only upgrade allowed are 'major', 'minor' and 'patch'.")

    new_version = ".".join([new_major, new_minor, new_patch])
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
        return

    proceed = None
    while proceed not in {"y", "n", ""}:
        proceed = input(
            f"Upgrading to version {new_version}. Do you wish to proceed? [y/N]"
        )
        proceed = proceed.lower()

    if proceed == "y":
        replace_version_in_toml(
            new_major=new_major,
            new_minor=new_minor,
            new_patch=new_patch,
        )
        ret = call(["git", "checkout", "-b", tmp_branch_name])
        if ret != 0:
            print(f"cannot checkout to new branch {tmp_branch_name}")
            return
        call(["git", "add", "pyproject.toml"])
        ret = call(["git", "commit", "-m", f"chg: bump version to {new_version}"])
        if ret != 0:
            print("git commit failed")
            print("rolling back to previous version in pyproject.toml")
            replace_version_in_toml(
                new_major=old_major,
                new_minor=old_minor,
                new_patch=old_patch,
            )
            call(["git", "add", "pyproject.toml"])
            print("aborting")
            return

        print("version bump committed")
        ret = call(["git", "push", "--set-upstream", "origin", tmp_branch_name])
        if ret != 0:
            print("git push failed, try to push again manually")
            return

        print("version bump pushed")
        print("remember to open MR: a new tag will be registered after merge")
    else:
        print("upgrade interrupted")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "upgrade",
        type=str,
        choices=["patch", "minor", "major"],
        help="which tag to release",
    )
    args = parser.parse_args()
    main(args.upgrade)
