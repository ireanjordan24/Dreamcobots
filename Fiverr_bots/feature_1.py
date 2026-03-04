"""
Feature 1: Fiverr bot for service listings.
Functionality: Automatically lists services on Fiverr based on user input.
Use Cases: Freelancers wanting to attract clients.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uuid
from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class FiverrListingBot(BotBase):
    """Automatically creates and manages Fiverr service gigs."""

    def __init__(self) -> None:
        super().__init__("FiverrListingBot", AutonomyLevel.SEMI_AUTONOMOUS, ScalingLevel.MODERATE)
        self._listings: list = []

    def create_listing(self, title: str, description: str, price: float, category: str, delivery_days: int) -> dict:
        """Create a new service listing."""
        listing = {
            "listing_id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "price": price,
            "category": category,
            "delivery_days": delivery_days,
            "status": "active",
            "views": 0,
            "orders": 0,
        }
        self._listings.append(listing)
        return {"status": "ok", "listing_id": listing["listing_id"], "title": title}

    def get_listings(self) -> list:
        """Return all active listings."""
        return [l for l in self._listings if l["status"] == "active"]

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "create_listing":
            return self.create_listing(
                task.get("title", ""), task.get("description", ""),
                task.get("price", 0), task.get("category", ""),
                task.get("delivery_days", 3),
            )
        return super()._run_task(task)


if __name__ == "__main__":
    bot = FiverrListingBot()
    bot.start()
    print(bot.create_listing("AI Bot Development", "I will build your custom AI bot.", 500, "Programming", 7))
    bot.stop()