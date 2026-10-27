"""Loads Python source files from a target project root."""
from pathlib import Path
from typing import List, Tuple, Union

IGNORED_DIRS = {
    "__pycache__",
    ".venv",
    "venv",
    ".git",
    "node_modules",
    ".pytest_cache",
    ".idea",
    ".vscode",
}

def load_python_files(root: Union[str, Path]) -> List[Tuple[str, str]]:
    """Walk root, skip ignored directories, and return list of (rel_path, text) for all .py files."""
    root_path = Path(root).resolve()
    if not root_path.exists() or not root_path.is_dir():
        raise FileNotFoundError(f"Directory not found: {root_path}")

    results: List[Tuple[str, str]] = []

    for path in sorted(root_path.rglob("*.py")):
        # Skip if any ignored directory is in the path parts relative to root
        rel_parts = path.relative_to(root_path).parts
        if any(part in IGNORED_DIRS for part in rel_parts[:-1]):
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            rel_path = path.relative_to(root_path).as_posix()
            results.append((rel_path, content))
        except Exception as e:
            # Skip unreadable files or log
            continue

    return results
