"""FastAPI server wrapping Google GenAI ADK multi-agent Code Helper."""
import inspect
import uuid
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from code_helper.agent import root_agent
from code_helper.trace import parse_event_trace, extract_final_answer

APP_NAME = "code_helper"
USER_ID = "student"

app = FastAPI(title="Multi-Agent Code Helper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

active_sessions: set[str] = set()

class HealthResponse(BaseModel):
    status: str
    agents: int

class SessionResponse(BaseModel):
    session_id: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str
    agent: str
    trace: List[Dict[str, Any]]

@app.get("/api/health", response_model=HealthResponse)
async def health():
    """Health check endpoint reporting agent count."""
    return {"status": "ok", "agents": 5}

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session():
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    active_sessions.add(session_id)
    return {"session_id": session_id}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint executing the multi-agent system on user queries."""
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    # Validate session existence
    if request.session_id not in active_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{request.session_id}' not found.",
        )

    try:
        # Fresh ADK session per call ensures coordinator always handles routing
        adk_session_id = str(uuid.uuid4())
        create_call = session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=adk_session_id,
        )
        if inspect.isawaitable(create_call):
            await create_call

        msg = types.Content(role="user", parts=[types.Part(text=request.message)])
        trace: List[Dict[str, Any]] = []
        answer = ""
        agent = ""

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=adk_session_id,
            new_message=msg,
        ):
            steps = parse_event_trace(event)
            trace.extend(steps)

            ans, ag = extract_final_answer(event)
            if ans:
                answer = ans
                agent = ag

        return {"answer": answer, "agent": agent, "trace": trace}

    except HTTPException:
        raise
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "quota" in err_str.lower() or "RESOURCE_EXHAUSTED" in err_str:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Wait a minute and try again.",
            )
        # Avoid leaking sensitive keys in unexpected errors
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the request.",
        )
