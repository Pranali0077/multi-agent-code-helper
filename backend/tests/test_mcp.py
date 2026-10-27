"""Tests for Filesystem MCP read_source_file integration and security boundaries."""
from pathlib import Path
import pytest

from code_helper.tools.mcp_tools import read_source_file

CODE_HELPER_DIR = Path(__file__).resolve().parent.parent / "code_helper"

def test_no_forbidden_mcp_tool_references():
    """Verify our code never references modification tools anywhere."""
    forbidden = [
        "write" + "_" + "file",
        "edit" + "_" + "file",
        "move" + "_" + "file",
    ]
    for py_file in CODE_HELPER_DIR.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8", errors="replace")
        for tool_name in forbidden:
            assert tool_name not in text, f"Forbidden tool name '{tool_name}' found in {py_file}"

@pytest.mark.live
@pytest.mark.asyncio
async def test_mcp_read_main_py_live():
    """Live check: read_source_file successfully reads main.py from the target project."""
    content = await read_source_file("main.py")
    assert "def run" in content or "models" in content
    assert "Error" not in content

@pytest.mark.live
@pytest.mark.asyncio
async def test_mcp_rejects_outside_path_live():
    """Live check: path outside target project (../.env or absolute) is denied."""
    res_traversal = await read_source_file("../.env")
    assert "Error" in res_traversal or "Access denied" in res_traversal

    outside_abs = Path(__file__).resolve()
    res_abs = await read_source_file(str(outside_abs))
    assert "Error" in res_abs or "Access denied" in res_abs
