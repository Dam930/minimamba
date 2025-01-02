import argparse
import json
import os
import re

import requests
from pipreqs.pipreqs import get_all_imports, get_pkg_names


def get_imports_info(
    imports, pypi_server="https://pypi.python.org/pypi/", proxy=None
) -> tuple[dict, dict]:
    result, result_not_in_pypi = dict(), dict()
    for item in imports:
        response = requests.get(f"{pypi_server}{item}/json", proxies=proxy)
        if response.status_code == 200:
            if hasattr(response.content, "decode"):
                data = response.content.decode()
            else:
                data = response.content
            keys_json = dict(json.loads(data))
            result[item] = keys_json["info"]["version"]
        elif response.status_code >= 300:
            result_not_in_pypi[item] = [response.status_code, response.reason]
    return result, result_not_in_pypi


def recursive_search(path: str) -> set:
    reqs = set()
    for child_path in os.listdir(path):
        if os.path.isdir(child_path):
            if child_path[0] == ".":
                continue  # skip hidden folders
            if child_path == "__pycache__":
                continue  # skip pycache folders
            candidates = recursive_search(os.path.join(path, child_path))
        candidates = get_all_imports(path=path)  # return a list
        reqs.update(candidates)
    return reqs


def check_is_private_repo(pkg_version: str) -> int:
    if pkg_version[:3] == "git":
        print(
            "* It seems you are trying to define as a "
            "requirement a git library.\n"
            "Please, add it with this format:\n"
            "    <package_name> @ git+https://github.com/"
            "<github_repo_name>/<library_name>\n"
        )
        return True
    return False


def read_requirements_file(check_file) -> tuple[set, int]:
    specified_imports = set()
    check_file_path = os.path.join(os.path.curdir, check_file)
    if os.path.exists(check_file_path):
        with open(check_file_path, "r") as file:
            flag_exit = 0
            list_lines = file.readlines()
        for pkg_version in list_lines:
            pkg_version = pkg_version.strip()
            if len(pkg_version) == 0:
                continue
            if pkg_version[0] == "#":
                continue
            flag_exit += check_is_private_repo(pkg_version)
            pkg_no_version = re.sub("[<>=~!#@].*", "", pkg_version).strip()
            specified_imports.update([pkg_no_version])
        return specified_imports, flag_exit
    else:
        return set(), 0


def auto_add_not_listed(not_listed: set, check_file: str) -> None:
    check_file_path = os.path.join(os.path.curdir, check_file)
    # check if there is "\n" at the end of the file
    with open(check_file_path, "r") as file_to_write:
        list_lines = file_to_write.readlines()
    bool_end_of_file = False
    if len(list_lines):
        bool_end_of_file = "\n" not in list_lines[-1]
    # write packages not imported
    with open(check_file_path, "a+") as file_to_write:
        if bool_end_of_file:
            file_to_write.write("\n")
        for package in not_listed:
            file_to_write.write(f"{package}\n")


def check_imports(
    check_file: str, imports: dict, imports_not_in_pypi: dict, auto: bool
) -> tuple[int, int]:
    requirements, flag_exit = read_requirements_file(check_file)
    # check packages existing in pypi.org
    imported = set(imports.keys())
    not_listed = imported.difference(requirements)
    # check exceptions (packages not found in pypi.org)
    imported_not_from_pypi = set(imports_not_in_pypi.keys())
    not_listed_and_not_in_pypi = imported_not_from_pypi.difference(requirements)
    flags = print_error_scripts(check_file, not_listed, not_listed_and_not_in_pypi, auto)
    flag_exit += flags[0]
    flag_warn = flags[1]
    return flag_exit, flag_warn


def print_error_scripts(
    check_file: str, not_listed: set, not_listed_and_not_in_pypi: set, auto: bool
) -> tuple[int, int]:
    flag_exit = flag_warn = 0
    if not_listed or not_listed_and_not_in_pypi:
        print("* Some imports are not specified in the requirements.txt file.\n")
        if not_listed:
            if auto:
                auto_add_not_listed(not_listed, check_file)
            else:
                print(
                    "KNOWN : the following imports are available "
                    "at https://pypi.python.org/pypi/.\n"
                )
                for req in not_listed:
                    print(f"{req}")
                print("")
                print(
                    "Please, add them to the requirements.txt file manually or "
                    "if you desire to do it automaticaly use --auto-add option "
                    "as follows:\n"
                    "    $ python -m utils.requirement --auto-add\n"
                )
                flag_exit = 1
        if not_listed_and_not_in_pypi:
            print(
                "UNKNOWN : "
                "the following imports are not available at "
                "https://pypi.python.org/pypi/.\n"
            )
            for req in not_listed_and_not_in_pypi:
                print(f"{req}")
            print("")
            print(
                "Please, check their origin since the --auto-add"
                " option is not dealing with them (it simply ignores them).\n"
                "Then, add them to the requirements.txt file manually.\n"
                "If any of these come from a private git "
                "library please add them with this format:\n"
                "    <package_name> @ git+https://github.com/"
                "<github_repo_name>/<library_name>\n"
            )
            flag_warn = 1
    return flag_exit, flag_warn


def main(auto: bool) -> None:
    print("--------------{ >.< }-------------------")
    # define the directory where read the imports
    cwd = os.path.abspath(os.path.join(os.path.curdir, "artificonfig"))
    # recursive check the imports
    all_imports = recursive_search(cwd)
    # change from list to set: unique candidates are kept
    unique_imports = set(get_pkg_names(all_imports))
    # get info about which packages are availble from pipy.org and which not
    imports, imports_not_in_pypi = get_imports_info(unique_imports)
    # define with file to be checked
    check_file = "requirements.txt"
    # check if imports and imports not existing in pypi are declared
    # in the check_file
    flag_exit, flag_warn = check_imports(check_file, imports, imports_not_in_pypi, auto)
    if flag_exit:
        print("--------------{ >.< }-------------------")
        exit(1)
    elif flag_warn:
        print("--------------{ TLDR }------------------")
        print(
            f"The {check_file} file is up to date,\n"
            "but you have imported libraries not available in pypi.org.\n"
            "Please, check them and follow the instructions in the above section."
        )
    else:
        print(f"The {check_file} file is up to date.")
    print("--------------{ >.< }-------------------")


parser = argparse.ArgumentParser()
parser.add_argument(
    "--auto-add",
    action="store_true",
    help="automaticaly add the not specified imported packages"
    " in the requirements.txt file",
)
args = parser.parse_args()

if __name__ == "__main__":
    main(
        auto=args.auto_add,
    )
