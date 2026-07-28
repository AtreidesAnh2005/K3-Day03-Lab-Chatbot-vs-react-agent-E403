"""Profile tools for extracting dating preference signals."""


def extract_profile(user_query: str) -> dict:
    """Extract a lightweight profile from user input."""
    return {
        "raw_query": user_query,
        "interests": [],
        "preferences": [],
    }
