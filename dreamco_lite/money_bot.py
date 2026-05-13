"""
DreamCo Lite — Money Bot 💰

Finds leads (name, business, contact) for a given niche + location and
generates AI-personalised outreach messages ready to copy and send.

Modes
-----
SIMULATION_MODE=true  (default, no API keys required)
    Returns realistic-looking synthetic lead data so the full workflow can
    be exercised without live credentials.

SIMULATION_MODE=false
    Requires GOOGLE_PLACES_API_KEY and OPENAI_API_KEY environment variables.
    Uses Google Places API for real lead discovery and OpenAI for outreach.
"""

from __future__ import annotations

import os
import random
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SIMULATION = os.getenv("SIMULATION_MODE", "true").lower() != "false"
_GOOGLE_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
_OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
_PLACES_DETAIL_URL = "https://maps.googleapis.com/maps/api/place/details/json"
_OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

# ---------------------------------------------------------------------------
# Synthetic data used in simulation mode
# ---------------------------------------------------------------------------

_FIRST_NAMES = [
    "James", "Maria", "David", "Sarah", "Michael",
    "Linda", "Robert", "Patricia", "John", "Jennifer",
]
_LAST_NAMES = [
    "Johnson", "Williams", "Brown", "Jones", "Garcia",
    "Miller", "Davis", "Martinez", "Anderson", "Taylor",
]
_BUSINESS_SUFFIXES = [
    "LLC", "Inc.", "& Associates", "Group", "Solutions", "Agency", "Co.",
]


def _random_phone() -> str:
    return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"


def _random_email(name: str, business: str) -> str:
    domain = business.lower().replace(" ", "").replace(",", "")[:12]
    return name.lower().replace(" ", ".") + "@" + domain + ".com"


def _sim_leads(niche: str, location: str, count: int = 5) -> list[dict[str, Any]]:
    """Generate synthetic lead data for simulation mode."""
    results: list[dict[str, Any]] = []
    for i in range(count):
        first = random.choice(_FIRST_NAMES)
        last = random.choice(_LAST_NAMES)
        name = f"{first} {last}"
        suffix = random.choice(_BUSINESS_SUFFIXES)
        business = f"{last} {niche.title()} {suffix}"
        phone = _random_phone()
        email = _random_email(name, business)
        results.append(
            {
                "name": name,
                "business": business,
                "phone": phone,
                "email": email,
                "location": location,
                "source": "simulation",
                "rating": round(random.uniform(2.5, 4.5), 1),
            }
        )
    return results


# ---------------------------------------------------------------------------
# Google Places helpers
# ---------------------------------------------------------------------------

def _google_leads(niche: str, location: str) -> list[dict[str, Any]]:
    """Fetch real leads from Google Places API."""
    query = f"{niche} in {location}"
    try:
        resp = httpx.get(
            _PLACES_SEARCH_URL,
            params={"query": query, "key": _GOOGLE_KEY},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("Google Places search failed: %s", exc)
        return []

    results: list[dict[str, Any]] = []
    for place in data.get("results", [])[:10]:
        place_id = place.get("place_id")
        details = _google_place_details(place_id) if place_id else {}
        results.append(
            {
                "name": details.get("name") or place.get("name", "Unknown"),
                "business": place.get("name", "Unknown"),
                "phone": details.get("formatted_phone_number", "N/A"),
                "email": details.get("email", "N/A"),
                "location": place.get("formatted_address", location),
                "source": "google_places",
                "rating": place.get("rating", 0),
            }
        )
    return results


def _google_place_details(place_id: str) -> dict[str, Any]:
    """Fetch additional details for a single Google Place."""
    try:
        resp = httpx.get(
            _PLACES_DETAIL_URL,
            params={
                "place_id": place_id,
                "fields": "name,formatted_phone_number,website,email",
                "key": _GOOGLE_KEY,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("result", {})
    except Exception as exc:
        logger.warning("Google Place details failed for %s: %s", place_id, exc)
        return {}


# ---------------------------------------------------------------------------
# OpenAI helpers
# ---------------------------------------------------------------------------

def _openai_messages(leads: list[dict[str, Any]], niche: str) -> list[dict[str, Any]]:
    """Generate personalised outreach messages via OpenAI."""
    if not _OPENAI_KEY:
        logger.warning("OPENAI_API_KEY not set; returning template messages.")
        return _template_messages(leads, niche)

    enriched: list[dict[str, Any]] = []
    for lead in leads:
        prompt = (
            f"Write a short, friendly, personalised cold-outreach message (3–4 sentences) "
            f"to {lead['name']} at {lead['business']} who works in the {niche} industry. "
            f"Introduce DreamCo, an AI automation service, and explain how it can help their "
            f"business grow. End with a clear call to action asking for a 15-minute call. "
            f"Do not use emojis."
        )
        try:
            resp = httpx.post(
                _OPENAI_CHAT_URL,
                headers={"Authorization": f"Bearer {_OPENAI_KEY}"},
                json={
                    "model": _OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200,
                    "temperature": 0.8,
                },
                timeout=30,
            )
            resp.raise_for_status()
            message = resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            logger.warning("OpenAI message generation failed: %s", exc)
            message = _template_message(lead, niche)
        enriched.append({**lead, "outreach_message": message})

    return enriched


def _template_message(lead: dict[str, Any], niche: str) -> str:
    return (
        f"Hi {lead['name']}, I came across {lead['business']} and was impressed by your work "
        f"in the {niche} space. At DreamCo, we help {niche} businesses automate their "
        f"workflows so they can focus on growth. Would you have 15 minutes this week for a "
        f"quick call to explore how we could help you?"
    )


def _template_messages(leads: list[dict[str, Any]], niche: str) -> list[dict[str, Any]]:
    return [{**lead, "outreach_message": _template_message(lead, niche)} for lead in leads]


# ---------------------------------------------------------------------------
# MoneyBot
# ---------------------------------------------------------------------------

class MoneyBot:
    """
    💰 DreamCo Lite Money Bot.

    Usage::

        bot = MoneyBot()
        leads = bot.find_leads("real estate agents", "Wisconsin")
        results = bot.generate_messages(leads, "real estate agents")
    """

    def find_leads(self, niche: str, location: str) -> list[dict[str, Any]]:
        """
        Discover leads for *niche* in *location*.

        Returns a list of dicts with keys:
          name, business, phone, email, location, source, rating
        """
        if not niche or not location:
            raise ValueError("Both 'niche' and 'location' are required.")

        if _SIMULATION or not _GOOGLE_KEY:
            logger.info("Money Bot: simulation mode — returning synthetic leads.")
            return _sim_leads(niche, location)

        leads = _google_leads(niche, location)
        if not leads:
            logger.info("Money Bot: Google Places returned no results; falling back to simulation.")
            return _sim_leads(niche, location)
        return leads

    def generate_messages(
        self, leads: list[dict[str, Any]], niche: str
    ) -> list[dict[str, Any]]:
        """
        Generate personalised outreach messages for each lead.

        Each returned dict extends the input lead with an 'outreach_message' key.
        """
        if not leads:
            return []
        return _openai_messages(leads, niche)

    def run_automation(self, niche: str, location: str) -> list[dict[str, Any]]:
        """
        One-shot pipeline: find leads *and* generate outreach messages.
        """
        leads = self.find_leads(niche, location)
        return self.generate_messages(leads, niche)
