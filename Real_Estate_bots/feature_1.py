# Feature 1: Real estate bot for property listings.
# Functionality: Aggregates property listings from various sources.
# Use Cases: Home buyers looking for listings.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class PropertyListingsBot(BaseBot):
    """
    Real estate bot for aggregating and searching property listings.

    Matches buyers with listings based on preferences and sells
    property listing datasets to PropTech and mortgage companies.
    """

    def __init__(self):
        super().__init__(
            name="Property Listings Bot",
            domain="real_estate",
            category="business",
        )

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="US Residential Property Listings Dataset",
            description="10M property listings with prices, features, and geo-coordinates.",
            domain="real_estate",
            size_mb=1800.0,
            price_usd=599.00,
            license="Proprietary",
            tags=["real estate", "listings", "property", "PropTech"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()
        numbers = nlp_result.get("entities", {}).get("numbers", [])

        budget = f"${numbers[0]}" if numbers else "your budget"

        if intent == "greeting":
            response = (
                f"{prefix}Hello! I'm {self.name}. I'll help you find your perfect property. "
                "What location, budget, and property type are you looking for?"
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer US residential property listing datasets."
                + self._dataset_offer()
            )
        elif intent == "help":
            response = (
                "I can: 🏠 Search listings  |  📍 Filter by location  |  "
                "💰 Match to budget  |  💾 Sell property datasets."
            )
        else:
            response = (
                f"{prefix}I'm searching for properties around {budget}. "
                "Please specify: city/zip, number of bedrooms, and preferred property type "
                "(house, condo, townhouse)."
            )
        return response


if __name__ == "__main__":
    bot = PropertyListingsBot()
    print(bot.chat("Hi! I'm looking for a 3-bedroom house in Austin under $450000."))
    print(bot.status())