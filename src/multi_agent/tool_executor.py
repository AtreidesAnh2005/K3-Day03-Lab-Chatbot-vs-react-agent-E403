"""Consent-aware tool execution for specialist agents."""

from __future__ import annotations

from typing import Any

from multi_agent.state import AgentState
from tools import AVAILABLE_TOOLS

SUCCESS_STATUSES = {"success", "warning", "insufficient_data"}


def call_tool(
    state: AgentState,
    agent: str,
    tool_name: str,
    **arguments: Any,
) -> dict[str, Any] | None:
    """Execute a Role 2 tool, record its envelope, and return its data."""
    tool = AVAILABLE_TOOLS.get(tool_name)
    if tool is None:
        state.add_error(agent, "UNKNOWN_TOOL", f"Tool {tool_name!r} is not registered.")
        state.record(agent, "tool_rejected", {"tool": tool_name, "arguments": arguments})
        return None

    state.record(agent, "tool_call", {"tool": tool_name, "arguments": arguments})
    try:
        result = tool(**arguments)
    except Exception as exc:
        state.add_error(agent, "TOOL_EXCEPTION", str(exc), {"tool": tool_name})
        state.record(agent, "tool_exception", {"tool": tool_name, "message": str(exc)})
        return None

    observation = {
        "agent": agent,
        "tool": tool_name,
        "arguments": arguments,
        "result": result,
    }
    state.observations.append(observation)

    if not isinstance(result, dict):
        state.add_error(agent, "INVALID_TOOL_ENVELOPE", f"{tool_name} returned a non-object.")
        state.record(agent, "tool_failed", {"tool": tool_name, "status": "invalid"})
        return None

    status = result.get("status")
    if status not in SUCCESS_STATUSES or result.get("data") is None:
        error = result.get("error") or {}
        state.add_error(
            agent,
            str(error.get("code") or status or "TOOL_ERROR"),
            str(error.get("message") or f"{tool_name} failed."),
            {"tool": tool_name, "status": status},
        )
        state.record(agent, "tool_failed", {"tool": tool_name, "status": status})
        return None

    state.record(agent, "tool_result", {"tool": tool_name, "status": status})
    return result["data"]
