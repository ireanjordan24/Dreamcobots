# Feature 3: Marketing bot for customer feedback.
# Functionality: Collects and analyzes customer feedback on products/services.
# Use Cases: Businesses looking to improve customer satisfaction.
#
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
# See framework/global_ai_sources_flow.py for the full pipeline specification.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow


class FeedbackAnalyzer:
    def __init__(self):
        self.flow = GlobalAISourcesFlow(bot_name="FeedbackAnalyzer")
        self._feedback = []

    def _analyze_sentiment(self, text):
        text_lower = text.lower()
        positive_words = ["great", "excellent", "love", "amazing", "good", "fantastic", "wonderful", "perfect"]
        negative_words = ["bad", "terrible", "awful", "hate", "poor", "horrible", "worst", "disappointing"]
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"

    def add_feedback(self, customer_name, product, feedback_text, rating=None):
        sentiment = self._analyze_sentiment(feedback_text)
        entry = {"customer_name": customer_name, "product": product, "feedback_text": feedback_text, "rating": rating, "sentiment": sentiment}
        self._feedback.append(entry)
        return entry

    def get_summary(self):
        if not self._feedback:
            return {"total": 0, "positive": 0, "negative": 0, "neutral": 0}
        sentiments = [f["sentiment"] for f in self._feedback]
        return {"total": len(self._feedback), "positive": sentiments.count("positive"), "negative": sentiments.count("negative"), "neutral": sentiments.count("neutral")}

    def run(self):
        return self.flow.run_pipeline(raw_data={"bot": "FeedbackAnalyzer", "feedback_count": len(self._feedback)}, learning_method="supervised")
