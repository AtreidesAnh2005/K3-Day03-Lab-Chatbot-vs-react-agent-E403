"""Response specialist: synthesize only approved evidence into public output."""

from __future__ import annotations

from multi_agent.state import AgentState
from prompts import CHATBOT_BASELINE_PROMPT, SAFE_FALLBACK_MESSAGE
from providers import get_llm_provider
from services.privacy_guard import redact_sensitive_data


def _blocked_output(state: AgentState) -> dict:
    if state.intent == "chat":
        return {
            "reply": SAFE_FALLBACK_MESSAGE,
            "suggestedTopics": ["Gửi lời mời kết nối trong ứng dụng"],
            "safetyApproved": False,
        }
    return {
        "success": False,
        "message": SAFE_FALLBACK_MESSAGE,
        "safetyApproved": False,
    }


def _chat_output(state: AgentState) -> dict:
    reply = get_llm_provider().generate(
        state.user_query,
        system_prompt=CHATBOT_BASELINE_PROMPT,
    )
    return {
        "reply": redact_sensitive_data(reply),
        "suggestedTopics": [
            "Sở thích chung",
            "Ranh giới cá nhân",
            "Kế hoạch cuối tuần",
        ],
        "safetyApproved": True,
    }


def _profile_output(state: AgentState) -> dict:
    return {
        "success": not state.errors and state.profile_report.get("eligible", False),
        "profileId": state.user_id,
        "mode": "consented_dataset",
        "profile": state.profile,
        "completeness": state.profile_report.get("completeness", {}),
    }


def _date_output(state: AgentState) -> dict:
    return {
        "candidateName": state.plan.get("candidateName", state.candidate_id),
        "theme": state.plan.get("theme", ""),
        "items": state.plan.get("items", []),
        "icebreakerQuestions": state.plan.get("icebreakerQuestions", []),
        "appliedChanges": state.plan.get("appliedChanges", []),
        "preferredStartTime": state.plan.get("preferredStartTime"),
        "requestedEndTime": state.plan.get("requestedEndTime"),
        "requestedActivityCount": state.plan.get("requestedActivityCount"),
        "searchInterests": state.plan.get("searchInterests", []),
        "sharedInterests": state.plan.get("sharedInterests", []),
    }


def run_response_agent(state: AgentState) -> AgentState:
    agent = "response"
    state.record(agent, "started", {"safety_verdict": state.safety_verdict})

    if state.safety_verdict == "BLOCK" or state.preflight_verdict == "BLOCK":
        state.output = _blocked_output(state)
    elif state.safety_verdict != "PASS":
        state.add_error(
            agent,
            "SAFETY_REVIEW_REQUIRED",
            "Response Agent cannot run before a PASS verdict.",
        )
        state.output = _blocked_output(state)
    elif state.intent == "chat":
        state.output = _chat_output(state)
    elif state.intent == "matching":
        state.output = {"candidates": state.candidates}
    elif state.intent == "date_planning":
        state.output = _date_output(state)
    elif state.intent == "profile":
        state.output = _profile_output(state)

    reply = state.output.get("reply")
    state.final_answer = reply if isinstance(reply, str) else f"{state.intent} response ready"
    state.add_agent_result(
        agent,
        status="completed",
        result={"output_keys": sorted(state.output)},
        evidence=[
            f"safety_verdict={state.safety_verdict}",
            f"observation_count={len(state.observations)}",
        ],
        errors=[
            error for error in state.errors if error.get("task_id") == state.current_task_id
        ],
        recommendation="finish",
    )
    state.record(agent, "completed", {"output_keys": sorted(state.output)})
    state.complete(agent)
    return state
