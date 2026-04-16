# GlobalAISourcesFlow — GLOBAL AI SOURCES FLOW
"""OutreachBot metrics — tracks outreach activity."""

from __future__ import annotations


def track(emails_sent: int = 0, failed: int = 0) -> dict:
    """Return a metrics snapshot for this bot run."""
    return {
        "bot": "OutreachBot",
        "emails_sent": emails_sent,
        "failed": failed,
    }
