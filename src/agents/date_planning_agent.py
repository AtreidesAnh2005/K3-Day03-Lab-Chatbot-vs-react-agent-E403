"""Date specialist: shared interests, activity search, and cost verification."""

from __future__ import annotations

from typing import Any

from multi_agent.state import AgentState
from multi_agent.tool_executor import call_tool


def _indoor_preference(text: str | None) -> bool | None:
    normalized = (text or "").casefold()
    if any(marker in normalized for marker in {"ngoài trời", "ngoai troi", "outdoor"}):
        return False
    if any(marker in normalized for marker in {"trong nhà", "trong nha", "indoor"}):
        return True
    return None


def _date_items(
    activities: list[dict[str, Any]],
    verified_cost: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    times = ["17:30 - 18:45", "19:00 - 20:30", "20:45 - 21:45"]
    items: list[dict[str, Any]] = []
    for index, activity in enumerate(activities[:3]):
        cost = activity.get("estimated_cost") or 0
        if (
            index == 0
            and verified_cost
            and verified_cost.get("activity_id") == activity.get("activity_id")
        ):
            cost = verified_cost.get("total_estimated_cost", cost)
        items.append(
            {
                "step": index + 1,
                "time": times[index],
                "title": activity.get("name") or "Hoạt động hẹn hò",
                "location": activity.get("city") or "",
                "description": (
                    f"Chi phí ước tính {int(cost):,} VND cho hai người. "
                    "Đây là đề xuất, hệ thống chưa đặt chỗ."
                ),
                "tag": "Trong nhà" if activity.get("indoor") else "Ngoài trời",
            }
        )
    return items


def run_date_planning_agent(state: AgentState) -> AgentState:
    agent = "date_planning"
    state.record(agent, "started", {"stage": "plan_date"})
    errors_before = len(state.errors)

    if not state.candidate_id:
        state.add_error(agent, "CANDIDATE_REQUIRED", "candidate_id is required.")
        state.add_agent_result(
            agent,
            status="failed",
            errors=state.errors[errors_before:],
            recommendation="ask_human",
        )
        state.complete(agent)
        return state

    shared = call_tool(
        state,
        agent,
        "get_shared_interests",
        user_a_id=state.user_id,
        user_b_id=state.candidate_id,
    )
    city = state.city or state.target_profile.get("city") or state.profile.get("city")
    budget = (
        state.max_budget
        or state.profile.get("date_preferences", {}).get("max_budget")
        or 500000
    )
    indoor = _indoor_preference(state.request_data.get("customPrompt"))
    activities = None
    if city and shared is not None:
        activities = call_tool(
            state,
            agent,
            "search_date_activities",
            city=city,
            interests=shared.get("shared_interests") or [],
            max_budget=budget,
            indoor=indoor,
            max_results=3,
        )

    rows = (activities or {}).get("activities") or []
    if not rows and indoor is not None:
        state.plan = {}
        state.add_agent_result(
            agent,
            status="failed",
            result={"activity_count": 0, "recoverable_filter": "indoor"},
            evidence=["No activity matched the requested indoor/outdoor soft preference."],
            errors=state.errors[errors_before:],
            recommendation="replan",
        )
        state.record(agent, "completed", {"status": "replan", "activity_count": 0})
        state.complete(agent)
        return state

    verified_cost = None
    if rows:
        verified_cost = call_tool(
            state,
            agent,
            "estimate_date_cost",
            activity_id=rows[0]["activity_id"],
            people=2,
        )

    topics = ((shared or {}).get("shared_interests") or [])[:3]
    if not topics:
        topics = ["một ngày lý tưởng", "sở thích cuối tuần", "ẩm thực"]
    state.plan = {
        "candidateName": state.target_profile.get("display_name") or state.candidate_id,
        "theme": f"Kế hoạch hẹn hò an toàn tại {city or 'địa điểm đã chọn'}",
        "items": _date_items(rows, verified_cost),
        "icebreakerQuestions": [
            f"Bạn thích điều gì nhất ở chủ đề {topic}?" for topic in topics
        ],
        "budget": budget,
        "sharedInterests": (shared or {}).get("shared_interests") or [],
    }

    status = "completed" if rows else "failed"
    recommendation = "continue" if rows else "safe_fallback"
    if not rows:
        state.add_error(agent, "NO_ACTIVITIES", "No activity matches the grounded filters.")
    evidence = [
        f"shared_interests={(shared or {}).get('shared_interests') or []}",
        f"city={city}",
        f"max_budget={budget}",
        f"activity_count={len(rows)}",
        f"verified_activity_id={rows[0]['activity_id'] if rows else None}",
    ]
    state.add_agent_result(
        agent,
        status=status,
        result=state.plan,
        evidence=evidence,
        errors=state.errors[errors_before:],
        recommendation=recommendation,
    )
    state.record(agent, "completed", {"status": status, "activity_count": len(rows)})
    state.complete(agent)
    return state
