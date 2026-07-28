"""Matching tools for filtering and ranking candidates."""

try:
    from ..services.candidate_filtering import filter_candidates
    from ..services.compatibility_scoring import score_compatibility
except ImportError:
    from services.candidate_filtering import filter_candidates
    from services.compatibility_scoring import score_compatibility


def calculate_compatibility(user_a_id: str, user_b_id: str) -> dict:
    """Calculate compatibility through the fixture-backed registry."""
    from . import calculate_compatibility as registry_calculate_compatibility

    result = registry_calculate_compatibility(user_a_id, user_b_id)
    if result.get("status") not in {"success", "insufficient_data"}:
        error = result.get("error") or {}
        return {
            "eligible": False,
            "error": error.get("message", "Compatibility calculation failed."),
        }

    data = result.get("data") or {}
    contract_fields = (
        "candidate_id",
        "eligible",
        "score",
        "confidence",
        "breakdown",
        "strengths",
        "potential_conflicts",
    )
    return {field: data.get(field) for field in contract_fields}


def get_shared_interests(user_a_id: str, user_b_id: str) -> dict:
    """Return consented shared interests through the tool registry."""
    from . import get_shared_interests as registry_get_shared_interests

    result = registry_get_shared_interests(user_a_id, user_b_id)
    if result.get("status") not in {"success", "warning"}:
        error = result.get("error") or {}
        return {
            "shared_interests": [],
            "error": error.get("message", "Shared-interest lookup failed."),
        }
    return {"shared_interests": (result.get("data") or {}).get("shared_interests", [])}


def find_candidate_matches(profile: dict) -> list[dict]:
    """Return ranked candidate matches for a profile."""
    candidates = filter_candidates(profile)
    return sorted(
        candidates,
        key=lambda candidate: score_compatibility(profile, candidate),
        reverse=True,
    )
