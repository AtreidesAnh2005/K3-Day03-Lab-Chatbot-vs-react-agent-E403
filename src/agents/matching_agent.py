"""Matching specialist: candidate search, parallel scoring, aggregation, and rank."""

from __future__ import annotations

from typing import Any

from multi_agent.state import AgentState
from multi_agent.tool_executor import call_tool, call_tools_parallel

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


def _dimensions(score: dict[str, Any], breakdown: dict[str, Any]) -> list[dict[str, Any]]:
    scores = score.get("dimension_scores") or score.get("breakdown") or {}
    rows = breakdown.get("breakdown") or {}
    return [
        {
            "key": key,
            "label": DIMENSION_LABELS.get(key, key),
            "value": value,
            "result": (
                (rows.get(key) or {}).get("mutual_result", "unknown")
                if isinstance(rows.get(key), dict)
                else "aligned" if value >= 80
                else "trade_off" if value > 0
                else "unknown"
            ),
        }
        for key, value in scores.items()
        if isinstance(value, (int, float))
    ]


def _reasons(breakdown: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for item in breakdown.get("strengths", []):
        if isinstance(item, str):
            reasons.append(item)
        elif isinstance(item, dict):
            dimension = item.get("dimension", "Tiêu chí")
            reasons.append(f"{DIMENSION_LABELS.get(dimension, dimension)} phù hợp")
    if not reasons:
        reasons.append("Điểm được tính từ dữ liệu hai bên đã đồng ý chia sẻ")
    reasons.append("Điểm tương thích là ước lượng, không bảo đảm kết quả mối quan hệ")
    return reasons[:3]


def _candidate_model(
    candidate_id: str,
    row: dict[str, Any],
    score: dict[str, Any],
    breakdown: dict[str, Any],
) -> dict[str, Any]:
    display_name = row.get("display_name") or candidate_id
    city = row.get("city") or "Chưa chia sẻ"
    return {
        "id": candidate_id,
        "name": display_name,
        "age": row.get("age") or 18,
        "city": city,
        "careerField": "",
        "loveLanguage": "",
        "personality": "ambivert",
        "photo": "",
        "bio": f"{display_name} sống tại {city}.",
        "interests": [],
        "compatibility": score["score"],
        "confidence": score.get("confidence", "low"),
        "coverageRatio": score.get("coverage_ratio"),
        "reasons": _reasons(breakdown),
        "dimensions": _dimensions(score, breakdown),
        "limitations": breakdown.get("limitations") or score.get("limitations") or [],
    }


def _pair_analysis(state: AgentState, agent: str) -> tuple[list[dict[str, Any]], int]:
    if not state.candidate_id:
        return [], 0
    score = call_tool(
        state,
        agent,
        "calculate_compatibility",
        user_id=state.user_id,
        candidate_id=state.candidate_id,
    )
    breakdown = call_tool(
        state,
        agent,
        "get_compatibility_breakdown",
        user_id=state.user_id,
        candidate_id=state.candidate_id,
    )
    if not score or not breakdown or not score.get("eligible") or not score.get("score_available"):
        return [], 1
    row = {
        "candidate_id": state.candidate_id,
        "display_name": state.target_profile.get("display_name"),
        "age": state.target_profile.get("age"),
        "city": state.target_profile.get("city"),
    }
    return [_candidate_model(state.candidate_id, row, score, breakdown)], 1


def _discovery(state: AgentState, agent: str) -> tuple[list[dict[str, Any]], int]:
    search_args: dict[str, Any] = {"user_id": state.user_id, "max_results": 5}
    if state.city:
        search_args["city"] = state.city
    search = call_tool(state, agent, "search_candidates", **search_args)
    rows = (search or {}).get("candidates", [])
    score_calls = [
        (
            "calculate_compatibility",
            {"user_id": state.user_id, "candidate_id": row["candidate_id"]},
        )
        for row in rows
    ]
    scores = call_tools_parallel(state, agent, score_calls)
    eligible = [
        (row, score)
        for row, score in zip(rows, scores)
        if score and score.get("eligible") and score.get("score_available")
    ]
    breakdown_calls = [
        (
            "get_compatibility_breakdown",
            {"user_id": state.user_id, "candidate_id": row["candidate_id"]},
        )
        for row, _ in eligible
    ]
    breakdowns = call_tools_parallel(state, agent, breakdown_calls)
    candidates = [
        _candidate_model(row["candidate_id"], row, score, breakdown)
        for (row, score), breakdown in zip(eligible, breakdowns)
        if breakdown
    ]
    return candidates, len(rows)


def run_matching_agent(state: AgentState) -> AgentState:
    agent = "matching"
    task = state.current_task()
    stage = task.stage if task else "discover"
    state.record(agent, "started", {"stage": stage})
    errors_before = len(state.errors)

    if stage == "pair":
        candidates, retrieved_count = _pair_analysis(state, agent)
    else:
        candidates, retrieved_count = _discovery(state, agent)

    state.candidates = sorted(
        candidates,
        key=lambda item: item["compatibility"],
        reverse=True,
    )
    state.compatibility_results = [
        {
            "candidate_id": candidate["id"],
            "score": candidate["compatibility"],
            "confidence": candidate["confidence"],
            "dimensions": candidate["dimensions"],
            "limitations": candidate["limitations"],
        }
        for candidate in state.candidates
    ]

    status = "completed" if state.candidates else "failed"
    recommendation = "continue" if state.candidates else "safe_fallback"
    evidence = [
        f"{retrieved_count} candidates retrieved",
        f"{len(state.candidates)} compatibility calculations aggregated",
        "ranked descending by deterministic compatibility score",
    ]
    state.add_agent_result(
        agent,
        status=status,
        result={
            "ranked_matches": state.compatibility_results,
            "candidate_count": len(state.candidates),
        },
        evidence=evidence,
        errors=state.errors[errors_before:],
        recommendation=recommendation,
    )
    state.record(
        agent,
        "completed",
        {
            "stage": stage,
            "status": status,
            "candidate_count": len(state.candidates),
        },
    )
    state.complete(agent)
    return state
