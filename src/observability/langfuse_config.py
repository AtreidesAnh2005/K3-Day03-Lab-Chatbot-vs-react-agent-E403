"""Langfuse configuration placeholder."""

import os


def get_langfuse_config() -> dict:
    """Return Langfuse-related settings from environment variables."""
    return {
        "public_key": os.getenv("LANGFUSE_PUBLIC_KEY"),
        "secret_key": os.getenv("LANGFUSE_SECRET_KEY"),
        "host": os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    }
