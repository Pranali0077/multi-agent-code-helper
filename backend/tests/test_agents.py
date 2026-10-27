"""Offline tests for agent configurations, sub-agent hierarchies, and tool assignments."""
from code_helper.agent import (
    root_agent,
    code_searcher,
    code_explainer,
    architecture_mapper,
    onboarding_guide,
)
from code_helper.tools import (
    search_codebase,
    read_source_file,
    explain_code,
    list_project_files,
    inspect_project_structure,
    generate_architecture_diagram,
    get_onboarding_guide,
)

def test_all_five_agents_exist_with_exact_names():
    """Exactly 5 agents exist with exact canonical names."""
    assert root_agent.name == "coordinator"
    assert code_searcher.name == "code_searcher"
    assert code_explainer.name == "code_explainer"
    assert architecture_mapper.name == "architecture_mapper"
    assert onboarding_guide.name == "onboarding_guide"

def test_coordinator_has_no_tools():
    """Coordinator must not have any tools assigned (it only delegates)."""
    assert not root_agent.tools

def test_coordinator_has_four_sub_agents():
    """Coordinator must have exactly the 4 specialist sub-agents registered."""
    sub_agents = root_agent.sub_agents or []
    assert len(sub_agents) == 4
    sub_agent_names = {a.name for a in sub_agents}
    expected_names = {
        "code_searcher",
        "code_explainer",
        "architecture_mapper",
        "onboarding_guide",
    }
    assert sub_agent_names == expected_names

def test_code_searcher_tools():
    """code_searcher has search_codebase."""
    assert code_searcher.tools == [search_codebase]

def test_code_explainer_tools():
    """code_explainer has read_source_file and explain_code."""
    assert set(code_explainer.tools) == {read_source_file, explain_code}

def test_architecture_mapper_tools():
    """architecture_mapper has list_project_files, inspect_project_structure, generate_architecture_diagram."""
    assert set(architecture_mapper.tools) == {
        list_project_files,
        inspect_project_structure,
        generate_architecture_diagram,
    }

def test_onboarding_guide_tools():
    """onboarding_guide has get_onboarding_guide and list_project_files."""
    assert set(onboarding_guide.tools) == {get_onboarding_guide, list_project_files}

def test_descriptions_are_distinct():
    """Every agent has a non-empty, distinct description."""
    agents = [
        root_agent,
        code_searcher,
        code_explainer,
        architecture_mapper,
        onboarding_guide,
    ]
    descriptions = [a.description.strip() for a in agents]
    assert all(descriptions)
    assert len(set(descriptions)) == 5
