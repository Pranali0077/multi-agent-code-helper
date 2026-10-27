# Implementation — Multi-Agent Code Helper

## 1. Stack
- Python 3.10+: `google-adk`, `litellm>=1.84`, `pinecone`, `python-dotenv`, `fastapi`, `uvicorn`, `pytest`, `pytest-asyncio`, `mcp` (installed with ADK; add if missing)
- Node.js 18+ (Filesystem MCP via `npx`, and the frontend)
- Frontend: React 18 + Vite + TypeScript + Tailwind + `react-markdown` + `rehype-highlight` + `mermaid`
- Windows: set `PYTHONUTF8=1` if you hit `UnicodeDecodeError`.

## 2. Environment (`backend/code_helper/.env`, never committed)
```
GOOGLE_API_KEY=your-gemini-key
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GEMINI_MODEL=gemini-2.5-flash

NVIDIA_API_KEY=nvapi-your-key
NVIDIA_NIM_API_KEY=nvapi-your-key
NVIDIA_EMBED_MODEL=nvidia_nim/nvidia/nemotron-3-embed-1b
EMBED_DIM=2048

PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=code-helper
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

TARGET_PROJECT_PATH=/absolute/path/to/target_project
```
`settings.py` loads this with `python-dotenv`, exposes constants, and raises a clear error naming any missing variable (only checked when the value is first used, so offline tests do not need keys).

## 3. Shared model
```python
# model.py
from .settings import GEMINI_MODEL
MODEL = GEMINI_MODEL   # ADK accepts a Gemini model name string directly
```
All 5 agents import `MODEL`.

## 4. RAG pipeline (own code, `rag/`)

1. **Read** (`loader.py`): `load_python_files(root) -> list[(rel_path, text)]`; skip `__pycache__`, `.venv`, `.git`, `node_modules`.
2. **Split** (`chunker.py`): `chunk_text(file, text, size=800, overlap=150) -> list[Chunk]`. Character window that prefers to end at a newline. Keep `start_line`/`end_line`. Compare 800/150 with 400/80 on 5 questions; record the winner in the README.
3. **Embed** (`embedder.py`):
   ```python
   import litellm
   def embed(texts, input_type):            # "passage" or "query"
       resp = litellm.embedding(model=EMBED_MODEL, input=texts,
                                input_type=input_type)  # if rejected, drop and retry without it
       vectors = [d["embedding"] for d in resp["data"]]
       for v in vectors:
           if len(v) != 2048:
               raise ValueError(f"Expected 2048 dims, got {len(v)}")
       return vectors
   ```
   Batch size 16; retry with backoff on 429. **Never pad or truncate.**
4. **Store** (`store.py`): create index if missing (`dimension=2048`, `metric="cosine"`, serverless spec), wait until ready, upsert `(id, vector, metadata)` with id `"<file>:<start>-<end>"` and metadata `{file, start_line, end_line, text}`. `ensure_index()` must fail loudly if an existing index has a different dimension or metric.
5. **Search** (`search.py`): `search(query, top_k=4)` embeds the query (`input_type="query"`), queries Pinecone, returns `[{file, start_line, end_line, score, text}]`.
6. **Answer**: the `code_searcher` agent receives the formatted chunks from `search_codebase` and answers only from them.

`index_codebase.py` runs read -> split -> embed -> store; safe to re-run (deterministic ids).

## 5. The seven tools (`tools/`)
Plain Python functions, type hints, clear docstrings (the agent reads them). Return strings; catch exceptions and return a readable error instead of raising. All paths pass through `safe_path()` (resolve and reject anything outside `TARGET_PROJECT_PATH`).

| Tool | File | Behavior |
|------|------|----------|
| `search_codebase(query: str, top_k: int = 4) -> str` | `rag_tools.py` | Calls `rag.search`; formats `file:start-end (score)` + code. Returns `"No relevant code found."` when empty. |
| `read_source_file(file_name: str) -> str` (async) | `mcp_tools.py` | Opens the Filesystem MCP server over stdio, calls `read_text_file` (fallback `read_file`) and returns text. Never calls any other MCP tool. |
| `explain_code(file_name: str) -> str` | `code_tools.py` | `ast` summary: module docstring, classes, functions with signatures/docstrings/line numbers, top-level calls. No AI. |
| `list_project_files() -> str` | `project_tools.py` | Relative paths + line counts of `.py` files. |
| `inspect_project_structure() -> str` | `project_tools.py` | Per file: classes, functions, imports; marks local (project) imports. |
| `generate_architecture_diagram() -> str` | `diagram_tools.py` | Builds import edges between project modules and returns a fenced ```mermaid block. |
| `get_onboarding_guide() -> str` | `onboarding_tools.py` | Markdown: what the project does (from docstrings/README), file table, entry point(s), how to run, suggested reading order. |

### 5.1 `read_source_file` via MCP (read-only)
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ALLOWED = {"read_text_file", "read_file"}          # read-only allow-list

async def read_source_file(file_name: str) -> str:
    """Read one source file from the target project and return its text."""
    path = safe_path(file_name)
    params = StdioServerParameters(command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", TARGET_PROJECT_PATH])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            tools = {t.name for t in (await session.list_tools()).tools}
            name = next(n for n in ("read_text_file", "read_file") if n in tools and n in ALLOWED)
            result = await session.call_tool(name, {"path": str(path)})
            return "".join(c.text for c in result.content if hasattr(c, "text"))
```
Notes: write/move/edit tools of the server are never referenced or exposed. Server args restrict it to the target folder. Starting `npx` per call is slow but simple; keep it unless it is a real problem.

### 5.2 Diagram generation
- Parse each file with `ast`; collect `import x` / `from x import y`; keep only modules that exist in the project.
- Node id = file stem with non `[A-Za-z0-9_]` replaced by `_`; label = filename.
- Output:
  ````
  ```mermaid
  graph TD
    main["main.py"] --> models["models.py"]
    main --> utils["utils.py"]
  ```
  ````
- Isolated files still appear as nodes. Deterministic order (sorted).

## 6. Agents (`agent.py`)
```python
from google.adk.agents import LlmAgent

code_searcher = LlmAgent(name="code_searcher", model=MODEL,
    description="Finds where something is in the code using semantic (RAG) search.",
    instruction=SEARCHER, tools=[search_codebase])

code_explainer = LlmAgent(name="code_explainer", model=MODEL,
    description="Explains source code, functions and their purpose for a named file.",
    instruction=EXPLAINER, tools=[read_source_file, explain_code])

architecture_mapper = LlmAgent(name="architecture_mapper", model=MODEL,
    description="Shows project structure and generates Mermaid architecture diagrams.",
    instruction=MAPPER, tools=[list_project_files, inspect_project_structure, generate_architecture_diagram])

onboarding_guide = LlmAgent(name="onboarding_guide", model=MODEL,
    description="Helps new developers understand the project, its files, and how to run it.",
    instruction=GUIDE, tools=[get_onboarding_guide, list_project_files])

root_agent = LlmAgent(name="coordinator", model=MODEL,
    description="Understands the request and delegates it to the right specialist.",
    instruction=BOSS,
    sub_agents=[code_searcher, code_explainer, architecture_mapper, onboarding_guide])
```
Exactly 5 `LlmAgent` objects. `root_agent` is the Coordinator.

### Instructions (`prompts.py`)
- **BOSS:** "You never answer yourself. Transfer to exactly one specialist. Where/find/which code -> code_searcher. Explain a file/function/what does X do -> code_explainer. Structure/diagram/how files connect -> architecture_mapper. New to project/where to start/how to run -> onboarding_guide."
- **SEARCHER:** "Call search_codebase first. Answer only from the returned code. Cite file and line range. If nothing useful, say 'I could not find that'."
- **EXPLAINER:** "Call read_source_file for the named file and explain_code for its structure. Explain purpose, main functions, inputs/outputs. If the file is missing, say 'I could not find that'."
- **MAPPER:** "Use your tools; never guess. For diagrams, call generate_architecture_diagram and return its mermaid block unchanged, then add 2-3 sentences explaining it."
- **GUIDE:** "Call get_onboarding_guide. Present what the project does, key files, how to run, and a reading order. Do not invent commands or files."

## 7. Execution with Runner and sessions (`server.py`)
One small FastAPI app wraps ADK's `Runner`; this is also how the frontend talks to the agents.

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

APP_NAME, USER_ID = "code_helper", "student"
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

async def ask(session_id: str, text: str) -> dict:
    # create session on first use (in newer ADK versions create_session is async)
    msg = types.Content(role="user", parts=[types.Part(text=text)])
    trace, answer, agent = [], "", ""
    async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=msg):
        for call in event.get_function_calls():
            if call.name == "transfer_to_agent":
                trace.append({"kind": "route", "from": event.author, "to": call.args.get("agent_name")})
            else:
                trace.append({"kind": "tool_call", "agent": event.author, "name": call.name, "args": call.args})
        for resp in event.get_function_responses():
            trace.append({"kind": "tool_result", "agent": event.author, "name": resp.name,
                          "preview": str(resp.response)[:300]})
        if event.is_final_response() and event.content and event.content.parts:
            answer = "".join(p.text or "" for p in event.content.parts)
            agent = event.author
    return {"answer": answer, "agent": agent, "trace": trace}
```
Endpoints:
- `GET /api/health` -> `{status:"ok", agents:5}`
- `POST /api/sessions` -> `{session_id}` (uuid; creates the ADK session)
- `POST /api/chat` body `{session_id, message}` -> `{answer, agent, trace}`
- Map 429/quota errors to HTTP 429 with message "Too many requests. Wait a minute and try again."
- CORS not needed with the Vite proxy; add `allow_origins=["http://localhost:5173"]` anyway.

`adk run` and `adk web` also work against the same `root_agent` for debugging (run from `backend/`). If your ADK version differs on `get_function_calls` or `create_session` signatures, adjust and note it in `docs/DECISIONS.md`.

## 8. Frontend implementation
- `api.ts`: `health()`, `newSession()`, `chat(sessionId, message)` against `/api/*` (Vite proxy to `http://localhost:8000`); 90s timeout; maps 429 to the friendly error.
- `useChat.ts`: `messages`, `loading`, `sessionId`, `activeAgent`, `send()`, `newChat()`.
- `MessageBubble`: `react-markdown` + `rehype-highlight`; custom `code` renderer: if language is `mermaid`, render `<MermaidBlock code=.../>`.
- `MermaidBlock`: `mermaid.initialize({startOnLoad:false, theme: dark ? "dark":"default"})`, then `mermaid.render(id, code)` inside `useEffect`; on parse error show the raw code with a small "diagram could not be rendered" note.
- `TeamSidebar` (5 cards from `data/agents.ts`, highlight `activeAgent`), `TracePanel`, `ExampleChips`, `StatusBar`, `ExportButton`, `ErrorBanner`.
- Agent names and descriptions in `data/agents.ts` must match the backend exactly.

## 9. Tests (`backend/tests/`)
Offline fixtures: `tests/fixture_project/{main.py, models.py, utils.py}` where `main.py` imports `models` and `utils`.

| File | Tests |
|------|-------|
| `test_agents.py` | 5 LlmAgents exist; names exact; coordinator has 4 sub_agents; coordinator has no tools; each specialist has expected tools |
| `test_tools_registered.py` | The 7 tool names are each attached to at least one agent; exactly these 7 custom tools |
| `test_project_tools.py` | list/inspect/explain_code/onboarding against fixture; path guard rejects `../x` |
| `test_chunker.py` | sizes, overlap, line numbers, no empty chunks |
| `test_embedder.py` | mock `litellm.embedding`; 2048 passes; 1024 or 2049 raises; no padding |
| `test_diagram.py` | output starts with a ```mermaid fence and `graph TD`; contains `main --> models` and `main --> utils`; node ids valid; no hardcoded names when fixture changes |
| `test_live.py` (`@pytest.mark.live`) | real embed is 2048; Pinecone index is 2048/cosine and returns an upserted chunk; MCP reads `main.py`, a path outside the target fails, server's write tools are not among our allow-list; Runner returns a real Gemini answer; 4 canonical questions route correctly |

`pytest.ini`: `markers = live: needs network and API keys`; `conftest.py` skips `live` tests unless `RUN_LIVE=1`.
Frontend: Vitest for `exportMarkdown` and a render test for `MermaidBlock` error fallback.
