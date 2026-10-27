# Build Guide — Multi-Agent Code Helper

Follow phases in order. Do not start a phase until its gate passes. Keep everything small; add nothing that is not in `prd.md`.

## Phase 0 — Scaffold
1. Create the tree from `structure.md`; `git init`; add `.gitignore`.
2. Backend:
   ```
   cd backend
   python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install google-adk "litellm>=1.84" pinecone python-dotenv fastapi uvicorn pytest pytest-asyncio
   pip freeze > requirements.txt
   ```
3. Put the target project in `target_project/` (professor's project or the guide's repo). Avoid spaces in the folder path.
4. Copy `.env.example` to `backend/code_helper/.env`; fill in `GOOGLE_API_KEY`, `NVIDIA_API_KEY`, `NVIDIA_NIM_API_KEY`, `PINECONE_API_KEY`, and the absolute `TARGET_PROJECT_PATH`. Check `node -v`.
5. Create `backend/tests/fixture_project/` with `main.py` (imports `models` and `utils`), `models.py`, `utils.py`.

**Gate 0:** `python -c "import google.adk, litellm, pinecone"` succeeds; `pytest` runs (0 tests is fine).

## Phase 1 — RAG on its own
1. Write `loader.py`, `chunker.py`, `embedder.py`, `store.py`, `search.py`, `index_codebase.py`.
2. Offline tests first: `test_chunker.py`, `test_embedder.py` (mocked, enforces 2048, no padding).
3. Run `python code_helper/index_codebase.py` (from `backend/`; use `python -m code_helper.index_codebase` if imports fail).
4. Try `search("where are embeddings created?")` in a Python shell.

**Gate 1:** `pytest` passes offline; the Pinecone index is 2048 / cosine; real embeddings are exactly 2048 long; top-3 results for 5 test questions include the right file in at least 4. Record the 800/150 vs 400/80 comparison for the README.

## Phase 2 — Non-AI tools
1. Write `safe_path.py`, `project_tools.py`, `code_tools.py`, `diagram_tools.py`, `onboarding_tools.py`.
2. Tests against `fixture_project`: `test_project_tools.py`, `test_diagram.py` (must contain `main --> models` and `main --> utils`; changing the fixture changes the diagram).

**Gate 2:** offline tests pass; `../` paths are rejected; diagram output starts with a ```mermaid fence and `graph TD`.

## Phase 3 — MCP read tool
1. Write `mcp_tools.py` (`read_source_file`) as in `implementation.md` 5.1.
2. List the server's tools once and confirm the read tool name (`read_text_file` vs `read_file`).
3. Live check: read `main.py`; try a path outside the target (must fail); confirm no write/edit/move tool is referenced anywhere in our code.

**Gate 3:** `RUN_LIVE=1 pytest -k mcp` passes: reads the intended file, denies outside paths.

## Phase 4 — `search_codebase` + one specialist + Coordinator
1. Write `rag_tools.py`, `model.py`, `prompts.py`, then `code_searcher` only in `agent.py`.
2. `adk run code_helper` (from `backend/`): "Where is the User class defined?"
3. Add the Coordinator with `sub_agents=[code_searcher]`; make it `root_agent`. Check in `adk web` that you see coordinator -> code_searcher -> `search_codebase`.

**Gate 4:** the Coordinator delegates without answering; the searcher answers from chunks and says "I could not find that" for an unrelated question.

## Phase 5 — Remaining specialists (one at a time)
1. `architecture_mapper` -> "Show me the architecture diagram."
2. `onboarding_guide` -> "I am new. Where do I start?"
3. `code_explainer` -> "Explain what main.py does."
4. Add `test_agents.py` and `test_tools_registered.py` (5 agents, 4 sub_agents, 7 tools).

**Gate 5:** offline tests pass; all 4 canonical questions route to the right specialist in `adk web`. If one misroutes, fix the description or the Coordinator instruction, not the code structure.

## Phase 6 — Runner + API server
1. Write `server.py` (Runner, InMemorySessionService, `/api/health`, `/api/sessions`, `/api/chat`).
2. Run: `cd backend && uvicorn server:app --port 8000 --reload`
3. Test with curl:
   ```
   curl -s localhost:8000/api/health
   SID=$(curl -s -X POST localhost:8000/api/sessions | python -c "import sys,json;print(json.load(sys.stdin)['session_id'])")
   curl -s -X POST localhost:8000/api/chat -H "Content-Type: application/json" \
     -d "{\"session_id\":\"$SID\",\"message\":\"Where is the search done?\"}"
   ```
4. Write `test_live.py` (embedding dims, Pinecone, MCP, Runner real Gemini call, 4 routing questions).

**Gate 6:** response has `answer`, `agent`, and a `trace` containing a `route` step and a tool call. `RUN_LIVE=1 pytest` passes fully; plain `pytest` passes with no network.

## Phase 7 — Frontend
1. Scaffold:
   ```
   cd frontend
   npm create vite@latest . -- --template react-ts
   npm i react-markdown rehype-highlight highlight.js mermaid
   npm i -D tailwindcss postcss autoprefixer vitest @testing-library/react
   npx tailwindcss init -p
   ```
2. Vite proxy: `/api` -> `http://localhost:8000` (no rewrite; paths already start with `/api`).
3. Build order: `types.ts` -> `data/agents.ts` -> `lib/api.ts` -> `hooks/useChat.ts` -> `ChatPanel`/`ChatInput`/`MessageBubble` -> `MermaidBlock` -> `TeamSidebar`/`AgentCard` -> `TracePanel` -> `ExampleChips` -> `StatusBar`/`ErrorBanner` -> `ExportButton` -> polish (dark mode, 360px layout).
4. Run both:
   ```
   # terminal 1 (backend/)   uvicorn server:app --port 8000 --reload
   # terminal 2 (frontend/)  npm run dev
   ```

**Gate 7:**
- Each example chip returns an answer, highlights the correct agent, and shows the trace.
- "Show me the architecture diagram" renders a real diagram of the target project.
- Backend stopped -> status bar shows "not reachable" and send shows a friendly error.
- "New chat" starts a fresh session. Export downloads a markdown file.

## Phase 8 — README and final check
1. `README.md`: 2–3 sentence description, agents table, tools table, chunk size and why, MCP server and why, run commands (index, `pytest`, `RUN_LIVE=1 pytest`, `adk web`, `uvicorn`, `npm run dev`), 3 sample Q&A with agent (use Export), 1 problem + fix.
2. Secret scan:
   ```
   grep -rniE "nvapi-|pcsk_|AIza" --exclude-dir=node_modules --exclude-dir=.venv --exclude=.env .
   ```
   Only placeholders may match.

## Final checklist (maps to professor's sections)
- [ ] 1. Exactly 5 agents (Coordinator + 4 specialists)
- [ ] 2. Real ADK: `LlmAgent`, `sub_agents`, `Runner`, `InMemorySessionService`, real Gemini calls
- [ ] 3. 7 tools registered, functional, on the right agents
- [ ] 4. Custom RAG, no LangChain/LlamaIndex, answers use retrieved code
- [ ] 5. `nvidia_nim/nvidia/nemotron-3-embed-1b`, exactly 2048 dims, no pad/truncate, both NVIDIA env vars supported
- [ ] 6. Pinecone 2048 / cosine, chunks + metadata stored and retrieved
- [ ] 7. Filesystem MCP limited to target, read-only usage verified
- [ ] 8. Mermaid diagram from real imports, valid, renders in UI
- [ ] 9. Offline tests pass with no network; live tests pass with `RUN_LIVE=1`
- [ ] 10. Small and simple: no extra agents, tools, MCP servers or frameworks

## Troubleshooting
| Symptom | Fix |
|---------|-----|
| Gemini auth error | `GOOGLE_API_KEY` set and `GOOGLE_GENAI_USE_VERTEXAI=FALSE` |
| LiteLLM NVIDIA auth error | Set both `NVIDIA_API_KEY` and `NVIDIA_NIM_API_KEY` |
| Embedding length not 2048 | Wrong model id; do not pad/truncate, fix the model |
| `input_type` rejected | Remove that argument and retry |
| Pinecone dimension error | Delete and recreate index (2048, cosine) |
| MCP tool not found | List server tools; use the real read tool name |
| Coordinator answers itself | Strengthen "never answer yourself"; sharpen specialist descriptions |
| `create_session` / event method errors | ADK API differs by version; check installed version docs, note in DECISIONS.md |
| 429 / quota | Wait a minute; use a lighter Gemini model |
| Mermaid fails to render | Check node ids are alphanumeric/underscore; frontend falls back to raw code |
