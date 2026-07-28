"""Candidate filtering service."""


def filter_candidates(profile: dict) -> list[dict]:
    """Return candidate records that pass basic filters."""
    return [
        {
            "id": "candidate_001",
            "name": "Minh Anh",
            "score": 85,
            "interests": ["coffee", "books"],
        },
        {
            "id": "candidate_002",
            "name": "Gia Bao",
            "score": 78,
            "interests": ["music", "travel"],
        },
    ]
