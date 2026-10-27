"""Live integration tests requiring API keys and network access (marked with @pytest.mark.live)."""
import asyncio
import inspect
import time
import uuid
import pytest

from code_helper.agent import root_agent
from code_helper.rag.embedder import embed
from code_helper.rag.store import get_client, ensure_index, get_index, store_chunks
from code_helper.rag.chunker import Chunk
from code_helper.tools.mcp_tools import read_source_file
from code_helper.trace import parse_event_trace, extract_final_answer

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

pytestmark = pytest.mark.live

@pytest.mark.asyncio
async def test_live_embed_dimension():
    """Real embedding call returns vectors with exactly 2048 dimensions."""
    texts = ["def sample_function():\n    return 'test'"]
    vectors = embed(texts, input_type="passage")
    assert len(vectors) == 1
    assert len(vectors[0]) == 2048

@pytest.mark.asyncio
async def test_live_pinecone_index_and_upsert():
    """Pinecone index exists with 2048/cosine and returns an upserted chunk."""
    pc = get_client()
    desc = ensure_index(pc)
    dim = getattr(desc, "dimension", None)
    metric = getattr(desc, "metric", None)
    assert dim == 2048
    assert metric == "cosine"

    # Upsert a test chunk and query it
    test_chunk = Chunk(
        file="live_test_file.py",
        start_line=1,
        end_line=5,
        text="def test_vector_upsert(): pass",
    )
    vec = embed([test_chunk.text], input_type="passage")
    upserted = store_chunks([test_chunk], vec)
    assert upserted == 1

    # Query back
    index = get_index()
    # give Pinecone a moment for consistency
    time.sleep(2)
    query_res = index.query(vector=vec[0], top_k=1, include_metadata=True)
    matches = getattr(query_res, "matches", [])
    assert len(matches) > 0
    match_ids = [m["id"] for m in matches]
    assert test_chunk.id in match_ids

@pytest.mark.asyncio
async def test_live_mcp_read_and_security():
    """MCP filesystem reads main.py and rejects outside paths."""
    content = await read_source_file("main.py")
    assert "def run" in content or "models" in content

    res_outside = await read_source_file("../.env")
    assert "Error" in res_outside or "Access denied" in res_outside

async def _run_agent_query(query: str, max_retries: int = 3):
    """Helper to run a query with Runner and retry on transient quota/503 spikes."""
    for attempt in range(max_retries):
        try:
            session_service = InMemorySessionService()
            runner = Runner(agent=root_agent, app_name="code_helper", session_service=session_service)
            session_id = str(uuid.uuid4())

            create_call = session_service.create_session(
                user_id="tester",
                session_id=session_id,
                app_name="code_helper",
            )
            if inspect.isawaitable(create_call):
                await create_call

            msg = types.Content(role="user", parts=[types.Part(text=query)])
            trace = []
            answer = ""
            agent = ""

            async for event in runner.run_async(
                user_id="tester",
                session_id=session_id,
                new_message=msg,
            ):
                steps = parse_event_trace(event)
                trace.extend(steps)
                ans, ag = extract_final_answer(event)
                if ans:
                    answer = ans
                    agent = ag

            return answer, agent, trace
        except Exception as e:
            err_str = str(e)
            if ("429" in err_str or "503" in err_str or "UNAVAILABLE" in err_str) and attempt < max_retries - 1:
                wait_secs = 12 * (attempt + 1)
                await asyncio.sleep(wait_secs)
                continue
            raise

@pytest.mark.asyncio
async def test_live_runner_returns_gemini_answer():
    """Runner returns a real Gemini answer to a basic question."""
    answer, agent, trace = await _run_agent_query("What does main.py do?")
    assert answer
    assert agent in ["code_explainer", "code_searcher", "onboarding_guide", "architecture_mapper"]
    await asyncio.sleep(3)

@pytest.mark.asyncio
async def test_live_routing_code_searcher():
    """'Where is the User class defined?' routes to code_searcher."""
    answer, agent, trace = await _run_agent_query("Where is the User class defined?")
    routes = [t for t in trace if t["kind"] == "route"]
    assert any(r["to"] == "code_searcher" for r in routes)
    assert agent == "code_searcher"
    await asyncio.sleep(3)

@pytest.mark.asyncio
async def test_live_routing_architecture_mapper():
    """'Show me the architecture diagram.' routes to architecture_mapper."""
    answer, agent, trace = await _run_agent_query("Show me the architecture diagram.")
    routes = [t for t in trace if t["kind"] == "route"]
    assert any(r["to"] == "architecture_mapper" for r in routes)
    assert agent == "architecture_mapper"
    await asyncio.sleep(3)

@pytest.mark.asyncio
async def test_live_routing_onboarding_guide():
    """'I am new. Where do I start?' routes to onboarding_guide."""
    answer, agent, trace = await _run_agent_query("I am new. Where do I start?")
    routes = [t for t in trace if t["kind"] == "route"]
    assert any(r["to"] == "onboarding_guide" for r in routes)
    assert agent == "onboarding_guide"
    await asyncio.sleep(3)

@pytest.mark.asyncio
async def test_live_routing_code_explainer():
    """'Explain what main.py does.' routes to code_explainer."""
    answer, agent, trace = await _run_agent_query("Explain what main.py does.")
    routes = [t for t in trace if t["kind"] == "route"]
    assert any(r["to"] == "code_explainer" for r in routes)
    assert agent == "code_explainer"
    await asyncio.sleep(3)
