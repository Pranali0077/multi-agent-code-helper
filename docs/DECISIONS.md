# Decisions Log — Multi-Agent Code Helper

All architectural and implementation decisions made during the project build are recorded here.

## Decision 1: Python Runtime Environment
- **Decision**: Use Python 3.12 (`py -3.12`) for backend virtual environment.
- **Rationale**: Python 3.14 was recently released and has limited precompiled wheel support for dependencies such as pydantic, grpc, and certain ML packages. Python 3.12.4 is stable and fully compatible with google-adk, litellm, and pinecone.

## Decision 2: MCP Filesystem Read-Only Tool
- **Decision**: Restrict StdioServerParameters to `TARGET_PROJECT_PATH` and only invoke `read_text_file` / `read_file` from the server.
- **Rationale**: Guarantees read-only behavior as required by PRD R7 and R9.

## Decision 3: Single Root Agent Coordinator with Sub-agents
- **Decision**: Coordinator configured as `root_agent` with `sub_agents=[code_searcher, code_explainer, architecture_mapper, onboarding_guide]`.
- **Rationale**: Exactly 5 agents, ADK genuine delegation via transfer_to_agent.

## Decision 4: Gemini Model Selection
- **Decision**: Set `GEMINI_MODEL=gemini-3.5-flash-lite` in `.env` and `.env.example`.
- **Rationale**: `gemini-2.5-flash` returned a 404 NOT_FOUND error from the Google Gemini API ("This model models/gemini-2.5-flash is no longer available to new users"). Querying `client.models.list()` confirmed `gemini-3.5-flash-lite` is active, cheap, and fully supports function calling and multi-agent transfers.

## Decision 5: Fresh ADK Session Per Chat Turn in FastAPI Server
- **Decision**: In `server.py`, validate the client's `session_id` against `active_sessions`, but create a fresh internal ADK session for each `/api/chat` call.
- **Rationale**: In ADK's multi-agent architecture, once a session transfers to a specialist (e.g. `code_searcher`), subsequent turns in that same session remain with that specialist unless transferred back. To avoid specialists incorrectly handling unrelated queries or requiring complex re-routing rules, running each turn with the `root_agent` (coordinator) in a fresh ADK session ensures clean, deterministic specialist routing for every user query while maintaining persistent session tracking for the client.
