# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
# Feature 1: App bot for user onboarding.
# Functionality: Guides new users through the app setup process.
# Use Cases: Improving user retention rates.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class OnboardingBot(BaseBot):
    """
    App bot that guides new users through app setup and feature discovery.

    Uses adaptive learning to personalise the onboarding flow and sells
    user-behaviour datasets to UX research firms.
    """

    _ONBOARDING_STEPS = [
        "Create your profile",
        "Set your preferences",
        "Connect your integrations",
        "Explore the dashboard",
        "Set your first goal",
    ]

    def __init__(self):
        super().__init__(
            name="Onboarding Bot",
            domain="app_engagement",
            category="app",
        )
        self._user_progress = {}

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="User Onboarding Behaviour Dataset",
            description="Anonymised onboarding funnel data from 500K users across 20 SaaS apps.",
            domain="app_engagement",
            size_mb=120.0,
            price_usd=249.00,
            license="CC-BY-4.0",
            tags=["onboarding", "UX", "retention", "SaaS"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()

        step_idx = self._user_progress.get(user_id, 0)
        if step_idx < len(self._ONBOARDING_STEPS):
            current_step = self._ONBOARDING_STEPS[step_idx]
            self._user_progress[user_id] = step_idx + 1
        else:
            current_step = None

        if intent == "greeting" or step_idx == 0:
            response = (
                f"{prefix}Welcome! I'm {self.name}. I'll walk you through getting started. "
                f"Step 1: **{self._ONBOARDING_STEPS[0]}**. Ready?"
            )
        elif intent == "help":
            response = (
                "I can: 🚀 Guide app setup  |  🎯 Personalise your experience  |  "
                "❓ Answer feature questions  |  💾 Sell onboarding behaviour datasets."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer user-onboarding behaviour datasets."
                + self._dataset_offer()
            )
        elif current_step:
            response = (
                f"{prefix}Great progress! Next step: **{current_step}**. "
                "Let me know when you're done and I'll guide you further."
            )
        else:
            response = (
                f"{prefix}You've completed onboarding! 🎉 "
                "Explore the full feature set or ask me anything about the app."
            )
        return response


if __name__ == "__main__":
    bot = OnboardingBot()
    print(bot.chat("Hi, I just signed up!", user_id="user-001"))
    print(bot.chat("Done, what's next?", user_id="user-001"))
    print(bot.status())