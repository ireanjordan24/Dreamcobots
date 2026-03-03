# Feature 2: Fiverr bot for order management.
# Functionality: Tracks and manages incoming orders from clients.
# Use Cases: Sellers needing to stay organized.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot


class FiverrOrderBot(BaseBot):
    """
    Fiverr bot for tracking orders, deadlines, and client communications.
    """

    def __init__(self):
        super().__init__(
            name="Fiverr Order Bot",
            domain="freelance_marketplace",
            category="side_hustle",
        )
        self._orders = {}

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Freelance Order Completion Patterns Dataset",
            description="Anonymised order timelines, revision counts, and satisfaction scores.",
            domain="freelance_marketplace",
            size_mb=55.0,
            price_usd=99.00,
            license="Proprietary",
            tags=["orders", "freelance", "completion", "satisfaction"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()

        if intent == "greeting":
            order_count = len(self._orders)
            response = (
                f"{prefix}Hi! I'm {self.name}. "
                f"You have {order_count} active orders tracked. "
                "Tell me your order ID or share a new order to track."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer freelance order completion pattern datasets."
                + self._dataset_offer()
            )
        elif intent == "help":
            response = (
                "I can: 📦 Track order status  |  ⏰ Alert on deadlines  |  "
                "💬 Draft client messages  |  💾 Sell order datasets."
            )
        else:
            order_id = f"ORD-{len(self._orders) + 1:04d}"
            self._orders[order_id] = {"user": user_id, "status": "in_progress"}
            response = (
                f"{prefix}Order **{order_id}** is now being tracked. "
                "I'll alert you 24 hours before the deadline. "
                "Share the deliverable details and due date."
            )
        return response


if __name__ == "__main__":
    bot = FiverrOrderBot()
    print(bot.chat("Hi! I have a new logo design order due in 3 days."))
    print(bot.status())