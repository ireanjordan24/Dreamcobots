"""
Bot Marketplace for Dreamcobots platform.

Allows users to browse, purchase, deploy, and list pre-configured bots
for sale or resale.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class BotListing:
    """
    A bot available in the marketplace.

    Args:
        name: Display name.
        description: Detailed description and use-case explanation.
        category: Bot category (e.g. 'communication', 'healthcare', 'real_estate').
        price_usd: Purchase price. Use 0.0 for free bots.
        seller_id: Identifier of the seller/deployer.
        version: Semantic version string (e.g. '1.0.0').
        tags: Search tags to aid discoverability.
    """
    name: str
    description: str
    category: str
    price_usd: float
    seller_id: str
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    listing_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    available: bool = True
    instructions: str = ""
    purchases: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Purchase:
    """Records a bot purchase transaction."""
    purchase_id: str
    listing_id: str
    buyer_id: str
    price_paid_usd: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    deployed: bool = False


# ---------------------------------------------------------------------------
# BotMarketplace
# ---------------------------------------------------------------------------

class BotMarketplace:
    """
    Dreamcobots Bot Marketplace.

    Users can:
    - Browse and search the catalogue of pre-configured bots.
    - Purchase bots for personal use.
    - List their own bots for resale.
    - Deploy purchased bots to their environment.

    Usage::

        market = BotMarketplace()
        listing = market.list_bot(BotListing(name="CRM Bot", ...))
        purchase = market.purchase("user-42", listing.listing_id)
        market.deploy(purchase.purchase_id)
    """

    def __init__(self) -> None:
        self._listings: Dict[str, BotListing] = {}
        self._purchases: Dict[str, Purchase] = {}

    # ------------------------------------------------------------------
    # Listings
    # ------------------------------------------------------------------

    def list_bot(self, listing: BotListing) -> BotListing:
        """
        Add a bot to the marketplace.

        Args:
            listing: Populated BotListing to publish.

        Returns:
            The registered BotListing.
        """
        self._listings[listing.listing_id] = listing
        return listing

    def delist_bot(self, listing_id: str, seller_id: str) -> bool:
        """
        Remove a bot from sale.

        Args:
            listing_id: ID of the listing to delist.
            seller_id: Must match the original seller for authorisation.

        Returns:
            True if the listing was found and deactivated.
        """
        listing = self._listings.get(listing_id)
        if listing and listing.seller_id == seller_id:
            listing.available = False
            return True
        return False

    def get_listing(self, listing_id: str) -> Optional[BotListing]:
        """Return a listing or None."""
        return self._listings.get(listing_id)

    def browse(
        self,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        tag: Optional[str] = None,
        available_only: bool = True,
    ) -> List[BotListing]:
        """
        Browse marketplace listings with optional filters.

        Args:
            category: Filter by category string (case-insensitive).
            max_price: Maximum price in USD.
            tag: Filter listings that contain this tag.
            available_only: When True, return only active listings.

        Returns:
            Sorted list of matching BotListing objects (by price ascending).
        """
        results = list(self._listings.values())
        if available_only:
            results = [l for l in results if l.available]
        if category:
            results = [l for l in results if l.category.lower() == category.lower()]
        if max_price is not None:
            results = [l for l in results if l.price_usd <= max_price]
        if tag:
            results = [l for l in results if tag.lower() in [t.lower() for t in l.tags]]
        return sorted(results, key=lambda l: l.price_usd)

    def search(self, query: str) -> List[BotListing]:
        """
        Full-text search across listing names, descriptions, and tags.

        Args:
            query: Search string.

        Returns:
            Listings whose name, description, or tags contain the query.
        """
        q = query.lower()
        return [
            l for l in self._listings.values()
            if l.available and (
                q in l.name.lower()
                or q in l.description.lower()
                or any(q in t.lower() for t in l.tags)
            )
        ]

    # ------------------------------------------------------------------
    # Purchasing
    # ------------------------------------------------------------------

    def purchase(self, buyer_id: str, listing_id: str) -> Purchase:
        """
        Purchase a bot for *buyer_id*.

        Args:
            buyer_id: Identifier of the purchasing user.
            listing_id: The listing to purchase.

        Returns:
            Purchase record.

        Raises:
            ValueError: If the listing does not exist or is unavailable.
        """
        listing = self._listings.get(listing_id)
        if not listing:
            raise ValueError(f"Listing '{listing_id}' not found.")
        if not listing.available:
            raise ValueError(f"Listing '{listing.name}' is no longer available.")

        purchase = Purchase(
            purchase_id=str(uuid.uuid4()),
            listing_id=listing_id,
            buyer_id=buyer_id,
            price_paid_usd=listing.price_usd,
        )
        self._purchases[purchase.purchase_id] = purchase
        listing.purchases += 1
        return purchase

    def get_purchases(self, buyer_id: str) -> List[Purchase]:
        """Return all purchases made by *buyer_id*."""
        return [p for p in self._purchases.values() if p.buyer_id == buyer_id]

    # ------------------------------------------------------------------
    # Deployment
    # ------------------------------------------------------------------

    def deploy(self, purchase_id: str) -> bool:
        """
        Mark a purchased bot as deployed.

        Args:
            purchase_id: ID of the purchase to deploy.

        Returns:
            True if the purchase was found and marked deployed.
        """
        purchase = self._purchases.get(purchase_id)
        if purchase:
            purchase.deployed = True
            return True
        return False

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def marketplace_stats(self) -> Dict[str, Any]:
        """Return aggregate marketplace statistics."""
        active = [l for l in self._listings.values() if l.available]
        total_revenue = sum(p.price_paid_usd for p in self._purchases.values())
        categories = list({l.category for l in self._listings.values()})
        return {
            "total_listings": len(self._listings),
            "active_listings": len(active),
            "total_purchases": len(self._purchases),
            "total_revenue_usd": round(total_revenue, 2),
            "deployed_bots": sum(1 for p in self._purchases.values() if p.deployed),
            "categories": categories,
        }
