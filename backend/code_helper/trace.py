"""Event to trace step parsing utility for ADK Runner events."""
from typing import Any, Dict, List, Tuple

def parse_event_trace(event: Any) -> List[Dict[str, Any]]:
    """
    Parse an ADK event into standardized trace items:
    - {"kind": "route", "from": ..., "to": ...}
    - {"kind": "tool_call", "agent": ..., "name": ..., "args": ...}
    - {"kind": "tool_result", "agent": ..., "name": ..., "preview": ...} (preview max 300 chars)
    """
    steps: List[Dict[str, Any]] = []
    author = getattr(event, "author", "") or "coordinator"

    calls = event.get_function_calls() if hasattr(event, "get_function_calls") else []
    for call in calls:
        call_name = getattr(call, "name", "")
        call_args = getattr(call, "args", {}) or {}
        if call_name == "transfer_to_agent":
            to_agent = call_args.get("agent_name", "") if isinstance(call_args, dict) else ""
            steps.append({
                "kind": "route",
                "from": author,
                "to": to_agent,
            })
        else:
            steps.append({
                "kind": "tool_call",
                "agent": author,
                "name": call_name,
                "args": call_args,
            })

    responses = event.get_function_responses() if hasattr(event, "get_function_responses") else []
    for resp in responses:
        resp_name = getattr(resp, "name", "")
        if resp_name == "transfer_to_agent":
            continue
        resp_val = getattr(resp, "response", "")
        steps.append({
            "kind": "tool_result",
            "agent": author,
            "name": resp_name,
            "preview": str(resp_val)[:300],
        })

    return steps

def extract_final_answer(event: Any) -> Tuple[str, str]:
    """Extract (answer, agent) from an event if it contains the final response."""
    is_final = event.is_final_response() if hasattr(event, "is_final_response") else False
    if is_final and getattr(event, "content", None) and getattr(event.content, "parts", None):
        text = "".join(getattr(p, "text", "") or "" for p in event.content.parts)
        author = getattr(event, "author", "") or "coordinator"
        return text, author
    return "", ""
