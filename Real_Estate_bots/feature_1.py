"""
Feature 1: Real estate property listing aggregator.

Aggregates property listings across markets and surfaces key metrics
(price, rent, cap rate) for buyers and investors.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bots', 'ai-models-integration'))

from tiers import Tier
from bots.home_flipping_analyzer.home_flipping_analyzer import HomeFlippingAnalyzerBot
from bots.rental_cashflow_bot.rental_cashflow_bot import RentalCashflowBot


class PropertyListingAggregator:
    """Aggregates and surfaces property listings from multiple internal databases."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self._flip_bot = HomeFlippingAnalyzerBot(tier=tier)
        self._rental_bot = RentalCashflowBot(tier=tier)

    def get_flip_listings(self, limit: int = 5) -> list:
        """Return top flip opportunities sorted by flip score."""
        return self._flip_bot.get_top_flip_opportunities(limit=limit)

    def get_rental_listings(self, market: str = None) -> list:
        """Return rental property listings, optionally filtered by market."""
        all_props = list(self._rental_bot.RENTAL_DATABASE.items())
        if market:
            all_props = [(pid, p) for pid, p in all_props if p.get("market", "").lower() == market.lower()]
        return [
            {
                "id": pid,
                "address": p["address"],
                "beds": p["beds"],
                "baths": p["baths"],
                "sqft": p["sqft"],
                "type": p["type"],
                "listing_price_usd": p["purchase_price"],
                "monthly_rent_usd": p["monthly_rent"],
                "market": p.get("market"),
            }
            for pid, p in all_props
        ]

    def search_by_budget(self, max_price: float, property_type: str = None) -> list:
        """Return all listings (flip + rental) under a given budget."""
        results = []
        for pid, prop in self._rental_bot.RENTAL_DATABASE.items():
            if prop["purchase_price"] <= max_price:
                if property_type is None or prop["type"] == property_type:
                    results.append({
                        "source": "rental_database",
                        "id": pid,
                        "address": prop["address"],
                        "price_usd": prop["purchase_price"],
                        "type": prop["type"],
                        "beds": prop["beds"],
                    })
        for pid, prop in self._flip_bot.FLIP_DATABASE.items():
            if prop["purchase_price"] <= max_price:
                results.append({
                    "source": "flip_database",
                    "id": pid,
                    "address": prop["address"],
                    "price_usd": prop["purchase_price"],
                    "condition": prop["current_condition"],
                    "beds": prop["beds"],
                })
        return sorted(results, key=lambda x: x["price_usd"])

    def summarize_market(self, market: str) -> dict:
        """Return a brief market summary from available data."""
        rental_props = [p for p in self._rental_bot.RENTAL_DATABASE.values()
                        if p.get("market", "").lower() == market.lower()]
        flip_props = [p for p in self._flip_bot.FLIP_DATABASE.values()
                      if p.get("market", "").lower() == market.lower()]

        if not rental_props and not flip_props:
            return {"market": market, "data_available": False}

        avg_rent = round(sum(p["monthly_rent"] for p in rental_props) / len(rental_props), 0) if rental_props else None
        avg_flip_price = round(sum(p["purchase_price"] for p in flip_props) / len(flip_props), 0) if flip_props else None

        return {
            "market": market,
            "data_available": True,
            "rental_listings_count": len(rental_props),
            "flip_listings_count": len(flip_props),
            "avg_monthly_rent_usd": avg_rent,
            "avg_flip_purchase_price_usd": avg_flip_price,
        }