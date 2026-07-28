"""Consent-aware date planning specialist."""

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


def _date_items(activities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    times = ["17:30 - 18:45", "19:00 - 20:30", "20:45 - 21:45"]
    return [
        {
            "step": index + 1,
            "time": times[index],
            "title": activity.get("name") or "Hoạt động hẹn hò",
            "location": activity.get("city") or "",
            "description": (
                f"Chi phí ước tính {int(activity.get('estimated_pair_cost') or 0):,} VND "
                f"cho hai người, thời lượng khoảng {activity.get('duration_minutes', 0)} phút. "
                "Đây là đề xuất, hệ thống chưa đặt chỗ."
            ),
            "tag": "Trong nhà" if activity.get("indoor") else "Ngoài trời",
        }
        for index, activity in enumerate(activities[:3])
    ]


def run_date_planning_agent(state: AgentState) -> AgentState:
    agent = "date_planning"
    state.record(agent, "started")
    if not state.candidate_id:
        state.add_error(agent, "CANDIDATE_REQUIRED", "candidate_id is required.")
        state.complete(agent)
        return state

    candidate_data = call_tool(
        state,
        agent,
        "get_match_profile",
        user_id=state.candidate_id,
        requester_id=state.user_id,
    )
    requester_data = call_tool(state, agent, "get_match_profile", user_id=state.user_id)
    shared = call_tool(
        state,
        agent,
        "get_shared_interests",
        user_a_id=state.user_id,
        user_b_id=state.candidate_id,
    )

    candidate_profile = (candidate_data or {}).get("profile") or {}
    requester_profile = (requester_data or {}).get("profile") or {}
    city = state.city or candidate_profile.get("city") or requester_profile.get("city")
    budget = (
        state.max_budget
        or requester_profile.get("date_preferences", {}).get("max_budget")
        or 500000
    )
    activities = None
    if city and shared is not None:
        activities = call_tool(
            state,
            agent,
            "search_date_activities",
            city=city,
            interests=shared.get("shared_interests") or [],
            max_budget=budget,
            indoor=_indoor_preference(state.request_data.get("customPrompt")),
            max_results=3,
        )

    rows = (activities or {}).get("activities") or []
    topics = ((shared or {}).get("shared_interests") or [])[:3]
    if not topics:
        topics = ["một ngày lý tưởng", "sở thích cuối tuần", "ẩm thực"]
    state.plan = {
        "candidateName": candidate_profile.get("display_name") or state.candidate_id,
        "theme": f"Kế hoạch hẹn hò an toàn tại {city or 'địa điểm đã chọn'}",
        "items": _date_items(rows),
        "icebreakerQuestions": [
            f"Bạn thích điều gì nhất ở chủ đề {topic}?" for topic in topics
        ],
    }
    if not rows and not state.errors:
        state.add_error(agent, "NO_ACTIVITIES", "No activity matches the current filters.")
    state.output = state.plan
    state.record(agent, "completed", {"activity_count": len(rows)})
    state.complete(agent)
    return state
