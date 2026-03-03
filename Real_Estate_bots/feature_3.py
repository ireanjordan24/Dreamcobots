# Feature 3: Real estate bot for market analysis.
# Functionality: Analyzes market trends and provides insights.
# Use Cases: Investors making data-driven decisions.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot


class MarketAnalysisBot(BaseBot):
    """
    Real estate bot that provides market trend analysis and investment insights.

    Delivers price trend reports, neighbourhood comparisons, and sells
    real-estate market datasets to investors and analysts.
    """

    def __init__(self):
        super().__init__(
            name="Market Analysis Bot",
            domain="real_estate_investment",
            category="business",
        )

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Real Estate Market Trends Dataset",
            description="Historical price trends, rental yields, and market indices for 500 US metros.",
            domain="real_estate_investment",
            size_mb=420.0,
            price_usd=499.00,
            license="CC-BY-4.0",
            tags=["real estate", "investment", "trends", "market-data"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()
        entities = nlp_result.get("entities", {})
        locations = entities.get("capitalized", [])
        location = locations[0] if locations else "the market"

        if intent == "dataset_purchase":
            response = (
                f"{prefix}I offer comprehensive real estate market datasets."
                + self._dataset_offer()
            )
        elif intent == "greeting":
            response = (
                f"{prefix}Hi! I'm {self.name}. I provide data-driven real estate "
                "market insights. Which market or metro area interests you?"
            )
        elif intent == "help":
            response = (
                "I can: 📈 Analyse price trends  |  🏘️ Compare neighbourhoods  |  "
                "💰 Estimate ROI  |  💾 Sell market datasets."
            )
        else:
            response = (
                f"{prefix}Analysing **{location}** real estate market. "
                "Key metrics: median price, price/sqft trend, rental yield, and days-on-market. "
                "Specify a timeframe (e.g. 'last 12 months') for detailed analysis."
            )
        return response


if __name__ == "__main__":
    bot = MarketAnalysisBot()
    print(bot.chat("Hi! What are the real estate trends in Austin, Texas?"))
    print(bot.chat("Can I buy your market dataset?"))
    print(bot.status())