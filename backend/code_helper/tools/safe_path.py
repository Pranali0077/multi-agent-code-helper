"""Path validation guard to prevent directory traversal and outside-target access."""
from pathlib import Path
from typing import Union
from ..settings import get_target_project_path

def safe_path(file_path: Union[str, Path], base_dir: Union[str, Path, None] = None) -> Path:
    """
    Resolve file_path within base_dir (defaults to TARGET_PROJECT_PATH).
    Rejects directory traversal (e.g., '../') and any path that resolves outside base_dir.
    Raises ValueError if path is outside the allowed directory.
    """
    if base_dir is None:
        base = get_target_project_path().resolve()
    else:
        base = Path(base_dir).resolve()

    raw_path = Path(file_path)

    # If relative, anchor to base_dir
    if not raw_path.is_absolute():
        resolved = (base / raw_path).resolve()
    else:
        resolved = raw_path.resolve()

    try:
        resolved.relative_to(base)
    except ValueError:
        raise ValueError(
            f"Access denied: path '{file_path}' resolves outside allowed directory '{base}'"
        )

    return resolved
