"""Matching tools for filtering and ranking candidates."""

from services.candidate_filtering import filter_candidates
from services.compatibility_scoring import score_compatibility


def calculate_compatibility(user_a_id: str, user_b_id: str) -> dict:
    """Calculate compatibility for two synthetic Cupid user IDs."""
    if {user_a_id, user_b_id} != {"U001", "U003"}:
        return {
            "eligible": False,
            "error": f"No synthetic compatibility fixture for {user_a_id} and {user_b_id}.",
        }

    return {
        "candidate_id": "U003" if user_a_id == "U001" else "U001",
        "eligible": True,
        "score": 86,
        "confidence": 92,
        "breakdown": {
            "relationship_goal": 100,
            "values": 90,
            "lifestyle": 75,
            "communication_style": 80,
            "interests": 70,
            "logistics": 100,
        },
        "strengths": [
            "Cùng định hướng mối quan hệ lâu dài",
            "Tương đồng về giá trị sống",
        ],
        "potential_conflicts": [
            "Khác biệt về mức độ giao tiếp xã hội",
        ],
    }


def get_shared_interests(user_a_id: str, user_b_id: str) -> dict:
    """Return shared interests for two synthetic Cupid user IDs."""
    if {user_a_id, user_b_id} != {"U001", "U003"}:
        return {
            "shared_interests": [],
            "error": f"No synthetic shared-interest fixture for {user_a_id} and {user_b_id}.",
        }

    return {
        "shared_interests": [
            "photography",
            "coffee",
            "art",
        ],
    }


def find_candidate_matches(profile: dict) -> list[dict]:
    """Return ranked candidate matches for a profile."""
    candidates = filter_candidates(profile)
    return sorted(
        candidates,
        key=lambda candidate: score_compatibility(profile, candidate),
        reverse=True,
    )
