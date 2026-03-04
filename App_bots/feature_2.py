"""
Feature 2: App bot for user support.
Functionality: Provides customer support through chat interface.
Use Cases: Users needing help with technical issues.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class SupportBot(BotBase):
    """Provides chat-based customer support and ticket management."""

    KNOWN_ISSUES = {
        "login": "Try resetting your password at /reset-password.",
        "payment": "Contact billing@dreamcobots.com for payment issues.",
        "crash": "Please update the app to the latest version and retry.",
        "slow": "Clear your cache and ensure you have a stable internet connection.",
    }

    def __init__(self) -> None:
        super().__init__("SupportBot", AutonomyLevel.SEMI_AUTONOMOUS, ScalingLevel.MODERATE)
        self._tickets: list = []

    def handle_query(self, user_id: str, query: str) -> dict:
        """Return a resolution for a support query or open a ticket."""
        for keyword, resolution in self.KNOWN_ISSUES.items():
            if keyword in query.lower():
                return {"status": "ok", "resolution": resolution, "ticket_opened": False}
        ticket_id = f"TKT-{len(self._tickets) + 1:04d}"
        self._tickets.append({"ticket_id": ticket_id, "user_id": user_id, "query": query, "status": "open"})
        return {"status": "ok", "resolution": "A support agent will contact you shortly.", "ticket_id": ticket_id, "ticket_opened": True}

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "support_query":
            return self.handle_query(task.get("user_id", ""), task.get("query", ""))
        return super()._run_task(task)


if __name__ == "__main__":
    bot = SupportBot()
    bot.start()
    print(bot.handle_query("user-002", "I cannot login to my account"))
    bot.stop()