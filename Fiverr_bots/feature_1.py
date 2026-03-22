# Feature 1: Fiverr bot for service listings.
# Functionality: Automatically lists services on Fiverr based on user input.
# Use Cases: Freelancers wanting to attract clients.
#
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
# See framework/global_ai_sources_flow.py for the full pipeline specification.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow


class FiverrServiceLister:
    def __init__(self):
        self.flow = GlobalAISourcesFlow(bot_name="FiverrServiceLister")
        self._listings = []

    def create_listing(self, title, description, price_usd, delivery_days, category="general"):
        listing = {"id": f"listing_{len(self._listings)+1}", "title": title, "description": description, "price_usd": price_usd, "delivery_days": delivery_days, "category": category, "active": True}
        self._listings.append(listing)
        return listing

    def get_listings(self, category=None):
        if category:
            return [l for l in self._listings if l["category"] == category]
        return list(self._listings)

    def deactivate_listing(self, listing_id):
        for l in self._listings:
            if l["id"] == listing_id:
                l["active"] = False
                return True
        return False

    def run(self):
        return self.flow.run_pipeline(raw_data={"bot": "FiverrServiceLister", "listings": len(self._listings)}, learning_method="supervised")
