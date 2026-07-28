"""Supervisor reflection and bounded replanning."""

from __future__ import annotations

from typing import Any

from multi_agent.state import AgentState, PlanTask

MAX_REPLANS = 2
MAX_CRITIC_REVISIONS = 2


def _latest_result(state: AgentState) -> dict[str, Any]:
    return state.agent_results[-1] if state.agent_results else {}


def reflect_on_current_task(state: AgentState) -> str:
    """Evaluate the latest structured agent result without creating evidence."""
    task = state.current_task()
    if task is None:
        return "STOP_SAFE"
    result = _latest_result(state)
    recommendation = result.get("recommendation", "continue")
    state.status = "reflecting"

    if state.preflight_verdict == "BLOCK" or state.safety_verdict == "BLOCK":
        decision = "STOP_SAFE"
        reason = "Safety Critic vetoed the request."
    elif recommendation == "ask_human":
        decision = "WAIT_HUMAN"
        reason = "A required profile field or approval is missing."
    elif recommendation == "replan":
        decision = "REPLAN"
        reason = "The specialist reported a recoverable soft-constraint failure."
    elif result.get("status") in {"failed", "blocked"}:
        decision = "STOP_SAFE"
        reason = "The specialist could not complete the task safely."
    else:
        decision = "CONTINUE"
        reason = "The task returned grounded structured evidence."

    state.record(
        "supervisor",
        "reflection",
        {
            "decision": decision,
            "reason": reason,
            "recommendation": recommendation,
        },
    )
    return decision


def _reset_task(state: AgentState, task: PlanTask) -> None:
    task.status = "pending"
    if task.task_id in state.completed_tasks:
        state.completed_tasks.remove(task.task_id)


def apply_replan(state: AgentState) -> bool:
    """Relax only recoverable soft filters and keep every hard gate unchanged."""
    task = state.current_task()
    if task is None or state.replan_count >= MAX_REPLANS:
        return False

    state.replan_count += 1
    state.status = "replanning"
    note: dict[str, Any] = {
        "replan_count": state.replan_count,
        "task_id": task.task_id,
        "hard_constraints_preserved": [
            "minimum_age",
            "consent",
            "block_list",
            "safety_policy",
            "dealbreakers",
        ],
    }

    if task.route == "date_planning":
        state.request_data["customPrompt"] = None
        state.plan = {}
        note["change"] = "Removed only the indoor/outdoor soft preference."
        _reset_task(state, task)
    elif task.route == "safety_critic" and state.critic_revision_count < MAX_CRITIC_REVISIONS:
        state.critic_revision_count += 1
        target = state.safety_report.get("replan_target")
        target_task = next(
            (item for item in state.global_plan if item.route == target),
            None,
        )
        if target_task is None:
            return False
        note["change"] = f"Re-run {target} to restore missing grounding evidence."
        _reset_task(state, target_task)
        _reset_task(state, task)
    else:
        return False

    state.replan_notes.append(note)
    state.record("supervisor", "replanned", note)
    return True


def finalize_current_task(state: AgentState, decision: str) -> None:
    task = state.current_task()
    if task is None:
        return
    if decision in {"CONTINUE", "STOP_SAFE"}:
        task.status = "completed"
        if task.task_id not in state.completed_tasks:
            state.completed_tasks.append(task.task_id)
    elif decision == "WAIT_HUMAN":
        task.status = "blocked"
        state.status = "waiting_human"
    elif decision == "REPLAN":
        task.status = "pending"
