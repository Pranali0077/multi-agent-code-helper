"""ADK Agent definitions. Exactly 5 agents: coordinator (root_agent) + 4 specialists."""
from google.adk.agents import LlmAgent

from .model import MODEL
from .prompts import BOSS, SEARCHER, EXPLAINER, MAPPER, GUIDE
from .tools import (
    search_codebase,
    read_source_file,
    explain_code,
    list_project_files,
    inspect_project_structure,
    generate_architecture_diagram,
    get_onboarding_guide,
)

# Specialist 1: code_searcher
code_searcher = LlmAgent(
    name="code_searcher",
    model=MODEL,
    description="Finds where something is in the code using semantic (RAG) search.",
    instruction=SEARCHER,
    tools=[search_codebase],
)

# Specialist 2: code_explainer
code_explainer = LlmAgent(
    name="code_explainer",
    model=MODEL,
    description="Explains source code, functions and their purpose for a named file.",
    instruction=EXPLAINER,
    tools=[read_source_file, explain_code],
)

# Specialist 3: architecture_mapper
architecture_mapper = LlmAgent(
    name="architecture_mapper",
    model=MODEL,
    description="Shows project structure and generates Mermaid architecture diagrams.",
    instruction=MAPPER,
    tools=[list_project_files, inspect_project_structure, generate_architecture_diagram],
)

# Specialist 4: onboarding_guide
onboarding_guide = LlmAgent(
    name="onboarding_guide",
    model=MODEL,
    description="Helps new developers understand the project, its files, and how to run it.",
    instruction=GUIDE,
    tools=[get_onboarding_guide, list_project_files],
)

# Coordinator (root_agent)
root_agent = LlmAgent(
    name="coordinator",
    model=MODEL,
    description="Understands the request and delegates it to the right specialist.",
    instruction=BOSS,
    sub_agents=[code_searcher, code_explainer, architecture_mapper, onboarding_guide],
)
