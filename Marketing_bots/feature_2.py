# Feature 2: Marketing bot for email campaigns.
# Functionality: Designs and sends out email marketing campaigns.
# Use Cases: Companies promoting products to their customer base.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class EmailCampaignBot(BaseBot):
    """
    Marketing bot for designing, personalising, and dispatching email campaigns.

    Applies NLP to optimise subject lines and sells email-performance
    datasets to email service providers and growth teams.
    """

    def __init__(self):
        super().__init__(
            name="Email Campaign Bot",
            domain="email_marketing",
            category="marketing",
        )
        self._campaigns_created = 0

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Email Campaign Performance Dataset",
            description="2M email campaigns with open rates, CTR, and revenue attribution data.",
            domain="email_marketing",
            size_mb=230.0,
            price_usd=279.00,
            license="Proprietary",
            tags=["email", "campaigns", "open-rate", "CTR", "marketing"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()
        sentiment = nlp_result["sentiment"]

        if intent == "greeting":
            response = (
                f"{prefix}Hi! I'm {self.name}. I'll help you run high-converting "
                "email campaigns. What product or message would you like to promote?"
            )
        elif intent == "help":
            response = (
                "I can: ✉️ Write email copy  |  📬 Optimise subject lines  |  "
                "👥 Segment audiences  |  📊 Track open & click rates."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer email campaign performance datasets for marketers."
                + self._dataset_offer()
            )
        else:
            self._campaigns_created += 1
            tone = "enthusiastic" if sentiment == "positive" else "professional"
            response = (
                f"{prefix}Campaign #{self._campaigns_created} started! "
                f"I'll use a **{tone}** tone based on your message. "
                "Provide the audience segment, key message, and CTA and I'll draft the copy."
            )
        return response


if __name__ == "__main__":
    bot = EmailCampaignBot()
    print(bot.chat("Hi! I want to send a product launch email to our subscribers."))
    print(bot.chat("The product is a new AI assistant for small businesses."))
    print(bot.status())