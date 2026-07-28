"""Shared state models for the multi-agent workflow."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    """State passed between supervisor, dispatcher, agents, and subgraphs."""

    user_query: str
    profile: dict[str, Any] = field(default_factory=dict)
    candidates: list[dict[str, Any]] = field(default_factory=list)
    plan: dict[str, Any] = field(default_factory=dict)
    trace: list[str] = field(default_factory=list)
    final_answer: str | None = None
