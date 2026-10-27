"""Mermaid architecture diagram generator from static code imports."""
import ast
import re
from pathlib import Path
from typing import Union, Dict, Set, Tuple

from .safe_path import safe_path
from ..settings import get_target_project_path
from ..rag.loader import IGNORED_DIRS

def _clean_node_id(stem: str) -> str:
    """Replace non-alphanumeric/underscore characters with underscores."""
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    if cleaned and cleaned[0].isdigit():
        cleaned = f"m_{cleaned}"
    return cleaned or "module"

def generate_architecture_diagram(target_dir: Union[str, Path, None] = None) -> str:
    """
    Generate a Mermaid architecture diagram showing import dependencies between project modules.
    Isolated modules are retained as individual nodes.
    Output starts with ```mermaid and graph TD.
    """
    try:
        if target_dir is None:
            root = get_target_project_path().resolve()
        else:
            root = safe_path("", base_dir=target_dir)

        py_files = []
        for p in sorted(root.rglob("*.py")):
            rel_parts = p.relative_to(root).parts
            if any(part in IGNORED_DIRS for part in rel_parts[:-1]):
                continue
            py_files.append(p)

        if not py_files:
            return "```mermaid\ngraph TD\n```"

        stem_to_id: Dict[str, str] = {}
        id_to_filename: Dict[str, str] = {}

        for p in py_files:
            node_id = _clean_node_id(p.stem)
            stem_to_id[p.stem] = node_id
            id_to_filename[node_id] = p.name

        edges: Set[Tuple[str, str]] = set()

        for p in py_files:
            src_id = stem_to_id[p.stem]
            try:
                code = p.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(code, filename=p.name)
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        target_stem = alias.name.split(".")[0]
                        if target_stem in stem_to_id and target_stem != p.stem:
                            edges.add((src_id, stem_to_id[target_stem]))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        target_stem = node.module.split(".")[0]
                        if target_stem in stem_to_id and target_stem != p.stem:
                            edges.add((src_id, stem_to_id[target_stem]))

        lines = ["```mermaid", "graph TD"]

        # Declare nodes deterministically
        for node_id in sorted(id_to_filename.keys()):
            filename = id_to_filename[node_id]
            lines.append(f'  {node_id}["{filename}"]')

        # Add edges deterministically
        for src, dst in sorted(edges):
            lines.append(f"  {src} --> {dst}")

        lines.append("```")
        return "\n".join(lines)
    except Exception as e:
        return f"Error generating architecture diagram: {e}"
