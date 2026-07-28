"""Consent-aware tool execution and parallel fan-out for specialist agents."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from multi_agent.state import AgentState
from tools import AVAILABLE_TOOLS

SUCCESS_STATUSES = {"success", "warning", "insufficient_data"}


def _record_result(
    state: AgentState,
    agent: str,
    tool_name: str,
    arguments: dict[str, Any],
    result: Any,
) -> dict[str, Any] | None:
    observation = {
        "agent": agent,
        "task_id": state.current_task_id,
        "tool": tool_name,
        "arguments": arguments,
        "result": result,
    }
    state.observations.append(observation)
    state.executed_actions.append(
        {
            "task_id": state.current_task_id,
            "agent": agent,
            "tool": tool_name,
            "arguments": arguments,
            "status": result.get("status") if isinstance(result, dict) else "invalid",
        }
    )

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


def call_tool(
    state: AgentState,
    agent: str,
    tool_name: str,
    **arguments: Any,
) -> dict[str, Any] | None:
    """Execute one whitelisted Role 2 tool and preserve its full observation."""
    tool = AVAILABLE_TOOLS.get(tool_name)
    if tool is None:
        state.add_error(agent, "UNKNOWN_TOOL", f"Tool {tool_name!r} is not registered.")
        state.record(agent, "tool_rejected", {"tool": tool_name, "arguments": arguments})
        return None

    state.tool_calls_count += 1
    state.record(agent, "tool_call", {"tool": tool_name, "arguments": arguments})
    try:
        result = tool(**arguments)
    except Exception as exc:
        state.add_error(agent, "TOOL_EXCEPTION", str(exc), {"tool": tool_name})
        state.record(agent, "tool_exception", {"tool": tool_name, "message": str(exc)})
        return None
    return _record_result(state, agent, tool_name, arguments, result)


def call_tools_parallel(
    state: AgentState,
    agent: str,
    calls: list[tuple[str, dict[str, Any]]],
    *,
    max_workers: int = 5,
) -> list[dict[str, Any] | None]:
    """Fan out independent deterministic tool calls, then reduce in input order."""
    valid_calls: list[tuple[str, dict[str, Any], Any]] = []
    for tool_name, arguments in calls:
        tool = AVAILABLE_TOOLS.get(tool_name)
        if tool is None:
            state.add_error(agent, "UNKNOWN_TOOL", f"Tool {tool_name!r} is not registered.")
            continue
        valid_calls.append((tool_name, arguments, tool))
        state.tool_calls_count += 1
        state.record(agent, "tool_call", {"tool": tool_name, "arguments": arguments})

    state.record(
        agent,
        "parallel_fan_out",
        {"call_count": len(valid_calls), "max_workers": min(max_workers, len(valid_calls) or 1)},
    )

    def invoke(item: tuple[str, dict[str, Any], Any]) -> Any:
        _, arguments, tool = item
        try:
            return tool(**arguments)
        except Exception as exc:
            return exc

    with ThreadPoolExecutor(max_workers=min(max_workers, len(valid_calls) or 1)) as pool:
        raw_results = list(pool.map(invoke, valid_calls))

    reduced: list[dict[str, Any] | None] = []
    for (tool_name, arguments, _), result in zip(valid_calls, raw_results):
        if isinstance(result, Exception):
            state.add_error(agent, "TOOL_EXCEPTION", str(result), {"tool": tool_name})
            state.record(agent, "tool_exception", {"tool": tool_name, "message": str(result)})
            reduced.append(None)
        else:
            reduced.append(_record_result(state, agent, tool_name, arguments, result))
    state.record(agent, "parallel_reduce", {"result_count": len(reduced)})
    return reduced
