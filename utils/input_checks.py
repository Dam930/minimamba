import re
from typing import List


def check_min_len(string: str, min_len: int = 3) -> bool:
    if len(string) < min_len:
        print(f"Invalid input: it must contains at least {min_len} characters")
        return False
    return True


def is_empty(string: str) -> bool:
    if not string:
        return True
    return False


def check_name(string: str, allow_dash: bool) -> bool:
    if allow_dash and re.match(r"^[a-z][a-z0-9_-]+$", string, flags=re.ASCII) is None:
        print(
            "Invalid input: it must start with a letter and contain only lowercase "
            + "alphanumeric characters, '-' or '_' without spaces"
        )
        return False
    elif (
        not allow_dash and re.match(r"^[a-z][a-z0-9_]+$", string, flags=re.ASCII) is None
    ):
        print(
            "Invalid input: it must start with a letter and contain only lowercase "
            + "alphanumeric characters or '_' without spaces"
        )
        return False

    return True


def check_email(string: str) -> bool:
    if re.match(r"^\S+@\S+\.\S+$", string, flags=re.ASCII) is None:
        print("Invalid input: it is not a valid email")
        return False
    return True


def check_git_url(string: str) -> bool:
    if (
        re.match(
            r"((git|ssh|http(s)?)|(git@[\w\.-]+))(:(\/\/)?)([\w\.@\:/\-~]+)(\.git)(\/)?$",
            string,
            flags=re.ASCII,
        )
        is None
    ):
        print("Invalid input: it is not a valid Git URL")
        return False
    return True


def check_choice_in_list(choice: str, allowed_values: List[str]) -> bool:
    if choice not in allowed_values:
        print(f"Invalid input: it must be one of {allowed_values}")
        return False
    return True
