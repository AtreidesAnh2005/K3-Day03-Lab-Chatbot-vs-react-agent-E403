from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.tools import (  # noqa: E402
    AVAILABLE_TOOLS,
    apply_hard_constraints,
    calculate_compatibility_score,
    compare_compatibility_dimensions,
    detect_preference_gaps,
    get_consent_scope,
    get_preference_profile,
    rank_candidate_shortlist,
    search_candidate_profiles,
)


EXPECTED_TOOLS = {
    "get_consent_scope",
    "get_preference_profile",
    "detect_preference_gaps",
    "search_candidate_profiles",
    "apply_hard_constraints",
    "compare_compatibility_dimensions",
    "calculate_compatibility_score",
    "rank_candidate_shortlist",
}


def assert_json_serializable(result: dict[str, Any]) -> None:
    json.dumps(result, ensure_ascii=False)


def assert_envelope(result: dict[str, Any]) -> None:
    assert set(result) == {"status", "tool", "data", "error", "metadata"}
    assert result["status"] in {"success", "warning", "error", "insufficient_data", "denied"}
    assert_json_serializable(result)


def assert_error(result: dict[str, Any], code: str) -> None:
    assert_envelope(result)
    assert result["error"]["code"] == code


def test_registry() -> None:
    assert set(AVAILABLE_TOOLS) == EXPECTED_TOOLS


def test_consent_scope() -> None:
    result = get_consent_scope("USR001", "USR002")
    assert_envelope(result)
    assert result["status"] == "success"
    assert result["data"]["consent_active"] is True
    assert "contact_information" not in result["data"]["allowed_fields"]

    assert_error(get_consent_scope("USR001", "USR007"), "CONSENT_REVOKED")
    assert_error(get_consent_scope("USR001", "USR999"), "PROFILE_NOT_FOUND")
    assert_error(get_consent_scope("USR001", "USR001"), "SELF_ANALYSIS_NOT_ALLOWED")


def test_preference_profile() -> None:
    result = get_preference_profile("USR001")
    assert_envelope(result)
    assert result["status"] == "success"
    assert result["data"]["user_id"] == "USR001"

    assert_error(get_preference_profile("USR999"), "PROFILE_NOT_FOUND")
    assert_error(get_preference_profile("USR003"), "PREFERENCE_PROFILE_NOT_FOUND")


def test_preference_gaps() -> None:
    complete = detect_preference_gaps("USR001")
    assert_envelope(complete)
    assert complete["data"]["needs_clarification"] is False

    gaps = detect_preference_gaps("USR002")
    assert_envelope(gaps)
    issues = {gap["issue"] for gap in gaps["data"]["gaps"]}
    assert "missing" in issues
    assert "uncertain" in issues
    assert "contradiction" in issues
    assert "unconfirmed_hard_constraint" in issues


def test_search_candidate_profiles() -> None:
    result = search_candidate_profiles("USR001")
    assert_envelope(result)
    assert result["status"] == "success"
    ids = {candidate["user_id"] for candidate in result["data"]["candidates"]}
    assert {"USR002", "USR003", "USR004", "USR005", "USR009"}.issubset(ids)
    assert "USR006" not in ids
    assert "USR007" not in ids
    assert "USR008" not in ids
    assert all("contact_information" not in candidate for candidate in result["data"]["candidates"])

    city = search_candidate_profiles("USR001", city="Ha Noi")
    city_ids = {candidate["user_id"] for candidate in city["data"]["candidates"]}
    assert "USR009" not in city_ids

    age = search_candidate_profiles("USR001", min_age=24, max_age=25)
    age_ids = {candidate["user_id"] for candidate in age["data"]["candidates"]}
    assert age_ids == {"USR002", "USR004"}

    assert_error(search_candidate_profiles("USR001", min_age=35, max_age=22), "INVALID_AGE_RANGE")
    assert_error(search_candidate_profiles("USR001", max_results=0), "INVALID_MAX_RESULTS")


def test_apply_hard_constraints() -> None:
    result = apply_hard_constraints("USR001", ["USR002", "USR003", "USR004", "USR005"])
    assert_envelope(result)
    assert "USR002" in result["data"]["eligible_candidates"]
    assert "USR005" in result["data"]["eligible_candidates"]

    rejected = {item["candidate_id"]: item for item in result["data"]["rejected_candidates"]}
    assert "RELATIONSHIP_GOAL_MISMATCH" in rejected["USR003"]["reason_codes"]
    assert "DEALBREAKER_MATCH" in rejected["USR004"]["reason_codes"]

    assert_error(apply_hard_constraints("USR001", ["USR002", "USR002"]), "DUPLICATE_CANDIDATE_ID")
    assert_error(apply_hard_constraints("USR001", ["USR999"]), "CANDIDATE_NOT_FOUND")


def test_compare_compatibility_dimensions() -> None:
    high = compare_compatibility_dimensions("USR001", "USR002")
    assert_envelope(high)
    assert high["data"]["summary_counts"]["aligned"] >= 5

    conflict = compare_compatibility_dimensions("USR001", "USR009")
    assert conflict["data"]["summary_counts"]["possible_conflict"] >= 2

    unknown = compare_compatibility_dimensions("USR001", "USR005")
    assert unknown["data"]["summary_counts"]["unknown"] >= 4

    assert_error(compare_compatibility_dimensions("USR001", "USR007"), "CONSENT_REVOKED")
    assert_error(compare_compatibility_dimensions("USR001", "USR999"), "PROFILE_NOT_FOUND")


def test_calculate_compatibility_score() -> None:
    score = calculate_compatibility_score("USR001", "USR002")
    assert_envelope(score)
    assert score["status"] == "success"
    assert score["data"]["score_available"] is True
    assert 0 <= score["data"]["compatibility_score"] <= 100
    assert score == calculate_compatibility_score("USR001", "USR002")

    low = calculate_compatibility_score("USR001", "USR005")
    assert_envelope(low)
    assert low["status"] == "insufficient_data"
    assert low["data"]["score_available"] is False
    assert low["data"]["coverage_ratio"] < 0.60


def test_rank_candidate_shortlist() -> None:
    result = rank_candidate_shortlist(
        "USR001",
        ["USR002", "USR003", "USR004", "USR005", "USR009"],
        shortlist_size=3,
    )
    assert_envelope(result)
    assert result["status"] == "success"
    shortlist_ids = [item["candidate_id"] for item in result["data"]["shortlist"]]
    assert shortlist_ids[0] == "USR002"
    assert "USR003" not in shortlist_ids
    assert "USR004" not in shortlist_ids
    assert any(
        item["candidate_id"] == "USR005" and item["score_available"] is False
        for item in result["data"]["shortlist"]
    )

    again = rank_candidate_shortlist(
        "USR001",
        ["USR002", "USR005", "USR009"],
        shortlist_size=3,
    )
    assert again == rank_candidate_shortlist(
        "USR001",
        ["USR002", "USR005", "USR009"],
        shortlist_size=3,
    )

    assert_error(rank_candidate_shortlist("USR001", ["USR002"], shortlist_size=0), "INVALID_SHORTLIST_SIZE")
    assert_error(rank_candidate_shortlist("USR001", ["USR003", "USR004"], shortlist_size=2), "NO_ELIGIBLE_CANDIDATES")


def main() -> None:
    tests = [
        test_registry,
        test_consent_scope,
        test_preference_profile,
        test_preference_gaps,
        test_search_candidate_profiles,
        test_apply_hard_constraints,
        test_compare_compatibility_dimensions,
        test_calculate_compatibility_score,
        test_rank_candidate_shortlist,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print("All Cupid tool smoke tests passed.")


if __name__ == "__main__":
    main()
