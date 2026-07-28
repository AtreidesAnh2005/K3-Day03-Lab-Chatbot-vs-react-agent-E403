"""Deterministic privacy and prompt-injection guardrails."""

from __future__ import annotations

import re
from typing import Any

INJECTION_MARKERS = {
    "ignore all previous instructions",
    "ignore previous instructions",
    "developer mode",
    "system prompt",
    "bypass consent",
    "bypass safety",
    "bo qua huong dan",
    "bỏ qua hướng dẫn",
}
PRIVATE_DATA_MARKERS = {
    "phone",
    "phone number",
    "email",
    "address",
    "exact location",
    "matching_consent",
    "số điện thoại",
    "địa chỉ",
    "vị trí chính xác",
    "so dien thoai",
    "dia chi",
}
DISCLOSURE_MARKERS = {
    "give me",
    "show me",
    "tell me",
    "reveal",
    "leak",
    "find their",
    "lấy cho tôi",
    "cho tôi",
    "tiết lộ",
    "cung cấp",
}
MINOR_MARKERS = {
    "minor",
    "underage",
    "under 18",
    "người chưa thành niên",
    "chưa đủ 18",
    "duoi 18",
}

PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.-]?\d){9,10}(?!\d)")
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)


def assess_request(text: str) -> dict[str, Any]:
    """Return a PASS/BLOCK verdict without reading application data."""
    normalized = text.casefold()
    reasons: list[str] = []
    if any(marker in normalized for marker in INJECTION_MARKERS):
        reasons.append("PROMPT_INJECTION")
    if (
        any(marker in normalized for marker in PRIVATE_DATA_MARKERS)
        and any(marker in normalized for marker in DISCLOSURE_MARKERS)
    ):
        reasons.append("PRIVATE_DATA_REQUEST")
    if any(marker in normalized for marker in MINOR_MARKERS):
        reasons.append("MINOR_SAFETY")
    return {"verdict": "BLOCK" if reasons else "PASS", "reasons": reasons}


def redact_sensitive_data(text: str) -> str:
    """Redact phone numbers and email addresses from generated text."""
    redacted = PHONE_PATTERN.sub("[redacted phone]", text)
    return EMAIL_PATTERN.sub("[redacted email]", redacted)
