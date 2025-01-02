import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from utils.input_checks import (
    check_choice_in_list,
    check_email,
    check_git_url,
    check_min_len,
    check_name,
    is_empty,
)

project_root = Path(".")
file_setup = project_root / "setup.py"


def ask_for_yn_input(message: str) -> bool:
    valid = False
    bool_val = False
    while not valid:
        choice = input(message).lower().strip()
        valid = check_choice_in_list(choice, ["y", "n"])
        if valid:
            bool_val = choice == "y"

    return bool_val


def recursive_sub(path: Path, pattern: str, replacement: str) -> None:
    for child_path in path.glob("*"):
        if child_path.is_dir():
            if child_path.name[0] == ".":
                continue  # skip hidden folders
            if child_path.name == "__pycache__":
                continue
            recursive_sub(child_path, pattern, replacement)
        else:
            with open(child_path, "rt") as file:
                try:
                    file_content = file.read()
                except UnicodeDecodeError:
                    continue

            if str(child_path.absolute()) == __file__:
                continue  # do not change occurences in this file

            num_occurrences = len(re.findall(pattern, file_content))
            if num_occurrences == 0:
                continue

            print(f"replacing {num_occurrences} occurences in file {str(child_path)}")
            new_content = re.sub(pattern, replacement, file_content)
            with open(child_path, "wt") as file:
                file.write(new_content)


def read_project_info() -> Tuple[str, str, str, str, str]:
    valid = False
    while not valid:
        name = input("Enter project name: ").strip()
        valid = check_min_len(name) and check_name(name, allow_dash=False)

    valid = False
    default = "An Artificialy SA project"
    while not valid:
        description = input(f"Enter project description [{default}]: ").strip()
        if is_empty(description):
            description = default

        valid = check_min_len(description)

    valid = False
    default = "python,machine-learning"
    while not valid:
        keywords = input(f"Enter project keywords, comma separated [{default}]: ").strip()
        if is_empty(keywords):
            keywords = default

        valid = check_min_len(keywords)

    valid = False
    default = "Artificialy SA"
    while not valid:
        author_name = input(f"Enter author name [{default}]: ").strip()
        if is_empty(author_name):
            author_name = default

        valid = check_min_len(author_name)

    valid = False
    default = "info@artificialy.com"
    while not valid:
        author_email = input(f"Enter author email [{default}]: ").strip()
        if is_empty(author_email):
            author_email = default

        valid = check_email(author_email)

    return name, description, keywords, author_name, author_email


def rename(old_name: str, new_name: str) -> None:
    if not (project_root / old_name).exists():
        print(f"{str(project_root / old_name)} directory does not exist, aborting")
        exit(1)

    if (project_root / new_name).exists():
        print(f"{str(project_root / new_name)} directory already exists, aborting")
        exit(1)

    print(f"moving {str(project_root / old_name)} to {str(project_root / new_name)}")
    shutil.move(project_root / old_name, project_root / new_name)

    recursive_sub(project_root, old_name, new_name)

    old_name_uppercase = old_name.replace("_", " ").upper()
    new_name_uppercase = new_name.replace("_", " ").upper()
    recursive_sub(project_root, old_name_uppercase, new_name_uppercase)

    old_name_dash = old_name.replace("_", "-")
    new_name_dash = new_name.replace("_", "-")
    recursive_sub(project_root, old_name_dash, new_name_dash)


def fill_setup(description: str, keywords: str, author: str, author_email: str) -> None:
    lines = []
    with open(file_setup, "r") as f:
        for line in f:
            line = line.rstrip()

            if 'description="Add here description."' in line:
                line = line.replace(
                    'description="Add here description."', f'description="{description}"'
                )
            if 'keywords="Add here keywords"' in line:
                line = line.replace(
                    'keywords="Add here keywords"', f'keywords="{keywords}"'
                )
            if 'author="Add here author"' in line:
                line = line.replace('author="Add here author"', f'author="{author}"')
            if 'author_email="Add here author mail"' in line:
                line = line.replace(
                    'author_email="Add here author mail"',
                    f'author_email="{author_email}"',
                )

            # Add new line character to use writelines function below
            line += "\n"

            lines.append(line)

    with open(file_setup, "w") as f:
        f.writelines(lines)


def update_python_version(project_name: str, python_version: str) -> None:
    min_python_minor = int(python_version.split(".")[1])
    max_python_minor = min_python_minor + 1

    # Update file with python version checks
    file_python_version = project_root / project_name / "__init__.py"
    lines = []
    with open(file_python_version, "r") as f:
        for line in f:
            line = line.rstrip()

            if line.startswith("_MIN_PYTHON_MINOR = "):
                line = f"_MIN_PYTHON_MINOR = {min_python_minor}"
            if line.startswith("_MAX_PYTHON_MINOR = "):
                line = f"_MAX_PYTHON_MINOR = {max_python_minor}"

            # Add new line character to use writelines function below
            line += "\n"

            lines.append(line)

    with open(file_python_version, "w") as f:
        f.writelines(lines)

    # Update README.md
    path_readme = project_root / "README.md"
    lines = []
    with open(path_readme, "r") as f:
        for line in f:
            line = line.rstrip()

            if "Python 3.9" in line:
                line = line.replace("Python 3.9", f"Python 3.{min_python_minor}")
            if "python=3.9" in line:
                line = line.replace("python=3.9", f"python=3.{min_python_minor}")

            # Add new line character to use writelines function below
            line += "\n"

            lines.append(line)

    with open(path_readme, "w") as f:
        f.writelines(lines)

    # Update .gitlab-ci.yml
    path_ci = project_root / ".gitlab-ci.yml"
    lines = []
    with open(path_ci, "r") as f:
        for line in f:
            line = line.rstrip()

            if "image: python:3.9" in line:
                line = line.replace(
                    "image: python:3.9", f"image: python:3.{min_python_minor}"
                )

            # Add new line character to use writelines function below
            line += "\n"

            lines.append(line)

    with open(path_ci, "w") as f:
        f.writelines(lines)


def setup_conda_env(project_name: str) -> Optional[str]:
    create_env = ask_for_yn_input(
        "Do you want to create a conda environment for the project? y/n "
    )
    if not create_env:
        return None

    print("Setting up conda environment")

    valid = False
    default = f"{os.environ.get('USER')}_{project_name}"
    while not valid:
        env_name = input(f"Enter conda env name [{default}]: ").strip()
        if is_empty(env_name):
            env_name = default

        valid = check_min_len(env_name) and check_name(env_name, allow_dash=True)

    valid = False
    default = "3.9"
    while not valid:
        python_version = input(
            "Choose the Python version to install. Allowed: [3.9, 3.10, 3.11]. "
            + f"Default: {default}\nVersion: "
        )
        if is_empty(python_version):
            python_version = default

        valid = check_choice_in_list(python_version, ["3.9", "3.10", "3.11"])

    update_python_version(project_name, python_version)

    # Setup conda environment
    out = subprocess.run(
        f"conda create -n {env_name} python={python_version}", shell=True
    )
    out.check_returncode()

    return env_name


def setup_git_repo() -> None:
    setup_remote = ask_for_yn_input("Do you want to setup a Git remote repository? y/n ")

    if setup_remote:
        valid = False
        while not valid:
            remote_url = input("Enter Git remote repository URL: ").strip()
            valid = check_git_url(remote_url)

        print("Erasing old .git directory")
        out = subprocess.run(["rm", "-rf", ".git"])
        out.check_returncode()
        print("Committing changes of initialization script")
        out = subprocess.run(["git", "init", "--initial-branch=development"])
        out.check_returncode()
        out = subprocess.run(["git", "add", "."])
        out.check_returncode()
        out = subprocess.run(["git", "commit", "-m", "Initial commit"])
        out.check_returncode()

        out = subprocess.run(
            ["git", "remote", "add", "origin", "-m", "development", remote_url]
        )
        out.check_returncode()
        out = subprocess.run(["git", "push", "origin", "development"])
        out.check_returncode()
    else:
        print(
            "Skipping setup of remote repository\n"
            + "This can be done later calling:\n"
            + "git remote add origin -m <branch_name> <remote_url>\n"
            + "git push origin <branch_name>"
        )
        print("Committing changes of initialization script")
        out = subprocess.run(["git", "add", "."])
        out.check_returncode()
        out = subprocess.run(["git", "commit", "-m", "Initial commit"])
        out.check_returncode()


def main() -> None:
    print("Project initialization")
    name, description, keywords, author_name, author_email = read_project_info()

    rename("python_template", name)
    fill_setup(description, keywords, author_name, author_email)
    env_name = setup_conda_env(name)
    setup_git_repo()

    print("\n\nExecution ended")
    if env_name is None:
        print(
            "To complete the initialization follow the instructions "
            + "in the Initialization section of the README file"
        )
    else:
        print(
            "To complete the initialization run: "
            + f"\nconda activate {env_name}"
            + "\nmake dev"
        )


if __name__ == "__main__":
    main()
