"""Date specialist: shared interests, activity search, and cost verification."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from multi_agent.state import AgentState
from multi_agent.tool_executor import call_tool
from providers import get_llm_provider


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


def _provider_allows_live_call() -> bool:
    return (os.getenv("LLM_PROVIDER") or "mock").strip().casefold() != "mock"


def _json_from_llm_response(response: str) -> dict[str, Any] | None:
    cleaned = response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.casefold().startswith("json"):
            cleaned = cleaned[4:].strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        data = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _minutes_from_hhmm(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"\s*([01]\d|2[0-3]):([0-5]\d)\s*", value)
    if not match:
        return None
    return int(match.group(1)) * 60 + int(match.group(2))


def _llm_schedule_prompt(
    state: AgentState,
    *,
    city: str | None,
    budget: int,
    prompt: str | None,
    rows: list[dict[str, Any]],
    fallback_items: list[dict[str, Any]],
    start_minutes: int,
    end_minutes: int | None,
    requested_count: int,
    search_interests: list[str],
) -> str:
    activities = [
        {
            "activity_id": row.get("activity_id"),
            "name": row.get("name"),
            "city": row.get("city"),
            "interests": row.get("interests", []),
            "estimated_cost": row.get("estimated_cost"),
            "duration_minutes": row.get("duration_minutes"),
            "indoor": row.get("indoor"),
        }
        for row in rows
    ]
    payload = {
        "user_request": state.user_query,
        "custom_prompt": prompt,
        "city": city,
        "max_budget_vnd": budget,
        "requested_start_time": _format_minutes(start_minutes),
        "requested_end_time": _format_minutes(end_minutes) if end_minutes is not None else None,
        "requested_activity_count": requested_count,
        "search_interests": search_interests,
        "candidate_activities": activities,
        "fallback_schedule": fallback_items,
    }
    return (
        "You are the Date Planning Agent scheduler for a consent-aware dating app.\n"
        "Create a flexible schedule that follows the user's requested timing and activity preferences.\n"
        "Hard rules:\n"
        "- Use only activity_id values from candidate_activities.\n"
        "- Do not invent venues, prices, private data, bookings, contacts, or payments.\n"
        "- Keep every selected activity within max_budget_vnd evidence already provided.\n"
        "- If requested_end_time is present, choose activities that fit before it when possible.\n"
        "- Return JSON only, no markdown.\n"
        "Schema:\n"
        "{\n"
        '  "items": [{"activity_id": "A02", "start_time": "18:00"}],\n'
        '  "appliedChanges": ["short note"],\n'
        '  "rationale": "one short sentence"\n'
        "}\n\n"
        f"Context JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )


def _refine_items_with_llm(
    state: AgentState,
    *,
    city: str | None,
    budget: int,
    prompt: str | None,
    rows: list[dict[str, Any]],
    fallback_items: list[dict[str, Any]],
    verified_cost: dict[str, Any] | None,
    start_minutes: int,
    end_minutes: int | None,
    requested_count: int,
    search_interests: list[str],
) -> tuple[list[dict[str, Any]], list[str], str]:
    if not _provider_allows_live_call() or not rows or not fallback_items:
        return fallback_items, [], "deterministic"

    provider = get_llm_provider()
    provider_name = provider.__class__.__name__
    schedule_prompt = _llm_schedule_prompt(
        state,
        city=city,
        budget=budget,
        prompt=prompt,
        rows=rows,
        fallback_items=fallback_items,
        start_minutes=start_minutes,
        end_minutes=end_minutes,
        requested_count=requested_count,
        search_interests=search_interests,
    )
    system_prompt = (
        "Return valid JSON only. Use only supplied activity_id values. "
        "Never claim a booking, reservation, payment, contact, or guaranteed outcome."
    )
    response = provider.generate(schedule_prompt, system_prompt=system_prompt)
    if response.startswith("[") and ("Error" in response or "Exception" in response):
        state.record("date_planning", "llm_schedule_failed", {"provider": provider_name, "message": response[:160]})
        return fallback_items, [f"LLM scheduler unavailable; used deterministic fallback ({provider_name})"], "fallback"

    parsed = _json_from_llm_response(response)
    if not parsed:
        state.record("date_planning", "llm_schedule_invalid_json", {"provider": provider_name})
        return fallback_items, [f"LLM scheduler returned invalid JSON; used deterministic fallback ({provider_name})"], "fallback"

    rows_by_id = {str(row.get("activity_id")): row for row in rows}
    selected_rows: list[dict[str, Any]] = []
    selected_starts: list[int] = []
    for raw_item in parsed.get("items", []):
        if not isinstance(raw_item, dict):
            continue
        activity_id = str(raw_item.get("activity_id") or "")
        start = _minutes_from_hhmm(raw_item.get("start_time"))
        row = rows_by_id.get(activity_id)
        if row is None or start is None:
            continue
        selected_rows.append(row)
        selected_starts.append(start)
        if len(selected_rows) >= requested_count:
            break

    if not selected_rows:
        state.record("date_planning", "llm_schedule_no_valid_items", {"provider": provider_name})
        return fallback_items, [f"LLM scheduler selected no valid activities; used deterministic fallback ({provider_name})"], "fallback"

    refined: list[dict[str, Any]] = []
    for row, item_start in zip(selected_rows, selected_starts):
        refined.extend(
            _date_items(
                [row],
                verified_cost if not refined else None,
                item_start,
                end_minutes,
                1,
            )
        )
    if not refined:
        return fallback_items, [f"LLM scheduler did not fit the time window; used deterministic fallback ({provider_name})"], "fallback"

    notes = [
        str(item)
        for item in parsed.get("appliedChanges", [])
        if isinstance(item, str) and item.strip()
    ]
    notes.append(f"Refined by {provider_name} from .env")
    state.record(
        "date_planning",
        "llm_schedule_refined",
        {"provider": provider_name, "item_count": len(refined)},
    )
    return refined, notes, "llm"


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
    fallback_items = _date_items(rows, verified_cost, preferred_start, end_minutes, requested_count)
    if not fallback_items and rows and end_minutes is not None:
        first_duration = int(rows[0].get("duration_minutes") or 90)
        preferred_start = max(0, end_minutes - first_duration)
        fallback_items = _date_items(rows, verified_cost, preferred_start, end_minutes, requested_count)
    items, llm_notes, schedule_source = _refine_items_with_llm(
        state,
        city=city,
        budget=budget,
        prompt=prompt,
        rows=rows,
        fallback_items=fallback_items,
        verified_cost=verified_cost,
        start_minutes=preferred_start,
        end_minutes=end_minutes,
        requested_count=requested_count,
        search_interests=search_interests,
    )
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
        "appliedChanges": [
            *_schedule_notes(
                prompt,
                activity_count=requested_count,
                start_minutes=preferred_start,
                end_minutes=end_minutes,
            ),
            *llm_notes,
        ],
        "scheduleSource": schedule_source,
        "llmProvider": get_llm_provider().__class__.__name__ if schedule_source == "llm" else None,
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
