"""Privacy guard service."""


def redact_sensitive_data(text: str) -> str:
    """Redact obvious sensitive placeholders from response text."""
    blocked_terms = ["phone", "email", "address"]
    redacted = text
    for term in blocked_terms:
        redacted = redacted.replace(term, "[redacted]")
    return redacted
