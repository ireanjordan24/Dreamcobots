"""
Feature 3: Marketing bot for customer feedback.
Functionality: Collects and analyzes customer feedback on products/services.
Use Cases: Businesses looking to improve customer satisfaction.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class FeedbackBot(BotBase):
    """Collects and analyses customer satisfaction feedback."""

    def __init__(self) -> None:
        super().__init__("FeedbackBot", AutonomyLevel.FULLY_AUTONOMOUS, ScalingLevel.MODERATE)
        self._feedback: list = []

    def collect_feedback(self, user_id: str, product: str, rating: int, comment: str = "") -> dict:
        """Record a feedback entry (rating 1-5)."""
        if not 1 <= rating <= 5:
            return {"status": "error", "message": "Rating must be between 1 and 5."}
        entry = {"user_id": user_id, "product": product, "rating": rating, "comment": comment}
        self._feedback.append(entry)
        return {"status": "ok", "average_rating": self.average_rating(product)}

    def average_rating(self, product: str) -> float:
        """Return the average rating for a product."""
        ratings = [f["rating"] for f in self._feedback if f["product"] == product]
        return round(sum(ratings) / len(ratings), 2) if ratings else 0.0

    def sentiment_summary(self, product: str) -> dict:
        """Categorise feedback as positive, neutral, or negative."""
        entries = [f for f in self._feedback if f["product"] == product]
        positive = sum(1 for f in entries if f["rating"] >= 4)
        neutral = sum(1 for f in entries if f["rating"] == 3)
        negative = sum(1 for f in entries if f["rating"] <= 2)
        return {"product": product, "positive": positive, "neutral": neutral, "negative": negative}

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "collect_feedback":
            return self.collect_feedback(
                task.get("user_id", ""), task.get("product", ""),
                task.get("rating", 3), task.get("comment", ""),
            )
        return super()._run_task(task)


if __name__ == "__main__":
    bot = FeedbackBot()
    bot.start()
    bot.collect_feedback("u1", "CommunicationBot", 5, "Excellent!")
    bot.collect_feedback("u2", "CommunicationBot", 4, "Very good")
    print(bot.sentiment_summary("CommunicationBot"))
    bot.stop()