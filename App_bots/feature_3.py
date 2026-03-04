"""
Feature 3: App bot for feature updates.
Functionality: Notifies users of new features and updates in the app.
Use Cases: Ensuring users are aware of improvements.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class UpdateNotificationBot(BotBase):
    """Pushes feature update notifications to users."""

    def __init__(self) -> None:
        super().__init__("UpdateNotificationBot", AutonomyLevel.FULLY_AUTONOMOUS, ScalingLevel.MODERATE)
        self._updates: list = []
        self._sent: list = []

    def publish_update(self, version: str, features: list, affected_tiers: list) -> dict:
        """Register a new platform update to be broadcast."""
        update = {"version": version, "features": features, "tiers": affected_tiers}
        self._updates.append(update)
        return {"status": "ok", "version": version, "feature_count": len(features)}

    def notify_users(self, user_ids: list, version: str) -> dict:
        """Send an update notification to a list of users."""
        for user_id in user_ids:
            self._sent.append({"user_id": user_id, "version": version})
        return {"status": "ok", "notified": len(user_ids)}

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "notify_update":
            return self.notify_users(task.get("user_ids", []), task.get("version", ""))
        return super()._run_task(task)


if __name__ == "__main__":
    bot = UpdateNotificationBot()
    bot.start()
    bot.publish_update("2.0.0", ["Dark mode", "Faster search", "New marketplace"], ["premium", "elite"])
    print(bot.notify_users(["user-001", "user-002"], "2.0.0"))
    bot.stop()