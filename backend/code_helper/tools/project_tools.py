"""Project inspection tools: list files and inspect code structure."""
import ast
from pathlib import Path
from typing import Union, List, Set

from .safe_path import safe_path
from ..settings import get_target_project_path
from ..rag.loader import IGNORED_DIRS

def _get_project_root(target_dir: Union[str, Path, None]) -> Path:
    if target_dir is None:
        return get_target_project_path().resolve()
    return safe_path("", base_dir=target_dir)

def list_project_files(target_dir: Union[str, Path, None] = None) -> str:
    """
    List all Python source files in the target project with their relative paths and line counts.
    Returns a formatted string report.
    """
    try:
        root = _get_project_root(target_dir)
        py_files: List[Path] = []
        for p in sorted(root.rglob("*.py")):
            rel_parts = p.relative_to(root).parts
            if any(part in IGNORED_DIRS for part in rel_parts[:-1]):
                continue
            py_files.append(p)

        if not py_files:
            return "No Python source files found in the project."

        lines = [f"Project Python files ({len(py_files)} total):"]
        for p in py_files:
            rel_path = p.relative_to(root).as_posix()
            try:
                line_count = len(p.read_text(encoding="utf-8", errors="replace").splitlines())
                lines.append(f"- {rel_path} ({line_count} lines)")
            except Exception as e:
                lines.append(f"- {rel_path} (unreadable: {e})")

        return "\n".join(lines)
    except Exception as e:
        return f"Error listing project files: {e}"

def inspect_project_structure(target_dir: Union[str, Path, None] = None) -> str:
    """
    Inspect all project Python files, extracting classes, functions, and imports.
    Distinguishes local (project) imports from external libraries.
    """
    try:
        root = _get_project_root(target_dir)
        py_files = []
        local_modules: Set[str] = set()

        for p in sorted(root.rglob("*.py")):
            rel_parts = p.relative_to(root).parts
            if any(part in IGNORED_DIRS for part in rel_parts[:-1]):
                continue
            py_files.append(p)
            local_modules.add(p.stem)

        if not py_files:
            return "No Python source files found to inspect."

        output = ["Project Structure Overview:"]

        for p in py_files:
            rel_path = p.relative_to(root).as_posix()
            output.append(f"\nFile: {rel_path}")

            try:
                code = p.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(code, filename=rel_path)
            except Exception as e:
                output.append(f"  [Parse Error: {e}]")
                continue

            # Imports
            imports: List[str] = []
            for node in tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        is_local = alias.name.split(".")[0] in local_modules
                        tag = " (local)" if is_local else ""
                        imports.append(f"{alias.name}{tag}")
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    is_local = mod.split(".")[0] in local_modules or node.level > 0
                    names_str = ", ".join(a.name for a in node.names)
                    tag = " (local)" if is_local else ""
                    imports.append(f"from {mod} import {names_str}{tag}")

            if imports:
                output.append("  Imports:")
                for imp in imports:
                    output.append(f"    - {imp}")

            # Classes
            classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
            if classes:
                output.append("  Classes:")
                for cls in classes:
                    methods = [
                        m.name for m in cls.body
                        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ]
                    methods_str = f" [methods: {', '.join(methods)}]" if methods else ""
                    output.append(f"    - {cls.name}{methods_str} (line {cls.lineno})")

            # Functions (top-level)
            functions = [
                node for node in tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            if functions:
                output.append("  Functions:")
                for fn in functions:
                    output.append(f"    - {fn.name}() (line {fn.lineno})")

        return "\n".join(output)
    except Exception as e:
        return f"Error inspecting project structure: {e}"
