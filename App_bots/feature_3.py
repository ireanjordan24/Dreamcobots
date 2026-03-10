# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
# Feature 3: App bot for feature updates.
# Functionality: Notifies users of new features and updates in the app.
# Use Cases: Ensuring users are aware of improvements.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class FeatureUpdatesBot(BaseBot):
    """
    App bot that proactively communicates new feature releases to users.

    Personalises announcements based on user interaction history and sells
    product-engagement datasets to product analytics companies.
    """

    _UPDATES = [
        {"version": "2.1", "feature": "AI-powered smart search", "benefit": "Find anything 5× faster."},
        {"version": "2.2", "feature": "Dark mode & accessibility upgrades", "benefit": "Easier on the eyes."},
        {"version": "2.3", "feature": "Real-time collaboration", "benefit": "Work simultaneously with teammates."},
        {"version": "2.4", "feature": "Dataset marketplace integration", "benefit": "Buy and sell datasets in-app."},
    ]

    def __init__(self):
        super().__init__(
            name="Feature Updates Bot",
            domain="product_engagement",
            category="app",
        )

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Feature Adoption Analytics Dataset",
            description="Feature adoption rates and engagement metrics from 1M app users.",
            domain="product_engagement",
            size_mb=75.0,
            price_usd=159.00,
            license="Proprietary",
            tags=["product", "adoption", "engagement", "analytics"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()
        top_intents = self.learning.top_intents(n=3)

        if intent == "greeting":
            latest = self._UPDATES[-1]
            response = (
                f"{prefix}Hi! 🎉 New in v{latest['version']}: **{latest['feature']}** – "
                f"{latest['benefit']} Want a full rundown of recent updates?"
            )
        elif intent == "help":
            summaries = "  |  ".join(
                f"v{u['version']}: {u['feature']}" for u in self._UPDATES
            )
            response = f"Recent updates: {summaries}"
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer feature adoption analytics datasets."
                + self._dataset_offer()
            )
        elif intent == "feedback":
            response = (
                f"{prefix}Thanks for your input! Your feedback helps shape our roadmap. "
                "I've logged your suggestion for the product team."
            )
        else:
            personalised = (
                f" Based on your usage ({', '.join(top_intents)}), "
                "you might especially enjoy the collaboration features."
                if top_intents else ""
            )
            response = (
                f"{prefix}We have {len(self._UPDATES)} recent updates to share!{personalised} "
                "Ask me about any specific feature or type 'help' to see the full list."
            )
        return response


if __name__ == "__main__":
    bot = FeatureUpdatesBot()
    print(bot.chat("Hi! What's new in the app?"))
    print(bot.chat("Tell me more about the collaboration feature."))
    print(bot.status())