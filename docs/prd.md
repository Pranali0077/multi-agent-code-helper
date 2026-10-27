# PRD — Multi-Agent Code Helper (Google ADK + Custom RAG + Frontend)

## 1. Summary
A multi-agent assistant that helps developers understand and explore a Python codebase. Built with the real Google ADK framework: exactly 5 agents (1 Coordinator + 4 specialists), 7 registered tools, a hand-written RAG pipeline (NVIDIA embeddings + Pinecone), a read-only Filesystem MCP integration, and Mermaid architecture diagrams. A small React chat frontend sits on top so the system is easy to demo.

Guiding constraint from the professor: **keep it small, understandable, easy to explain.** No extra agents, tools, MCP servers, or frameworks.

## 2. Users
- Primary: a developer new to a codebase.
- Secondary: the professor/reviewer checking each requirement.

## 3. Non-goals
No login, no chat history database, no editing/running the target code, no deployment setup, no LangChain/LlamaIndex, no extra agents/tools/MCP servers.

## 4. Requirements and how they are met (traceability)

### R1 — Exactly 5 agents
| # | Agent (ADK name) | Responsibility |
|---|------------------|----------------|
| 1 | `coordinator` | Understands the request and delegates to one specialist. Never answers itself. |
| 2 | `code_searcher` | Finds relevant code using RAG. |
| 3 | `code_explainer` | Explains source code, functions, and their purpose. |
| 4 | `architecture_mapper` | Examines project structure and generates Mermaid diagrams. |
| 5 | `onboarding_guide` | Helps new developers understand the project, files, and workflow. |
The Coordinator is one of the five. Total = 5, not 6.

### R2 — Real Google ADK
- Agents are `google.adk.agents.LlmAgent`; the Coordinator uses `sub_agents=[...]` for genuine delegation (`transfer_to_agent`).
- Execution uses ADK `Runner` + `InMemorySessionService`.
- Real model calls through the configured Gemini model (`GEMINI_MODEL`, default `gemini-2.5-flash`).
- No simulating agents with plain Python functions.

### R3 — Seven registered tools
| # | Tool | Owner agent | AI used? | Purpose |
|---|------|-------------|----------|---------|
| 1 | `search_codebase` | code_searcher | embeddings only | Semantic search over Pinecone |
| 2 | `read_source_file` | code_explainer | no | Reads a file through the Filesystem MCP server (read-only) |
| 3 | `explain_code` | code_explainer | no | Returns structured facts about a file (classes, functions, signatures, docstrings, calls) so the agent can explain accurately |
| 4 | `list_project_files` | architecture_mapper, onboarding_guide | no | Lists Python files with sizes |
| 5 | `inspect_project_structure` | architecture_mapper | no | Per-file classes, functions, imports (via `ast`) |
| 6 | `generate_architecture_diagram` | architecture_mapper | no | Mermaid diagram built from real import relationships |
| 7 | `get_onboarding_guide` | onboarding_guide | no | Builds a guide: purpose, files, entry point, how to run |
All seven are functional and attached to the agents that need them.

### R4 — Custom RAG (no LangChain/LlamaIndex)
Read files -> split into chunks -> embed -> store in Pinecone -> embed the query -> retrieve by semantic search -> the agent answers using the retrieved code.

### R5 — NVIDIA embeddings
- Model Nemotron-3 Embed 1B via NVIDIA NIM through LiteLLM; identifier `nvidia_nim/nvidia/nemotron-3-embed-1b`.
- Dimension **2048**, native output. Never pad or truncate; raise an error if the length is not 2048.
- Credentials from environment: `NVIDIA_API_KEY` and `NVIDIA_NIM_API_KEY`.

### R6 — Pinecone
Index `code-helper` (already verified earlier): dimension 2048, cosine. Stores chunk text + metadata (file, start_line, end_line). Retrieval by semantic similarity.

### R7 — Filesystem MCP
`@modelcontextprotocol/server-filesystem` scoped to the target project folder only. Only read operations are ever called (allow-list: `read_text_file`, `list_directory`). Final verification of read-only behavior and full MCP integration is part of the tests (see R9).

### R8 — Mermaid architecture diagram
Generated from the target project's real imports (e.g. `main.py --> models.py`, `main.py --> utils.py`). No hardcoded sample diagram. Output must be valid Mermaid (`graph TD`, safe node IDs). The frontend renders it.

### R9 — Testing
Offline unit tests run with no network or API keys. Live tests are marked `live` and run only with `RUN_LIVE=1`.

| Check | Type |
|-------|------|
| 5 agents registered; Coordinator has exactly 4 sub_agents | offline |
| 7 tools registered and attached to the right agents | offline |
| Each non-network tool works on a fixture project | offline |
| Chunker produces correct chunks/line numbers | offline |
| Embedding wrapper rejects any vector not 2048 long (mocked) | offline |
| Mermaid output valid and reflects fixture imports | offline |
| Onboarding guide mentions files, entry point, run command | offline |
| Path guard rejects paths outside the target project | offline |
| Real NVIDIA embedding has exactly 2048 dims | live |
| Pinecone upsert + query returns expected chunk; index is 2048/cosine | live |
| Filesystem MCP reads a source file; write tools not exposed; outside path denied | live |
| Coordinator routes the 4 canonical questions to the right specialist | live |
| ADK executes a real Gemini request via Runner | live |

### R10 — Keep it simple
One shared Gemini model object, ~7 small tool functions, 5 small RAG modules, 1 small FastAPI file, small React app. Do not rewrite working components without a reason.

## 5. Frontend requirements
- **Chat panel** with markdown answers, syntax-highlighted code, and **Mermaid diagrams rendered** from ```mermaid blocks.
- **Team sidebar** with the 5 agents; the answering agent is highlighted.
- **Trace panel** per answer: delegation (`coordinator -> code_searcher`) and tool calls with short results.
- **Example chips** for the 4 canonical questions.
- **Status bar**: backend health, session id. "New chat" button.
- **Export** conversation as `sample_questions.md` (question, answer, agent).
- Loading state, friendly errors (network, rate limit), responsive to 360px, light/dark.

## 6. Canonical questions (also used in tests and README)
| Question | Expected agent |
|----------|----------------|
| Where is the User class defined? | code_searcher |
| Explain what main.py does. | code_explainer |
| Show me the architecture diagram. | architecture_mapper |
| I am new. Where do I start? | onboarding_guide |

## 7. Deliverables
Code (no keys), `.env.example`, `README.md` (description, agents table, tools table, chunk size and why, MCP server and why, run commands, 3 sample Q&A with agent, 1 problem + fix).

## 8. Acceptance criteria
- [ ] Exactly 5 agents; Coordinator delegates to 4 specialists
- [ ] Real ADK `LlmAgent`, `Runner`, `InMemorySessionService`, Gemini calls
- [ ] 7 tools registered, functional, attached to correct agents
- [ ] Custom RAG, no LangChain/LlamaIndex
- [ ] 2048-dim NVIDIA embeddings, no padding/truncation
- [ ] Pinecone 2048 / cosine
- [ ] Filesystem MCP restricted to the target, read-only usage verified
- [ ] Mermaid diagram from real structure, renders in frontend
- [ ] Offline tests pass without network; live tests pass with `RUN_LIVE=1`
- [ ] Keys only in `.env`

## 9. Open items
- Target project: use the professor's project (e.g. `main.py`, `models.py`, `utils.py`) or the guide's repo; set `TARGET_PROJECT_PATH`. Repo link still **TO CONFIRM**.
- `server-filesystem` tool names change between versions (`read_text_file` vs `read_file`); confirm by listing tools on first run.
- The filesystem server is not read-only by itself. Read-only is enforced by our allow-list and path guard (optionally also `chmod -R a-w` on the target).
