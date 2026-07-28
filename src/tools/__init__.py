"""Deterministic CupidMAS tool registry for Role 2.

The tools in this module are plain Python callables. They read fictional mock
data from data/, return JSON-serializable envelopes, and do not call LLMs,
network APIs, environment variables, or external services.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ToolResult = dict[str, Any]

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

VALID_STATUSES = {"success", "warning", "insufficient_data", "denied", "error"}
VALID_PURPOSES = {"matching", "date_planning"}
VALID_PRIORITIES = {"required", "preferred", "negotiable", "uncertain"}
VALID_SOURCES = {"user_confirmed", "model_inferred", "behavior_observed"}
VALID_ACCOUNT_STATUSES = {"active", "suspended", "banned"}
VALID_SAFETY_STATUSES = {"clear", "warning", "review_required", "blocked"}

DIMENSIONS = [
    "relationship_goal",
    "values",
    "lifestyle",
    "communication_style",
    "future_plans",
    "interests",
    "availability",
    "logistics",
]

DIMENSION_WEIGHTS = {
    "relationship_goal": 0.20,
    "values": 0.20,
    "lifestyle": 0.15,
    "communication_style": 0.15,
    "future_plans": 0.10,
    "interests": 0.08,
    "availability": 0.07,
    "logistics": 0.05,
}

PRIORITY_WEIGHTS = {
    "required": 1.0,
    "preferred": 0.75,
    "negotiable": 0.40,
    "uncertain": 0.0,
}

RESULT_SCORES = {
    "aligned": 1.0,
    "trade_off": 0.4,
}

PROFILE_FIELD_GROUPS = {
    "basic_profile": ["display_name", "age", "city", "active"],
    "relationship_goal": ["relationship_goal"],
    "interests": ["interests"],
    "values": ["values"],
    "lifestyle": ["lifestyle"],
    "communication_style": ["communication_style"],
    "future_plans": ["future_plans"],
    "availability": ["availability"],
    "date_preferences": ["date_preferences"],
}

SELF_PROFILE_FIELDS = [
    "user_id",
    "display_name",
    "age",
    "city",
    "active",
    "matching_enabled",
    "consent_to_matching",
    "relationship_goal",
    "interests",
    "values",
    "lifestyle",
    "communication_style",
    "future_plans",
    "availability",
    "date_preferences",
]

MATCHING_REQUIRED_FIELDS = [
    "age",
    "active",
    "matching_enabled",
    "consent_to_matching",
    "relationship_goal",
]

MATCHING_OPTIONAL_FIELDS = [
    "values",
    "lifestyle",
    "communication_style",
    "future_plans",
    "interests",
    "availability",
]

DATE_PLANNING_FIELDS = [
    "city",
    "interests",
    "date_preferences.max_budget",
    "date_preferences.indoor_preference",
    "availability",
]

EXTRA_PRICES = {
    "drinks": 80000,
    "snacks": 60000,
    "dessert": 90000,
    "photo_print": 50000,
}

LIMITATIONS = [
    "Score only reflects declared mock data.",
    "Result does not predict relationship success.",
]


def _success_response(
    tool: str,
    data: Any,
    status: str = "success",
    metadata: dict[str, Any] | None = None,
) -> ToolResult:
    return {
        "status": status if status in VALID_STATUSES else "success",
        "tool": tool,
        "data": data,
        "error": None,
        "metadata": metadata or {},
    }


def _error_response(
    tool: str,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    status: str = "error",
    metadata: dict[str, Any] | None = None,
) -> ToolResult:
    return {
        "status": status if status in VALID_STATUSES else "error",
        "tool": tool,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "metadata": metadata or {},
    }


def _load_json_data(filename: str) -> Any:
    with (DATA_DIR / filename).open("r", encoding="utf-8") as file:
        return json.load(file)


def _load_profiles() -> list[dict[str, Any]]:
    data = _load_json_data("cupid_profiles.json")
    if not isinstance(data, list):
        raise ValueError("profiles must be a list")
    return data


def _load_preferences() -> list[dict[str, Any]]:
    data = _load_json_data("cupid_preferences.json")
    if not isinstance(data, list):
        raise ValueError("preferences must be a list")
    return data


def _load_consents() -> list[dict[str, Any]]:
    data = _load_json_data("cupid_consents.json")
    if not isinstance(data, list):
        raise ValueError("consents must be a list")
    return data


def _load_safety_records() -> list[dict[str, Any]]:
    data = _load_json_data("cupid_safety.json")
    if not isinstance(data, list):
        raise ValueError("safety records must be a list")
    return data


def _load_date_activities() -> list[dict[str, Any]]:
    data = _load_json_data("cupid_date_activities.json")
    if not isinstance(data, list):
        raise ValueError("date activities must be a list")
    return data


def _load_compatibility_assessments() -> list[dict[str, Any]]:
    data = _load_json_data("cupid_compatibility_assessments.json")
    if not isinstance(data, list):
        raise ValueError("compatibility assessments must be a list")
    return data


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_user_id(value: Any) -> bool:
    return _is_non_empty_string(value)


def _profile_by_id(user_id: str) -> dict[str, Any] | None:
    if not _is_non_empty_string(user_id):
        return None
    requested = user_id.strip().casefold()
    return next(
        (
            item
            for item in _load_profiles()
            if requested
            in {
                str(item.get("user_id", "")).casefold(),
                str(item.get("external_id", "")).casefold(),
            }
        ),
        None,
    )


def _internal_user_id(user_id: str) -> str | None:
    profile = _profile_by_id(user_id)
    internal_id = profile.get("user_id") if profile else None
    return str(internal_id) if _is_non_empty_string(internal_id) else None


def _external_user_id(user_id: str) -> str:
    profile = _profile_by_id(user_id)
    if profile and _is_non_empty_string(profile.get("external_id")):
        return str(profile["external_id"])
    return user_id.strip() if _is_non_empty_string(user_id) else user_id


def _same_user_id(left: str, right: str) -> bool:
    left_internal = _internal_user_id(left)
    right_internal = _internal_user_id(right)
    return left_internal is not None and left_internal == right_internal


def _preference_profile_by_user_id(user_id: str) -> dict[str, Any] | None:
    internal_id = _internal_user_id(user_id)
    if internal_id is None:
        return None
    return next(
        (item for item in _load_preferences() if item.get("user_id") == internal_id),
        None,
    )


def _safety_record_by_user_id(user_id: str) -> dict[str, Any] | None:
    internal_id = _internal_user_id(user_id)
    if internal_id is None:
        return None
    return next(
        (item for item in _load_safety_records() if item.get("user_id") == internal_id),
        None,
    )


def _activity_by_id(activity_id: str) -> dict[str, Any] | None:
    return next(
        (item for item in _load_date_activities() if item.get("activity_id") == activity_id),
        None,
    )


def _consent_record(owner_id: str, viewer_id: str) -> dict[str, Any] | None:
    internal_owner_id = _internal_user_id(owner_id)
    internal_viewer_id = _internal_user_id(viewer_id)
    if internal_owner_id is None or internal_viewer_id is None:
        return None
    return next(
        (
            item
            for item in _load_consents()
            if item.get("owner_id") == internal_owner_id
            and item.get("viewer_id") == internal_viewer_id
        ),
        None,
    )


def _active_consent(owner_id: str, viewer_id: str) -> dict[str, Any] | None:
    consent = _consent_record(owner_id, viewer_id)
    if consent and consent.get("consent_active") is True:
        return consent
    return None


def _field_allowed(owner_id: str, viewer_id: str, field_group: str) -> bool:
    consent = _active_consent(owner_id, viewer_id)
    return bool(consent and field_group in consent.get("allowed_fields", []))


def _value_at(data: dict[str, Any], dotted_field: str) -> Any:
    value: Any = data
    for part in dotted_field.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _has_value(data: dict[str, Any], dotted_field: str) -> bool:
    value = _value_at(data, dotted_field)
    return value not in (None, "", [], {})


def _preferences_for(user_id: str) -> list[dict[str, Any]] | None:
    profile = _preference_profile_by_user_id(user_id)
    if not profile:
        return None
    preferences = profile.get("preferences")
    if not isinstance(preferences, list):
        return None
    return preferences


def _public_profile_view(
    profile: dict[str, Any],
    requester_id: str,
    view_type: str,
) -> tuple[dict[str, Any], list[str], list[str]]:
    if view_type == "self":
        return (
            {field: profile[field] for field in SELF_PROFILE_FIELDS if field in profile},
            SELF_PROFILE_FIELDS[:],
            [],
        )

    consent = _active_consent(profile["user_id"], requester_id)
    if not consent:
        return {}, [], []

    allowed_groups = consent.get("allowed_fields", [])
    visible: dict[str, Any] = {"user_id": profile["user_id"]}
    for group in allowed_groups:
        for field in PROFILE_FIELD_GROUPS.get(group, []):
            if field in profile:
                visible[field] = profile[field]
    return visible, allowed_groups, consent.get("restricted_fields", [])


def _blocked_between(user: dict[str, Any], candidate: dict[str, Any]) -> bool:
    return (
        candidate.get("user_id") in user.get("blocked_user_ids", [])
        or user.get("user_id") in candidate.get("blocked_user_ids", [])
    )


def _overlap(left: Any, right: Any) -> list[str]:
    if not isinstance(left, list) or not isinstance(right, list):
        return []
    right_set = {str(item).casefold() for item in right}
    overlap: list[str] = []
    seen: set[str] = set()
    for item in left:
        normalized = str(item).casefold()
        if normalized in right_set and normalized not in seen:
            overlap.append(str(item))
            seen.add(normalized)
    return overlap


def _canonical_city(value: str) -> str:
    normalized = " ".join(value.strip().casefold().replace(".", " ").split())
    aliases = {
        "hanoi": "Hanoi",
        "ha noi": "Hanoi",
        "hà nội": "Hanoi",
        "ho chi minh": "Ho Chi Minh City",
        "ho chi minh city": "Ho Chi Minh City",
        "hồ chí minh": "Ho Chi Minh City",
        "tp hcm": "Ho Chi Minh City",
        "hcm": "Ho Chi Minh City",
    }
    return aliases.get(normalized, value.strip())


def _compatibility_assessment(user_id: str, candidate_id: str) -> dict[str, Any] | None:
    internal_ids = {_internal_user_id(user_id), _internal_user_id(candidate_id)}
    if None in internal_ids or len(internal_ids) != 2:
        return None
    for assessment in _load_compatibility_assessments():
        participant_ids = assessment.get("participant_ids")
        if not isinstance(participant_ids, list) or len(participant_ids) != 2:
            continue
        assessment_ids = {
            _internal_user_id(str(participant_id))
            for participant_id in participant_ids
        }
        if assessment_ids == internal_ids:
            return assessment
    return None


def _validated_assessment_data(
    assessment: dict[str, Any],
    candidate_id: str,
) -> dict[str, Any] | None:
    breakdown = assessment.get("breakdown")
    confidence = assessment.get("confidence")
    strengths = assessment.get("strengths")
    potential_conflicts = assessment.get("potential_conflicts")
    if (
        not isinstance(breakdown, dict)
        or not breakdown
        or not all(
            isinstance(score, (int, float))
            and not isinstance(score, bool)
            and 0 <= score <= 100
            for score in breakdown.values()
        )
        or not isinstance(confidence, (int, float))
        or isinstance(confidence, bool)
        or not 0 <= confidence <= 100
        or not isinstance(strengths, list)
        or not all(_is_non_empty_string(item) for item in strengths)
        or not isinstance(potential_conflicts, list)
        or not all(_is_non_empty_string(item) for item in potential_conflicts)
    ):
        return None

    normalized_breakdown = {
        str(dimension): int(round(score))
        for dimension, score in breakdown.items()
    }
    score = int(round(sum(normalized_breakdown.values()) / len(normalized_breakdown)))
    return {
        "candidate_id": _external_user_id(candidate_id),
        "eligible": True,
        "score_available": True,
        "score": score,
        "confidence": int(round(confidence)),
        "breakdown": normalized_breakdown,
        "strengths": [str(item) for item in strengths],
        "potential_conflicts": [str(item) for item in potential_conflicts],
        "hard_conflicts": [],
        "limitations": LIMITATIONS,
    }


def _confidence_from_coverage(coverage_ratio: float) -> str:
    if coverage_ratio >= 0.80:
        return "high"
    if coverage_ratio >= 0.60:
        return "medium"
    return "low"


def _dimension_for_field(field: str) -> str:
    if field == "age_range" or field in {"city", "max_distance"}:
        return "logistics"
    if field.startswith("lifestyle."):
        return "lifestyle"
    if field.startswith("future_plans."):
        return "future_plans"
    return field if field in DIMENSIONS else "logistics"


def _consent_group_for_dimension(dimension: str) -> str:
    if dimension == "logistics":
        return "basic_profile"
    return dimension


def _hard_constraint_preferences(user_id: str) -> list[dict[str, Any]]:
    preferences = _preferences_for(user_id) or []
    return [
        item
        for item in preferences
        if item.get("priority") == "required"
        and item.get("source") == "user_confirmed"
        and item.get("field") != "dealbreakers"
    ]


def _dealbreakers(user_id: str) -> list[dict[str, Any]]:
    preferences = _preferences_for(user_id) or []
    for item in preferences:
        if (
            item.get("field") == "dealbreakers"
            and item.get("priority") == "required"
            and item.get("source") == "user_confirmed"
            and isinstance(item.get("value"), list)
        ):
            return [entry for entry in item["value"] if isinstance(entry, dict)]
    return []


def _evaluate_single_preference(
    preference: dict[str, Any],
    target_profile: dict[str, Any],
    target_owner_id: str,
    viewer_id: str,
) -> dict[str, Any]:
    field = preference.get("field")
    priority = preference.get("priority")
    preferred = preference.get("value")
    dimension = _dimension_for_field(str(field))

    if priority not in VALID_PRIORITIES:
        return {
            "dimension": dimension,
            "result": "unknown",
            "evidence": [],
            "missing_fields": [str(field)],
            "priority": "uncertain",
        }
    if priority == "uncertain":
        return {
            "dimension": dimension,
            "result": "unknown",
            "evidence": [],
            "missing_fields": [str(field)],
            "priority": priority,
        }
    if not _field_allowed(target_owner_id, viewer_id, _consent_group_for_dimension(dimension)):
        return {
            "dimension": dimension,
            "result": "unknown",
            "evidence": [],
            "missing_fields": [str(field)],
            "priority": priority,
        }

    actual = _value_at(target_profile, str(field))
    if field == "age_range":
        actual = target_profile.get("age")
        if not isinstance(preferred, dict) or not isinstance(actual, int):
            result = "unknown"
        else:
            result = (
                "aligned"
                if preferred.get("min", 0) <= actual <= preferred.get("max", 200)
                else "hard_conflict" if priority == "required" else "trade_off"
            )
    elif isinstance(preferred, list):
        actual_list = actual if isinstance(actual, list) else []
        result = "aligned" if _overlap(preferred, actual_list) else "unknown" if not actual_list else "trade_off"
    elif isinstance(preferred, dict):
        actual_dict = actual if isinstance(actual, dict) else {}
        if not actual_dict:
            result = "unknown"
        else:
            result = "aligned" if all(actual_dict.get(k) == v for k, v in preferred.items()) else "trade_off"
    else:
        if actual in (None, "", [], {}):
            result = "unknown"
        else:
            result = "aligned" if actual == preferred else "hard_conflict" if priority == "required" else "trade_off"

    return {
        "dimension": dimension,
        "result": result,
        "evidence": [
            {
                "field": str(field),
                "result": result,
                "priority": priority,
            }
        ]
        if result != "unknown"
        else [],
        "missing_fields": [str(field)] if result == "unknown" else [],
        "priority": priority,
    }


def _evaluate_directional_preferences(
    preference_owner_id: str,
    target_id: str,
) -> dict[str, Any]:
    target_profile = _profile_by_id(target_id)
    preferences = _preferences_for(preference_owner_id)
    if target_profile is None or preferences is None:
        return {
            "score_available": False,
            "score": None,
            "coverage_ratio": 0.0,
            "confidence": "low",
            "dimensions": {},
            "hard_conflicts": ["PREFERENCE_PROFILE_NOT_FOUND"],
            "unknown_dimensions": DIMENSIONS[:],
        }

    dimension_rows: dict[str, list[dict[str, Any]]] = {dimension: [] for dimension in DIMENSIONS}
    for preference in preferences:
        field = preference.get("field")
        if field == "dealbreakers":
            continue
        row = _evaluate_single_preference(preference, target_profile, target_id, preference_owner_id)
        dimension_rows[row["dimension"]].append(row)

    dimensions: dict[str, dict[str, Any]] = {}
    hard_conflicts: list[str] = []
    unknown_dimensions: list[str] = []
    total_weight = 0.0
    available_weight = 0.0
    weighted_score = 0.0

    for dimension in DIMENSIONS:
        base_weight = DIMENSION_WEIGHTS[dimension]
        rows = dimension_rows[dimension]
        if not rows:
            dimensions[dimension] = {
                "result": "unknown",
                "evidence": [],
                "missing_fields": [dimension],
            }
            unknown_dimensions.append(dimension)
            total_weight += base_weight
            continue

        priority_weight = max(PRIORITY_WEIGHTS.get(row["priority"], 0.0) for row in rows)
        dimension_weight = base_weight * priority_weight
        total_weight += dimension_weight
        if dimension_weight == 0:
            dimensions[dimension] = {
                "result": "unknown",
                "evidence": [],
                "missing_fields": [dimension],
            }
            unknown_dimensions.append(dimension)
            continue

        if any(row["result"] == "hard_conflict" for row in rows):
            result = "hard_conflict"
        elif any(row["result"] == "trade_off" for row in rows):
            result = "trade_off"
        elif any(row["result"] == "aligned" for row in rows):
            result = "aligned"
        else:
            result = "unknown"

        evidence = [entry for row in rows for entry in row["evidence"]]
        missing = sorted({field for row in rows for field in row["missing_fields"]})
        dimensions[dimension] = {
            "result": result,
            "evidence": evidence,
            "missing_fields": missing,
        }

        if result == "unknown":
            unknown_dimensions.append(dimension)
            continue
        if result == "hard_conflict":
            hard_conflicts.append(dimension)
            continue
        available_weight += dimension_weight
        weighted_score += dimension_weight * RESULT_SCORES[result]

    coverage_ratio = round(available_weight / total_weight, 2) if total_weight else 0.0
    score_available = coverage_ratio >= 0.60 and not hard_conflicts and available_weight > 0
    return {
        "score_available": score_available,
        "score": int(round((weighted_score / available_weight) * 100)) if score_available else None,
        "coverage_ratio": coverage_ratio,
        "confidence": _confidence_from_coverage(coverage_ratio),
        "dimensions": dimensions,
        "hard_conflicts": hard_conflicts,
        "unknown_dimensions": unknown_dimensions,
    }


def _check_self_eligibility_data(user_id: str) -> tuple[dict[str, Any] | None, list[str], list[dict[str, Any]], str, bool]:
    profile = _profile_by_id(user_id)
    failed: list[str] = []
    evidence: list[dict[str, Any]] = []
    if profile is None:
        return None, ["PROFILE_NOT_FOUND"], evidence, "unknown", False

    checks = [
        ("AGE_NOT_ELIGIBLE", isinstance(profile.get("age"), int) and profile["age"] >= 18, "age"),
        ("INACTIVE_PROFILE", profile.get("active") is True, "active"),
        ("MATCHING_DISABLED", profile.get("matching_enabled") is True, "matching_enabled"),
        ("MATCHING_CONSENT_MISSING", profile.get("consent_to_matching") is True, "consent_to_matching"),
    ]
    for code, passed, field in checks:
        evidence.append({"gate": code, "field": field, "result": "pass" if passed else "fail"})
        if not passed:
            failed.append(code)

    safety = _safety_record_by_user_id(user_id)
    if safety is None:
        failed.append("SAFETY_RECORD_NOT_FOUND")
        return profile, failed, evidence, "unknown", False

    safety_status = safety.get("safety_status")
    requires_review = safety.get("requires_human_review") is True
    safety_checks = [
        ("AGE_NOT_VERIFIED", safety.get("age_verified") is True, "age_verified"),
        ("ACCOUNT_NOT_ACTIVE", safety.get("account_status") == "active", "account_status"),
        ("SAFETY_BLOCKED", safety_status != "blocked", "safety_status"),
        ("SAFETY_REVIEW_REQUIRED", not requires_review, "requires_human_review"),
    ]
    for code, passed, field in safety_checks:
        evidence.append({"gate": code, "field": field, "result": "pass" if passed else "fail"})
        if not passed:
            failed.append(code)
    return profile, failed, evidence, str(safety_status), requires_review


def _check_directional_hard_constraints(
    preference_owner_id: str,
    target_id: str,
) -> dict[str, Any]:
    target = _profile_by_id(target_id)
    preferences = _preferences_for(preference_owner_id)
    if target is None:
        return {"status": "fail", "checks": [{"gate": "PROFILE_NOT_FOUND", "result": "fail"}]}
    if preferences is None:
        return {"status": "fail", "checks": [{"gate": "PREFERENCE_PROFILE_NOT_FOUND", "result": "fail"}]}

    checks: list[dict[str, Any]] = []
    for preference in _hard_constraint_preferences(preference_owner_id):
        row = _evaluate_single_preference(preference, target, target_id, preference_owner_id)
        passed = row["result"] != "hard_conflict"
        checks.append(
            {
                "gate": f"HARD_CONSTRAINT_{row['dimension'].upper()}",
                "dimension": row["dimension"],
                "result": "pass" if passed else "fail",
            }
        )

    for dealbreaker in _dealbreakers(preference_owner_id):
        field = str(dealbreaker.get("field"))
        disallowed = dealbreaker.get("disallowed_value")
        actual = _value_at(target, field)
        passed = actual != disallowed
        checks.append(
            {
                "gate": "DEALBREAKER",
                "dimension": _dimension_for_field(field),
                "result": "pass" if passed else "fail",
            }
        )

    return {
        "status": "pass" if all(check["result"] == "pass" for check in checks) else "fail",
        "checks": checks,
    }


def _check_pair_eligibility_data(user_id: str, candidate_id: str) -> dict[str, Any]:
    failed: list[str] = []
    evidence: list[dict[str, Any]] = []
    user, user_failed, user_evidence, user_safety, user_review = _check_self_eligibility_data(user_id)
    candidate, candidate_failed, candidate_evidence, candidate_safety, candidate_review = _check_self_eligibility_data(candidate_id)
    evidence.extend({"side": "user", **item} for item in user_evidence)
    evidence.extend({"side": "candidate", **item} for item in candidate_evidence)
    failed.extend(user_failed)
    failed.extend(candidate_failed)

    if user is None or candidate is None:
        return {
            "eligible": False,
            "failed_gates": sorted(set(failed)),
            "user_to_candidate": {"status": "fail", "checks": []},
            "candidate_to_user": {"status": "fail", "checks": []},
            "safety_status": candidate_safety,
            "requires_human_review": candidate_review,
            "evidence": evidence,
        }

    consent_candidate_to_user = _consent_record(candidate_id, user_id)
    consent_user_to_candidate = _consent_record(user_id, candidate_id)
    if consent_candidate_to_user is None or consent_user_to_candidate is None:
        failed.append("CONSENT_NOT_FOUND")
    elif (
        consent_candidate_to_user.get("consent_active") is not True
        or consent_user_to_candidate.get("consent_active") is not True
    ):
        failed.append("CONSENT_REVOKED")

    if _blocked_between(user, candidate):
        failed.append("BLOCKED_PAIR")

    user_to_candidate = _check_directional_hard_constraints(user_id, candidate_id)
    candidate_to_user = _check_directional_hard_constraints(candidate_id, user_id)
    if user_to_candidate["status"] == "fail":
        failed.append("USER_TO_CANDIDATE_HARD_CONFLICT")
    if candidate_to_user["status"] == "fail":
        failed.append("CANDIDATE_TO_USER_HARD_CONFLICT")

    return {
        "eligible": not failed,
        "failed_gates": sorted(set(failed)),
        "user_to_candidate": user_to_candidate,
        "candidate_to_user": candidate_to_user,
        "safety_status": candidate_safety,
        "requires_human_review": candidate_review or user_review,
        "evidence": evidence,
    }


def _mutual_score(left: int | None, right: int | None) -> int | None:
    if left is None or right is None or left + right == 0:
        return None
    return round(2 * left * right / (left + right))


def _estimated_activity_cost(activity: dict[str, Any], people: int = 2) -> int:
    base_cost = int(activity.get("base_cost", 0))
    if activity.get("cost_unit") == "per_person":
        return base_cost * people
    return base_cost


def _common_docstring(name: str) -> str:
    return name


def get_match_profile(user_id: str, requester_id: str | None = None) -> ToolResult:
    """
    Name:
        get_match_profile
    Purpose:
        Read a self or consented candidate profile for matching.
    When to use:
        Profile Agent needs structured profile data.
    When not to use:
        Do not retrieve private messages, contact data, raw candidate preferences,
        internal safety reports, or data outside consent.
    Args:
        user_id: Profile owner ID.
        requester_id: Viewer ID. Defaults to user_id for self view.
    Returns:
        ToolResult with view_type, profile, available_fields, and restricted_fields when relevant.
    Error semantics:
        Business errors return structured ToolResult and never crash.
    Side effects:
        None.
    Safety notes:
        Candidate profile fields are limited by active consent.
    Example:
        get_match_profile("USR002", requester_id="USR001")
    """
    tool = "get_match_profile"
    try:
        if not _validate_user_id(user_id):
            return _error_response(tool, "INVALID_USER_ID", "user_id must be a non-empty string.")
        requester = requester_id if requester_id is not None else user_id
        if not _validate_user_id(requester):
            return _error_response(tool, "INVALID_USER_ID", "requester_id must be a non-empty string.")
        profile = _profile_by_id(user_id)
        requester_profile = _profile_by_id(requester)
        if profile is None or requester_profile is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "Profile was not found.")
        if requester == user_id:
            public_profile, available, _ = _public_profile_view(profile, requester, "self")
            return _success_response(
                tool,
                {
                    "profile_id": user_id,
                    "view_type": "self",
                    "profile": public_profile,
                    "available_fields": available,
                },
            )
        consent = _consent_record(user_id, requester)
        if consent is None:
            return _error_response(tool, "CONSENT_NOT_FOUND", "Consent record was not found.", status="denied")
        if consent.get("consent_active") is not True:
            return _error_response(tool, "CONSENT_REVOKED", "Consent is revoked.", status="denied")
        public_profile, available, restricted = _public_profile_view(profile, requester, "consented_candidate")
        if not public_profile:
            return _error_response(tool, "PROFILE_ACCESS_DENIED", "No profile fields are available.", status="denied")
        return _success_response(
            tool,
            {
                "profile_id": user_id,
                "view_type": "consented_candidate",
                "profile": public_profile,
                "available_fields": available,
                "restricted_fields": restricted,
            },
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def check_profile_completeness(user_id: str, purpose: str = "matching") -> ToolResult:
    """
    Name:
        check_profile_completeness
    Purpose:
        Check whether a profile has enough declared data for matching or date planning.
    When to use:
        Profile Agent needs to decide whether to continue or ask for clarification.
    When not to use:
        Do not use to fill missing fields or update a profile.
    Args:
        user_id: Profile owner ID.
        purpose: matching or date_planning.
    Returns:
        ToolResult with completeness ratio, missing fields, recommended_action, and suggested_questions.
    Error semantics:
        Invalid inputs and missing profiles return structured errors.
    Side effects:
        None.
    Safety notes:
        Missing data is reported only; it is never inferred.
    Example:
        check_profile_completeness("USR001", "matching")
    """
    tool = "check_profile_completeness"
    try:
        if not _validate_user_id(user_id):
            return _error_response(tool, "INVALID_USER_ID", "user_id must be a non-empty string.")
        if purpose not in VALID_PURPOSES:
            return _error_response(tool, "INVALID_PURPOSE", "purpose must be matching or date_planning.")
        profile = _profile_by_id(user_id)
        if profile is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "Profile was not found.")

        if purpose == "matching":
            required_fields = MATCHING_REQUIRED_FIELDS
            optional_fields = MATCHING_OPTIONAL_FIELDS
        else:
            required_fields = DATE_PLANNING_FIELDS
            optional_fields = []

        missing_required = [field for field in required_fields if not _has_value(profile, field)]
        missing_optional = [field for field in optional_fields if not _has_value(profile, field)]
        total = len(required_fields) + len(optional_fields)
        present = total - len(missing_required) - len(missing_optional)
        ratio = round(present / total, 2) if total else 1.0
        recommended_action = "ask_human" if missing_required else "continue"
        questions = [f"Please clarify {field}." for field in missing_required + missing_optional]
        return _success_response(
            tool,
            {
                "user_id": user_id,
                "purpose": purpose,
                "profile_complete": not missing_required,
                "completeness_ratio": ratio,
                "missing_required_fields": missing_required,
                "missing_optional_fields": missing_optional,
                "low_confidence_fields": missing_optional if purpose == "matching" else [],
                "recommended_action": recommended_action,
                "suggested_questions": questions,
            },
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def check_matching_eligibility(user_id: str, candidate_id: str | None = None) -> ToolResult:
    """
    Name:
        check_matching_eligibility
    Purpose:
        Check self or pair eligibility gates before candidate search and scoring.
    When to use:
        Profile or Matching Agent needs deterministic eligibility results.
    When not to use:
        Do not use to loosen hard constraints or expose raw candidate preferences.
    Args:
        user_id: Requesting user ID.
        candidate_id: Optional candidate ID for pair eligibility.
    Returns:
        ToolResult with eligible, failed_gates, directional checks, safety status, and evidence.
    Error semantics:
        Missing records can be errors; eligibility false can be a normal business result.
    Side effects:
        None.
    Safety notes:
        Safety review is reported as a status, not as a personal judgment.
    Example:
        check_matching_eligibility("USR001", "USR002")
    """
    tool = "check_matching_eligibility"
    try:
        if not _validate_user_id(user_id):
            return _error_response(tool, "INVALID_USER_ID", "user_id must be a non-empty string.")
        if candidate_id is not None and not _validate_user_id(candidate_id):
            return _error_response(tool, "INVALID_USER_ID", "candidate_id must be a non-empty string.")
        if _same_user_id(candidate_id, user_id):
            return _error_response(tool, "SELF_MATCH_NOT_ALLOWED", "Self match is not allowed.")
        if _profile_by_id(user_id) is None or (candidate_id is not None and _profile_by_id(candidate_id) is None):
            return _error_response(tool, "PROFILE_NOT_FOUND", "Profile was not found.")
        if _safety_record_by_user_id(user_id) is None or (
            candidate_id is not None and _safety_record_by_user_id(candidate_id) is None
        ):
            return _error_response(tool, "SAFETY_RECORD_NOT_FOUND", "Safety record was not found.")
        if candidate_id is None:
            _, failed, evidence, safety_status, requires_review = _check_self_eligibility_data(user_id)
            return _success_response(
                tool,
                {
                    "user_id": user_id,
                    "candidate_id": None,
                    "eligible": not failed,
                    "eligibility_mode": "self",
                    "failed_gates": sorted(set(failed)),
                    "user_to_candidate": {"status": "not_applicable", "checks": []},
                    "candidate_to_user": {"status": "not_applicable", "checks": []},
                    "safety_status": safety_status,
                    "requires_human_review": requires_review,
                    "evidence": evidence,
                },
            )
        if _preference_profile_by_user_id(user_id) is None or _preference_profile_by_user_id(candidate_id) is None:
            return _error_response(tool, "PREFERENCE_PROFILE_NOT_FOUND", "Preference profile was not found.")
        pair = _check_pair_eligibility_data(user_id, candidate_id)
        return _success_response(
            tool,
            {
                "user_id": user_id,
                "candidate_id": candidate_id,
                "eligibility_mode": "pair",
                **pair,
            },
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def search_candidates(
    user_id: str,
    city: str | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    max_results: int = 5,
) -> ToolResult:
    """
    Name:
        search_candidates
    Purpose:
        Find candidate profiles that pass basic visibility and safety gates.
    When to use:
        Matching Agent needs a deterministic candidate pool.
    When not to use:
        Do not calculate compatibility or loosen filters in this tool.
    Args:
        user_id: Requesting user ID.
        city: Optional city filter.
        min_age: Optional inclusive minimum age.
        max_age: Optional inclusive maximum age.
        max_results: Maximum returned candidates, 1 to 20.
    Returns:
        ToolResult with candidates, filtered_out_counts, and relaxable_filters.
    Error semantics:
        Invalid input returns errors; empty results return warning.
    Side effects:
        None.
    Safety notes:
        Safety and consent gates cannot be relaxed.
    Example:
        search_candidates("USR001", city="Ha Noi")
    """
    tool = "search_candidates"
    try:
        if not _validate_user_id(user_id):
            return _error_response(tool, "INVALID_USER_ID", "user_id must be a non-empty string.")
        requester = _profile_by_id(user_id)
        if requester is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "Profile was not found.")
        if city is not None and not _is_non_empty_string(city):
            return _error_response(tool, "INVALID_CITY", "city must be a non-empty string.")
        if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
            return _error_response(tool, "INVALID_MAX_RESULTS", "max_results must be from 1 to 20.")
        if min_age is not None and (not isinstance(min_age, int) or min_age < 18 or min_age > 100):
            return _error_response(tool, "INVALID_AGE_RANGE", "min_age must be from 18 to 100.")
        if max_age is not None and (not isinstance(max_age, int) or max_age < 18 or max_age > 100):
            return _error_response(tool, "INVALID_AGE_RANGE", "max_age must be from 18 to 100.")
        if min_age is not None and max_age is not None and min_age > max_age:
            return _error_response(tool, "INVALID_AGE_RANGE", "min_age must be <= max_age.")

        counts = {
            "inactive": 0,
            "matching_disabled": 0,
            "consent": 0,
            "blocked": 0,
            "safety": 0,
            "city": 0,
            "age": 0,
        }
        candidates: list[dict[str, Any]] = []
        city_filter = _canonical_city(city) if isinstance(city, str) else None
        for profile in sorted(_load_profiles(), key=lambda item: item.get("user_id", "")):
            candidate_id = profile.get("user_id")
            if _same_user_id(str(candidate_id), user_id):
                continue
            if profile.get("active") is not True:
                counts["inactive"] += 1
                continue
            if profile.get("matching_enabled") is not True or profile.get("consent_to_matching") is not True:
                counts["matching_disabled"] += 1
                continue
            if _blocked_between(requester, profile):
                counts["blocked"] += 1
                continue
            if _active_consent(candidate_id, user_id) is None:
                counts["consent"] += 1
                continue
            safety = _safety_record_by_user_id(candidate_id)
            if (
                safety is None
                or safety.get("safety_status") in {"blocked", "review_required"}
                or safety.get("requires_human_review") is True
            ):
                counts["safety"] += 1
                continue
            if city_filter and _canonical_city(str(profile.get("city", ""))).casefold() != city_filter.casefold():
                counts["city"] += 1
                continue
            if min_age is not None and profile.get("age", 0) < min_age:
                counts["age"] += 1
                continue
            if max_age is not None and profile.get("age", 101) > max_age:
                counts["age"] += 1
                continue
            public_profile, available, _ = _public_profile_view(profile, user_id, "consented_candidate")
            candidates.append(
                {
                    "candidate_id": candidate_id,
                    "display_name": public_profile.get("display_name"),
                    "age": public_profile.get("age"),
                    "city": public_profile.get("city"),
                    "available_fields": available,
                }
            ) if len(candidates) < max_results else None

        data = {
            "query": {
                "user_id": user_id,
                "city": city_filter,
                "min_age": min_age,
                "max_age": max_age,
                "max_results": max_results,
            },
            "total_found": len(candidates),
            "candidates": candidates,
            "filtered_out_counts": counts,
            "relaxable_filters": [
                {"field": "city", "priority": "preferred"}
            ]
            if city_filter and not candidates
            else [],
        }
        if not candidates:
            data.update(
                {
                    "non_relaxable_gates": ["consent", "safety", "dealbreakers"],
                    "recommended_action": "replan_or_ask_human",
                }
            )
            return _success_response(tool, data, status="warning")
        return _success_response(tool, data)
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def calculate_compatibility(user_id: str, candidate_id: str) -> ToolResult:
    """
    Name:
        calculate_compatibility
    Purpose:
        Check pair eligibility and calculate deterministic two-way compatibility.
    When to use:
        Matching Agent needs a score for an eligible pair.
    When not to use:
        Do not use to produce guaranteed-match language or override hard conflicts.
    Args:
        user_id: Requesting user ID.
        candidate_id: Candidate ID.
    Returns:
        ToolResult with mutual score, directional scores, coverage, conflicts, unknowns, and limitations.
    Error semantics:
        Validation errors are structured; ineligible pairs return success with eligible=false.
    Side effects:
        None.
    Safety notes:
        Candidate raw preferences are used only internally and never exposed.
    Example:
        calculate_compatibility("USR001", "USR002")
    """
    tool = "calculate_compatibility"
    try:
        if not _validate_user_id(user_id) or not _validate_user_id(candidate_id):
            return _error_response(tool, "INVALID_USER_ID", "User IDs must be non-empty strings.")
        if _same_user_id(user_id, candidate_id):
            return _error_response(tool, "SELF_MATCH_NOT_ALLOWED", "Self match is not allowed.")
        if _profile_by_id(user_id) is None or _profile_by_id(candidate_id) is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "Profile was not found.")

        eligibility = check_matching_eligibility(user_id, candidate_id)
        if eligibility["status"] != "success":
            eligibility["tool"] = tool
            return eligibility
        if not eligibility["data"]["eligible"]:
            return _success_response(
                tool,
                {
                    "candidate_id": _external_user_id(candidate_id),
                    "eligible": False,
                    "score_available": False,
                    "score": None,
                    "confidence": "low",
                    "coverage_ratio": 0.0,
                    "user_to_candidate_score": None,
                    "candidate_to_user_score": None,
                    "dimension_scores": {},
                    "hard_conflicts": eligibility["data"]["failed_gates"],
                    "unknown_dimensions": [],
                    "limitations": LIMITATIONS,
                },
            )

        assessment = _compatibility_assessment(user_id, candidate_id)
        if assessment is not None:
            assessment_data = _validated_assessment_data(assessment, candidate_id)
            if assessment_data is None:
                return _error_response(
                    tool,
                    "INVALID_COMPATIBILITY_ASSESSMENT",
                    "Compatibility assessment fixture is malformed.",
                )
            return _success_response(tool, assessment_data)

        user_to_candidate = _evaluate_directional_preferences(user_id, candidate_id)
        candidate_to_user = _evaluate_directional_preferences(candidate_id, user_id)
        hard_conflicts = sorted(
            set(user_to_candidate["hard_conflicts"] + candidate_to_user["hard_conflicts"])
        )
        coverage_ratio = round(
            (user_to_candidate["coverage_ratio"] + candidate_to_user["coverage_ratio"]) / 2,
            2,
        )
        score_available = (
            user_to_candidate["score_available"]
            and candidate_to_user["score_available"]
            and not hard_conflicts
        )
        score = _mutual_score(user_to_candidate["score"], candidate_to_user["score"]) if score_available else None
        unknown_dimensions = sorted(
            set(user_to_candidate["unknown_dimensions"] + candidate_to_user["unknown_dimensions"])
        )
        dimension_scores: dict[str, int] = {}
        for dimension in DIMENSIONS:
            results = [
                user_to_candidate["dimensions"].get(dimension, {}).get("result"),
                candidate_to_user["dimensions"].get(dimension, {}).get("result"),
            ]
            if "hard_conflict" in results:
                dimension_scores[dimension] = 0
            elif "trade_off" in results:
                dimension_scores[dimension] = 40
            elif all(result == "aligned" for result in results):
                dimension_scores[dimension] = 100

        if not score_available:
            return _success_response(
                tool,
                {
                    "candidate_id": _external_user_id(candidate_id),
                    "eligible": True,
                    "score_available": False,
                    "score": None,
                    "confidence": _confidence_from_coverage(coverage_ratio),
                    "coverage_ratio": coverage_ratio,
                    "user_to_candidate_score": user_to_candidate["score"],
                    "candidate_to_user_score": candidate_to_user["score"],
                    "dimension_scores": dimension_scores,
                    "hard_conflicts": hard_conflicts,
                    "unknown_dimensions": unknown_dimensions,
                    "recommended_action": "ask_human_or_continue_without_score",
                    "limitations": LIMITATIONS,
                },
                status="insufficient_data",
            )

        return _success_response(
            tool,
            {
                "candidate_id": _external_user_id(candidate_id),
                "eligible": True,
                "score_available": True,
                "score": score,
                "confidence": _confidence_from_coverage(coverage_ratio),
                "coverage_ratio": coverage_ratio,
                "user_to_candidate_score": user_to_candidate["score"],
                "candidate_to_user_score": candidate_to_user["score"],
                "dimension_scores": dimension_scores,
                "hard_conflicts": hard_conflicts,
                "unknown_dimensions": unknown_dimensions,
                "limitations": LIMITATIONS,
            },
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def get_compatibility_breakdown(user_id: str, candidate_id: str) -> ToolResult:
    """
    Name:
        get_compatibility_breakdown
    Purpose:
        Return structured explanation for compatibility without marketing language.
    When to use:
        Matching Agent needs evidence, conflicts, unknowns, and verification questions.
    When not to use:
        Do not expose raw candidate preferences or add claims beyond evidence.
    Args:
        user_id: Requesting user ID.
        candidate_id: Candidate ID.
    Returns:
        ToolResult with score summary, per-dimension breakdown, strengths, conflicts, unknowns, and limitations.
    Error semantics:
        Validation errors are structured and never crash.
    Side effects:
        None.
    Safety notes:
        Candidate preference evidence is sanitized to direction-level conclusions.
    Example:
        get_compatibility_breakdown("USR001", "USR002")
    """
    tool = "get_compatibility_breakdown"
    try:
        score_result = calculate_compatibility(user_id, candidate_id)
        if score_result["status"] not in {"success", "insufficient_data"}:
            score_result["tool"] = tool
            return score_result
        score_data = score_result["data"]
        if isinstance(score_data.get("breakdown"), dict):
            return _success_response(
                tool,
                {
                    "candidate_id": score_data["candidate_id"],
                    "eligible": score_data["eligible"],
                    "score": score_data.get("score"),
                    "confidence": score_data.get("confidence"),
                    "breakdown": score_data["breakdown"],
                    "strengths": score_data.get("strengths", []),
                    "potential_conflicts": score_data.get("potential_conflicts", []),
                    "unknowns": [],
                    "questions_to_verify": [],
                    "limitations": score_data.get("limitations", LIMITATIONS),
                },
                status=score_result["status"],
            )
        user_to_candidate = _evaluate_directional_preferences(user_id, candidate_id)
        candidate_to_user = _evaluate_directional_preferences(candidate_id, user_id)
        breakdown: dict[str, Any] = {}
        strengths: list[dict[str, Any]] = []
        conflicts: list[dict[str, Any]] = []
        unknowns: list[dict[str, Any]] = []
        questions: list[str] = []

        for dimension in DIMENSIONS:
            left = user_to_candidate["dimensions"].get(dimension, {"result": "unknown", "evidence": [], "missing_fields": [dimension]})
            right = candidate_to_user["dimensions"].get(dimension, {"result": "unknown", "evidence": [], "missing_fields": [dimension]})
            results = [left["result"], right["result"]]
            if "hard_conflict" in results:
                mutual = "hard_conflict"
            elif "unknown" in results:
                mutual = "unknown"
            elif "trade_off" in results:
                mutual = "trade_off"
            else:
                mutual = "aligned"
            missing = sorted(set(left.get("missing_fields", []) + right.get("missing_fields", [])))
            breakdown[dimension] = {
                "user_to_candidate": {
                    "result": left["result"],
                    "evidence": left.get("evidence", []),
                },
                "candidate_to_user": {
                    "result": right["result"],
                    "evidence": [
                        {
                            "direction": "candidate_to_user",
                            "dimension": dimension,
                            "result": right["result"],
                        }
                    ]
                    if right["result"] != "unknown"
                    else [],
                },
                "mutual_result": mutual,
                "missing_fields": missing,
            }
            if mutual == "aligned":
                strengths.append({"dimension": dimension, "reason": f"{dimension} is aligned.", "evidence": left.get("evidence", [])})
            elif mutual in {"trade_off", "hard_conflict"}:
                conflicts.append({"dimension": dimension, "result": mutual, "evidence": left.get("evidence", [])})
            else:
                unknowns.append({"dimension": dimension, "missing_fields": missing})
                questions.append(f"Clarify {dimension} before relying on this dimension.")

        data = score_data
        return _success_response(
            tool,
            {
                "candidate_id": candidate_id,
                "eligible": data["eligible"],
                "score": data.get("score"),
                "confidence": data.get("confidence"),
                "breakdown": breakdown,
                "strengths": strengths,
                "potential_conflicts": conflicts,
                "unknowns": unknowns,
                "questions_to_verify": questions,
                "limitations": LIMITATIONS,
            },
            status=score_result["status"],
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def get_shared_interests(user_a_id: str, user_b_id: str) -> ToolResult:
    """
    Name:
        get_shared_interests
    Purpose:
        Find shared interests for date planning.
    When to use:
        Date Planning Agent needs consented common interests.
    When not to use:
        Do not invent interests or bypass pair eligibility.
    Args:
        user_a_id: First user ID.
        user_b_id: Second user ID.
    Returns:
        ToolResult with shared_interests, count, completeness, and evidence.
    Error semantics:
        Invalid users and missing profiles return errors; no overlap returns warning.
    Side effects:
        None.
    Safety notes:
        Requires interests consent in both directions.
    Example:
        get_shared_interests("USR001", "USR002")
    """
    tool = "get_shared_interests"
    try:
        if not _validate_user_id(user_a_id) or not _validate_user_id(user_b_id):
            return _error_response(tool, "INVALID_USER_ID", "User IDs must be non-empty strings.")
        if _same_user_id(user_a_id, user_b_id):
            return _error_response(tool, "SELF_MATCH_NOT_ALLOWED", "Self pair is not allowed.")
        user_a = _profile_by_id(user_a_id)
        user_b = _profile_by_id(user_b_id)
        if user_a is None or user_b is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "Profile was not found.")
        eligibility = check_matching_eligibility(user_a_id, user_b_id)
        if eligibility["status"] != "success" or not eligibility["data"]["eligible"]:
            return _error_response(tool, "PROFILE_ACCESS_DENIED", "Pair is not eligible for date planning.", status="denied")
        if not (_field_allowed(user_a_id, user_b_id, "interests") and _field_allowed(user_b_id, user_a_id, "interests")):
            return _error_response(tool, "PERMISSION_DENIED", "Interests are not consented both ways.", status="denied")
        shared = _overlap(user_a.get("interests", []), user_b.get("interests", []))
        data = {
            "user_a_id": _external_user_id(user_a_id),
            "user_b_id": _external_user_id(user_b_id),
            "shared_interests": shared,
            "shared_interest_count": len(shared),
            "data_complete": bool(user_a.get("interests")) and bool(user_b.get("interests")),
            "evidence": [{"field": "interests", "source": "consented_profile_data"}],
        }
        if not shared:
            data["recommended_action"] = "use_neutral_activity"
            return _success_response(tool, data, status="warning")
        return _success_response(tool, data)
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def search_date_activities(
    city: str,
    interests: list[str] | None = None,
    max_budget: int | float | None = None,
    indoor: bool | None = None,
    max_results: int = 5,
) -> ToolResult:
    """
    Name:
        search_date_activities
    Purpose:
        Search deterministic local mock date activities.
    When to use:
        Date Planning Agent needs activity options.
    When not to use:
        Do not book, reserve, message, or increase budget automatically.
    Args:
        city: Activity city.
        interests: Optional interest tags.
        max_budget: Optional maximum estimated pair budget.
        indoor: Optional indoor filter.
        max_results: Maximum activities, 1 to 20.
    Returns:
        ToolResult with the normalized query and matching activity records.
    Error semantics:
        Invalid filters return structured errors; empty results return warning.
    Side effects:
        None.
    Safety notes:
        Uses only mock activity data.
    Example:
        search_date_activities("Ha Noi", ["coffee", "art"], 500000)
    """
    tool = "search_date_activities"
    try:
        if not _is_non_empty_string(city):
            return _error_response(tool, "INVALID_CITY", "city must be a non-empty string.")
        if interests is not None and (
            not isinstance(interests, list) or not all(_is_non_empty_string(item) for item in interests)
        ):
            return _error_response(tool, "INVALID_INTERESTS", "interests must be a list of strings.")
        if max_budget is not None and (
            not isinstance(max_budget, (int, float)) or isinstance(max_budget, bool) or max_budget < 0
        ):
            return _error_response(tool, "INVALID_BUDGET", "max_budget must be a non-negative number.")
        if indoor is not None and not isinstance(indoor, bool):
            return _error_response(tool, "INVALID_INDOOR", "indoor must be a boolean.")
        if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
            return _error_response(tool, "INVALID_MAX_RESULTS", "max_results must be from 1 to 20.")

        normalized_city = _canonical_city(city)
        interest_filter = interests or []
        rows: list[dict[str, Any]] = []
        for activity in _load_date_activities():
            if activity.get("active") is not True:
                continue
            activity_city = _canonical_city(str(activity.get("city", "")))
            if activity_city.casefold() != normalized_city.casefold():
                continue
            if indoor is not None and activity.get("indoor") is not indoor:
                continue
            estimated_cost = _estimated_activity_cost(activity, 2)
            if max_budget is not None and estimated_cost > int(max_budget):
                continue
            matched = _overlap(interest_filter, activity.get("interests", []))
            if interest_filter and not matched:
                continue
            rows.append(
                {
                    "activity_id": activity["activity_id"],
                    "name": activity["name"],
                    "city": activity_city,
                    "interests": list(activity.get("interests", [])),
                    "estimated_cost": estimated_cost,
                    "duration_minutes": activity.get("duration_minutes"),
                    "indoor": activity["indoor"],
                }
            )
        rows.sort(key=lambda item: item["activity_id"])
        rows = rows[:max_results]
        data = {
            "query": {
                "city": normalized_city,
                "interests": interest_filter,
                "max_budget": max_budget,
                "indoor": indoor,
                "max_results": max_results,
            },
            "total_found": len(rows),
            "activities": rows,
        }
        if not rows:
            data["recommended_action"] = "relax_optional_date_filter"
            return _success_response(tool, data, status="warning")
        return _success_response(tool, data)
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def estimate_date_cost(
    activity_id: str,
    people: int = 2,
    extras: list[str] | None = None,
) -> ToolResult:
    """
    Name:
        estimate_date_cost
    Purpose:
        Estimate deterministic date activity cost.
    When to use:
        Date Planning Agent needs cost estimates for a selected mock activity.
    When not to use:
        Do not perform payment, reservation, or booking.
    Args:
        activity_id: Mock activity ID.
        people: Number of people, 1 to 10.
        extras: Optional extras from the mock extras table.
    Returns:
        ToolResult with base cost, extras cost, total cost, currency, and cost breakdown.
    Error semantics:
        Invalid activity, people, and extras return structured errors.
    Side effects:
        None.
    Safety notes:
        Cost is an estimate only and uses integer VND values.
    Example:
        estimate_date_cost("A01", 2, ["drinks"])
    """
    tool = "estimate_date_cost"
    try:
        if not _is_non_empty_string(activity_id):
            return _error_response(tool, "INVALID_ACTIVITY_ID", "activity_id must be a non-empty string.")
        if not isinstance(people, int) or people < 1 or people > 10:
            return _error_response(tool, "INVALID_PEOPLE", "people must be from 1 to 10.")
        if extras is not None and (
            not isinstance(extras, list) or not all(_is_non_empty_string(item) for item in extras)
        ):
            return _error_response(tool, "INVALID_EXTRAS", "extras must be a list of strings.")
        activity = _activity_by_id(activity_id)
        if activity is None:
            return _error_response(tool, "ACTIVITY_NOT_FOUND", "Activity was not found.")
        if activity.get("active") is not True:
            return _error_response(tool, "ACTIVITY_INACTIVE", "Activity is inactive.")

        selected_extras = extras or []
        invalid = [item for item in selected_extras if item not in EXTRA_PRICES]
        if invalid:
            return _error_response(tool, "INVALID_EXTRAS", "One or more extras are invalid.", {"extras": invalid})
        base_total = _estimated_activity_cost(activity, people)
        extras_breakdown = [
            {"extra": item, "cost": EXTRA_PRICES[item]} for item in selected_extras
        ]
        extras_cost = sum(item["cost"] for item in extras_breakdown)
        cost_breakdown = [
            {
                "item": "base",
                "cost_unit": activity["cost_unit"],
                "cost": base_total,
            },
            *extras_breakdown,
        ]
        return _success_response(
            tool,
            {
                "activity_id": activity_id,
                "activity_name": activity["name"],
                "people": people,
                "base_cost": base_total,
                "extras_cost": extras_cost,
                "total_estimated_cost": base_total + extras_cost,
                "currency": "VND",
                "within_budget": None,
                "cost_breakdown": cost_breakdown,
            },
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


PROFILE_TOOLS = {
    "get_match_profile": get_match_profile,
    "check_profile_completeness": check_profile_completeness,
    "check_matching_eligibility": check_matching_eligibility,
}

MATCHING_TOOLS = {
    "search_candidates": search_candidates,
    "calculate_compatibility": calculate_compatibility,
    "get_compatibility_breakdown": get_compatibility_breakdown,
}

DATE_TOOLS = {
    "get_shared_interests": get_shared_interests,
    "search_date_activities": search_date_activities,
    "estimate_date_cost": estimate_date_cost,
}

AVAILABLE_TOOLS = {
    **PROFILE_TOOLS,
    **MATCHING_TOOLS,
    **DATE_TOOLS,
}

# Compatibility exports for Role 4 sample code in main. They are intentionally
# not registered in AVAILABLE_TOOLS.
from .date_tools import get_weather, search_flights  # noqa: E402


def extract_profile(user_query: str) -> dict[str, Any]:
    return {"raw_query": user_query, "interests": [], "preferences": []}


def find_candidate_matches(profile: dict[str, Any]) -> list[dict[str, Any]]:
    return []


def suggest_date_plan(profile: dict[str, Any], candidate: dict[str, Any]) -> dict[str, str]:
    return {
        "idea": "Cafe yen tinh de tro chuyen va tim hieu nhau",
        "location": "Quan cafe trung tam",
        "safety_note": "Gap o noi cong cong va tu bao quan thong tin ca nhan.",
    }
