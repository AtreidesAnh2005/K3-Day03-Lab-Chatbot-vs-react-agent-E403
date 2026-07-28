"""
Deterministic Cupid Agent tool registry.

This module is intentionally self-contained and read-only. It uses fictional
mock data from data/ and does not call external APIs, LLMs, environment
variables, or network resources.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ToolResult = dict[str, Any]

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

VALID_STATUSES = {"success", "warning", "error", "insufficient_data", "denied"}
VALID_PRIORITIES = {"required", "preferred", "negotiable", "uncertain"}
VALID_CONFIDENCES = {"high", "medium", "low"}
VALID_RELATIONSHIP_GOALS = {"serious", "casual", "friendship", "unsure"}
VALID_COMMUNICATION_STYLES = {"direct", "gentle", "reflective", "expressive"}

DIMENSIONS = [
    "relationship_goal",
    "values",
    "lifestyle",
    "communication_style",
    "future_plans",
    "interests",
    "availability",
]

DIMENSION_WEIGHTS = {
    "relationship_goal": 0.25,
    "values": 0.25,
    "lifestyle": 0.15,
    "communication_style": 0.15,
    "future_plans": 0.10,
    "interests": 0.05,
    "availability": 0.05,
}

DIMENSION_SCORES = {
    "aligned": 1.0,
    "possible_conflict": 0.4,
}

FIELD_GROUPS = {
    "basic_profile": {"display_name", "age", "city"},
    "relationship_goal": {"relationship_goal"},
    "interests": {"interests"},
    "values": {"values"},
    "lifestyle": {"lifestyle"},
    "communication_style": {"communication_style"},
    "future_plans": {"future_plans"},
    "availability": {"availability"},
}


def _success_response(
    tool: str,
    data: Any,
    status: str = "success",
    metadata: dict[str, Any] | None = None,
) -> ToolResult:
    return {
        "status": status,
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
    if status not in VALID_STATUSES:
        status = "error"
    return {
        "status": status,
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
    path = DATA_DIR / filename
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _load_profiles() -> list[dict[str, Any]]:
    data = _load_json_data("cupid_profiles.json")
    if not isinstance(data, list):
        raise ValueError("Profile data must be a list.")
    return data


def _load_preferences() -> list[dict[str, Any]]:
    data = _load_json_data("cupid_preferences.json")
    if not isinstance(data, list):
        raise ValueError("Preference data must be a list.")
    return data


def _load_consents() -> list[dict[str, Any]]:
    data = _load_json_data("cupid_consents.json")
    if not isinstance(data, list):
        raise ValueError("Consent data must be a list.")
    return data


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_user_id(value: Any) -> bool:
    return _is_non_empty_string(value)


def _profile_by_id(user_id: str) -> dict[str, Any] | None:
    return next(
        (profile for profile in _load_profiles() if profile.get("user_id") == user_id),
        None,
    )


def _preference_profile_by_user_id(user_id: str) -> dict[str, Any] | None:
    return next(
        (
            preference_profile
            for preference_profile in _load_preferences()
            if preference_profile.get("user_id") == user_id
        ),
        None,
    )


def _consent_record(owner_id: str, viewer_id: str) -> dict[str, Any] | None:
    return next(
        (
            consent
            for consent in _load_consents()
            if consent.get("owner_id") == owner_id and consent.get("viewer_id") == viewer_id
        ),
        None,
    )


def _get_preferences(user_id: str) -> list[dict[str, Any]] | None:
    preference_profile = _preference_profile_by_user_id(user_id)
    if not preference_profile:
        return None
    preferences = preference_profile.get("preferences")
    if not isinstance(preferences, list):
        raise ValueError("Preference profile has invalid schema.")
    return preferences


def _preference_for_field(
    preferences: list[dict[str, Any]],
    field: str,
    priority: str | None = None,
) -> dict[str, Any] | None:
    for preference in preferences:
        if preference.get("field") != field:
            continue
        if priority and preference.get("priority") != priority:
            continue
        return preference
    return None


def _preferences_for_prefix(
    preferences: list[dict[str, Any]],
    prefix: str,
    priority: str | None = None,
) -> list[dict[str, Any]]:
    return [
        preference
        for preference in preferences
        if isinstance(preference.get("field"), str)
        and (
            preference["field"] == prefix
            or preference["field"].startswith(f"{prefix}.")
        )
        and (priority is None or preference.get("priority") == priority)
    ]


def _validated_candidate_ids(
    tool: str,
    user_id: str,
    candidate_ids: Any,
) -> ToolResult | list[str]:
    if not isinstance(candidate_ids, list) or not candidate_ids:
        return _error_response(
            tool,
            "INVALID_CANDIDATE_IDS",
            "candidate_ids must be a non-empty list of user IDs.",
        )
    if not all(_validate_user_id(candidate_id) for candidate_id in candidate_ids):
        return _error_response(
            tool,
            "INVALID_CANDIDATE_IDS",
            "Every candidate ID must be a non-empty string.",
        )
    if len(set(candidate_ids)) != len(candidate_ids):
        return _error_response(
            tool,
            "DUPLICATE_CANDIDATE_ID",
            "candidate_ids must not contain duplicates.",
        )
    if user_id in candidate_ids:
        return _error_response(
            tool,
            "SELF_ANALYSIS_NOT_ALLOWED",
            "A user cannot analyze themselves as a candidate.",
        )
    missing = [
        candidate_id for candidate_id in candidate_ids if _profile_by_id(candidate_id) is None
    ]
    if missing:
        return _error_response(
            tool,
            "CANDIDATE_NOT_FOUND",
            "One or more candidate profiles were not found.",
            {"candidate_ids": missing},
        )
    return candidate_ids


def _is_blocked(user_profile: dict[str, Any], candidate_profile: dict[str, Any]) -> bool:
    user_id = user_profile.get("user_id")
    candidate_id = candidate_profile.get("user_id")
    return (
        candidate_id in user_profile.get("blocked_user_ids", [])
        or user_id in candidate_profile.get("blocked_user_ids", [])
    )


def _active_consent(owner_id: str, viewer_id: str) -> dict[str, Any] | None:
    consent = _consent_record(owner_id, viewer_id)
    if consent and consent.get("consent_active") is True:
        return consent
    return None


def _field_allowed(consent: dict[str, Any], field_group: str) -> bool:
    return field_group in consent.get("allowed_fields", [])


def _public_candidate_view(
    candidate_profile: dict[str, Any],
    consent: dict[str, Any],
) -> dict[str, Any]:
    view: dict[str, Any] = {"user_id": candidate_profile["user_id"]}
    allowed_fields = consent.get("allowed_fields", [])
    if _field_allowed(consent, "basic_profile"):
        for field in sorted(FIELD_GROUPS["basic_profile"]):
            if field in candidate_profile:
                view[field] = candidate_profile[field]
    if _field_allowed(consent, "relationship_goal"):
        view["relationship_goal"] = candidate_profile.get("relationship_goal")
    view["available_fields"] = allowed_fields
    return view


def _overlap(left: Any, right: Any) -> list[Any]:
    if not isinstance(left, list) or not isinstance(right, list):
        return []
    right_set = set(right)
    return sorted(item for item in left if item in right_set)


def _confidence_from_coverage(coverage_ratio: float) -> str:
    if coverage_ratio >= 0.80:
        return "high"
    if coverage_ratio >= 0.60:
        return "medium"
    return "low"


def _candidate_value(candidate: dict[str, Any], field: str) -> Any:
    current: Any = candidate
    for part in field.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _reject_candidate(
    rejected: list[dict[str, Any]],
    candidate_id: str,
    reason_code: str,
    field: str,
    user_requirement: Any,
    candidate_value: Any,
) -> None:
    rejected.append(
        {
            "candidate_id": candidate_id,
            "reason_codes": [reason_code],
            "evidence": [
                {
                    "field": field,
                    "user_requirement": user_requirement,
                    "candidate_value": candidate_value,
                }
            ],
        }
    )


def _hard_constraint_result(user_id: str, candidate_ids: list[str]) -> dict[str, Any]:
    user_profile = _profile_by_id(user_id)
    preferences = _get_preferences(user_id)
    if user_profile is None or preferences is None:
        raise ValueError("User profile and preferences must exist before filtering.")

    eligible: list[str] = []
    rejected: list[dict[str, Any]] = []

    required_preferences = [
        preference
        for preference in preferences
        if preference.get("priority") == "required"
        and preference.get("source") == "user_confirmed"
        and preference.get("field") != "dealbreakers"
    ]
    dealbreakers = _preference_for_field(preferences, "dealbreakers", "required")
    confirmed_dealbreakers = (
        dealbreakers.get("value", [])
        if dealbreakers and dealbreakers.get("source") == "user_confirmed"
        else []
    )

    for candidate_id in candidate_ids:
        candidate = _profile_by_id(candidate_id)
        if candidate is None:
            continue

        if candidate.get("matching_enabled") is not True:
            _reject_candidate(
                rejected,
                candidate_id,
                "MATCHING_DISABLED",
                "matching_enabled",
                True,
                candidate.get("matching_enabled"),
            )
            continue
        if candidate.get("consent_to_matching") is not True:
            _reject_candidate(
                rejected,
                candidate_id,
                "MATCHING_CONSENT_MISSING",
                "consent_to_matching",
                True,
                candidate.get("consent_to_matching"),
            )
            continue
        if _is_blocked(user_profile, candidate):
            _reject_candidate(
                rejected,
                candidate_id,
                "BLOCKED_USER",
                "blocked_user_ids",
                "not_blocked",
                "blocked",
            )
            continue
        consent = _active_consent(candidate_id, user_id)
        if consent is None:
            _reject_candidate(
                rejected,
                candidate_id,
                "CONSENT_NOT_ACTIVE",
                "consent_active",
                True,
                False,
            )
            continue

        reason_codes: list[str] = []
        evidence: list[dict[str, Any]] = []

        for preference in required_preferences:
            field = preference.get("field")
            required_value = preference.get("value")
            if field == "age_range":
                age = candidate.get("age")
                min_age = required_value.get("min") if isinstance(required_value, dict) else None
                max_age = required_value.get("max") if isinstance(required_value, dict) else None
                if not isinstance(age, int) or age < min_age or age > max_age:
                    reason_codes.append("AGE_RANGE_MISMATCH")
                    evidence.append(
                        {
                            "field": "age",
                            "user_requirement": required_value,
                            "candidate_value": age,
                        }
                    )
            elif field == "relationship_goal":
                value = candidate.get("relationship_goal")
                if value != required_value:
                    reason_codes.append("RELATIONSHIP_GOAL_MISMATCH")
                    evidence.append(
                        {
                            "field": field,
                            "user_requirement": required_value,
                            "candidate_value": value,
                        }
                    )
            elif field == "city":
                value = candidate.get("city")
                if value != required_value:
                    reason_codes.append("CITY_MISMATCH")
                    evidence.append(
                        {
                            "field": field,
                            "user_requirement": required_value,
                            "candidate_value": value,
                        }
                    )
            elif field == "lifestyle.smoking":
                value = _candidate_value(candidate, field)
                if value != required_value:
                    reason_codes.append("SMOKING_MISMATCH")
                    evidence.append(
                        {
                            "field": field,
                            "user_requirement": required_value,
                            "candidate_value": value,
                        }
                    )

        for dealbreaker in confirmed_dealbreakers:
            if not isinstance(dealbreaker, dict):
                continue
            field = dealbreaker.get("field")
            disallowed_value = dealbreaker.get("disallowed_value")
            value = _candidate_value(candidate, field) if isinstance(field, str) else None
            if value == disallowed_value:
                reason_codes.append("DEALBREAKER_MATCH")
                evidence.append(
                    {
                        "field": field,
                        "user_requirement": f"not {disallowed_value}",
                        "candidate_value": value,
                    }
                )

        if reason_codes:
            rejected.append(
                {
                    "candidate_id": candidate_id,
                    "reason_codes": reason_codes,
                    "evidence": evidence,
                }
            )
        else:
            eligible.append(candidate_id)

    return {
        "eligible_candidates": eligible,
        "rejected_candidates": rejected,
    }


def _dimension_comparison(
    user_profile: dict[str, Any],
    candidate_profile: dict[str, Any],
    consent: dict[str, Any],
) -> dict[str, Any]:
    dimensions: dict[str, Any] = {}

    for dimension in DIMENSIONS:
        if not _field_allowed(consent, dimension):
            dimensions[dimension] = {
                "result": "unknown",
                "evidence": [],
                "missing_fields": [dimension],
            }
            continue

        user_value = user_profile.get(dimension)
        candidate_value = candidate_profile.get(dimension)
        if user_value in (None, "", [], {}) or candidate_value in (None, "", [], {}):
            dimensions[dimension] = {
                "result": "unknown",
                "evidence": [],
                "missing_fields": [
                    field
                    for field, value in (
                        (f"user.{dimension}", user_value),
                        (f"candidate.{dimension}", candidate_value),
                    )
                    if value in (None, "", [], {})
                ],
            }
            continue

        evidence = [
            {
                "field": dimension,
                "user_value": user_value,
                "candidate_value": candidate_value,
            }
        ]

        if dimension in {"relationship_goal", "communication_style"}:
            result = "aligned" if user_value == candidate_value else "possible_conflict"
        elif dimension in {"values", "interests", "availability"}:
            result = "aligned" if _overlap(user_value, candidate_value) else "possible_conflict"
            evidence[0]["overlap"] = _overlap(user_value, candidate_value)
        elif dimension == "lifestyle":
            smoking_match = user_value.get("smoking") == candidate_value.get("smoking")
            drinking_match = user_value.get("drinking") == candidate_value.get("drinking")
            exercise_match = user_value.get("exercise") == candidate_value.get("exercise")
            result = (
                "aligned"
                if smoking_match and (drinking_match or exercise_match)
                else "possible_conflict"
            )
        elif dimension == "future_plans":
            preferred_city_match = user_value.get("preferred_city") == candidate_value.get(
                "preferred_city"
            )
            children_match = user_value.get("wants_children") == candidate_value.get(
                "wants_children"
            )
            result = (
                "aligned"
                if preferred_city_match and children_match
                else "possible_conflict"
            )
        else:
            result = "unknown"

        dimensions[dimension] = {
            "result": result,
            "evidence": evidence,
            "missing_fields": [],
        }

    return dimensions


def _score_from_dimensions(dimensions: dict[str, Any]) -> dict[str, Any]:
    available_weight = 0.0
    weighted_score = 0.0
    breakdown: dict[str, Any] = {}
    missing_dimensions: list[str] = []

    for dimension, weight in DIMENSION_WEIGHTS.items():
        result = dimensions[dimension]["result"]
        if result == "unknown":
            missing_dimensions.append(dimension)
            breakdown[dimension] = {
                "result": result,
                "weight": weight,
                "included": False,
                "score": None,
            }
            continue

        dimension_score = DIMENSION_SCORES[result]
        available_weight += weight
        weighted_score += weight * dimension_score
        breakdown[dimension] = {
            "result": result,
            "weight": weight,
            "included": True,
            "score": dimension_score,
        }

    coverage_ratio = round(available_weight / sum(DIMENSION_WEIGHTS.values()), 2)
    confidence = _confidence_from_coverage(coverage_ratio)
    compatibility_score = (
        int(round((weighted_score / available_weight) * 100))
        if available_weight
        else None
    )
    return {
        "score_available": coverage_ratio >= 0.60,
        "compatibility_score": compatibility_score,
        "coverage_ratio": coverage_ratio,
        "confidence": confidence,
        "breakdown": breakdown,
        "missing_dimensions": missing_dimensions,
    }


def get_consent_scope(requester_id: str, profile_id: str) -> ToolResult:
    """
    Name:
        get_consent_scope

    Purpose:
        Check which declared profile fields a requester may use.

    When to use:
        Use before reading or analyzing another user's profile.

    When not to use:
        Do not use for self-analysis or to infer permission for unlisted fields.

    Args:
        requester_id: User ID requesting access.
        profile_id: Profile owner ID being inspected.

    Returns:
        A ToolResult envelope with consent_active, allowed_fields, and restricted_fields.

    Error semantics:
        Business errors return status="error" or status="denied" with error.code.

    Side effects:
        None.

    Safety notes:
        Restricted data is never returned, and consent is never expanded.

    Example:
        get_consent_scope("USR001", "USR002")
    """
    tool = "get_consent_scope"
    try:
        if not _validate_user_id(requester_id) or not _validate_user_id(profile_id):
            return _error_response(tool, "INVALID_USER_ID", "User IDs must be non-empty strings.")
        if requester_id == profile_id:
            return _error_response(
                tool,
                "SELF_ANALYSIS_NOT_ALLOWED",
                "A user cannot request consent scope for themselves.",
            )
        if _profile_by_id(requester_id) is None or _profile_by_id(profile_id) is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "Requester or profile was not found.")
        consent = _consent_record(profile_id, requester_id)
        if consent is None:
            return _error_response(tool, "CONSENT_NOT_FOUND", "Consent record was not found.")
        if consent.get("consent_active") is not True:
            return _error_response(
                tool,
                "CONSENT_REVOKED",
                "Consent is not active for this requester.",
                status="denied",
            )
        return _success_response(
            tool,
            {
                "requester_id": requester_id,
                "profile_id": profile_id,
                "consent_active": True,
                "allowed_fields": consent.get("allowed_fields", []),
                "restricted_fields": consent.get("restricted_fields", []),
            },
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def get_preference_profile(user_id: str) -> ToolResult:
    """
    Name:
        get_preference_profile

    Purpose:
        Return the dating criteria a user has confirmed.

    When to use:
        Use when the agent needs the user's declared matching preferences.

    When not to use:
        Do not use to fill missing criteria or infer preferences.

    Args:
        user_id: User ID whose preference profile should be returned.

    Returns:
        A ToolResult envelope with user_id, profile_version, preferences, and last_confirmed_at.

    Error semantics:
        Missing users or preference profiles return structured errors.

    Side effects:
        None.

    Safety notes:
        Preserves priority, confidence, and source exactly as declared.

    Example:
        get_preference_profile("USR001")
    """
    tool = "get_preference_profile"
    try:
        if not _validate_user_id(user_id):
            return _error_response(tool, "INVALID_USER_ID", "user_id must be a non-empty string.")
        if _profile_by_id(user_id) is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "User profile was not found.")
        preference_profile = _preference_profile_by_user_id(user_id)
        if preference_profile is None:
            return _error_response(
                tool,
                "PREFERENCE_PROFILE_NOT_FOUND",
                "Preference profile was not found.",
            )
        return _success_response(tool, preference_profile)
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def detect_preference_gaps(user_id: str) -> ToolResult:
    """
    Name:
        detect_preference_gaps

    Purpose:
        Find missing, uncertain, low-confidence, invalid, or contradictory preferences.

    When to use:
        Use before candidate ranking when the user's criteria may need clarification.

    When not to use:
        Do not use to automatically repair or invent preference values.

    Args:
        user_id: User ID whose preferences should be inspected.

    Returns:
        A ToolResult envelope with needs_clarification, gap_count, and gaps.

    Error semantics:
        Invalid users, missing profiles, and malformed preference schemas return errors.

    Side effects:
        None.

    Safety notes:
        Suggests clarification questions only; it never mutates user preferences.

    Example:
        detect_preference_gaps("USR002")
    """
    tool = "detect_preference_gaps"
    try:
        if not _validate_user_id(user_id):
            return _error_response(tool, "INVALID_USER_ID", "user_id must be a non-empty string.")
        if _profile_by_id(user_id) is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "User profile was not found.")
        preference_profile = _preference_profile_by_user_id(user_id)
        if preference_profile is None:
            return _error_response(
                tool,
                "PREFERENCE_PROFILE_NOT_FOUND",
                "Preference profile was not found.",
            )
        preferences = preference_profile.get("preferences")
        if not isinstance(preferences, list):
            return _error_response(
                tool,
                "INVALID_PREFERENCE_SCHEMA",
                "preferences must be a list.",
            )

        gaps: list[dict[str, Any]] = []
        required_dimensions = [
            "age_range",
            "relationship_goal",
            "values",
            "lifestyle",
            "communication_style",
            "future_plans",
        ]
        for dimension in required_dimensions:
            if not _preferences_for_prefix(preferences, dimension):
                gaps.append(
                    {
                        "field": dimension,
                        "issue": "missing",
                        "severity": "high",
                        "reason": f"No declared preference for {dimension}.",
                        "suggested_question": f"Please clarify your preference for {dimension}.",
                    }
                )
        if not _preferences_for_prefix(preferences, "city") and not _preferences_for_prefix(
            preferences, "max_distance"
        ):
            gaps.append(
                {
                    "field": "city_or_max_distance",
                    "issue": "missing",
                    "severity": "high",
                    "reason": "No location boundary is declared.",
                    "suggested_question": "Which city or maximum distance should be used?",
                }
            )

        seen_required: dict[str, Any] = {}
        for preference in preferences:
            field = preference.get("field")
            priority = preference.get("priority")
            confidence = preference.get("confidence")
            source = preference.get("source")
            value = preference.get("value")

            if priority not in VALID_PRIORITIES:
                gaps.append(
                    {
                        "field": field,
                        "issue": "invalid_enum",
                        "severity": "high",
                        "reason": f"Invalid priority: {priority}.",
                        "suggested_question": "Please choose a valid priority.",
                    }
                )
            if confidence not in VALID_CONFIDENCES:
                gaps.append(
                    {
                        "field": field,
                        "issue": "invalid_enum",
                        "severity": "medium",
                        "reason": f"Invalid confidence: {confidence}.",
                        "suggested_question": "Please choose a valid confidence level.",
                    }
                )
            if field == "relationship_goal" and value not in VALID_RELATIONSHIP_GOALS:
                gaps.append(
                    {
                        "field": field,
                        "issue": "invalid_enum",
                        "severity": "high",
                        "reason": f"Invalid relationship goal: {value}.",
                        "suggested_question": "Which relationship goal should be used?",
                    }
                )
            if field == "communication_style" and value not in VALID_COMMUNICATION_STYLES:
                gaps.append(
                    {
                        "field": field,
                        "issue": "invalid_enum",
                        "severity": "medium",
                        "reason": f"Invalid communication style: {value}.",
                        "suggested_question": "Which communication style should be used?",
                    }
                )
            if priority == "uncertain":
                gaps.append(
                    {
                        "field": field,
                        "issue": "uncertain",
                        "severity": "medium",
                        "reason": "Preference priority is uncertain.",
                        "suggested_question": f"How important is {field} for you?",
                    }
                )
            if priority == "required" and confidence != "high":
                gaps.append(
                    {
                        "field": field,
                        "issue": "low_confidence_required",
                        "severity": "high",
                        "reason": "Required criteria should have high confidence.",
                        "suggested_question": f"Can you confirm that {field} is required?",
                    }
                )
            if priority == "required" and source != "user_confirmed":
                gaps.append(
                    {
                        "field": field,
                        "issue": "unconfirmed_hard_constraint",
                        "severity": "high",
                        "reason": "Hard constraints must come from user_confirmed source.",
                        "suggested_question": f"Can you confirm this hard constraint for {field}?",
                    }
                )
            if priority == "required":
                if field in seen_required and seen_required[field] != value:
                    gaps.append(
                        {
                            "field": field,
                            "issue": "contradiction",
                            "severity": "high",
                            "reason": "Conflicting required values were declared.",
                            "suggested_question": f"Which value should be used for {field}?",
                        }
                    )
                seen_required[field] = value

        age_range = _preference_for_field(preferences, "age_range")
        if age_range and isinstance(age_range.get("value"), dict):
            min_age = age_range["value"].get("min")
            max_age = age_range["value"].get("max")
            if isinstance(min_age, int) and isinstance(max_age, int) and min_age > max_age:
                gaps.append(
                    {
                        "field": "age_range",
                        "issue": "contradiction",
                        "severity": "high",
                        "reason": "Minimum age is greater than maximum age.",
                        "suggested_question": "What age range should be used?",
                    }
                )

        dealbreakers = _preference_for_field(preferences, "dealbreakers")
        if dealbreakers and isinstance(dealbreakers.get("value"), list):
            relationship_goal = _preference_for_field(preferences, "relationship_goal")
            for dealbreaker in dealbreakers["value"]:
                if (
                    isinstance(dealbreaker, dict)
                    and relationship_goal
                    and dealbreaker.get("field") == "relationship_goal"
                    and dealbreaker.get("disallowed_value") == relationship_goal.get("value")
                ):
                    gaps.append(
                        {
                            "field": "relationship_goal",
                            "issue": "contradiction",
                            "severity": "high",
                            "reason": "Required goal is also listed as a deal-breaker.",
                            "suggested_question": "Which relationship goal should be allowed?",
                        }
                    )

        return _success_response(
            tool,
            {
                "needs_clarification": bool(gaps),
                "gap_count": len(gaps),
                "gaps": gaps,
            },
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def search_candidate_profiles(
    user_id: str,
    city: str | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    max_results: int = 10,
) -> ToolResult:
    """
    Name:
        search_candidate_profiles

    Purpose:
        Filter the mock candidate database using visibility, consent, block, city, and age rules.

    When to use:
        Use when the agent needs visible candidate profiles for a requester.

    When not to use:
        Do not use to bypass consent or retrieve restricted profile details.

    Args:
        user_id: Requesting user ID.
        city: Optional city filter.
        min_age: Optional inclusive minimum age.
        max_age: Optional inclusive maximum age.
        max_results: Maximum candidates to return, from 1 to 20.

    Returns:
        A ToolResult envelope with query, total_found, and visible candidate summaries.

    Error semantics:
        Invalid filters and no-result cases return structured errors.

    Side effects:
        None.

    Safety notes:
        Only fields permitted by active consent are returned.

    Example:
        search_candidate_profiles("USR001", city="Ha Noi", min_age=22, max_age=30)
    """
    tool = "search_candidate_profiles"
    try:
        if not _validate_user_id(user_id):
            return _error_response(tool, "INVALID_USER_ID", "user_id must be a non-empty string.")
        user_profile = _profile_by_id(user_id)
        if user_profile is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "User profile was not found.")
        if city is not None and not _is_non_empty_string(city):
            return _error_response(tool, "INVALID_USER_ID", "city must not be empty.")
        if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
            return _error_response(
                tool,
                "INVALID_MAX_RESULTS",
                "max_results must be an integer from 1 to 20.",
            )
        if min_age is not None and (not isinstance(min_age, int) or min_age < 18 or min_age > 100):
            return _error_response(tool, "INVALID_AGE_RANGE", "min_age must be from 18 to 100.")
        if max_age is not None and (not isinstance(max_age, int) or max_age < 18 or max_age > 100):
            return _error_response(tool, "INVALID_AGE_RANGE", "max_age must be from 18 to 100.")
        if min_age is not None and max_age is not None and min_age > max_age:
            return _error_response(tool, "INVALID_AGE_RANGE", "min_age must be <= max_age.")

        candidates: list[dict[str, Any]] = []
        city_filter = city.strip() if isinstance(city, str) else None
        for candidate in sorted(_load_profiles(), key=lambda item: item.get("user_id", "")):
            candidate_id = candidate.get("user_id")
            if candidate_id == user_id:
                continue
            if candidate.get("matching_enabled") is not True:
                continue
            if candidate.get("consent_to_matching") is not True:
                continue
            if _is_blocked(user_profile, candidate):
                continue
            consent = _active_consent(candidate_id, user_id)
            if consent is None:
                continue
            if city_filter and candidate.get("city") != city_filter:
                continue
            if min_age is not None and candidate.get("age", 0) < min_age:
                continue
            if max_age is not None and candidate.get("age", 101) > max_age:
                continue
            candidates.append(_public_candidate_view(candidate, consent))
            if len(candidates) >= max_results:
                break

        if not candidates:
            return _error_response(tool, "NO_CANDIDATES_FOUND", "No eligible candidates were found.")

        return _success_response(
            tool,
            {
                "query": {
                    "user_id": user_id,
                    "city": city_filter,
                    "min_age": min_age,
                    "max_age": max_age,
                    "max_results": max_results,
                },
                "total_found": len(candidates),
                "candidates": candidates,
            },
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def apply_hard_constraints(user_id: str, candidate_ids: list[str]) -> ToolResult:
    """
    Name:
        apply_hard_constraints

    Purpose:
        Reject candidates that violate confirmed required criteria or deal-breakers.

    When to use:
        Use before scoring or ranking candidate compatibility.

    When not to use:
        Do not use preferred, negotiable, or uncertain preferences to reject candidates.

    Args:
        user_id: Requesting user ID.
        candidate_ids: Non-empty list of candidate IDs.

    Returns:
        A ToolResult envelope with eligible_candidates and rejected_candidates.

    Error semantics:
        Invalid users, missing preferences, duplicate IDs, self-analysis, and missing candidates
        return structured errors.

    Side effects:
        None.

    Safety notes:
        Only user_confirmed required criteria and deal-breakers are enforced.

    Example:
        apply_hard_constraints("USR001", ["USR002", "USR003"])
    """
    tool = "apply_hard_constraints"
    try:
        if not _validate_user_id(user_id):
            return _error_response(tool, "INVALID_USER_ID", "user_id must be a non-empty string.")
        if _profile_by_id(user_id) is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "User profile was not found.")
        if _preference_profile_by_user_id(user_id) is None:
            return _error_response(
                tool,
                "PREFERENCE_PROFILE_NOT_FOUND",
                "Preference profile was not found.",
            )
        validated = _validated_candidate_ids(tool, user_id, candidate_ids)
        if isinstance(validated, dict):
            return validated
        return _success_response(tool, _hard_constraint_result(user_id, validated))
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def compare_compatibility_dimensions(user_id: str, candidate_id: str) -> ToolResult:
    """
    Name:
        compare_compatibility_dimensions

    Purpose:
        Compare two profiles dimension by dimension with evidence and without a final verdict.

    When to use:
        Use after consent is available and before calculating a compatibility score.

    When not to use:
        Do not use for self-analysis or to infer missing/sensitive attributes.

    Args:
        user_id: Requesting user ID.
        candidate_id: Candidate profile ID.

    Returns:
        A ToolResult envelope with dimensions and summary_counts.

    Error semantics:
        Invalid users, self-analysis, missing profiles, revoked consent, and insufficient consent
        return structured errors.

    Side effects:
        None.

    Safety notes:
        Only consented candidate fields are used. Missing values produce unknown results.

    Example:
        compare_compatibility_dimensions("USR001", "USR002")
    """
    tool = "compare_compatibility_dimensions"
    try:
        if not _validate_user_id(user_id) or not _validate_user_id(candidate_id):
            return _error_response(tool, "INVALID_USER_ID", "User IDs must be non-empty strings.")
        if user_id == candidate_id:
            return _error_response(
                tool,
                "SELF_ANALYSIS_NOT_ALLOWED",
                "A user cannot compare compatibility with themselves.",
            )
        user_profile = _profile_by_id(user_id)
        candidate_profile = _profile_by_id(candidate_id)
        if user_profile is None or candidate_profile is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "User or candidate profile was not found.")
        consent = _consent_record(candidate_id, user_id)
        if consent is None:
            return _error_response(
                tool,
                "INSUFFICIENT_CONSENT_SCOPE",
                "Consent record was not found for this comparison.",
                status="denied",
            )
        if consent.get("consent_active") is not True:
            return _error_response(
                tool,
                "CONSENT_REVOKED",
                "Consent is not active for this comparison.",
                status="denied",
            )
        if not any(_field_allowed(consent, dimension) for dimension in DIMENSIONS):
            return _error_response(
                tool,
                "INSUFFICIENT_CONSENT_SCOPE",
                "No compatibility dimensions are available in consent scope.",
                status="denied",
            )

        dimensions = _dimension_comparison(user_profile, candidate_profile, consent)
        summary_counts = {"aligned": 0, "possible_conflict": 0, "unknown": 0}
        for dimension in dimensions.values():
            summary_counts[dimension["result"]] += 1
        return _success_response(
            tool,
            {
                "user_id": user_id,
                "candidate_id": candidate_id,
                "dimensions": dimensions,
                "summary_counts": summary_counts,
            },
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def calculate_compatibility_score(user_id: str, candidate_id: str) -> ToolResult:
    """
    Name:
        calculate_compatibility_score

    Purpose:
        Calculate a deterministic compatibility score from dimension comparison results.

    When to use:
        Use when enough consented comparison dimensions may be available for scoring.

    When not to use:
        Do not use score as an absolute prediction of relationship success.

    Args:
        user_id: Requesting user ID.
        candidate_id: Candidate profile ID.

    Returns:
        A ToolResult envelope with score data, or status="insufficient_data" when coverage is low.

    Error semantics:
        Comparison validation errors are propagated as structured errors.

    Side effects:
        None.

    Safety notes:
        Unknown dimensions are excluded from numerator and denominator.

    Example:
        calculate_compatibility_score("USR001", "USR002")
    """
    tool = "calculate_compatibility_score"
    try:
        comparison = compare_compatibility_dimensions(user_id, candidate_id)
        if comparison["status"] != "success":
            comparison["tool"] = tool
            return comparison

        score = _score_from_dimensions(comparison["data"]["dimensions"])
        if not score["score_available"]:
            return _success_response(
                tool,
                {
                    "score_available": False,
                    "coverage_ratio": score["coverage_ratio"],
                    "confidence": score["confidence"],
                    "missing_dimensions": score["missing_dimensions"],
                    "message": "Chua du du lieu de tao diem tuong thich dang tin cay.",
                },
                status="insufficient_data",
            )

        return _success_response(
            tool,
            {
                "score_available": True,
                "compatibility_score": score["compatibility_score"],
                "coverage_ratio": score["coverage_ratio"],
                "confidence": score["confidence"],
                "breakdown": score["breakdown"],
                "disclaimer": (
                    "Diem chi phan anh du lieu da khai bao va khong du doan "
                    "thanh cong cua moi quan he."
                ),
            },
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


def rank_candidate_shortlist(
    user_id: str,
    candidate_ids: list[str],
    shortlist_size: int = 3,
) -> ToolResult:
    """
    Name:
        rank_candidate_shortlist

    Purpose:
        Build a deterministic shortlist with strengths, trade-offs, unknowns, and rejections.

    When to use:
        Use after collecting candidate IDs that should be considered for a user.

    When not to use:
        Do not use to auto-message candidates or declare one candidate absolutely best.

    Args:
        user_id: Requesting user ID.
        candidate_ids: Non-empty list of candidate IDs.
        shortlist_size: Number of candidates to return, from 1 to 20.

    Returns:
        A ToolResult envelope with requested_size, eligible_count, shortlist, and rejected_candidates.

    Error semantics:
        Invalid inputs and no eligible candidates return structured errors.

    Side effects:
        None.

    Safety notes:
        Candidates with insufficient data are labeled as such, not as incompatible.

    Example:
        rank_candidate_shortlist("USR001", ["USR002", "USR005", "USR009"], 3)
    """
    tool = "rank_candidate_shortlist"
    try:
        if not _validate_user_id(user_id):
            return _error_response(tool, "INVALID_USER_ID", "user_id must be a non-empty string.")
        if not isinstance(shortlist_size, int) or shortlist_size < 1 or shortlist_size > 20:
            return _error_response(
                tool,
                "INVALID_SHORTLIST_SIZE",
                "shortlist_size must be an integer from 1 to 20.",
            )
        if _profile_by_id(user_id) is None:
            return _error_response(tool, "PROFILE_NOT_FOUND", "User profile was not found.")
        validated = _validated_candidate_ids(tool, user_id, candidate_ids)
        if isinstance(validated, dict):
            if validated["error"]["code"] == "DUPLICATE_CANDIDATE_ID":
                validated["error"]["code"] = "INVALID_CANDIDATE_IDS"
            return validated

        hard_constraints = apply_hard_constraints(user_id, validated)
        if hard_constraints["status"] != "success":
            hard_constraints["tool"] = tool
            return hard_constraints

        eligible_ids = hard_constraints["data"]["eligible_candidates"]
        if not eligible_ids:
            return _error_response(
                tool,
                "NO_ELIGIBLE_CANDIDATES",
                "No candidates remain after hard constraints.",
                {"rejected_candidates": hard_constraints["data"]["rejected_candidates"]},
            )

        ranked: list[dict[str, Any]] = []
        for candidate_id in eligible_ids:
            candidate_profile = _profile_by_id(candidate_id)
            comparison = compare_compatibility_dimensions(user_id, candidate_id)
            score_result = calculate_compatibility_score(user_id, candidate_id)
            if comparison["status"] != "success":
                continue

            dimensions = comparison["data"]["dimensions"]
            if score_result["status"] == "success":
                score_data = score_result["data"]
            else:
                score_data = score_result["data"]

            strengths = [
                {
                    "dimension": dimension,
                    "reason": f"{dimension} is aligned based on declared data.",
                    "evidence": result["evidence"],
                }
                for dimension, result in dimensions.items()
                if result["result"] == "aligned"
            ]
            tradeoffs = [
                {
                    "dimension": dimension,
                    "reason": f"{dimension} may need discussion.",
                    "evidence": result["evidence"],
                }
                for dimension, result in dimensions.items()
                if result["result"] == "possible_conflict"
            ]
            unknowns = [
                {
                    "dimension": dimension,
                    "missing_fields": result["missing_fields"],
                }
                for dimension, result in dimensions.items()
                if result["result"] == "unknown"
            ]

            ranked.append(
                {
                    "candidate_id": candidate_id,
                    "display_name": candidate_profile.get("display_name") if candidate_profile else None,
                    "score_available": score_data["score_available"],
                    "compatibility_score": score_data.get("compatibility_score"),
                    "confidence": score_data["confidence"],
                    "coverage_ratio": score_data["coverage_ratio"],
                    "strengths": strengths,
                    "tradeoffs": tradeoffs,
                    "unknowns": unknowns,
                }
            )

        ranked.sort(
            key=lambda item: (
                0 if item["score_available"] else 1,
                -(item["compatibility_score"] or -1),
                -item["coverage_ratio"],
                item["candidate_id"],
            )
        )
        shortlist = ranked[:shortlist_size]
        return _success_response(
            tool,
            {
                "requested_size": shortlist_size,
                "eligible_count": len(eligible_ids),
                "shortlist": shortlist,
                "rejected_candidates": hard_constraints["data"]["rejected_candidates"],
            },
        )
    except Exception:
        return _error_response(tool, "INTERNAL_TOOL_ERROR", "Unexpected tool error.")


AVAILABLE_TOOLS = {
    "get_consent_scope": get_consent_scope,
    "get_preference_profile": get_preference_profile,
    "detect_preference_gaps": detect_preference_gaps,
    "search_candidate_profiles": search_candidate_profiles,
    "apply_hard_constraints": apply_hard_constraints,
    "compare_compatibility_dimensions": compare_compatibility_dimensions,
    "calculate_compatibility_score": calculate_compatibility_score,
    "rank_candidate_shortlist": rank_candidate_shortlist,
}
