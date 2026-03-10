# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
# Feature 3: Fiverr bot for review generation.
# Functionality: Requests feedback from clients after service is completed.
# Use Cases: Freelancers wanting to build their reputation.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot


class FiverrReviewBot(BaseBot):
    """
    Fiverr bot that automates post-delivery review requests and reputation management.

    Sends personalised follow-ups after order completion and tracks review
    sentiment to identify areas for service improvement.
    """

    def __init__(self):
        super().__init__(
            name="Fiverr Review Bot",
            domain="freelance_reputation",
            category="side_hustle",
        )
        self._reviews_collected = 0
        self._avg_rating = 0.0

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Freelancer Review & Rating Dataset",
            description="500K freelancer reviews with star ratings and text feedback.",
            domain="freelance_reputation",
            size_mb=78.0,
            price_usd=119.00,
            license="CC-BY-4.0",
            tags=["reviews", "ratings", "freelance", "sentiment"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        sentiment = nlp_result["sentiment"]
        score = nlp_result["sentiment_score"]
        prefix = self._emotion_prefix()

        if intent == "feedback" or sentiment != "neutral":
            self._reviews_collected += 1
            self._avg_rating = (
                (self._avg_rating * (self._reviews_collected - 1) + (score + 1) * 2.5)
                / self._reviews_collected
            )
            response = (
                f"{prefix}Thank you for the review! 🌟 "
                f"Sentiment: **{sentiment}** (score: {score:+.2f}). "
                f"Running average rating: {self._avg_rating:.1f}/5.0 "
                f"({self._reviews_collected} reviews collected)."
            )
        elif intent == "greeting":
            response = (
                f"{prefix}Hi! I'm {self.name}. I'll help you collect and leverage "
                "client reviews to grow your Fiverr reputation."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer freelancer review and rating datasets."
                + self._dataset_offer()
            )
        elif intent == "help":
            response = (
                "I can: 📨 Send review requests  |  ⭐ Track ratings  |  "
                "💡 Suggest improvements  |  💾 Sell review datasets."
            )
        else:
            response = (
                f"{prefix}Want me to send a review request to your latest client? "
                "Share the client name and completed order ID."
            )
        return response


if __name__ == "__main__":
    bot = FiverrReviewBot()
    print(bot.chat("The client loved my work and said it was exceptional!"))
    print(bot.chat("Another client said the delivery was a bit slow but quality was good."))
    print(bot.status())