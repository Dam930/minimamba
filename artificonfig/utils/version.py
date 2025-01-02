import argparse

try:
    import tomllib  # python >= 3.11
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib  # python < 3.11


def get_version(ignore_stab: bool) -> str:
    with open("pyproject.toml", "rt") as f:
        file_content = f.read()
    config_toml: dict = tomllib.loads(file_content)

    curr_version = config_toml["project"]["version"]
    if ignore_stab and curr_version[-1] in ["a", "b"]:
        curr_version = curr_version[:-1]
    return curr_version


def main(ignore_stab: bool):
    version = get_version(ignore_stab)
    print(version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ignore-stab",
        action="store_true",
        help="Ignore the stability of the version (alpha, beta, stable)",
    )

    args = parser.parse_args()
    main(args.ignore_stab)
