"""
Marketplace Deployer — packages and deploys generated tools to the DreamCo
marketplace so developers and organizations can purchase or integrate them.

Wraps the existing ``marketplace.marketplace.Marketplace`` to add tool-specific
listing lifecycle management, pricing, and deployment status tracking.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .tool_generator import GeneratedTool


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ToolListing:
    """A marketplace listing entry for a generated tool."""
    listing_id: str
    tool_id: str
    library_name: str
    language: str
    purpose_category: str
    title: str
    description: str
    price_usd_monthly: float
    tags: list[str] = field(default_factory=list)
    version: str = "1.0.0"
    deployed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "active"         # "active" | "deprecated" | "pending"
    downloads: int = 0

    def to_dict(self) -> dict:
        return {
            "listing_id": self.listing_id,
            "tool_id": self.tool_id,
            "library_name": self.library_name,
            "language": self.language,
            "purpose_category": self.purpose_category,
            "title": self.title,
            "description": self.description,
            "price_usd_monthly": self.price_usd_monthly,
            "tags": self.tags,
            "version": self.version,
            "deployed_at": self.deployed_at,
            "status": self.status,
            "downloads": self.downloads,
        }


class MarketplaceDeployerError(Exception):
    """Raised for marketplace deployment errors."""


# ---------------------------------------------------------------------------
# MarketplaceDeployer
# ---------------------------------------------------------------------------

class MarketplaceDeployer:
    """
    Packages generated tools into marketplace listings.

    Pricing
    -------
    - Hidden capability tools: $9.99 / month (premium tier)
    - Standard documented-symbol tools: $2.99 / month
    - Free tools: $0.00 (open-source libraries)

    ENTERPRISE tier users can deploy; PRO can list; FREE can browse.
    """

    _PRICE_HIDDEN = 9.99
    _PRICE_STANDARD = 2.99
    _PRICE_FREE = 0.00

    def __init__(self) -> None:
        self._listings: dict[str, ToolListing] = {}   # listing_id → ToolListing
        self._tool_to_listing: dict[str, str] = {}     # tool_id → listing_id

    # ------------------------------------------------------------------
    # Deployment
    # ------------------------------------------------------------------

    def deploy(self, tool: GeneratedTool,
               price_override: Optional[float] = None) -> ToolListing:
        """
        Deploy a generated tool to the marketplace.

        Parameters
        ----------
        tool : GeneratedTool
            The tool to list.
        price_override : float, optional
            If supplied, use this monthly price instead of the default.

        Returns
        -------
        ToolListing
        """
        if tool.tool_id in self._tool_to_listing:
            existing_id = self._tool_to_listing[tool.tool_id]
            return self._listings[existing_id]

        if price_override is not None:
            price = price_override
        elif tool.is_hidden_capability:
            price = self._PRICE_HIDDEN
        elif tool.library_name in ("requests", "beautifulsoup4", "lodash"):
            price = self._PRICE_FREE
        else:
            price = self._PRICE_STANDARD

        listing_id = str(uuid.uuid4())
        listing = ToolListing(
            listing_id=listing_id,
            tool_id=tool.tool_id,
            library_name=tool.library_name,
            language=tool.language,
            purpose_category=tool.purpose_category,
            title=f"{tool.library_name}.{tool.symbol} Tool",
            description=tool.description,
            price_usd_monthly=price,
            tags=list(tool.tags),
            version=tool.version,
            status="active",
        )
        self._listings[listing_id] = listing
        self._tool_to_listing[tool.tool_id] = listing_id
        return listing

    def deploy_batch(self, tools: list[GeneratedTool]) -> list[ToolListing]:
        """Deploy multiple tools at once."""
        return [self.deploy(t) for t in tools]

    # ------------------------------------------------------------------
    # Lifecycle management
    # ------------------------------------------------------------------

    def deprecate(self, listing_id: str) -> bool:
        """Mark a listing as deprecated."""
        if listing_id not in self._listings:
            return False
        self._listings[listing_id].status = "deprecated"
        return True

    def update_version(self, listing_id: str, new_version: str) -> bool:
        """Update the version of a deployed listing."""
        if listing_id not in self._listings:
            return False
        self._listings[listing_id].version = new_version
        return True

    def record_download(self, listing_id: str) -> bool:
        """Increment the download counter for a listing."""
        if listing_id not in self._listings:
            return False
        self._listings[listing_id].downloads += 1
        return True

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_listing(self, listing_id: str) -> Optional[ToolListing]:
        """Return a listing by ID."""
        return self._listings.get(listing_id)

    def listing_for_tool(self, tool_id: str) -> Optional[ToolListing]:
        """Return the listing for a specific tool_id."""
        listing_id = self._tool_to_listing.get(tool_id)
        if listing_id is None:
            return None
        return self._listings.get(listing_id)

    def search(self, query: str = "", language: Optional[str] = None,
               purpose: Optional[str] = None,
               status: str = "active") -> list[ToolListing]:
        """Search active marketplace listings."""
        results = [lst for lst in self._listings.values() if lst.status == status]
        if language:
            results = [lst for lst in results if lst.language == language.lower()]
        if purpose:
            results = [lst for lst in results if lst.purpose_category == purpose.lower()]
        if query:
            q = query.lower()
            results = [lst for lst in results
                       if q in lst.title.lower() or q in lst.description.lower()
                       or any(q in tag for tag in lst.tags)]
        return results

    def marketplace_summary(self) -> dict:
        """Return a high-level marketplace summary."""
        active = [lst for lst in self._listings.values() if lst.status == "active"]
        total_revenue = sum(lst.price_usd_monthly * lst.downloads for lst in active)
        by_language: dict[str, int] = {}
        for lst in active:
            by_language[lst.language] = by_language.get(lst.language, 0) + 1
        return {
            "total_listings": len(self._listings),
            "active_listings": len(active),
            "total_downloads": sum(lst.downloads for lst in self._listings.values()),
            "estimated_monthly_revenue_usd": round(total_revenue, 2),
            "listings_by_language": by_language,
        }
