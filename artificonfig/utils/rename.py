import argparse
import re
import shutil
from pathlib import Path


def recursive_sub(path: Path, pattern: str, replacement: str):
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


def main(old_name: str, new_name: str, old_url_name: str, new_url_name: str):
    cwd = Path(".")

    if not (cwd / old_name).exists():
        print(f"{str(cwd / old_name)} directory does not exist, aborting")
        exit(1)

    if (cwd / new_name).exists():
        print(f"{str(cwd / new_name)} directory already exists, aborting")
        exit(1)

    if "-" in new_name:
        print("new name contains '-' (use '_' instead), aborting")
        exit(1)

    print(f"moving {str(cwd / old_name)} to {str(cwd / new_name)}")
    shutil.move(cwd / old_name, cwd / new_name)

    recursive_sub(cwd, old_name, new_name)
    recursive_sub(cwd, old_url_name, new_url_name)

    old_name_uppercase = old_name.replace("_", " ").upper()
    new_name_uppercase = new_name.replace("_", " ").upper()
    recursive_sub(cwd, old_name_uppercase, new_name_uppercase)

    old_name_dash = old_name.replace("_", "-")
    new_name_dash = new_name.replace("_", "-")
    recursive_sub(cwd, old_name_dash, new_name_dash)


parser = argparse.ArgumentParser()
parser.add_argument(
    "--new-name",
    "-n",
    type=str,
    required=True,
    help="which tag to release",
)
parser.add_argument(
    "--url-name",
    "-u",
    type=str,
    required=True,
    help="which url to publish",
)
args = parser.parse_args()


if __name__ == "__main__":
    main("artificonfig", args.new_name, "project_remote_url", args.url_name)
