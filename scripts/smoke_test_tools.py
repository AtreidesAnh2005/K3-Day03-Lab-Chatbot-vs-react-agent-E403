from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.tools import (  # noqa: E402
    AVAILABLE_TOOLS,
    DATE_TOOLS,
    MATCHING_TOOLS,
    PROFILE_TOOLS,
    calculate_compatibility,
    check_matching_eligibility,
    check_profile_completeness,
    estimate_date_cost,
    get_compatibility_breakdown,
    get_match_profile,
    get_shared_interests,
    search_candidates,
    search_date_activities,
)

EXPECTED_PROFILE_TOOLS = {
    "get_match_profile",
    "check_profile_completeness",
    "check_matching_eligibility",
}
EXPECTED_MATCHING_TOOLS = {
    "search_candidates",
    "calculate_compatibility",
    "get_compatibility_breakdown",
}
EXPECTED_DATE_TOOLS = {
    "get_shared_interests",
    "search_date_activities",
    "estimate_date_cost",
}


def assert_envelope(result: dict[str, Any]) -> None:
    assert set(result) == {"status", "tool", "data", "error", "metadata"}
    assert result["status"] in {"success", "warning", "insufficient_data", "denied", "error"}
    json.dumps(result, ensure_ascii=False)


def assert_error(result: dict[str, Any], code: str) -> None:
    assert_envelope(result)
    assert result["error"]["code"] == code


def assert_no_private_payload(result: dict[str, Any]) -> None:
    serialized = json.dumps(result, ensure_ascii=False)
    forbidden = [
        "candidate_secret_preference",
        "confirmed_report_count",
        "blocked_user_ids",
    ]
    for item in forbidden:
        assert item not in serialized


def test_registry() -> None:
    assert set(PROFILE_TOOLS) == EXPECTED_PROFILE_TOOLS
    assert set(MATCHING_TOOLS) == EXPECTED_MATCHING_TOOLS
    assert set(DATE_TOOLS) == EXPECTED_DATE_TOOLS
    assert set(AVAILABLE_TOOLS) == EXPECTED_PROFILE_TOOLS | EXPECTED_MATCHING_TOOLS | EXPECTED_DATE_TOOLS


def test_profile_tools() -> None:
    self_profile = get_match_profile("USR001")
    assert_envelope(self_profile)
    assert self_profile["status"] == "success"
    assert self_profile["data"]["view_type"] == "self"
    assert_no_private_payload(self_profile)

    candidate_profile = get_match_profile("USR002", requester_id="USR001")
    assert_envelope(candidate_profile)
    assert candidate_profile["data"]["view_type"] == "consented_candidate"
    assert "date_preferences" in candidate_profile["data"]["profile"]
    assert_no_private_payload(candidate_profile)

    revoked = get_match_profile("USR007", requester_id="USR001")
    assert_error(revoked, "CONSENT_REVOKED")

    complete = check_profile_completeness("USR001", "matching")
    assert_envelope(complete)
    assert complete["data"]["profile_complete"] is True
    assert complete["data"]["recommended_action"] == "continue"

    missing_date = check_profile_completeness("USR005", "date_planning")
    assert_envelope(missing_date)
    assert missing_date["data"]["recommended_action"] == "ask_human"
    assert "date_preferences.max_budget" in missing_date["data"]["missing_required_fields"]

    self_eligible = check_matching_eligibility("USR001")
    assert_envelope(self_eligible)
    assert self_eligible["data"]["eligible"] is True

    disabled = check_matching_eligibility("USR006")
    assert_envelope(disabled)
    assert disabled["data"]["eligible"] is False
    assert "MATCHING_DISABLED" in disabled["data"]["failed_gates"]

    blocked = check_matching_eligibility("USR001", "USR008")
    assert_envelope(blocked)
    assert blocked["data"]["eligible"] is False
    assert "BLOCKED_PAIR" in blocked["data"]["failed_gates"]

    dealbreaker = check_matching_eligibility("USR001", "USR004")
    assert_envelope(dealbreaker)
    assert dealbreaker["data"]["eligible"] is False
    assert "USER_TO_CANDIDATE_HARD_CONFLICT" in dealbreaker["data"]["failed_gates"]

    safety = check_matching_eligibility("USR001", "USR010")
    assert_envelope(safety)
    assert safety["data"]["eligible"] is False
    assert "SAFETY_REVIEW_REQUIRED" in safety["data"]["failed_gates"]


def test_search_candidates() -> None:
    result = search_candidates("USR001")
    assert_envelope(result)
    ids = {item["candidate_id"] for item in result["data"]["candidates"]}
    assert "USR002" in ids
    assert "USR006" not in ids
    assert "USR007" not in ids
    assert "USR008" not in ids
    assert "USR010" not in ids
    assert result["data"]["filtered_out_counts"]["matching_disabled"] >= 1
    assert result["data"]["filtered_out_counts"]["consent"] >= 1
    assert result["data"]["filtered_out_counts"]["blocked"] >= 1
    assert result["data"]["filtered_out_counts"]["safety"] >= 1
    assert_no_private_payload(result)

    city = search_candidates("USR001", city="Ha Noi")
    city_ids = {item["candidate_id"] for item in city["data"]["candidates"]}
    assert "USR009" not in city_ids

    age = search_candidates("USR001", min_age=24, max_age=25)
    age_ids = {item["candidate_id"] for item in age["data"]["candidates"]}
    assert age_ids == {"USR002", "USR004"}

    assert_error(search_candidates("USR001", city=""), "INVALID_CITY")
    empty = search_candidates("USR001", city="Da Nang")
    assert_envelope(empty)
    assert empty["status"] == "warning"
    assert empty["data"]["total_found"] == 0


def test_compatibility() -> None:
    high = calculate_compatibility("USR001", "USR002")
    assert_envelope(high)
    assert high["status"] == "success"
    assert high["data"]["eligible"] is True
    assert high["data"]["score_available"] is True
    assert high["data"]["score"] >= 80
    assert 0 <= high["data"]["score"] <= 100
    assert high == calculate_compatibility("USR001", "USR002")

    acceptance_pair = calculate_compatibility("U001", "U003")
    assert_envelope(acceptance_pair)
    assert acceptance_pair["data"]["candidate_id"] == "U003"
    assert acceptance_pair["data"]["eligible"] is True
    assert acceptance_pair["data"]["hard_conflicts"] == []
    assert acceptance_pair["data"]["score"] == 86
    assert acceptance_pair["data"]["confidence"] == 92
    assert acceptance_pair["data"]["breakdown"] == {
        "relationship_goal": 100,
        "values": 90,
        "lifestyle": 75,
        "communication_style": 80,
        "interests": 70,
        "logistics": 100,
    }
    assert acceptance_pair["data"]["strengths"] == [
        "Cùng định hướng mối quan hệ lâu dài",
        "Tương đồng về giá trị sống",
    ]
    assert acceptance_pair["data"]["potential_conflicts"] == [
        "Khác biệt về mức độ giao tiếp xã hội",
    ]

    smoking = calculate_compatibility("USR001", "USR004")
    assert_envelope(smoking)
    assert smoking["data"]["eligible"] is False

    low = calculate_compatibility("USR001", "USR005")
    assert_envelope(low)
    assert low["status"] == "insufficient_data"
    assert low["data"]["score_available"] is False

    tradeoff = calculate_compatibility("USR001", "USR009")
    assert_envelope(tradeoff)
    assert tradeoff["data"]["eligible"] is True
    assert tradeoff["data"]["score_available"] is True
    assert tradeoff["data"]["score"] < high["data"]["score"]

    breakdown = get_compatibility_breakdown("USR001", "USR009")
    assert_envelope(breakdown)
    serialized = json.dumps(breakdown, ensure_ascii=False)
    assert "aligned" in serialized
    assert "trade_off" in serialized
    assert "unknown" in json.dumps(get_compatibility_breakdown("USR001", "USR005"), ensure_ascii=False)
    acceptance_breakdown = get_compatibility_breakdown("U001", "U003")
    assert acceptance_breakdown["data"]["score"] == 86
    assert acceptance_breakdown["data"]["potential_conflicts"]
    assert breakdown["data"]["limitations"]
    assert_no_private_payload(breakdown)


def test_date_tools() -> None:
    shared = get_shared_interests("USR001", "USR002")
    assert_envelope(shared)
    assert shared["status"] == "success"
    assert set(shared["data"]["shared_interests"]) >= {"coffee", "reading", "art"}

    acceptance_shared = get_shared_interests("U001", "U003")
    assert acceptance_shared["data"]["shared_interests"] == [
        "photography",
        "coffee",
        "art",
    ]

    no_shared = get_shared_interests("USR001", "USR009")
    assert_envelope(no_shared)
    assert no_shared["status"] == "warning"
    assert no_shared["data"]["recommended_action"] == "use_neutral_activity"

    activities = search_date_activities(
        "Hanoi",
        ["photography", "coffee", "art"],
        500000,
    )
    assert_envelope(activities)
    assert activities["status"] == "success"
    ids = [item["activity_id"] for item in activities["data"]["activities"]]
    assert "A10" not in ids
    assert ids == ["A01", "A02"]
    assert activities["data"]["activities"][0] == {
        "activity_id": "A01",
        "name": "Workshop làm gốm",
        "city": "Hanoi",
        "interests": ["art", "creative"],
        "estimated_cost": 400000,
        "indoor": True,
    }
    assert activities["data"]["activities"][1] == {
        "activity_id": "A02",
        "name": "Cafe triển lãm ảnh",
        "city": "Hanoi",
        "interests": ["photography", "coffee", "art"],
        "estimated_cost": 250000,
        "indoor": True,
    }

    indoor = search_date_activities("Ha Noi", indoor=True)
    assert all(item["indoor"] is True for item in indoor["data"]["activities"])

    budget = search_date_activities("Ha Noi", max_budget=100000)
    assert all(item["estimated_cost"] <= 100000 for item in budget["data"]["activities"])

    empty = search_date_activities("Da Nang")
    assert_envelope(empty)
    assert empty["status"] == "warning"

    per_pair = estimate_date_cost("A01", people=2)
    assert_envelope(per_pair)
    assert per_pair["data"]["total_estimated_cost"] == 400000

    per_person = estimate_date_cost("A04", people=2)
    assert_envelope(per_person)
    assert per_person["data"]["total_estimated_cost"] == 560000

    extras = estimate_date_cost("A02", people=2, extras=["drinks", "dessert"])
    assert_envelope(extras)
    assert extras["data"]["extras_cost"] == 170000

    assert_error(estimate_date_cost("A99"), "ACTIVITY_NOT_FOUND")
    assert_error(estimate_date_cost("A01", people=0), "INVALID_PEOPLE")


def test_general_contract() -> None:
    calls = [
        lambda: get_match_profile("USR001"),
        lambda: check_profile_completeness("USR001"),
        lambda: check_matching_eligibility("USR001"),
        lambda: search_candidates("USR001"),
        lambda: calculate_compatibility("USR001", "USR002"),
        lambda: get_compatibility_breakdown("USR001", "USR002"),
        lambda: get_shared_interests("USR001", "USR002"),
        lambda: search_date_activities("Ha Noi", ["coffee"]),
        lambda: estimate_date_cost("A02"),
    ]
    for call in calls:
        first = call()
        second = call()
        assert_envelope(first)
        assert first == second

    business_errors = [
        lambda: get_match_profile(""),
        lambda: check_profile_completeness("USR001", "invalid"),
        lambda: search_candidates("USR001", max_results=0),
        lambda: search_date_activities("", ["coffee"]),
        lambda: estimate_date_cost("A01", extras=["invalid"]),
    ]
    for call in business_errors:
        assert_envelope(call())


def main() -> None:
    tests = [
        test_registry,
        test_profile_tools,
        test_search_candidates,
        test_compatibility,
        test_date_tools,
        test_general_contract,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print("All CupidMAS tool smoke tests passed.")


if __name__ == "__main__":
    main()
