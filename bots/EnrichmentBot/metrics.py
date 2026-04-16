"""EnrichmentBot metrics — tracks lead enrichment activity."""

from __future__ import annotations


def track(leads_enriched: int = 0, avg_score: float = 0.0) -> dict:
    """Return a metrics snapshot for this bot run."""
    return {
        "bot": "EnrichmentBot",
        "leads_enriched": leads_enriched,
        "avg_score": avg_score,
    }
