try:
    import tomllib  # python >= 3.11
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib  # python < 3.11


def main():
    with open("pyproject.toml", "rt") as file:
        file_content = file.read()
    toml: dict = tomllib.loads(file_content)
    print(toml["project"]["version"])


if __name__ == "__main__":
    main()
