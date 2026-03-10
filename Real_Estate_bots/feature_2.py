# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
# Feature 2: Real estate bot for scheduling viewings.
# Functionality: Allows users to schedule property viewings via chat.
# Use Cases: Prospective buyers wanting to view properties.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot


class ViewingSchedulerBot(BaseBot):
    """
    Real estate bot for scheduling and managing property viewings.
    """

    def __init__(self):
        super().__init__(
            name="Viewing Scheduler Bot",
            domain="real_estate",
            category="business",
        )
        self._viewings = []

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Property Viewing Behaviour Dataset",
            description="Anonymised viewing schedules and conversion rates from 50 agencies.",
            domain="real_estate",
            size_mb=30.0,
            price_usd=79.00,
            license="Proprietary",
            tags=["real estate", "viewings", "conversion", "scheduling"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()

        if intent in ("schedule", "greeting"):
            viewing_id = f"VIEW-{len(self._viewings) + 1:04d}"
            self._viewings.append({"id": viewing_id, "user": user_id})
            response = (
                f"{prefix}I've created viewing appointment **{viewing_id}**. "
                "Please confirm the property address and your preferred date/time."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer property viewing behaviour datasets."
                + self._dataset_offer()
            )
        elif intent == "help":
            response = (
                "I can: 📅 Book viewings  |  🔔 Send reminders  |  "
                "🗺️ Provide directions  |  💾 Sell viewing datasets."
            )
        else:
            response = (
                f"{prefix}Ready to book a property viewing? "
                "Share the listing address and your available times."
            )
        return response


if __name__ == "__main__":
    bot = ViewingSchedulerBot()
    print(bot.chat("Hi! I'd like to schedule a viewing for 123 Oak Street on Saturday."))
    print(bot.status())