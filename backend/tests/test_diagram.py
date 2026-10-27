"""Tests for diagram_tools.py: Mermaid diagram generation from project imports."""
import re
from pathlib import Path
from code_helper.tools.diagram_tools import generate_architecture_diagram

FIXTURE_DIR = Path(__file__).resolve().parent / "fixture_project"

def test_diagram_mermaid_structure_and_edges():
    """Diagram starts with ```mermaid and graph TD, and contains expected edges."""
    diagram = generate_architecture_diagram(target_dir=FIXTURE_DIR)
    lines = diagram.strip().splitlines()

    assert lines[0] == "```mermaid"
    assert lines[1].strip() == "graph TD"
    assert lines[-1] == "```"

    # Must contain main --> models and main --> utils
    assert "main --> models" in diagram
    assert "main --> utils" in diagram

def test_diagram_node_declarations():
    """All files in fixture appear as valid node declarations."""
    diagram = generate_architecture_diagram(target_dir=FIXTURE_DIR)
    assert 'main["main.py"]' in diagram
    assert 'models["models.py"]' in diagram
    assert 'utils["utils.py"]' in diagram

    # Verify node ids are alphanumeric / underscores
    node_id_matches = re.findall(r'^\s*([A-Za-z0-9_]+)\[', diagram, re.MULTILINE)
    for nid in node_id_matches:
        assert re.match(r"^[A-Za-z0-9_]+$", nid)

def test_diagram_isolated_node(tmp_path):
    """Isolated files with no dependencies still appear as nodes."""
    file_a = tmp_path / "service.py"
    file_a.write_text("x = 10\n", encoding="utf-8")

    diagram = generate_architecture_diagram(target_dir=tmp_path)
    assert 'service["service.py"]' in diagram
    assert "-->" not in diagram

def test_diagram_dynamic_changes(tmp_path):
    """Changing project files changes the diagram; no hardcoded names."""
    # Create a project with alpha -> beta
    alpha = tmp_path / "alpha.py"
    alpha.write_text("import beta\n", encoding="utf-8")
    beta = tmp_path / "beta.py"
    beta.write_text("def run(): pass\n", encoding="utf-8")

    diagram = generate_architecture_diagram(target_dir=tmp_path)
    assert "alpha --> beta" in diagram
    assert "main --> models" not in diagram
    assert 'alpha["alpha.py"]' in diagram
    assert 'beta["beta.py"]' in diagram
