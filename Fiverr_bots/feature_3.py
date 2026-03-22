# Feature 3: Fiverr bot for review generation.
# Functionality: Requests feedback from clients after service is completed.
# Use Cases: Freelancers wanting to build their reputation.
#
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
# See framework/global_ai_sources_flow.py for the full pipeline specification.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow


class FiverrReviewCollector:
    def __init__(self):
        self.flow = GlobalAISourcesFlow(bot_name="FiverrReviewCollector")
        self._reviews = []

    def request_review(self, client_name, service_title, order_id):
        request = {"order_id": order_id, "client_name": client_name, "service_title": service_title, "status": "requested"}
        return request

    def add_review(self, order_id, client_name, rating, comment=""):
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        review = {"order_id": order_id, "client_name": client_name, "rating": rating, "comment": comment}
        self._reviews.append(review)
        return review

    def get_average_rating(self):
        if not self._reviews:
            return 0.0
        return round(sum(r["rating"] for r in self._reviews) / len(self._reviews), 2)

    def run(self):
        return self.flow.run_pipeline(raw_data={"bot": "FiverrReviewCollector", "reviews": len(self._reviews)}, learning_method="supervised")
