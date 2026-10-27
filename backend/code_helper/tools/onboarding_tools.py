"""Onboarding guide generator for new developers studying the project."""
import ast
from pathlib import Path
from typing import Union, List, Dict, Set

from .safe_path import safe_path
from ..settings import get_target_project_path
from ..rag.loader import IGNORED_DIRS

def get_onboarding_guide(target_dir: Union[str, Path, None] = None) -> str:
    """
    Generate a markdown onboarding guide explaining what the project does,
    a table of key files, entry point(s), how to run the project, and a recommended reading order.
    """
    try:
        if target_dir is None:
            root = get_target_project_path().resolve()
        else:
            root = safe_path("", base_dir=target_dir)

        # 1. Project Overview from README or docstrings
        readme_path = root / "README.md"
        overview = ""
        how_to_run = ""

        if readme_path.exists():
            readme_text = readme_path.read_text(encoding="utf-8", errors="replace").strip()
            # Extract first non-header paragraph
            paragraphs = [p.strip() for p in readme_text.split("\n\n") if p.strip()]
            for p in paragraphs:
                if not p.startswith("#") and not overview:
                    overview = p
                if "run" in p.lower() or "how to run" in p.lower():
                    # Strip any markdown headings (e.g. '## How to run') from the extracted text
                    content_lines = [line for line in p.splitlines() if not line.strip().startswith("#")]
                    cleaned_p = "\n".join(content_lines).strip()
                    if cleaned_p:
                        how_to_run = cleaned_p

        py_files: List[Path] = []
        for p in sorted(root.rglob("*.py")):
            rel_parts = p.relative_to(root).parts
            if any(part in IGNORED_DIRS for part in rel_parts[:-1]):
                continue
            py_files.append(p)

        file_metadata: Dict[str, Dict[str, Union[str, int, List[str]]]] = {}
        entry_points: List[str] = []
        dep_graph: Dict[str, Set[str]] = {}

        for p in py_files:
            rel = p.relative_to(root).as_posix()
            try:
                code = p.read_text(encoding="utf-8", errors="replace")
                lines_count = len(code.splitlines())
                tree = ast.parse(code, filename=p.name)
                doc = ast.get_docstring(tree) or "No module docstring."
                first_line_doc = doc.strip().splitlines()[0] if doc.strip() else "No description"
            except Exception:
                lines_count = 0
                first_line_doc = "Could not parse file."
                code = ""
                tree = ast.Module(body=[], type_ignores=[])

            # Check for entry points
            is_entry = False
            if "__main__" in code or "def main" in code or "def run" in code:
                is_entry = True
                entry_points.append(rel)

            # Check imports for reading order
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        imports.add(a.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])

            dep_graph[p.stem] = imports
            file_metadata[rel] = {
                "stem": p.stem,
                "lines": lines_count,
                "summary": first_line_doc,
                "is_entry": is_entry,
            }

        if not overview and py_files:
            # Fallback overview from entry point or first file docstring
            first_meta = file_metadata[py_files[0].relative_to(root).as_posix()]
            overview = str(first_meta["summary"])

        if not overview:
            overview = "Python codebase without description."

        if not how_to_run:
            main_entry = entry_points[0] if entry_points else (py_files[0].relative_to(root).as_posix() if py_files else "main.py")
            how_to_run = f"Run the entry point via:\n```bash\npython {main_entry}\n```"

        # Reading order: modules imported by others first, then entry points
        reading_order: List[str] = []
        # Put models/data definitions first
        stems_order = sorted(py_files, key=lambda f: (
            0 if "model" in f.stem or "type" in f.stem else
            1 if "util" in f.stem or "helper" in f.stem else
            3 if f.relative_to(root).as_posix() in entry_points else 2
        ))
        for p in stems_order:
            reading_order.append(p.relative_to(root).as_posix())

        # Build Guide Markdown
        md: List[str] = [
            "# Project Onboarding Guide",
            "\n## 1. Project Overview",
            overview,
            "\n## 2. Key Files",
            "| File | Lines | Summary |",
            "| --- | ---: | --- |",
        ]

        for rel, meta in file_metadata.items():
            md.append(f"| `{rel}` | {meta['lines']} | {meta['summary']} |")

        md.append("\n## 3. Entry Points")
        if entry_points:
            for ep in entry_points:
                md.append(f"- `{ep}`")
        else:
            md.append("- No explicit `__main__` entry point found.")

        md.append("\n## 4. How to Run")
        md.append(how_to_run)

        md.append("\n## 5. Suggested Reading Order")
        for i, path in enumerate(reading_order, 1):
            md.append(f"{i}. `{path}`")

        return "\n".join(md)
    except Exception as e:
        return f"Error generating onboarding guide: {e}"
