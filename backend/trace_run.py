"""Execution tracer using ADK Runner and InMemorySessionService with automatic retry on transient spikes."""
import asyncio
import inspect
import sys
import time
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from code_helper.agent import root_agent

APP_NAME = "code_helper"
USER_ID = "tester"

async def trace_query(query: str, max_retries: int = 3):
    print(f"\n==================================================", flush=True)
    print(f"QUERY: \"{query}\"", flush=True)
    print(f"==================================================", flush=True)

    for attempt in range(max_retries):
        try:
            session_service = InMemorySessionService()
            runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
            session_id = str(uuid.uuid4())

            create_call = session_service.create_session(user_id=USER_ID, session_id=session_id, app_name=APP_NAME)
            if inspect.isawaitable(create_call):
                await create_call

            msg = types.Content(role="user", parts=[types.Part(text=query)])
            final_agent = ""
            final_text = ""

            from code_helper.trace import parse_event_trace, extract_final_answer

            async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=msg):
                steps = parse_event_trace(event)
                for step in steps:
                    if step["kind"] == "route":
                        print(f"[EVENT] Author: {step['from']} | Function Call: transfer_to_agent | Args: {{'agent_name': '{step['to']}'}}", flush=True)
                        print(f"[EVENT] Author: {step['from']} | Function Response: transfer_to_agent | Result: {{'result': None}}...", flush=True)
                    elif step["kind"] == "tool_call":
                        print(f"[EVENT] Author: {step['agent']} | Function Call: {step['name']} | Args: {step['args']}", flush=True)
                    elif step["kind"] == "tool_result":
                        preview = step["preview"][:200]
                        print(f"[EVENT] Author: {step['agent']} | Function Response: {step['name']} | Result: {preview}...", flush=True)

                ans, ag = extract_final_answer(event)
                if ans:
                    final_text = ans
                    final_agent = ag

            print(f"[FINAL ANSWER] (Agent: {final_agent}):\n{final_text}\n", flush=True)
            return final_agent, final_text

        except Exception as e:
            err_str = str(e)
            if ("503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str) and attempt < max_retries - 1:
                wait_time = 10 * (attempt + 1)
                print(f"[RETRY] Hit transient {e.__class__.__name__}. Waiting {wait_time}s before retry...", flush=True)
                await asyncio.sleep(wait_time)
                continue
            raise

async def main():
    if len(sys.argv) > 1:
        queries = sys.argv[1:]
    else:
        queries = [
            "Where is the User class defined?",
            "What is the capital of France?",
        ]

    for q in queries:
        await trace_query(q)
        await asyncio.sleep(2)  # small pause between turns

if __name__ == "__main__":
    asyncio.run(main())
