import fnmatch
import os
import re
from pathlib import Path
from typing import Optional


def load_gitignore(path_dir: Optional[Path] = None) -> set:
    if path_dir:
        gitignore_path = path_dir / ".gitignore"
        if gitignore_path.exists():
            with gitignore_path.open() as f:
                return {
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                }
        return set()
    return set()


def is_allowed(path_str: str, gitignore_patterns: Optional[set] = None) -> bool:
    path = Path(path_str)
    if gitignore_patterns:
        if any(
            re.search(fnmatch.translate(pattern.rstrip("/")), path.name)
            for pattern in gitignore_patterns
        ):
            return False
    return not (path.name.endswith(".egg-info") or path.name.endswith(".git"))


def main() -> None:
    path_dir = Path(__file__).resolve().parent.parent
    gitignore_patterns = load_gitignore(path_dir)
    print("=" * 32)
    print(f"{str(path_dir.name).upper()}")
    print("=" * 32)
    for root, dirs, files in os.walk(str(path_dir)):
        local_gitignore_patterns = gitignore_patterns | load_gitignore(Path(root))
        if not is_allowed(root, local_gitignore_patterns):
            dirs[:] = []
            continue
        dirs[:] = sorted([d for d in dirs if is_allowed(d, local_gitignore_patterns)])
        files = sorted([f for f in files if is_allowed(f, local_gitignore_patterns)])
        level = root.replace(str(path_dir), "").count(os.sep)
        print(f"{' ' * 4 * level}/{os.path.basename(root)}")
        for f in files:
            print(f"{' ' * 4 * (level + 1)}{f}")
    print("=" * 32)


if __name__ == "__main__":
    main()
