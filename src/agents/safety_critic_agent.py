"""Independent privacy, grounding, safety, and policy critic."""

from __future__ import annotations

import json
from typing import Any

from multi_agent.state import AgentState
from services.privacy_guard import EMAIL_PATTERN, PHONE_PATTERN, assess_request


def _tool_names(state: AgentState) -> set[str]:
    return {
        observation.get("tool", "")
        for observation in state.observations
        if observation.get("result", {}).get("status")
        in {"success", "warning", "insufficient_data"}
    }


def _review_evidence(state: AgentState) -> dict[str, Any]:
    violations: list[dict[str, str]] = []
    tools = _tool_names(state)
    replan_target: str | None = None

    if state.intent in {"profile", "matching", "date_planning"}:
        if not state.profile_report.get("eligible"):
            violations.append(
                {
                    "type": "eligibility",
                    "message": "Requester or selected pair did not pass eligibility gates.",
                }
            )

    if state.intent in {"matching", "date_planning"}:
        if not state.compatibility_results or "calculate_compatibility" not in tools:
            violations.append(
                {
                    "type": "missing_grounding",
                    "message": "Compatibility output lacks deterministic score evidence.",
                }
            )
            replan_target = "matching"

    if state.intent == "date_planning":
        required = {"get_shared_interests", "search_date_activities", "estimate_date_cost"}
        missing = sorted(required - tools)
        if missing or not state.plan.get("items"):
            violations.append(
                {
                    "type": "missing_grounding",
                    "message": f"Date plan lacks required tool evidence: {missing}.",
                }
            )
            replan_target = "date_planning"
        budget = state.plan.get("budget")
        search_observations = [
            item
            for item in state.observations
            if item.get("tool") == "search_date_activities"
        ]
        if budget and search_observations:
            activities = (
                search_observations[-1].get("result", {}).get("data", {}).get("activities", [])
            )
            if any(activity.get("estimated_cost", 0) > budget for activity in activities):
                violations.append(
                    {
                        "type": "budget",
                        "message": "At least one suggested activity exceeds the grounded budget.",
                    }
                )

    public_payload = json.dumps(
        {"candidates": state.candidates, "date_plan": state.plan},
        ensure_ascii=False,
    )
    if PHONE_PATTERN.search(public_payload) or EMAIL_PATTERN.search(public_payload):
        violations.append(
            {"type": "pii", "message": "Public specialist output contains contact information."}
        )
    lowered = public_payload.casefold()
    if any(term in lowered for term in {"chắc chắn phù hợp", "guaranteed match", "perfect match"}):
        violations.append(
            {
                "type": "overclaim",
                "message": "Compatibility was described as a guarantee.",
            }
        )

    block_types = {"pii", "eligibility"}
    if any(item["type"] in block_types for item in violations):
        verdict = "BLOCK"
    elif violations:
        verdict = "REVISE"
    else:
        verdict = "PASS"
    return {
        "verdict": verdict,
        "violations": violations,
        "safe_instructions": [
            "Use only consented tool observations.",
            "Describe compatibility as an estimate, never a guarantee.",
            "Keep date activities within the declared budget.",
        ],
        "replan_target": replan_target,
        "checked_tools": sorted(tools),
    }


def run_safety_critic_agent(state: AgentState) -> AgentState:
    agent = "safety_critic"
    task = state.current_task()
    stage = task.stage if task else "review"
    state.record(agent, "started", {"stage": stage})

    if stage == "preflight":
        report = assess_request(state.user_query)
        state.preflight_verdict = report["verdict"]
        if report["verdict"] == "BLOCK":
            state.safety_verdict = "BLOCK"
        report = {
            "stage": "preflight",
            "verdict": report["verdict"],
            "violations": [
                {"type": reason, "message": "Request blocked before data access."}
                for reason in report["reasons"]
            ],
            "safe_instructions": ["Do not call profile or matching data tools after a block."],
            "replan_target": None,
        }
    else:
        report = {"stage": "review", **_review_evidence(state)}
        state.safety_verdict = report["verdict"]

    state.safety_report = report
    verdict = report["verdict"]
    recommendation = (
        "continue" if verdict == "PASS"
        else "replan" if verdict == "REVISE"
        else "safe_fallback"
    )
    state.add_agent_result(
        agent,
        status="completed" if verdict in {"PASS", "REVISE"} else "blocked",
        result=report,
        evidence=[
            f"stage={stage}",
            f"verdict={verdict}",
            f"violations={len(report.get('violations', []))}",
        ],
        recommendation=recommendation,
    )
    state.record(
        agent,
        "verdict",
        {
            "stage": stage,
            "verdict": verdict,
            "violations": report.get("violations", []),
        },
    )
    state.complete(agent)
    return state
