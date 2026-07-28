"""Planning and dependency-aware delegation for the Cupid Supervisor Agent."""

from __future__ import annotations

from multi_agent.routes import RouteName
from multi_agent.state import AgentState, PlanTask


def _task(
    task_id: str,
    agent: str,
    route: RouteName,
    description: str,
    dependencies: list[str],
    stage: str,
) -> PlanTask:
    return PlanTask(
        task_id=task_id,
        agent=agent,
        route=route,
        description=description,
        dependencies=dependencies,
        stage=stage,
    )


def create_global_plan(state: AgentState) -> None:
    """Classify the goal and create a verifiable plan with dependencies."""
    state.status = "thinking"
    state.record(
        "supervisor",
        "thinking",
        {
            "intent": state.intent,
            "has_candidate": bool(state.candidate_id),
            "reason_summary": "Select only tasks required by the requested workflow.",
        },
    )

    plans: dict[str, tuple[str, str, list[PlanTask]]] = {
        "profile": (
            "Validate the requester profile for matching.",
            "low",
            [
                _task("T0", "safety_critic", "safety_critic", "Preflight request safety.", [], "preflight"),
                _task("T1", "profile", "profile", "Read profile, completeness, and eligibility.", ["T0"], "validate"),
                _task("T2", "safety_critic", "safety_critic", "Review profile evidence and policy.", ["T1"], "review"),
                _task("T3", "response", "response", "Synthesize the approved profile response.", ["T2"], "respond"),
            ],
        ),
        "matching": (
            "Find, score, explain, and rank consented candidates.",
            "medium",
            [
                _task("T0", "safety_critic", "safety_critic", "Preflight request safety.", [], "preflight"),
                _task("T1", "profile", "profile", "Validate requester profile and eligibility.", ["T0"], "validate"),
                _task("T2", "matching", "matching", "Search, score, aggregate, and rank candidates.", ["T1"], "discover"),
                _task("T3", "profile", "profile", "Read consented fields for ranked candidates.", ["T2"], "enrich"),
                _task("T4", "safety_critic", "safety_critic", "Review grounding, consent, and score evidence.", ["T3"], "review"),
                _task("T5", "response", "response", "Synthesize approved ranked matches.", ["T4"], "respond"),
            ],
        ),
        "date_planning": (
            "Validate the pair and create a grounded date plan within budget.",
            "medium",
            [
                _task("T0", "safety_critic", "safety_critic", "Preflight request safety.", [], "preflight"),
                _task("T1", "profile", "profile", "Validate requester, target consent, and pair eligibility.", ["T0"], "validate"),
                _task("T2", "matching", "matching", "Verify pair compatibility evidence.", ["T1"], "pair"),
                _task("T3", "date_planning", "date_planning", "Find activities and verify selected cost.", ["T2"], "plan_date"),
                _task("T4", "safety_critic", "safety_critic", "Review grounding, policy, and budget.", ["T3"], "review"),
                _task("T5", "response", "response", "Synthesize the approved date plan.", ["T4"], "respond"),
            ],
        ),
        "chat": (
            "Provide safe general dating guidance.",
            "low",
            [
                _task("T0", "safety_critic", "safety_critic", "Preflight request safety.", [], "preflight"),
                *(
                    [_task("T1", "profile", "profile", "Validate selected candidate consent.", ["T0"], "validate")]
                    if state.candidate_id
                    else []
                ),
                _task(
                    "T2",
                    "safety_critic",
                    "safety_critic",
                    "Review policy before response generation.",
                    ["T1"] if state.candidate_id else ["T0"],
                    "review",
                ),
                _task("T3", "response", "response", "Generate safe general guidance.", ["T2"], "respond"),
            ],
        ),
    }
    goal, risk, tasks = plans.get(state.intent, plans["chat"])
    state.goal = goal
    state.risk_level = risk  # type: ignore[assignment]
    state.reason_summary = "Tasks are delegated only after their dependencies complete."
    state.global_plan = tasks
    state.status = "planning"
    state.record(
        "supervisor",
        "plan_created",
        {
            "goal": goal,
            "risk_level": risk,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "agent": task.agent,
                    "dependencies": task.dependencies,
                    "stage": task.stage,
                }
                for task in tasks
            ],
        },
    )


def _dependencies_satisfied(state: AgentState, task: PlanTask) -> bool:
    terminal = {
        item.task_id
        for item in state.global_plan
        if item.status in {"completed", "skipped"}
    }
    return all(dependency in terminal for dependency in task.dependencies)


def _prepare_safe_fallback(state: AgentState) -> None:
    for task in state.global_plan:
        if task.status == "pending" and task.route != "response":
            task.status = "skipped"
    response_task = next(
        (task for task in state.global_plan if task.route == "response"),
        None,
    )
    if response_task:
        response_task.dependencies = [
            task.task_id
            for task in state.global_plan
            if task.route == "safety_critic" and task.status == "completed"
        ][-1:]


def choose_next_route(state: AgentState) -> RouteName:
    """Select one ready task and record the Supervisor delegation."""
    if not state.global_plan:
        create_global_plan(state)
    if state.safety_verdict == "BLOCK" or state.preflight_verdict == "BLOCK":
        _prepare_safe_fallback(state)

    pending = [
        task
        for task in state.global_plan
        if task.status == "pending" and _dependencies_satisfied(state, task)
    ]
    if not pending:
        return "done"

    task = pending[0]
    task.status = "running"
    task.attempts += 1
    state.current_task_id = task.task_id
    state.delegation_count += 1
    state.status = "delegating"
    state.record(
        "supervisor",
        "delegated",
        {
            "route": task.route,
            "agent": task.agent,
            "description": task.description,
            "attempt": task.attempts,
        },
    )
    return task.route  # type: ignore[return-value]
