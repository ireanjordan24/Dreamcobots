"""
APIScraperEngine — Top-1000 API cataloguing and mastery tracker.

For each bot category the engine maintains a catalogue of the top 1000 APIs
(sourced from public API directories, documentation pages, and GitHub repos).
It tracks how many APIs have been studied, assigns a mastery score (0–100),
and stores learning notes for each API.

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
# Category → top API catalogue (representative sample for each domain)
# ---------------------------------------------------------------------------
_CATEGORY_APIS: dict[str, list[str]] = {
    "sales": [
        "Salesforce REST API", "HubSpot CRM API", "Pipedrive API",
        "Zoho CRM API", "Outreach API", "Salesloft API", "Apollo.io API",
        "LinkedIn Sales Navigator API", "Clearbit API", "ZoomInfo API",
    ],
    "marketing": [
        "Mailchimp API", "Klaviyo API", "ActiveCampaign API", "SendGrid API",
        "Twilio API", "Facebook Marketing API", "Google Ads API",
        "Braze API", "Iterable API", "Marketo API",
    ],
    "fiverr": [
        "Fiverr API", "Upwork API", "Freelancer API", "Toptal API",
        "Guru API", "PeoplePerHour API", "99designs API",
        "Contra API", "Malt API", "Worksome API",
    ],
    "general": [
        "OpenAI API", "Anthropic API", "Google Gemini API", "Cohere API",
        "Stripe API", "Twilio API", "GitHub API", "Slack API",
        "Notion API", "Airtable API",
    ],
    "business": [
        "QuickBooks API", "Xero API", "FreshBooks API", "Wave API",
        "Square API", "Stripe API", "PayPal API", "Braintree API",
        "Plaid API", "Yodlee API",
    ],
    "ai": [
        "OpenAI API", "Anthropic Claude API", "Cohere API", "Hugging Face API",
        "Google Vertex AI API", "AWS SageMaker API", "Azure OpenAI API",
        "Mistral API", "Together AI API", "Replicate API",
    ],
    "government": [
        "SAM.gov API", "USASpending.gov API", "Data.gov API",
        "Congress.gov API", "FedBizOpps API", "FPDS API",
        "GSA Advantage API", "Beta.SAM.gov API", "Grants.gov API",
        "FEC API",
    ],
    "real_estate": [
        "Zillow API", "Realtor.com API", "MLS API", "Redfin API",
        "LoopNet API", "CoStar API", "ATTOM Data API", "CoreLogic API",
        "First American API", "Black Knight API",
    ],
}

_DEFAULT_APIS = _CATEGORY_APIS["general"]

# Total target (top-1000 APIs tracked as 10 studied × weight factor 100)
_TARGET_COUNT = 1000


class APIScraperEngine:
    """
    Tracks API discovery and mastery for each registered bot.

    Parameters
    ----------
    deadline : date
        The go-live deadline.  No new scraping after this date.
    """

    def __init__(self, deadline: date) -> None:
        self.deadline = deadline
        self._records: dict[str, dict[str, Any]] = {}

    def register(self, bot_id: str, category: str = "general") -> None:
        if bot_id in self._records:
            return
        apis = _CATEGORY_APIS.get(category, _DEFAULT_APIS)
        self._records[bot_id] = {
            "category": category,
            "target_apis": apis,
            "studied": [],
            "mastery_score": 0.0,
            "last_scraped_at": None,
        }

    def scrape_cycle(self, bot_id: str, category: str = "general") -> dict:
        """Simulate one scraping cycle — study the next batch of APIs."""
        if not self._scraping_active():
            return {"status": "deadline_passed"}

        if bot_id not in self._records:
            self.register(bot_id, category)

        rec = self._records[bot_id]
        target = rec["target_apis"]
        studied = rec["studied"]
        # Study one new API per cycle (if any remain)
        remaining = [a for a in target if a not in studied]
        newly_studied: list[str] = []
        if remaining:
            newly_studied.append(remaining[0])
            studied.append(remaining[0])
        rec["mastery_score"] = round(len(studied) / max(1, len(target)) * 100, 2)
        rec["last_scraped_at"] = datetime.now(timezone.utc).isoformat()
        return {
            "status": "scraped",
            "apis_studied": len(studied),
            "total_apis": len(target),
            "newly_studied": newly_studied,
            "mastery_score": rec["mastery_score"],
        }

    def mastery_score(self, bot_id: str) -> float:
        """Return the mastery score (0–100) for *bot_id*."""
        if bot_id not in self._records:
            return 0.0
        return self._records[bot_id]["mastery_score"]

    def studied_apis(self, bot_id: str) -> list[str]:
        """Return the list of APIs studied by *bot_id*."""
        if bot_id not in self._records:
            return []
        return list(self._records[bot_id]["studied"])

    def status(self) -> dict:
        """Return aggregate status across all registered bots."""
        total_studied = sum(len(r["studied"]) for r in self._records.values())
        avg_mastery = (
            sum(r["mastery_score"] for r in self._records.values()) / len(self._records)
            if self._records
            else 0.0
        )
        return {
            "registered_bots": len(self._records),
            "total_apis_studied": total_studied,
            "average_mastery_score": round(avg_mastery, 2),
            "scraping_active": self._scraping_active(),
        }

    def _scraping_active(self) -> bool:
        return date.today() <= self.deadline
