"""Filesystem MCP client for secure, read-only file access."""
import sys
import shutil
from pathlib import Path
from typing import Union
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .safe_path import safe_path
from ..settings import get_target_project_path

ALLOWED_READ_TOOLS = {"read_text_file", "read_file"}

def _get_npx_command() -> str:
    """Return npx.cmd on Windows if available, otherwise npx."""
    if sys.platform == "win32" and shutil.which("npx.cmd"):
        return "npx.cmd"
    return "npx"

async def _read_source_file_internal(file_name: str, target_dir: Union[str, Path, None] = None) -> str:
    """Internal implementation supporting custom target_dir for testing."""
    try:
        target_root = get_target_project_path().resolve() if target_dir is None else Path(target_dir).resolve()
        path = safe_path(file_name, base_dir=target_root)

        cmd = _get_npx_command()
        params = StdioServerParameters(
            command=cmd,
            args=["-y", "@modelcontextprotocol/server-filesystem", str(target_root)],
        )

        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as session:
                await session.initialize()
                tools = {t.name for t in (await session.list_tools()).tools}
                name = next(n for n in ("read_text_file", "read_file") if n in tools and n in ALLOWED_READ_TOOLS)
                result = await session.call_tool(name, {"path": str(path)})
                return "".join(c.text for c in result.content if hasattr(c, "text"))
    except Exception as e:
        return f"Error reading file '{file_name}': {e}"

async def read_source_file(file_name: str) -> str:
    """
    Read one source file from the target project and return its text via Filesystem MCP.
    Strictly restricted to allowed read tools.
    """
    return await _read_source_file_internal(file_name)
