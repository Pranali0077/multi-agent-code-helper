"""Tests verifying exactly the 7 custom tools are registered across the agent team."""
from code_helper.agent import (
    root_agent,
    code_searcher,
    code_explainer,
    architecture_mapper,
    onboarding_guide,
)

EXPECTED_SEVEN_TOOLS = {
    "search_codebase",
    "read_source_file",
    "explain_code",
    "list_project_files",
    "inspect_project_structure",
    "generate_architecture_diagram",
    "get_onboarding_guide",
}

def test_exactly_seven_tools_registered():
    """All 7 tools and only these 7 tools are registered across specialist agents."""
    specialists = [code_searcher, code_explainer, architecture_mapper, onboarding_guide]

    registered_tool_names = set()
    for agent in specialists:
        for tool in (agent.tools or []):
            name = getattr(tool, "__name__", str(tool))
            registered_tool_names.add(name)

    assert registered_tool_names == EXPECTED_SEVEN_TOOLS
    assert len(registered_tool_names) == 7

def test_every_tool_attached_to_specialist():
    """Each expected tool is present on at least one specialist agent."""
    specialists = [code_searcher, code_explainer, architecture_mapper, onboarding_guide]
    all_tools = {getattr(t, "__name__", str(t)) for a in specialists for t in (a.tools or [])}

    for expected_tool in EXPECTED_SEVEN_TOOLS:
        assert expected_tool in all_tools, f"Tool '{expected_tool}' is missing from agents"
