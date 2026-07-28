"""Privacy-safe observability configuration and trace serialization."""

from __future__ import annotations

import os
from typing import Any

TRACE_DETAIL_KEYS = {
    "agent",
    "attempt",
    "candidate_count",
    "decision",
    "delegation_count",
    "intent",
    "item_count",
    "output_keys",
    "recommendation",
    "replan_count",
    "risk_level",
    "route",
    "scored_count",
    "stage",
    "status",
    "tool_calls_count",
    "verdict",
}


def get_langfuse_config() -> dict[str, Any]:
    """Return optional Langfuse settings without exposing credentials."""
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    return {
        "enabled": bool(public_key and secret_key),
        "host": os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        "trace_name": "cupid-multi-agent-run",
        "agent_version": "v2-multi-agent",
    }


def _safe_details(details: Any) -> dict[str, Any]:
    if not isinstance(details, dict):
        return {}
    return {
        key: value
        for key, value in details.items()
        if key in TRACE_DETAIL_KEYS
        and (
            value is None
            or isinstance(value, (bool, int, float, str))
            or (
                key == "output_keys"
                and isinstance(value, list)
                and all(isinstance(item, str) for item in value)
            )
        )
    }


def build_trace_summary(state: dict[str, Any]) -> dict[str, Any]:
    """Keep operational evidence while excluding user text and profile data."""
    observations = [
        {
            "agent": item.get("agent"),
            "task_id": item.get("task_id"),
            "tool": item.get("tool"),
            "status": (item.get("result") or {}).get("status"),
        }
        for item in state.get("observations", [])
    ]
    trace = [
        {
            "step": item.get("step"),
            "agent": item.get("agent"),
            "event": item.get("event"),
            "task_id": item.get("task_id"),
            "details": _safe_details(item.get("details")),
        }
        for item in state.get("trace", [])
    ]
    errors = [
        {
            "source": item.get("source"),
            "code": item.get("code"),
            "task_id": item.get("task_id"),
        }
        for item in state.get("errors", [])
    ]
    return {
        "request_id": state.get("request_id"),
        "trace_name": "cupid-multi-agent-run",
        "agent_version": "v2-multi-agent",
        "intent": state.get("intent"),
        "goal": state.get("goal"),
        "risk_level": state.get("risk_level"),
        "status": state.get("status"),
        "global_plan": state.get("global_plan", []),
        "completed_tasks": state.get("completed_tasks", []),
        "completed_agents": state.get("completed_agents", []),
        "agent_run_counts": state.get("agent_run_counts", {}),
        "delegation_count": state.get("delegation_count", 0),
        "replan_count": state.get("replan_count", 0),
        "tool_calls_count": state.get("tool_calls_count", 0),
        "safety_verdict": state.get("safety_verdict"),
        "preflight_verdict": state.get("preflight_verdict"),
        "replan_notes": state.get("replan_notes", []),
        "errors": errors,
        "observations": observations,
        "trace": trace,
    }
