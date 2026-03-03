# Feature 2: App bot for user support.
# Functionality: Provides customer support through chat interface.
# Use Cases: Users needing help with technical issues.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class SupportBot(BaseBot):
    """
    App bot that handles customer support queries with adaptive responses.

    Learns from resolved tickets to improve answer quality over time and
    sells support-interaction datasets to CX analytics companies.
    """

    _COMMON_SOLUTIONS = {
        "login":     "Try resetting your password at Settings > Security > Reset Password.",
        "billing":   "Check your billing history under Account > Billing. Contact billing@dreamcobots.ai for disputes.",
        "performance": "Clear your cache (Ctrl+Shift+Delete) and ensure you're on the latest version.",
        "data":      "All data is auto-saved every 30 seconds. Check the History panel to restore a previous version.",
    }

    def __init__(self):
        super().__init__(
            name="Support Bot",
            domain="customer_support",
            category="app",
        )

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Customer Support Ticket Dataset",
            description="200K anonymised support tickets with categories, resolutions, and CSAT scores.",
            domain="customer_support",
            size_mb=310.0,
            price_usd=349.00,
            license="Proprietary",
            tags=["support", "tickets", "CX", "NLP"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        tokens = set(nlp_result.get("tokens", []))
        prefix = self._emotion_prefix()

        matched_solution = None
        for keyword, solution in self._COMMON_SOLUTIONS.items():
            if keyword in tokens:
                matched_solution = solution
                break

        if matched_solution:
            self.learning.reinforce(intent, reward=0.5)
            response = (
                f"{prefix}Here's what I'd suggest: {matched_solution} "
                "Did that resolve your issue? (yes/no)"
            )
        elif intent == "feedback":
            response = (
                f"{prefix}Thank you for your feedback! I've logged it for our team. "
                "Is there anything else I can help with?"
            )
        elif intent == "greeting":
            response = (
                f"{prefix}Hi! I'm {self.name}. How can I help you today? "
                "Describe your issue and I'll find a solution."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}We offer support-ticket datasets for CX research."
                + self._dataset_offer()
            )
        elif intent == "help":
            response = (
                "I can: 🛠️ Troubleshoot issues  |  📚 Provide how-to guides  |  "
                "🎫 Escalate complex tickets  |  💾 Sell support datasets."
            )
        else:
            response = (
                f"{prefix}I'm here to help! Could you describe the issue in a bit "
                "more detail? (e.g. login, billing, performance, data)"
            )
        return response


if __name__ == "__main__":
    bot = SupportBot()
    print(bot.chat("Hello, I can't log in to my account."))
    print(bot.chat("I'm having a billing problem."))
    print(bot.status())