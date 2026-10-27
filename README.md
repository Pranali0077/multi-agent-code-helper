# Multi-Agent Code Helper

Multi-Agent Code Helper is an intelligent developer assistant built on the Google Agent Development Kit (ADK) that coordinates specialized AI agents to help engineers navigate, understand, and onboard onto unfamiliar codebases. It features a custom Pinecone vector search pipeline using NVIDIA Nemotron 2048-dimensional embeddings, read-only Model Context Protocol (MCP) filesystem integration with strict path sandboxing, and dynamic Mermaid architecture diagram generation. The system provides both a native CLI/Web experience via Google ADK and an interactive full-stack web application with complete multi-agent execution trace visibility.

---

## Agent Architecture

The system uses a coordinator-specialist pattern with exactly 5 agents defined in `backend/code_helper/agent.py`. The `coordinator` acts as the root orchestrator, analyzing incoming user requests and delegating to the appropriate specialist without answering directly.

| Agent | Role | Tools Registered |
| :--- | :--- | :--- |
| `coordinator` | Root orchestrator that classifies queries and delegates to specialized sub-agents. Never answers queries directly. | *None* (Delegates to sub-agents) |
| `code_searcher` | Specialist for locating classes, functions, variables, and semantic references across the project. | `search_codebase` (from `backend/code_helper/tools/rag_tools.py`) |
| `code_explainer` | Specialist for explaining file implementations, mechanisms, and reading source details. | `explain_code` (from `backend/code_helper/tools/code_tools.py`), `read_source_file` (from `backend/code_helper/tools/mcp_tools.py`) |
| `architecture_mapper` | Specialist for visualizing high-level system structure, module relationships, and dependencies. | `generate_architecture_diagram` (from `backend/code_helper/tools/diagram_tools.py`), `inspect_project_structure` (from `backend/code_helper/tools/project_tools.py`) |
| `onboarding_guide` | Specialist for welcoming new contributors, detailing entry points, prerequisites, and starter tasks. | `get_onboarding_guide` (from `backend/code_helper/tools/onboarding_tools.py`), `list_project_files` (from `backend/code_helper/tools/project_tools.py`) |

---

## Tools Registry

The backend registers 7 focused, deterministic and AI-powered tools across the specialist agents:

| Tool | Source File | Registered Agent | AI Used? | Description |
| :--- | :--- | :--- | :--- | :--- |
| `search_codebase` | `backend/code_helper/tools/rag_tools.py` | `code_searcher` | Yes (NVIDIA Nemotron Embeddings + Pinecone) | Semantic vector search across chunked codebase using cosine similarity (threshold `MIN_RELEVANCE_SCORE = 0.2`). |
| `read_source_file` | `backend/code_helper/tools/mcp_tools.py` | `code_explainer` | No (Filesystem MCP client) | Securely reads file contents from target codebase via Model Context Protocol with path sandboxing (`backend/code_helper/tools/safe_path.py`). |
| `explain_code` | `backend/code_helper/tools/code_tools.py` | `code_explainer` | No (Deterministic analysis) | Inspects file existence, line metrics, imports, and top-level definitions to generate structured code explanations. |
| `generate_architecture_diagram` | `backend/code_helper/tools/diagram_tools.py` | `architecture_mapper` | No (Deterministic AST analysis) | Analyzes Python AST import statements across project files to output valid, self-contained Mermaid diagrams (`graph TD`). |
| `inspect_project_structure` | `backend/code_helper/tools/project_tools.py` | `architecture_mapper` | No (Local filesystem scan) | Traverses project directory structure, counts file types, and outputs a formatted directory tree with line metrics. |
| `get_onboarding_guide` | `backend/code_helper/tools/onboarding_tools.py` | `onboarding_guide` | No (Deterministic guide synthesis) | Scans for entry points (`main.py`, `app.py`, `cli.py`), dependencies (`requirements.txt`), and generates step-by-step onboarding instructions. |
| `list_project_files` | `backend/code_helper/tools/project_tools.py` | `onboarding_guide` | No (Local filesystem scan) | Lists all safe, non-hidden source files in the target project with relative paths and line counts. |

---

## Custom RAG & Chunk Size Analysis

### Custom Implementation
The RAG pipeline is built from scratch without LangChain or LlamaIndex:
- **Loader**: `backend/code_helper/rag/loader.py` reads valid Python files while skipping hidden folders and virtual environments.
- **Chunker**: `backend/code_helper/rag/chunker.py` chunks code into `Chunk(id, file, start_line, end_line, text)`.
- **Embedder**: `backend/code_helper/rag/embedder.py` uses `nvidia_nim/nvidia/nemotron-3-embed-1b` via LiteLLM to generate 2048-dimensional dense vectors, verifying exact dimension length and supporting both `NVIDIA_API_KEY` and `NVIDIA_NIM_API_KEY`.
- **Vector Database**: `backend/code_helper/rag/store.py` manages a Pinecone serverless index configured with 2048 dimensions and cosine metric. Metadata stored per vector: `{"file": chunk.file, "start_line": chunk.start_line, "end_line": chunk.end_line, "text": chunk.text}`.
- **Search**: `backend/code_helper/rag/search.py` queries Pinecone with embedded query vectors.
- **Relevance Guard**: In `backend/code_helper/tools/rag_tools.py`, results with cosine similarity score below `MIN_RELEVANCE_SCORE = 0.2` return `"No relevant code found."` to prevent irrelevant context injection.

### Chunk Size: 800 characters / 150-character overlap
On our target project (`target_project/` with `main.py`, `models.py`, `utils.py`), all three files are compact (under 400 characters each). As a result, both chunk size configurations (**800/150** and **400/80**) produced exactly **1 chunk per file**, yielding identical **5/5 (100%)** retrieval accuracy across evaluation queries.

We chose **800 characters with a 150-character overlap** because:
1. **Semantic Integrity**: 800 characters preserves entire Python classes and functions in a single continuous chunk.
2. **Boundary Protection**: The 150-character sliding overlap prevents key definitions, signatures, or docstrings from being severed across chunk boundaries as the project scales.

---

## Filesystem MCP Integration

Source file reading is powered by the official Model Context Protocol filesystem server:
- **Server Package**: `@modelcontextprotocol/server-filesystem` (executed on-demand via `npx` in `backend/code_helper/tools/mcp_tools.py`).
- **Read-Only Operation**: Only read tools (`read_text_file` / `read_file`) are utilized. No edit, write, create, or delete tools are exposed or invoked.
- **Path Sandboxing**: The MCP server is initialized targeting exclusively `TARGET_PROJECT_PATH`. Additionally, `backend/code_helper/tools/safe_path.py` validates all requested paths prior to invocation, rejecting any path traversal sequences (`../`) or absolute paths pointing outside the workspace.

---

## Exact Run Commands (Windows)

All commands are run from PowerShell.

### 1. Index Target Codebase into Pinecone
```powershell
cd backend
.\.venv\Scripts\python -m code_helper.index_codebase
```

### 2. Run Offline Backend Tests (No network required)
```powershell
cd backend
.\.venv\Scripts\pytest
```

### 3. Run Live Backend End-to-End Tests
```powershell
cd backend
$env:RUN_LIVE = "1"
.\.venv\Scripts\pytest -v
Remove-Item Env:\RUN_LIVE
```

### 4. Run Interactive ADK CLI
```powershell
cd backend
.\.venv\Scripts\adk run code_helper "Where is the User class defined?"
```

### 5. Run ADK Web Interface
```powershell
cd backend
.\.venv\Scripts\adk web --port 8085
```

### 6. Run FastAPI Backend Server
```powershell
cd backend
.\.venv\Scripts\python -m uvicorn server:app --port 8000 --reload
```

### 7. Run Frontend Development Server
```powershell
cd frontend
npm run dev
```

### 8. Run Frontend Tests and Production Build
```powershell
cd frontend
npm test
npm run build
```

---

## Canonical Queries & Real Agent Execution Traces

Below are the 4 canonical queries evaluated against `target_project/`, along with the actual agent routing and tool execution traces:

### 1. Class Search
- **Query**: `"Where is the User class defined?"`
- **Answering Agent**: `code_searcher`
- **Execution Trace**:
  1. `coordinator` routed query to `code_searcher`.
  2. `code_searcher` invoked `search_codebase(query="Where is the User class defined?")`.
  3. Pinecone vector search retrieved `models.py:3-11` (score: 0.738 &ge; 0.2).
  4. `code_searcher` cited `models.py` lines 3–11 and returned the `User` class definition.

### 2. Architecture Diagram
- **Query**: `"Show me the architecture diagram."`
- **Answering Agent**: `architecture_mapper`
- **Execution Trace**:
  1. `coordinator` routed query to `architecture_mapper`.
  2. `architecture_mapper` invoked `generate_architecture_diagram()`.
  3. AST analyzer inspected file imports across `target_project/` and generated:
     ```mermaid
     graph TD
         main[main.py] --> models[models.py]
         main[main.py] --> utils[utils.py]
         models[models.py]
         utils[utils.py]
     ```
  4. Frontend `MermaidBlock` dynamically rendered the interactive SVG diagram.

### 3. Developer Onboarding
- **Query**: `"I am new. Where do I start?"`
- **Answering Agent**: `onboarding_guide`
- **Execution Trace**:
  1. `coordinator` routed query to `onboarding_guide`.
  2. `onboarding_guide` invoked `get_onboarding_guide()`.
  3. Tool detected `main.py` entry point, Python environment requirements, and starter tasks.
  4. `onboarding_guide` returned the complete welcome walkthrough.

### 4. Code Explanation
- **Query**: `"Explain what main.py does."`
- **Answering Agent**: `code_explainer`
- **Execution Trace**:
  1. `coordinator` routed query to `code_explainer`.
  2. `code_explainer` invoked `read_source_file(file_path="main.py")` via MCP.
  3. `code_explainer` invoked `explain_code(file_path="main.py")`.
  4. `code_explainer` synthesized the execution flow: importing `models` and `utils`, instantiating `User`, formatting with `format_greeting()`, and printing output.

---

## Problems & Fixes

### 1. Follow-up Routing Problem (Persistent Session Sticking)
- **Problem**: When a single persistent ADK session was reused across multiple chat turns, the ADK `Runner` maintained state inside whichever sub-agent answered the previous turn (e.g. `architecture_mapper`). When the user subsequently asked an onboarding question, the query was delivered directly to the active sub-agent rather than returning to `coordinator`, resulting in misrouted responses.
- **Fix**: In `backend/server.py`, each chat request executes through an ephemeral ADK session (`adk_session_id = f"{chat_req.session_id}_{uuid.uuid4().hex[:8]}"`). This guarantees that every query enters through the root `coordinator` agent, achieving 100% routing accuracy across conversational turns while conversational history is maintained at the application level (Decision 5).

### 2. Gemini 404 Model Change
- **Problem**: Calls using `gemini-2.5-flash` failed with: `"This model models/gemini-2.5-flash is no longer available to new users."`
- **Fix**: Updated `GEMINI_MODEL` default in `backend/code_helper/settings.py` (and `.env.example`) to `gemini-3.5-flash-lite`, paired with `GOOGLE_GENAI_USE_VERTEXAI=FALSE`. This solved the 404 error and enabled reliable multi-agent function calling through Google AI Studio.

---

## Limitations

1. **Target Project Scope**: Currently optimized for Python codebases using standard AST module imports. Projects in other languages can be searched and read via MCP, but diagram AST parsing is Python-specific.
2. **Stateless Turn Routing**: To prevent the specialist sticking problem noted above, each turn re-enters through the `coordinator`. Complex multi-turn pronoun references (e.g., *"explain that again"*) rely on the client providing message context.
