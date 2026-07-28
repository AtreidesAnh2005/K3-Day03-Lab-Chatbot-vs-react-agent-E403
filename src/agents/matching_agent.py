"""Consent-aware candidate matching specialist."""

from __future__ import annotations

from typing import Any

from multi_agent.state import AgentState
from multi_agent.tool_executor import call_tool

DIMENSION_LABELS = {
    "relationship_goal": "Mục tiêu mối quan hệ",
    "values": "Giá trị sống",
    "lifestyle": "Lối sống",
    "communication_style": "Phong cách giao tiếp",
    "future_plans": "Kế hoạch tương lai",
    "interests": "Sở thích",
    "availability": "Lịch rảnh",
    "logistics": "Địa điểm",
}


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


def _candidate_model(
    candidate_id: str,
    score: dict[str, Any],
    profile: dict[str, Any],
    breakdown: dict[str, Any],
) -> dict[str, Any]:
    reasons = [
        f"{DIMENSION_LABELS.get(item.get('dimension'), item.get('dimension', 'Tiêu chí'))} phù hợp"
        for item in breakdown.get("strengths", [])
    ]
    if not reasons:
        reasons.append("Điểm được tính từ dữ liệu hai bên đã đồng ý chia sẻ")
    reasons.append("Điểm tương thích là ước lượng, không bảo đảm kết quả mối quan hệ")

    dimension_scores = score.get("dimension_scores") or {}
    breakdown_rows = breakdown.get("breakdown") or {}
    dimensions = [
        {
            "key": key,
            "label": DIMENSION_LABELS.get(key, key),
            "value": value,
            "result": (breakdown_rows.get(key) or {}).get("mutual_result", "unknown"),
        }
        for key, value in dimension_scores.items()
        if isinstance(value, (int, float))
    ]

    display_name = profile.get("display_name") or candidate_id
    city = profile.get("city") or "Chưa chia sẻ"
    bio = f"{display_name} sống tại {city}."
    if profile.get("relationship_goal"):
        bio += f" Mục tiêu mối quan hệ: {profile['relationship_goal']}."

    return {
        "id": candidate_id,
        "name": display_name,
        "age": profile.get("age") or 18,
        "city": city,
        "careerField": "",
        "loveLanguage": "",
        "personality": _personality(profile),
        "photo": "",
        "bio": bio,
        "interests": profile.get("interests") or [],
        "compatibility": score["score"],
        "confidence": score.get("confidence", "low"),
        "coverageRatio": score.get("coverage_ratio", 0),
        "reasons": reasons[:3],
        "dimensions": dimensions,
        "limitations": breakdown.get("limitations") or [],
    }


def run_matching_agent(state: AgentState) -> AgentState:
    agent = "matching"
    state.record(agent, "started")
    search_args: dict[str, Any] = {"user_id": state.user_id, "max_results": 10}
    if state.city:
        search_args["city"] = state.city
    search = call_tool(state, agent, "search_candidates", **search_args)

    candidates: list[dict[str, Any]] = []
    for row in (search or {}).get("candidates", []):
        candidate_id = row.get("candidate_id")
        if not candidate_id:
            continue
        score = call_tool(
            state,
            agent,
            "calculate_compatibility",
            user_id=state.user_id,
            candidate_id=candidate_id,
        )
        if not score or not score.get("eligible") or not score.get("score_available"):
            continue
        profile_data = call_tool(
            state,
            agent,
            "get_match_profile",
            user_id=candidate_id,
            requester_id=state.user_id,
        )
        breakdown = call_tool(
            state,
            agent,
            "get_compatibility_breakdown",
            user_id=state.user_id,
            candidate_id=candidate_id,
        )
        if profile_data and breakdown:
            candidates.append(
                _candidate_model(
                    candidate_id,
                    score,
                    profile_data.get("profile") or {},
                    breakdown,
                )
            )

    state.candidates = sorted(
        candidates,
        key=lambda item: item["compatibility"],
        reverse=True,
    )
    state.output = {"candidates": state.candidates}
    state.record(agent, "completed", {"candidate_count": len(state.candidates)})
    state.complete(agent)
    return state
