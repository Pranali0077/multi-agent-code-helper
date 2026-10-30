import type { AgentInfo } from "../types";

export const AGENTS: AgentInfo[] = [
  {
    name: "coordinator",
    label: "Coordinator",
    role: "Routes each question",
    color: "slate",
    description: "Understands the request and delegates it to the right specialist.",
  },
  {
    name: "code_searcher",
    label: "Code Searcher",
    role: "Finds code with RAG",
    color: "blue",
    description: "Finds where something is in the code using semantic (RAG) search.",
    example: "Where is the User class defined?",
  },
  {
    name: "code_explainer",
    label: "Code Explainer",
    role: "Explains files and functions",
    color: "green",
    description: "Explains source code, functions and their purpose for a named file.",
    example: "Explain what main.py does.",
  },
  {
    name: "architecture_mapper",
    label: "Architecture Mapper",
    role: "Structure and Mermaid diagrams",
    color: "purple",
    description: "Shows project structure and generates Mermaid architecture diagrams.",
    example: "Show me the architecture diagram.",
  },
  {
    name: "onboarding_guide",
    label: "Onboarding Guide",
    role: "Helps newcomers get started",
    color: "amber",
    description: "Helps new developers understand the project, its files, and how to run it.",
    example: "I am new. Where do I start?",
  },
];

export const EXAMPLE_CHIPS = AGENTS.filter((a) => a.example).map((a) => a.example as string);
