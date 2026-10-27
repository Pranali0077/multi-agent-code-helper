"""Tests for project_tools, code_tools, safe_path, and onboarding_tools against fixture_project."""
from pathlib import Path
import pytest

from code_helper.tools.safe_path import safe_path
from code_helper.tools.project_tools import list_project_files, inspect_project_structure
from code_helper.tools.code_tools import explain_code
from code_helper.tools.onboarding_tools import get_onboarding_guide

FIXTURE_DIR = Path(__file__).resolve().parent / "fixture_project"

def test_safe_path_valid():
    """Valid path within fixture directory resolves properly."""
    resolved = safe_path("main.py", base_dir=FIXTURE_DIR)
    assert resolved == (FIXTURE_DIR / "main.py").resolve()
    assert resolved.exists()

def test_safe_path_rejects_parent_traversal():
    """Attempting '../' traversal out of base directory must raise ValueError."""
    with pytest.raises(ValueError, match="Access denied"):
        safe_path("../conftest.py", base_dir=FIXTURE_DIR)

    with pytest.raises(ValueError, match="Access denied"):
        safe_path("../../README.md", base_dir=FIXTURE_DIR)

def test_safe_path_rejects_absolute_outside_path():
    """Absolute path pointing outside base directory must be rejected."""
    outside = Path(__file__).resolve().parent / "conftest.py"
    with pytest.raises(ValueError, match="Access denied"):
        safe_path(outside, base_dir=FIXTURE_DIR)

def test_list_project_files():
    """list_project_files returns relative paths and line counts of .py files."""
    report = list_project_files(target_dir=FIXTURE_DIR)
    assert "main.py" in report
    assert "models.py" in report
    assert "utils.py" in report
    assert "lines)" in report

def test_inspect_project_structure():
    """inspect_project_structure extracts classes, functions, and marks local imports."""
    report = inspect_project_structure(target_dir=FIXTURE_DIR)
    assert "main.py" in report
    assert "models (local)" in report
    assert "utils (local)" in report
    assert "Item" in report
    assert "format_item" in report
    assert "calculate_total" in report

def test_explain_code():
    """explain_code extracts module docstrings, classes, methods, and line numbers."""
    models_doc = explain_code("models.py", target_dir=FIXTURE_DIR)
    assert "Item" in models_doc
    assert "to_dict" in models_doc
    assert "lines" in models_doc

    main_doc = explain_code("main.py", target_dir=FIXTURE_DIR)
    assert "main()" in main_doc

def test_explain_code_missing_file():
    """explain_code on missing file returns friendly error string."""
    err = explain_code("non_existent.py", target_dir=FIXTURE_DIR)
    assert "Error:" in err or "not found" in err

def test_get_onboarding_guide():
    """get_onboarding_guide builds overview, file table, entry point, and reading order."""
    guide = get_onboarding_guide(target_dir=FIXTURE_DIR)
    assert "# Project Onboarding Guide" in guide
    assert "## 2. Key Files" in guide
    assert "main.py" in guide
    assert "models.py" in guide
    assert "utils.py" in guide
    assert "## 3. Entry Points" in guide
    assert "## 4. How to Run" in guide
    assert "## 5. Suggested Reading Order" in guide

def test_get_onboarding_guide_no_duplicate_heading(tmp_path):
    """Ensure section 4 does not duplicate markdown headings extracted from README."""
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n\nOverview text.\n\n## How to run\n```bash\npython main.py\n```\n", encoding="utf-8")
    main_py = tmp_path / "main.py"
    main_py.write_text("def main(): pass\n", encoding="utf-8")

    guide = get_onboarding_guide(target_dir=tmp_path)
    assert "## 4. How to Run" in guide
    assert "## How to run" not in guide
    assert "python main.py" in guide
