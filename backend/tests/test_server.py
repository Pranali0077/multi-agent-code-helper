"""Offline tests for FastAPI server endpoints and error mappings using TestClient."""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from server import app, session_service, APP_NAME, USER_ID

client = TestClient(app)

def test_health_endpoint():
    """GET /api/health returns status ok and agent count 5."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok", "agents": 5}

def test_create_session():
    """POST /api/sessions creates and returns a valid session UUID."""
    response = client.post("/api/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    # verify it parses as UUID
    parsed = uuid.UUID(data["session_id"])
    assert str(parsed) == data["session_id"]

def test_chat_empty_message():
    """POST /api/chat with empty or whitespace message returns 422."""
    sess_res = client.post("/api/sessions")
    sess_id = sess_res.json()["session_id"]

    res_empty = client.post("/api/chat", json={"session_id": sess_id, "message": ""})
    assert res_empty.status_code == 422

    res_spaces = client.post("/api/chat", json={"session_id": sess_id, "message": "   "})
    assert res_spaces.status_code == 422

def test_chat_unknown_session():
    """POST /api/chat with non-existent session returns 404."""
    response = client.post("/api/chat", json={"session_id": "non-existent-id", "message": "hello"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_chat_success_mocked_runner():
    """POST /api/chat returns response shape {answer, agent, trace} with parsed events."""
    sess_res = client.post("/api/sessions")
    sess_id = sess_res.json()["session_id"]

    # Mock event objects
    route_call = MagicMock()
    route_call.name = "transfer_to_agent"
    route_call.args = {"agent_name": "code_searcher"}

    event_route = MagicMock()
    event_route.author = "coordinator"
    event_route.get_function_calls.return_value = [route_call]
    event_route.get_function_responses.return_value = []
    event_route.is_final_response.return_value = False
    event_route.content = None

    tool_call = MagicMock()
    tool_call.name = "search_codebase"
    tool_call.args = {"query": "User"}

    event_tool = MagicMock()
    event_tool.author = "code_searcher"
    event_tool.get_function_calls.return_value = [tool_call]
    event_tool.get_function_responses.return_value = []
    event_tool.is_final_response.return_value = False
    event_tool.content = None

    tool_resp = MagicMock()
    tool_resp.name = "search_codebase"
    tool_resp.response = "models.py:1-10\nclass User"

    transfer_resp = MagicMock()
    transfer_resp.name = "transfer_to_agent"
    transfer_resp.response = None
    event_route.get_function_responses.return_value = [transfer_resp]

    event_result = MagicMock()
    event_result.author = "code_searcher"
    event_result.get_function_calls.return_value = []
    event_result.get_function_responses.return_value = [tool_resp]
    event_result.is_final_response.return_value = False
    event_result.content = None

    part = MagicMock()
    part.text = "The User class is defined in models.py."
    content = MagicMock()
    content.parts = [part]

    event_final = MagicMock()
    event_final.author = "code_searcher"
    event_final.get_function_calls.return_value = []
    event_final.get_function_responses.return_value = []
    event_final.is_final_response.return_value = True
    event_final.content = content

    async def mock_run_async(*args, **kwargs):
        for ev in [event_route, event_tool, event_result, event_final]:
            yield ev

    with patch("server.runner.run_async", side_effect=mock_run_async):
        response = client.post("/api/chat", json={"session_id": sess_id, "message": "Where is User defined?"})
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "The User class is defined in models.py."
        assert data["agent"] == "code_searcher"
        # Notice transfer_to_agent tool_result was dropped; trace has exactly 3 steps: route, tool_call, tool_result
        assert len(data["trace"]) == 3
        assert data["trace"][0] == {"kind": "route", "from": "coordinator", "to": "code_searcher"}
        assert data["trace"][1] == {"kind": "tool_call", "agent": "code_searcher", "name": "search_codebase", "args": {"query": "User"}}
        assert data["trace"][2]["kind"] == "tool_result"
        assert data["trace"][2]["name"] == "search_codebase"

def test_chat_multi_turn_fresh_adk_session():
    """Multi-turn requests on same client session run in fresh internal ADK sessions."""
    sess_res = client.post("/api/sessions")
    client_sess_id = sess_res.json()["session_id"]

    adk_sessions_called = []

    async def mock_run_async(*args, **kwargs):
        adk_sessions_called.append(kwargs.get("session_id"))
        ev = MagicMock()
        ev.author = "coordinator"
        ev.get_function_calls.return_value = []
        ev.get_function_responses.return_value = []
        ev.is_final_response.return_value = True
        part = MagicMock()
        part.text = "answer"
        ev.content = MagicMock(parts=[part])
        yield ev

    with patch("server.runner.run_async", side_effect=mock_run_async):
        res1 = client.post("/api/chat", json={"session_id": client_sess_id, "message": "Turn 1"})
        assert res1.status_code == 200
        res2 = client.post("/api/chat", json={"session_id": client_sess_id, "message": "Turn 2"})
        assert res2.status_code == 200

    assert len(adk_sessions_called) == 2
    assert adk_sessions_called[0] != adk_sessions_called[1]
    assert adk_sessions_called[0] != client_sess_id

def test_chat_rate_limit_429():
    """POST /api/chat maps 429 / quota errors to HTTP 429 with clear message."""
    sess_res = client.post("/api/sessions")
    sess_id = sess_res.json()["session_id"]

    async def mock_run_async_429(*args, **kwargs):
        raise Exception("429 RESOURCE_EXHAUSTED Quota exceeded")
        yield  # make it an async generator

    with patch("server.runner.run_async", side_effect=mock_run_async_429):
        response = client.post("/api/chat", json={"session_id": sess_id, "message": "query"})
        assert response.status_code == 429
        assert response.json()["detail"] == "Too many requests. Wait a minute and try again."
