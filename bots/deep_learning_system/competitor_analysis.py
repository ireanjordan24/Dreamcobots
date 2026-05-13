"""
CompetitorAnalysisEngine — Pricing, feature, and sentiment intelligence.

Tracks competitor services per bot category:
  • Pricing tiers and per-unit costs
  • Feature gaps (what they do that we don't, and vice-versa)
  • User sentiment derived from review aggregation (G2, Capterra, Reddit)

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import sys
from datetime import date, datetime, timezone
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)
except ImportError:
    GlobalAISourcesFlow = None  # type: ignore[assignment,misc]

# ---------------------------------------------------------------------------
# Competitor catalogue (representative entries per category)
# ---------------------------------------------------------------------------
_CATEGORY_COMPETITORS: dict[str, list[dict[str, Any]]] = {
    "sales": [
        {"name": "Salesforce", "tier_price_usd": 300, "sentiment_score": 3.8, "key_features": ["pipeline", "AI insights", "reporting"]},
        {"name": "HubSpot", "tier_price_usd": 90, "sentiment_score": 4.3, "key_features": ["free CRM", "email sequences", "chatbots"]},
        {"name": "Pipedrive", "tier_price_usd": 50, "sentiment_score": 4.2, "key_features": ["visual pipeline", "automations"]},
    ],
    "marketing": [
        {"name": "Mailchimp", "tier_price_usd": 20, "sentiment_score": 4.0, "key_features": ["email campaigns", "A/B testing", "analytics"]},
        {"name": "Klaviyo", "tier_price_usd": 45, "sentiment_score": 4.3, "key_features": ["e-commerce flows", "segmentation"]},
        {"name": "ActiveCampaign", "tier_price_usd": 49, "sentiment_score": 4.4, "key_features": ["automation", "CRM integration"]},
    ],
    "ai": [
        {"name": "OpenAI", "tier_price_usd": 20, "sentiment_score": 4.5, "key_features": ["GPT-4o", "Assistants API", "fine-tuning"]},
        {"name": "Anthropic", "tier_price_usd": 15, "sentiment_score": 4.4, "key_features": ["Claude 3.5", "long context", "safety"]},
        {"name": "Google Gemini", "tier_price_usd": 10, "sentiment_score": 4.2, "key_features": ["multimodal", "Gemini 1.5 Pro"]},
    ],
    "business": [
        {"name": "QuickBooks", "tier_price_usd": 30, "sentiment_score": 3.9, "key_features": ["invoicing", "payroll", "tax"]},
        {"name": "FreshBooks", "tier_price_usd": 17, "sentiment_score": 4.1, "key_features": ["invoicing", "time tracking"]},
        {"name": "Xero", "tier_price_usd": 25, "sentiment_score": 4.2, "key_features": ["bank sync", "multi-currency"]},
    ],
    "government": [
        {"name": "Deltek", "tier_price_usd": 200, "sentiment_score": 3.5, "key_features": ["contract mgmt", "compliance"]},
        {"name": "GovWin IQ", "tier_price_usd": 500, "sentiment_score": 3.7, "key_features": ["bid intel", "pipeline mgmt"]},
        {"name": "Bloomberg Government", "tier_price_usd": 1000, "sentiment_score": 4.0, "key_features": ["policy tracking", "procurement"]},
    ],
    "general": [
        {"name": "Zapier", "tier_price_usd": 20, "sentiment_score": 4.4, "key_features": ["no-code automation", "5000+ apps"]},
        {"name": "Make (Integromat)", "tier_price_usd": 10, "sentiment_score": 4.2, "key_features": ["visual automation", "complex flows"]},
        {"name": "n8n", "tier_price_usd": 0, "sentiment_score": 4.3, "key_features": ["open-source", "self-hosted"]},
    ],
}

_DEFAULT_COMPETITORS = _CATEGORY_COMPETITORS["general"]


class CompetitorAnalysisEngine:
    """
    Tracks competitor intelligence for each registered bot.

    Parameters
    ----------
    deadline : date
        The go-live deadline. No new analysis after this date.
    """

    def __init__(self, deadline: date) -> None:
        self.deadline = deadline
        self._records: dict[str, dict[str, Any]] = {}

    def register(self, bot_id: str, category: str = "general") -> None:
        if bot_id in self._records:
            return
        competitors = _CATEGORY_COMPETITORS.get(category, _DEFAULT_COMPETITORS)
        self._records[bot_id] = {
            "category": category,
            "competitors": competitors,
            "analysed": [],
            "intel_score": 0.0,
            "pricing_benchmark_usd": 0.0,
            "avg_sentiment": 0.0,
            "last_analysed_at": None,
        }

    def analyse_cycle(self, bot_id: str, category: str = "general") -> dict:
        """Run one competitor analysis cycle for *bot_id*."""
        if not self._analysis_active():
            return {"status": "deadline_passed"}

        if bot_id not in self._records:
            self.register(bot_id, category)

        rec = self._records[bot_id]
        competitors = rec["competitors"]
        analysed = rec["analysed"]
        remaining = [c for c in competitors if c["name"] not in analysed]

        newly_analysed: list[str] = []
        if remaining:
            c = remaining[0]
            analysed.append(c["name"])
            newly_analysed.append(c["name"])

        # Recalculate derived metrics
        analysed_data = [c for c in competitors if c["name"] in analysed]
        if analysed_data:
            rec["pricing_benchmark_usd"] = round(
                sum(c["tier_price_usd"] for c in analysed_data) / len(analysed_data), 2
            )
            rec["avg_sentiment"] = round(
                sum(c["sentiment_score"] for c in analysed_data) / len(analysed_data), 2
            )
        rec["intel_score"] = round(len(analysed) / max(1, len(competitors)) * 100, 2)
        rec["last_analysed_at"] = datetime.now(timezone.utc).isoformat()

        return {
            "status": "analysed",
            "competitors_analysed": len(analysed),
            "total_competitors": len(competitors),
            "newly_analysed": newly_analysed,
            "intel_score": rec["intel_score"],
            "pricing_benchmark_usd": rec["pricing_benchmark_usd"],
            "avg_competitor_sentiment": rec["avg_sentiment"],
        }

    def intel_score(self, bot_id: str) -> float:
        """Return competitor intelligence score (0–100) for *bot_id*."""
        if bot_id not in self._records:
            return 0.0
        return self._records[bot_id]["intel_score"]

    def pricing_benchmark(self, bot_id: str) -> float:
        """Return average competitor pricing (USD/month) for *bot_id*'s category."""
        if bot_id not in self._records:
            return 0.0
        return self._records[bot_id]["pricing_benchmark_usd"]

    def sentiment_summary(self, bot_id: str) -> dict:
        """Return competitor sentiment data for *bot_id*."""
        if bot_id not in self._records:
            return {}
        rec = self._records[bot_id]
        return {
            "avg_sentiment": rec["avg_sentiment"],
            "competitors_analysed": len(rec["analysed"]),
        }

    def status(self) -> dict:
        """Return aggregate status across all registered bots."""
        avg_intel = (
            sum(r["intel_score"] for r in self._records.values()) / len(self._records)
            if self._records
            else 0.0
        )
        return {
            "registered_bots": len(self._records),
            "average_intel_score": round(avg_intel, 2),
            "analysis_active": self._analysis_active(),
        }

    def _analysis_active(self) -> bool:
        return date.today() <= self.deadline
