"""
Feature 3: Fiverr bot for review generation.
Functionality: Requests feedback from clients after service is completed.
Use Cases: Freelancers wanting to build their reputation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class ReviewBot(BotBase):
    """Solicits and manages client reviews to build seller reputation."""

    def __init__(self) -> None:
        super().__init__("ReviewBot", AutonomyLevel.FULLY_AUTONOMOUS, ScalingLevel.MODERATE)
        self._reviews: list = []
        self._requests_sent: list = []

    def request_review(self, client: str, order_id: str) -> dict:
        """Send a review request to a client after order completion."""
        self._requests_sent.append({"client": client, "order_id": order_id})
        return {"status": "ok", "message": f"Review request sent to {client}"}

    def submit_review(self, client: str, order_id: str, rating: int, comment: str = "") -> dict:
        """Record a review submitted by a client."""
        if not 1 <= rating <= 5:
            return {"status": "error", "message": "Rating must be between 1 and 5"}
        review = {"client": client, "order_id": order_id, "rating": rating, "comment": comment}
        self._reviews.append(review)
        return {"status": "ok", "avg_rating": self._average_rating()}

    def _average_rating(self) -> float:
        if not self._reviews:
            return 0.0
        return round(sum(r["rating"] for r in self._reviews) / len(self._reviews), 2)

    def get_reviews(self) -> list:
        """Return all submitted reviews."""
        return list(self._reviews)

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "request_review":
            return self.request_review(task.get("client", ""), task.get("order_id", ""))
        return super()._run_task(task)


if __name__ == "__main__":
    bot = ReviewBot()
    bot.start()
    bot.request_review("Jane Smith", "order-001")
    print(bot.submit_review("Jane Smith", "order-001", 5, "Fantastic work!"))
    bot.stop()