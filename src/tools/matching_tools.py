"""Matching tools for filtering and ranking candidates."""

from services.candidate_filtering import filter_candidates
from services.compatibility_scoring import score_compatibility


def find_candidate_matches(profile: dict) -> list[dict]:
    """Return ranked candidate matches for a profile."""
    candidates = filter_candidates(profile)
    return sorted(
        candidates,
        key=lambda candidate: score_compatibility(profile, candidate),
        reverse=True,
    )
