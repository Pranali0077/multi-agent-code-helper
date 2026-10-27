Build the complete "Multi-Agent Code Helper" project (backend + React frontend) using these four files as the only source of truth:
@docs/prd.md @docs/implementation.md @docs/structure.md @docs/build.md

Read all four fully first. Then follow build.md from Phase 0, one phase at a time. Run each phase's gate and fix failures before moving on.

Rules:
- Real Google ADK: exactly 5 LlmAgents (1 coordinator with sub_agents + 4 specialists), run through ADK Runner and InMemorySessionService, real Gemini model calls.
- Exactly 7 tools with the exact names in prd.md, attached to the right agents.
- Own RAG in Python (read, split, embed, store in Pinecone, embed query, retrieve). No LangChain or LlamaIndex.
- Embeddings: LiteLLM model nvidia_nim/nvidia/nemotron-3-embed-1b, exactly 2048 dims, never pad or truncate. Pinecone index 2048 / cosine.
- Filesystem MCP restricted to the target project and used read-only (read tools only).
- Architecture diagram: Mermaid generated from real imports, never hardcoded.
- Frontend: React + Vite + TypeScript + Tailwind, talks to the FastAPI server in backend/server.py through the Vite proxy; renders markdown, code and Mermaid; shows the answering agent and tool trace.
- Offline unit tests must run with no network or keys; live tests are marked `live` and run only with RUN_LIVE=1.
- Keys only in .env; commit .env.example with placeholders.
- Keep it small and easy to explain. No extra agents, tools, MCP servers or frameworks. Don't rewrite working parts without a reason. If something is unclear, choose the simplest option and log it in docs/DECISIONS.md.
- After each phase, give a 2-3 line status and the command to see it working.

Start with Phase 0.
