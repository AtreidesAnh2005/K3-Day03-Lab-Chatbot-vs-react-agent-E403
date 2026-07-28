"""Runtime for the reflective CupidMAS supervisor loop."""

from __future__ import annotations

from typing import Any

from multi_agent.dispatcher import dispatch
from multi_agent.reflection import (
    apply_replan,
    finalize_current_task,
    reflect_on_current_task,
)
from multi_agent.state import AgentState
from multi_agent.supervisor import choose_next_route, create_global_plan


def run_multi_agent_workflow(
    user_query: str,
    *,
    intent: str = "chat",
    user_id: str = "USR001",
    candidate_id: str | None = None,
    city: str | None = None,
    max_budget: int | None = None,
    request_data: dict[str, Any] | None = None,
    max_steps: int = 16,
) -> AgentState:
    state = AgentState(
        user_query=user_query,
        intent=intent,
        user_id=user_id,
        candidate_id=candidate_id,
        city=city,
        max_budget=max_budget,
        request_data=request_data or {},
    )
    state.record("workflow", "started", {"intent": intent, "request_id": state.request_id})
    create_global_plan(state)

    for _ in range(max_steps):
        route = choose_next_route(state)
        if route == "done":
            break

        state.status = "operating"
        state = dispatch(route, state)
        state.status = "observing"
        decision = reflect_on_current_task(state)

        if decision == "REPLAN":
            if apply_replan(state):
                continue
            state.add_error(
                "supervisor",
                "REPLAN_EXHAUSTED",
                "The workflow could not recover within the replan budget.",
            )
            state.safety_verdict = "BLOCK"
            decision = "STOP_SAFE"

        finalize_current_task(state, decision)
        if decision == "WAIT_HUMAN":
            break
    else:
        state.add_error("supervisor", "MAX_STEPS", f"Workflow exceeded {max_steps} steps.")
        state.status = "failed"

    response_done = any(
        task.route == "response" and task.status == "completed"
        for task in state.global_plan
    )
    if response_done:
        state.status = "completed"
    elif state.status != "waiting_human":
        state.status = "failed"

    state.current_task_id = None
    state.complete("supervisor")
    state.record(
        "supervisor",
        "finished",
        {
            "status": state.status,
            "delegation_count": state.delegation_count,
            "replan_count": state.replan_count,
            "tool_calls_count": state.tool_calls_count,
        },
    )
    state.record("workflow", "completed", {"safety_verdict": state.safety_verdict})
    return state
