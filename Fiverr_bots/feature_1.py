# Feature 1: Fiverr bot for service listings.
# Functionality: Automatically lists services on Fiverr based on user input.
# Use Cases: Freelancers wanting to attract clients.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class FiverrListingsBot(BaseBot):
    """
    Fiverr bot that helps freelancers craft optimised service listings (gigs).

    Generates keyword-rich titles, descriptions, and pricing packages,
    and sells a Fiverr gig-performance dataset to freelance marketplace researchers.
    """

    def __init__(self):
        super().__init__(
            name="Fiverr Listings Bot",
            domain="freelance_marketplace",
            category="side_hustle",
        )

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Fiverr Gig Performance Dataset",
            description="300K Fiverr gig listings with impressions, orders, and revenue data.",
            domain="freelance_marketplace",
            size_mb=95.0,
            price_usd=149.00,
            license="Proprietary",
            tags=["Fiverr", "freelance", "gigs", "marketplace"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()
        sentiment = nlp_result["sentiment"]

        if intent == "greeting":
            response = (
                f"{prefix}Hi! I'm {self.name}. I'll help you create a high-ranking "
                "Fiverr gig. What service are you offering?"
            )
        elif intent == "help":
            response = (
                "I can: 📝 Write gig titles & descriptions  |  💵 Suggest pricing  |  "
                "🏷️ Recommend tags  |  💾 Sell gig-performance datasets."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer Fiverr gig performance datasets for marketplace research."
                + self._dataset_offer()
            )
        else:
            tone = "enthusiastic" if sentiment == "positive" else "professional"
            response = (
                f"{prefix}I'll create a compelling {tone} gig listing for you. "
                "Please share: your skill/service, target client, and your experience level "
                "(beginner/intermediate/expert)."
            )
        return response


if __name__ == "__main__":
    bot = FiverrListingsBot()
    print(bot.chat("Hi! I want to list my logo design services on Fiverr."))
    print(bot.chat("I have 5 years of experience in brand identity design."))
    print(bot.status())