# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
# Feature 3: Marketing bot for customer feedback.
# Functionality: Collects and analyzes customer feedback on products/services.
# Use Cases: Businesses looking to improve customer satisfaction.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class CustomerFeedbackBot(BaseBot):
    """
    Marketing bot that collects, analyses, and summarises customer feedback.

    Uses sentiment analysis to classify feedback and adaptive learning to
    surface emerging pain points.  Sells labelled feedback datasets to
    NLP researchers and CX analytics firms.
    """

    def __init__(self):
        super().__init__(
            name="Customer Feedback Bot",
            domain="customer_experience",
            category="marketing",
        )
        self._feedback_counts = {"positive": 0, "negative": 0, "neutral": 0}

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Customer Feedback Sentiment Dataset",
            description="500K labelled customer-feedback entries with NPS scores and categories.",
            domain="customer_experience",
            size_mb=140.0,
            price_usd=199.00,
            license="CC-BY-4.0",
            tags=["feedback", "sentiment", "NPS", "CX", "NLP"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        sentiment = nlp_result["sentiment"]
        score = nlp_result["sentiment_score"]
        prefix = self._emotion_prefix()

        self._feedback_counts[sentiment] = self._feedback_counts.get(sentiment, 0) + 1

        if intent == "feedback" or sentiment != "neutral":
            emoji = "😊" if sentiment == "positive" else ("😟" if sentiment == "negative" else "😐")
            self.learning.reinforce("feedback", reward=score)
            response = (
                f"{prefix}Thank you for sharing! {emoji} "
                f"I've recorded your **{sentiment}** feedback (score: {score:+.2f}). "
                f"Feedback summary so far: "
                f"👍 {self._feedback_counts['positive']}  "
                f"👎 {self._feedback_counts['negative']}  "
                f"➖ {self._feedback_counts['neutral']}"
            )
        elif intent == "greeting":
            response = (
                f"{prefix}Hi! I'm {self.name}. Share your experience and I'll "
                "analyse your feedback to help improve products and services."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer labelled customer feedback datasets."
                + self._dataset_offer()
            )
        elif intent == "help":
            response = (
                "I can: 📝 Collect feedback  |  😊 Analyse sentiment  |  "
                "📈 Summarise trends  |  💾 Sell feedback datasets."
            )
        else:
            response = (
                f"{prefix}Please share your thoughts on our product or service. "
                "Your feedback helps us improve!"
            )
        return response


if __name__ == "__main__":
    bot = CustomerFeedbackBot()
    print(bot.chat("The new dashboard is really intuitive and fast!"))
    print(bot.chat("The mobile app crashes when I try to upload files."))
    print(bot.status())
