# Structure — Multi-Agent Code Helper

## 1. Repository layout

```
multi-agent-code-helper/
├── .gitignore
├── README.md
├── docs/
│   ├── prd.md
│   ├── implementation.md
│   ├── structure.md
│   ├── build.md
│   └── DECISIONS.md
│
├── backend/                        # run ALL adk / uvicorn / pytest commands from here
│   ├── requirements.txt
│   ├── pytest.ini                  # registers the "live" marker
│   ├── .env.example                # placeholders only
│   ├── server.py                   # FastAPI + ADK Runner + InMemorySessionService
│   ├── code_helper/                # ADK agent package
│   │   ├── __init__.py             # from . import agent
│   │   ├── agent.py                # the 5 LlmAgents; root_agent = coordinator
│   │   ├── prompts.py              # 5 instruction strings
│   │   ├── model.py                # MODEL = GEMINI_MODEL
│   │   ├── settings.py             # loads .env, lazy validation
│   │   ├── index_codebase.py       # read -> split -> embed -> store
│   │   ├── .env                    # secrets (NEVER committed)
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── loader.py
│   │   │   ├── chunker.py
│   │   │   ├── embedder.py         # LiteLLM + NVIDIA NIM, enforces 2048
│   │   │   ├── store.py            # Pinecone index + upsert
│   │   │   └── search.py           # embed query + Pinecone query
│   │   └── tools/                  # the 7 registered tools
│   │       ├── __init__.py         # exports the 7 functions
│   │       ├── safe_path.py        # rejects paths outside target
│   │       ├── rag_tools.py        # search_codebase
│   │       ├── mcp_tools.py        # read_source_file (Filesystem MCP, read-only)
│   │       ├── code_tools.py       # explain_code
│   │       ├── project_tools.py    # list_project_files, inspect_project_structure
│   │       ├── diagram_tools.py    # generate_architecture_diagram
│   │       └── onboarding_tools.py # get_onboarding_guide
│   └── tests/
│       ├── conftest.py             # skip live tests unless RUN_LIVE=1
│       ├── fixture_project/        # main.py, models.py, utils.py
│       ├── test_agents.py
│       ├── test_tools_registered.py
│       ├── test_project_tools.py
│       ├── test_chunker.py
│       ├── test_embedder.py
│       ├── test_diagram.py
│       └── test_live.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts              # proxy /api -> http://localhost:8000
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── types.ts
│       ├── data/agents.ts          # 5 agents (name, description, color, example question)
│       ├── lib/
│       │   ├── api.ts
│       │   └── exportMarkdown.ts
│       ├── hooks/useChat.ts
│       └── components/
│           ├── ChatPanel.tsx
│           ├── MessageBubble.tsx   # markdown + code + mermaid
│           ├── MermaidBlock.tsx
│           ├── ChatInput.tsx
│           ├── ExampleChips.tsx
│           ├── TeamSidebar.tsx
│           ├── AgentCard.tsx
│           ├── TracePanel.tsx
│           ├── StatusBar.tsx
│           ├── ExportButton.tsx
│           └── ErrorBanner.tsx
│
└── target_project/                 # the codebase the helper studies (set TARGET_PROJECT_PATH)
```

## 2. Dependency rules
| Module | May depend on | Must not depend on |
|--------|---------------|--------------------|
| `settings.py` | dotenv | other package modules |
| `rag/*` | `settings`, litellm, pinecone | `tools`, `agent`, ADK |
| `tools/*` | `settings`, `safe_path`, `rag.search` (rag_tools only), `mcp` (mcp_tools only) | `agent` |
| `prompts.py`, `model.py` | `settings` (model only) | everything else |
| `agent.py` | `model`, `prompts`, `tools`, ADK | `rag` |
| `server.py` | `code_helper.agent`, ADK Runner/session | `rag`, `tools` |
| Frontend `components/*` | `lib`, `hooks`, `data`, `types` | each other except via props |

## 3. Naming
- Agent names (identical in backend, frontend `agents.ts`, tests): `coordinator`, `code_searcher`, `code_explainer`, `architecture_mapper`, `onboarding_guide`.
- Tool names (exact): `search_codebase`, `read_source_file`, `explain_code`, `list_project_files`, `inspect_project_structure`, `generate_architecture_diagram`, `get_onboarding_guide`.
- Pinecone ids: `<file>:<start_line>-<end_line>`.
- Python `snake_case`; React `PascalCase.tsx`, named exports.

## 4. `.gitignore` (minimum)
```
.env
backend/code_helper/.env
node_modules/
dist/
__pycache__/
*.pyc
.venv/
.pytest_cache/
```

## 5. API contract (backend <-> frontend)
```
GET  /api/health          -> { "status": "ok", "agents": 5 }
POST /api/sessions        -> { "session_id": "uuid" }
POST /api/chat            <- { "session_id": "uuid", "message": "..." }
                          -> { "answer": "markdown", "agent": "code_searcher", "trace": [TraceStep] }
```
```ts
type TraceStep =
  | { kind: "route"; from: string; to: string }
  | { kind: "tool_call"; agent: string; name: string; args: unknown }
  | { kind: "tool_result"; agent: string; name: string; preview: string };
type Message = { id: string; role: "user" | "assistant"; text: string;
                 agent?: string; trace?: TraceStep[]; error?: string };
```
