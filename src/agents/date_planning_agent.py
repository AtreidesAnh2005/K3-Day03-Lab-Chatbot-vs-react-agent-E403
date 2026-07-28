"""Date specialist: shared interests, activity search, and cost verification."""

from __future__ import annotations

import re
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


def _requested_start_minutes(text: str | None) -> int | None:
    normalized = (text or "").casefold()
    match = re.search(
        r"(?:\bluc\b|\blúc\b|\bvao\b|\bvào\b|\bat\b|\btime\b)?\s*"
        r"\b([01]?\d|2[0-3])\s*(?:h|:|g)\s*([0-5]\d)?\b",
        normalized,
    )
    if not match:
        return None
    return int(match.group(1)) * 60 + int(match.group(2) or "0")


def _format_minutes(minutes: int) -> str:
    return f"{(minutes // 60) % 24:02d}:{minutes % 60:02d}"


def _requested_end_minutes(text: str | None) -> int | None:
    normalized = (text or "").casefold()
    match = re.search(
        r"(?:ket thuc|kết thúc|truoc|trước|xong|den|đến|until|by)"
        r"[^\d]{0,20}([01]?\d|2[0-3])\s*(?:h|:|g)\s*([0-5]\d)?\b",
        normalized,
    )
    if not match:
        return None
    return int(match.group(1)) * 60 + int(match.group(2) or "0")


def _busy_minutes(text: str | None) -> int | None:
    normalized = (text or "").casefold()
    if not any(marker in normalized for marker in {"ban", "bận", "busy", "khong ranh", "không rảnh"}):
        return None
    return _requested_start_minutes(text)


def _requested_activity_count(text: str | None, default: int = 3) -> int:
    normalized = (text or "").casefold()
    if any(marker in normalized for marker in {"chi mot", "chỉ một", "only one", "1 hoat dong", "1 hoạt động"}):
        return 1
    words = {"mot": 1, "một": 1, "hai": 2, "ba": 3}
    word_match = re.search(r"\b(mot|một|hai|ba)\s+(?:diem|điểm|hoat dong|hoạt động|lich|lịch)\b", normalized)
    if word_match:
        return words[word_match.group(1)]
    number_match = re.search(r"\b([1-5])\s*(?:diem|điểm|hoat dong|hoạt động|lich|lịch)\b", normalized)
    if number_match:
        return max(1, min(5, int(number_match.group(1))))
    return default


def _prompt_interest_tags(text: str | None) -> list[str]:
    normalized = (text or "").casefold()
    keyword_tags = [
        ({"cafe", "coffee", "ca phe", "cà phê"}, ["coffee"]),
        ({"gom", "gốm", "workshop"}, ["art", "creative"]),
        ({"trien lam", "triển lãm", "anh", "ảnh", "photo"}, ["photography", "art"]),
        ({"nhac", "nhạc", "acoustic", "music"}, ["music"]),
        ({"di bo", "đi bộ", "walking", "ho guom", "hồ gươm"}, ["walking", "outdoor"]),
        ({"nau an", "nấu ăn", "cooking"}, ["cooking", "creative"]),
        ({"bao tang", "bảo tàng", "museum", "history", "culture"}, ["history", "culture"]),
    ]
    tags: list[str] = []
    for markers, marker_tags in keyword_tags:
        if any(marker in normalized for marker in markers):
            tags.extend(marker_tags)
    deduped: list[str] = []
    for tag in tags:
        if tag not in deduped:
            deduped.append(tag)
    return deduped


def _schedule_start_minutes(text: str | None) -> int:
    requested = _requested_start_minutes(text)
    busy = _busy_minutes(text)
    if busy is not None:
        return busy + 90
    return requested if requested is not None else 17 * 60 + 30


def _schedule_notes(text: str | None, *, activity_count: int, start_minutes: int, end_minutes: int | None) -> list[str]:
    notes = [f"Start at {_format_minutes(start_minutes)}"]
    busy = _busy_minutes(text)
    if busy is not None:
        notes.append(f"Avoid busy time around {_format_minutes(busy)}")
    if end_minutes is not None:
        notes.append(f"Keep the plan before {_format_minutes(end_minutes)}")
    notes.append(f"Plan up to {activity_count} activit{'ies' if activity_count != 1 else 'y'}")
    tags = _prompt_interest_tags(text)
    if tags:
        notes.append(f"Prioritize requested activity tags: {', '.join(tags)}")
    return notes


def _date_items(
    activities: list[dict[str, Any]],
    verified_cost: dict[str, Any] | None,
    start_minutes: int | None = None,
    end_minutes: int | None = None,
    max_items: int = 3,
) -> list[dict[str, Any]]:
    next_start = start_minutes or 17 * 60 + 30
    items: list[dict[str, Any]] = []
    for index, activity in enumerate(activities[:max_items]):
        duration = int(activity.get("duration_minutes") or 90)
        if end_minutes is not None and next_start + duration > end_minutes:
            break
        time = f"{_format_minutes(next_start)} - {_format_minutes(next_start + duration)}"
        next_start = next_start + duration + 15
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
                "time": time,
                "title": activity.get("name") or "Hoạt động hẹn hò",
                "location": activity.get("city") or "",
                "durationMinutes": duration,
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
    prompt = state.request_data.get("customPrompt")
    prompt_tags = _prompt_interest_tags(prompt)
    requested_count = _requested_activity_count(prompt)
    indoor = _indoor_preference(prompt)
    shared_interests = (shared or {}).get("shared_interests") or []
    search_interests = prompt_tags or shared_interests
    activities = None
    if city and shared is not None:
        activities = call_tool(
            state,
            agent,
            "search_date_activities",
            city=city,
            interests=search_interests,
            max_budget=budget,
            indoor=indoor,
            max_results=max(5, requested_count),
        )

    rows = (activities or {}).get("activities") or []
    if not rows and prompt_tags and city and shared is not None:
        activities = call_tool(
            state,
            agent,
            "search_date_activities",
            city=city,
            interests=shared_interests,
            max_budget=budget,
            indoor=indoor,
            max_results=max(5, requested_count),
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
    preferred_start = _schedule_start_minutes(prompt)
    end_minutes = _requested_end_minutes(prompt)
    items = _date_items(rows, verified_cost, preferred_start, end_minutes, requested_count)
    if not items and rows and end_minutes is not None:
        first_duration = int(rows[0].get("duration_minutes") or 90)
        preferred_start = max(0, end_minutes - first_duration)
        items = _date_items(rows, verified_cost, preferred_start, end_minutes, requested_count)
    state.plan = {
        "candidateName": state.target_profile.get("display_name") or state.candidate_id,
        "theme": f"Kế hoạch hẹn hò an toàn tại {city or 'địa điểm đã chọn'}",
        "items": items,
        "icebreakerQuestions": [
            f"Bạn thích điều gì nhất ở chủ đề {topic}?" for topic in topics
        ],
        "budget": budget,
        "preferredStartTime": _format_minutes(preferred_start) if preferred_start is not None else None,
        "requestedEndTime": _format_minutes(end_minutes) if end_minutes is not None else None,
        "requestedActivityCount": requested_count,
        "appliedChanges": _schedule_notes(
            prompt,
            activity_count=requested_count,
            start_minutes=preferred_start,
            end_minutes=end_minutes,
        ),
        "searchInterests": search_interests,
        "sharedInterests": shared_interests,
    }

    status = "completed" if items else "failed"
    recommendation = "continue" if items else "safe_fallback"
    if not items:
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
