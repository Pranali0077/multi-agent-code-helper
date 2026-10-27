"""Code explanation tools: deterministic AST code structure and docstring extraction."""
import ast
from pathlib import Path
from typing import Union, List

from .safe_path import safe_path

def _format_args(args: ast.arguments) -> str:
    """Format AST arguments into a readable signature string."""
    params: List[str] = []
    # Positional only and regular args
    for arg in args.posonlyargs + args.args:
        ann = f": {ast.unparse(arg.annotation)}" if arg.annotation else ""
        params.append(f"{arg.arg}{ann}")
    if args.vararg:
        ann = f": {ast.unparse(args.vararg.annotation)}" if args.vararg.annotation else ""
        params.append(f"*{args.vararg.arg}{ann}")
    for arg in args.kwonlyargs:
        ann = f": {ast.unparse(arg.annotation)}" if arg.annotation else ""
        params.append(f"{arg.arg}{ann}")
    if args.kwarg:
        ann = f": {ast.unparse(args.kwarg.annotation)}" if args.kwarg.annotation else ""
        params.append(f"**{args.kwarg.arg}{ann}")
    return ", ".join(params)

def explain_code(file_name: str, target_dir: Union[str, Path, None] = None) -> str:
    """
    Explain the code structure of a file using AST analysis (No AI).
    Extracts module docstring, classes, functions with signatures, line numbers, and top-level calls.
    """
    try:
        resolved = safe_path(file_name, base_dir=target_dir)
        if not resolved.exists() or not resolved.is_file():
            return f"Error: File '{file_name}' not found."

        code = resolved.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(code, filename=resolved.name)

        output: List[str] = [f"### Code Summary: {resolved.name}"]

        # Module docstring
        docstring = ast.get_docstring(tree)
        if docstring:
            output.append(f"\n**Module Description:**\n> {docstring.strip()}")
        else:
            output.append("\n**Module Description:** None")

        # Classes
        classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
        if classes:
            output.append("\n**Classes:**")
            for cls in classes:
                cls_doc = ast.get_docstring(cls) or "No docstring."
                output.append(f"- `class {cls.name}` (lines {cls.lineno}-{getattr(cls, 'end_lineno', cls.lineno)}):")
                output.append(f"  - Docstring: {cls_doc.strip()}")

                methods = [
                    m for m in cls.body
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                if methods:
                    output.append("  - Methods:")
                    for m in methods:
                        m_sig = _format_args(m.args)
                        ret = f" -> {ast.unparse(m.returns)}" if m.returns else ""
                        m_doc = ast.get_docstring(m) or "No docstring."
                        output.append(f"    - `def {m.name}({m_sig}){ret}` (lines {m.lineno}-{getattr(m, 'end_lineno', m.lineno)}): {m_doc.strip()}")

        # Top-level Functions
        functions = [
            node for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        if functions:
            output.append("\n**Functions:**")
            for fn in functions:
                sig = _format_args(fn.args)
                ret = f" -> {ast.unparse(fn.returns)}" if fn.returns else ""
                fn_doc = ast.get_docstring(fn) or "No docstring."
                output.append(f"- `def {fn.name}({sig}){ret}` (lines {fn.lineno}-{getattr(fn, 'end_lineno', fn.lineno)}):")
                output.append(f"  - Docstring: {fn_doc.strip()}")

        # Top-level calls (e.g. main() or run() called at module level or under if __name__ == '__main__':)
        top_calls: List[str] = []
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call_name = ast.unparse(node.value.func)
                top_calls.append(f"`{call_name}()` at line {node.lineno}")
            elif isinstance(node, ast.If):
                # Check for if __name__ == "__main__":
                test_str = ast.unparse(node.test)
                if "__main__" in test_str:
                    for sub in node.body:
                        if isinstance(sub, ast.Expr) and isinstance(sub.value, ast.Call):
                            call_name = ast.unparse(sub.value.func)
                            top_calls.append(f"`{call_name}()` inside `if __name__ == '__main__':` (line {sub.lineno})")

        if top_calls:
            output.append("\n**Top-level Invocations:**")
            for c in top_calls:
                output.append(f"- {c}")

        return "\n".join(output)
    except Exception as e:
        return f"Error explaining code for '{file_name}': {e}"
