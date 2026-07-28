"""Compatibility scoring service."""


def score_compatibility(profile: dict, candidate: dict) -> int:
    """Return a simple compatibility score."""
    return int(candidate.get("score", 0))
