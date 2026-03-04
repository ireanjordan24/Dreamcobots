"""
Feature 1: App bot for user onboarding.
Functionality: Guides new users through the app setup process.
Use Cases: Improving user retention rates.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class OnboardingBot(BotBase):
    """Guides new users through the app setup process."""

    def __init__(self) -> None:
        super().__init__("OnboardingBot", AutonomyLevel.SEMI_AUTONOMOUS, ScalingLevel.MODERATE)
        self._onboarded_users: list = []

    def onboard_user(self, user_id: str, preferences: dict) -> dict:
        """Walk a new user through the setup flow and record completion."""
        steps = ["create_profile", "set_preferences", "connect_integrations", "tour_dashboard"]
        results = {step: "complete" for step in steps}
        self._onboarded_users.append({"user_id": user_id, "preferences": preferences, "steps": results})
        return {"status": "ok", "user_id": user_id, "steps_completed": steps}

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "onboard":
            return self.onboard_user(task.get("user_id", ""), task.get("preferences", {}))
        return super()._run_task(task)


if __name__ == "__main__":
    bot = OnboardingBot()
    bot.start()
    result = bot.onboard_user("user-001", {"theme": "dark", "notifications": True})
    print(result)
    bot.stop()