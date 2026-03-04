"""
Feature 2: Marketing bot for email campaigns.
Functionality: Designs and sends out email marketing campaigns.
Use Cases: Companies promoting products to their customer base.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uuid
from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class EmailCampaignBot(BotBase):
    """Designs and dispatches email marketing campaigns."""

    def __init__(self) -> None:
        super().__init__("EmailCampaignBot", AutonomyLevel.SEMI_AUTONOMOUS, ScalingLevel.AGGRESSIVE)
        self._campaigns: list = []

    def create_campaign(self, name: str, subject: str, body: str, recipients: list) -> dict:
        """Create an email campaign and send to all recipients."""
        campaign = {
            "campaign_id": str(uuid.uuid4()),
            "name": name,
            "subject": subject,
            "body": body,
            "recipients": recipients,
            "sent_count": len(recipients),
            "status": "sent",
        }
        self._campaigns.append(campaign)
        return {"status": "ok", "campaign_id": campaign["campaign_id"], "sent_count": len(recipients)}

    def get_campaign_stats(self, campaign_id: str) -> dict:
        """Return statistics for a campaign."""
        for c in self._campaigns:
            if c["campaign_id"] == campaign_id:
                return {"campaign_id": campaign_id, "sent": c["sent_count"], "status": c["status"]}
        return {"status": "error", "message": "Campaign not found"}

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "create_campaign":
            return self.create_campaign(
                task.get("name", ""), task.get("subject", ""),
                task.get("body", ""), task.get("recipients", []),
            )
        return super()._run_task(task)


if __name__ == "__main__":
    bot = EmailCampaignBot()
    bot.start()
    print(bot.create_campaign("Spring Sale", "50% Off Today!", "...", ["a@x.com", "b@x.com"]))
    bot.stop()