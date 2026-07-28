"""Profile specialist: retrieval, consent, completeness, and eligibility."""

from __future__ import annotations

from typing import Any

from multi_agent.state import AgentState
from multi_agent.tool_executor import call_tool


def _personality(profile: dict[str, Any]) -> str:
    interests = set(profile.get("interests") or [])
    communication = profile.get("communication_style")
    if interests & {"art", "music", "cinema", "photography"}:
        return "creative"
    if interests & {"travel", "cycling", "walking"}:
        return "adventurous"
    if communication == "direct":
        return "analytical"
    if communication == "gentle":
        return "introvert"
    return "ambivert"


def _enrich_candidate(candidate: dict[str, Any], profile: dict[str, Any]) -> None:
    display_name = profile.get("display_name") or candidate["id"]
    city = profile.get("city") or candidate.get("city") or "Chưa chia sẻ"
    bio = f"{display_name} sống tại {city}."
    if profile.get("relationship_goal"):
        bio += f" Mục tiêu mối quan hệ: {profile['relationship_goal']}."
    candidate.update(
        {
            "name": display_name,
            "age": profile.get("age") or candidate.get("age") or 18,
            "city": city,
            "personality": _personality(profile),
            "bio": bio,
            "interests": profile.get("interests") or [],
        }
    )


def _run_enrichment(state: AgentState, agent: str) -> tuple[str, list[str], str]:
    evidence: list[str] = []
    for candidate in state.candidates:
        candidate_id = candidate.get("id")
        if not candidate_id:
            continue
        profile_data = call_tool(
            state,
            agent,
            "get_match_profile",
            user_id=candidate_id,
            requester_id=state.user_id,
        )
        if profile_data is None:
            continue
        _enrich_candidate(candidate, profile_data.get("profile") or {})
        evidence.append(f"{candidate_id}: consented profile fields retrieved")
    status = "completed" if evidence or not state.candidates else "failed"
    recommendation = "continue" if status == "completed" else "safe_fallback"
    return status, evidence, recommendation


def run_profile_agent(state: AgentState) -> AgentState:
    agent = "profile"
    task = state.current_task()
    stage = task.stage if task else "validate"
    state.record(agent, "started", {"stage": stage})
    errors_before = len(state.errors)

    if stage == "enrich":
        status, evidence, recommendation = _run_enrichment(state, agent)
        result = {"enriched_candidate_count": len(evidence)}
    else:
        purpose = "date_planning" if state.intent == "date_planning" else "matching"
        profile_data = call_tool(state, agent, "get_match_profile", user_id=state.user_id)
        completeness = call_tool(
            state,
            agent,
            "check_profile_completeness",
            user_id=state.user_id,
            purpose=purpose,
        )
        requester_eligibility = call_tool(
            state,
            agent,
            "check_matching_eligibility",
            user_id=state.user_id,
        )

        target_data = None
        pair_eligibility = None
        if state.candidate_id:
            target_data = call_tool(
                state,
                agent,
                "get_match_profile",
                user_id=state.candidate_id,
                requester_id=state.user_id,
            )
            pair_eligibility = call_tool(
                state,
                agent,
                "check_matching_eligibility",
                user_id=state.user_id,
                candidate_id=state.candidate_id,
            )

        if profile_data:
            state.profile = profile_data.get("profile") or {}
        if target_data:
            state.target_profile = target_data.get("profile") or {}

        eligible = bool(
            requester_eligibility
            and requester_eligibility.get("eligible")
            and (not state.candidate_id or (pair_eligibility and pair_eligibility.get("eligible")))
        )
        profile_complete = bool(completeness and completeness.get("profile_complete"))
        recommendation = "continue"
        status = "completed"
        if len(state.errors) > errors_before or not profile_data:
            status = "failed"
            recommendation = "safe_fallback"
        elif not eligible:
            status = "blocked"
            recommendation = "safe_fallback"
        elif not profile_complete:
            status = "blocked"
            recommendation = "ask_human"

        state.profile_report = {
            "requester_id": state.user_id,
            "candidate_id": state.candidate_id,
            "eligible": eligible,
            "profile_complete": profile_complete,
            "completeness": completeness or {},
            "requester_eligibility": requester_eligibility or {},
            "pair_eligibility": pair_eligibility or {},
            "recommendation": recommendation,
        }
        evidence = [
            f"requester_profile={'available' if profile_data else 'unavailable'}",
            f"profile_complete={profile_complete}",
            f"matching_eligible={eligible}",
        ]
        if target_data:
            evidence.append("candidate_profile=consented")
        result = state.profile_report

    task_errors = state.errors[errors_before:]
    state.add_agent_result(
        agent,
        status=status,
        result=result,
        evidence=evidence,
        errors=task_errors,
        recommendation=recommendation,
    )
    state.record(
        agent,
        "completed",
        {"stage": stage, "status": status, "recommendation": recommendation},
    )
    state.complete(agent)
    return state
