"""
DreamCo Marketplace

Central hub for sharing, hiring, and deploying bots tailored to specific
industries and job roles.

Features (via tier)
-------------------
FREE        — Browse listed bots and job postings.
PRO         — List your own bots, hire AI workers, post job openings.
ENTERPRISE  — White-label marketplace, robot contract sourcing, revenue sharing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class BotListing:
    """A bot available for hire or purchase in the marketplace."""
    listing_id: str
    bot_name: str
    industry: str
    job_title: str
    price_usd_monthly: float
    owner: str
    description: str
    is_human_worker: bool = False   # True if listing is for a human contractor
    is_robot: bool = False          # True if physical robot hardware
    tags: list[str] = field(default_factory=list)


class Marketplace:
    """
    DreamCo Marketplace — connects clients with bots, AI workers, and robots.

    Usage
    -----
        from marketplace.marketplace import Marketplace

        market = Marketplace()
        market.add_listing(BotListing(...))
        results = market.search("accountant")
    """

    def __init__(self) -> None:
        self._listings: dict[str, BotListing] = {}

    def add_listing(self, listing: BotListing) -> None:
        """Add a new listing to the marketplace."""
        self._listings[listing.listing_id] = listing

    def remove_listing(self, listing_id: str) -> bool:
        """Remove a listing.  Returns True if removed, False if not found."""
        if listing_id in self._listings:
            del self._listings[listing_id]
            return True
        return False

    def search(self, query: str) -> list[BotListing]:
        """Full-text search across bot names, industries, and job titles."""
        q = query.lower()
        return [
            l for l in self._listings.values()
            if q in l.bot_name.lower()
            or q in l.industry.lower()
            or q in l.job_title.lower()
            or any(q in tag.lower() for tag in l.tags)
        ]

    def by_industry(self, industry: str) -> list[BotListing]:
        """Return all listings for a given industry."""
        key = industry.lower()
        return [l for l in self._listings.values() if l.industry.lower() == key]

    def human_workers(self) -> list[BotListing]:
        """Return listings for human contractors."""
        return [l for l in self._listings.values() if l.is_human_worker]

    def robots(self) -> list[BotListing]:
        """Return listings for physical robot hardware."""
        return [l for l in self._listings.values() if l.is_robot]

    def all_listings(self) -> list[BotListing]:
        """Return all active listings."""
        return list(self._listings.values())

    def count(self) -> int:
        """Number of active listings."""
        return len(self._listings)

    def get(self, listing_id: str) -> Optional[BotListing]:
        """Look up a listing by ID."""
        return self._listings.get(listing_id)


__all__ = ["Marketplace", "BotListing"]
