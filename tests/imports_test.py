import ast
import importlib
import logging
import os
import traceback


def test_imports():
    root_dir = "minimamba"
    imports_not_to_be_checked = {"tomllib"}  # modify it if needed

    imported_packages_names = get_all_imports_recursively(root_dir)
    logging.info(f"imports found: {sorted(imported_packages_names)}")
    if imports_not_to_be_checked is not None and len(imports_not_to_be_checked) > 0:
        logging.info(
            f"imports that will not be checked: {sorted(imports_not_to_be_checked)}"
        )
        imported_packages_names = imported_packages_names - imports_not_to_be_checked
    found_missing = False
    for package_name in imported_packages_names:
        try:
            importlib.import_module(package_name)
        except ModuleNotFoundError:
            found_missing = True
            logging.error(f"cannot import '{package_name}', add it in requirements.txt")

    assert not found_missing


def get_all_imports_recursively(path: str) -> set:
    reqs = set()
    for child_path in os.listdir(path):
        if os.path.isdir(child_path):
            if child_path[0] == ".":
                continue  # skip hidden folders
            if child_path == "__pycache__":
                continue  # skip pycache folders
            candidates = get_all_imports_recursively(os.path.join(path, child_path))
        candidates = get_all_imports(path=path)  # return a list
        reqs.update(candidates)
    return reqs


# copied from https://github.com/bndr/pipreqs to not have this additional requirement
def get_all_imports(  # noqa: C901
    path, encoding=None, extra_ignore_dirs=None, follow_links=True
):
    imports = set()
    raw_imports = set()
    candidates = []
    ignore_errors = False
    ignore_dirs = [".hg", ".svn", ".git", ".tox", "__pycache__", "env", "venv"]

    if extra_ignore_dirs:
        ignore_dirs_parsed = []
        for e in extra_ignore_dirs:
            ignore_dirs_parsed.append(os.path.basename(os.path.realpath(e)))
        ignore_dirs.extend(ignore_dirs_parsed)

    walk = os.walk(path, followlinks=follow_links)
    for root, dirs, files in walk:
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        candidates.append(os.path.basename(root))
        files = [fn for fn in files if os.path.splitext(fn)[1] == ".py"]

        candidates += [os.path.splitext(fn)[0] for fn in files]
        for file_name in files:
            file_name = os.path.join(root, file_name)
            with open(file_name, "r", encoding=encoding) as f:
                contents = f.read()
            try:
                tree = ast.parse(contents)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for subnode in node.names:
                            raw_imports.add(subnode.name)
                    elif isinstance(node, ast.ImportFrom):
                        raw_imports.add(node.module)
            except Exception as exc:
                if ignore_errors:
                    traceback.print_exc(exc)
                    logging.warning("Failed on file: %s" % file_name)
                    continue
                else:
                    logging.error("Failed on file: %s" % file_name)
                    raise exc

    # Clean up imports
    for name in [n for n in raw_imports if n]:
        # Sanity check: Name could have been None if the import
        # statement was as ``from . import X``
        # Cleanup: We only want to first part of the import.
        # Ex: from django.conf --> django.conf. But we only want django
        # as an import.
        cleaned_name, _, _ = name.partition(".")
        imports.add(cleaned_name)

    packages = imports - (set(candidates) & imports)
    logging.debug("Found packages: {0}".format(packages))

    return list(packages)
