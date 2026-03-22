# Feature 2: Marketing bot for email campaigns.
# Functionality: Designs and sends out email marketing campaigns.
# Use Cases: Companies promoting products to their customer base.
#
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
# See framework/global_ai_sources_flow.py for the full pipeline specification.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow


class EmailCampaigner:
    def __init__(self):
        self.flow = GlobalAISourcesFlow(bot_name="EmailCampaigner")
        self._campaigns = []
        self._subscribers = []

    def add_subscriber(self, email, name):
        sub = {"email": email, "name": name, "active": True}
        self._subscribers.append(sub)
        return sub

    def create_campaign(self, subject, body, target_segment="all"):
        campaign = {"id": f"campaign_{len(self._campaigns)+1}", "subject": subject, "body": body, "target_segment": target_segment, "status": "draft"}
        self._campaigns.append(campaign)
        return campaign

    def send_campaign(self, campaign_id):
        for c in self._campaigns:
            if c["id"] == campaign_id:
                c["status"] = "sent"
                return {"sent_to": len(self._subscribers), "campaign_id": campaign_id}
        return None

    def run(self):
        return self.flow.run_pipeline(raw_data={"bot": "EmailCampaigner", "campaigns": len(self._campaigns)}, learning_method="supervised")
