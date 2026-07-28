"""Shared state and task contracts for CupidMAS."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal
from uuid import uuid4

TaskStatus = Literal["pending", "running", "completed", "blocked", "failed", "skipped"]
WorkflowStatus = Literal[
    "thinking",
    "planning",
    "delegating",
    "operating",
    "observing",
    "reflecting",
    "replanning",
    "waiting_human",
    "ready_to_answer",
    "completed",
    "failed",
]


@dataclass
class PlanTask:
    task_id: str
    agent: str
    route: str
    description: str
    dependencies: list[str] = field(default_factory=list)
    stage: str = "operate"
    status: TaskStatus = "pending"
    attempts: int = 0


@dataclass
class AgentState:
    user_query: str
    intent: str = "chat"
    user_id: str = "USR001"
    candidate_id: str | None = None
    city: str | None = None
    max_budget: int | None = None
    request_data: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: uuid4().hex)

    goal: str = ""
    reason_summary: str = ""
    risk_level: Literal["low", "medium", "high"] = "low"
    status: WorkflowStatus = "thinking"
    global_plan: list[PlanTask] = field(default_factory=list)
    completed_tasks: list[str] = field(default_factory=list)
    current_task_id: str | None = None

    profile: dict[str, Any] = field(default_factory=dict)
    target_profile: dict[str, Any] = field(default_factory=dict)
    profile_report: dict[str, Any] = field(default_factory=dict)
    candidates: list[dict[str, Any]] = field(default_factory=list)
    compatibility_results: list[dict[str, Any]] = field(default_factory=list)
    plan: dict[str, Any] = field(default_factory=dict)
    safety_report: dict[str, Any] = field(default_factory=dict)

    observations: list[dict[str, Any]] = field(default_factory=list)
    executed_actions: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    agent_results: list[dict[str, Any]] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    completed_agents: list[str] = field(default_factory=list)
    agent_run_counts: dict[str, int] = field(default_factory=dict)
    replan_notes: list[dict[str, Any]] = field(default_factory=list)

    delegation_count: int = 0
    replan_count: int = 0
    tool_calls_count: int = 0
    critic_revision_count: int = 0
    safety_verdict: str = "PENDING"
    preflight_verdict: str = "PENDING"

    output: dict[str, Any] = field(default_factory=dict)
    final_answer: str | None = None

    def record(
        self,
        agent: str,
        event: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.trace.append(
            {
                "step": len(self.trace) + 1,
                "agent": agent,
                "event": event,
                "task_id": self.current_task_id,
                "details": details or {},
            }
        )

    def complete(self, agent: str) -> None:
        if agent not in self.completed_agents:
            self.completed_agents.append(agent)
        self.agent_run_counts[agent] = self.agent_run_counts.get(agent, 0) + 1

    def add_error(
        self,
        source: str,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.errors.append(
            {
                "source": source,
                "code": code,
                "message": message,
                "task_id": self.current_task_id,
                "details": details or {},
            }
        )

    def add_agent_result(
        self,
        agent: str,
        *,
        status: str,
        result: dict[str, Any] | None = None,
        evidence: list[str] | None = None,
        errors: list[dict[str, Any]] | None = None,
        recommendation: str = "continue",
    ) -> dict[str, Any]:
        envelope = {
            "task_id": self.current_task_id,
            "agent": agent,
            "status": status,
            "result": result or {},
            "evidence": evidence or [],
            "errors": errors or [],
            "recommendation": recommendation,
        }
        self.agent_results.append(envelope)
        return envelope

    def current_task(self) -> PlanTask | None:
        return next(
            (task for task in self.global_plan if task.task_id == self.current_task_id),
            None,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
