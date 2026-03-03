# Feature 1: Business bot for scheduling meetings.
# Functionality: Integrates with calendars to check availability and schedule meetings.
# Use Cases: Teams needing to coordinate schedules.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class MeetingSchedulerBot(BaseBot):
    """
    Business bot that assists with meeting scheduling and calendar coordination.

    Integrates with calendar APIs (stub), detects scheduling intent,
    and sells anonymised scheduling-pattern datasets to productivity companies.
    """

    def __init__(self):
        super().__init__(
            name="Meeting Scheduler Bot",
            domain="business_productivity",
            category="business",
        )
        self._scheduled_meetings = []

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Corporate Meeting Patterns Dataset",
            description="Anonymised meeting metadata (duration, size, frequency) from 500 companies.",
            domain="business_productivity",
            size_mb=60.0,
            price_usd=129.00,
            license="Proprietary",
            tags=["meetings", "productivity", "scheduling", "enterprise"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()
        numbers = nlp_result.get("entities", {}).get("numbers", [])

        if intent == "schedule":
            meeting_id = f"MTG-{len(self._scheduled_meetings) + 1:04d}"
            self._scheduled_meetings.append({"id": meeting_id, "user": user_id})
            response = (
                f"{prefix}I've started scheduling your meeting (ID: {meeting_id}). "
                "Please provide the attendees, preferred date/time, and agenda, "
                "and I'll send out calendar invites."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer corporate meeting-pattern datasets for productivity research."
                + self._dataset_offer()
            )
        elif intent == "greeting":
            response = (
                f"{prefix}Hi! I'm {self.name}. I'll help coordinate your team's schedule. "
                "Do you need to book a meeting or check availability?"
            )
        elif intent == "help":
            response = (
                "I can: 📅 Schedule meetings  |  ✅ Check calendar availability  |  "
                "📤 Send invites  |  📊 Sell scheduling-pattern datasets."
            )
        else:
            response = (
                f"{prefix}I can help schedule your next meeting. "
                "Who are the attendees and when are you looking to meet?"
            )
        return response


if __name__ == "__main__":
    bot = MeetingSchedulerBot()
    print(bot.chat("Hello! I need to schedule a team meeting for next Monday."))
    print(bot.chat("The meeting is with Alice, Bob, and Carol at 10am."))
    print(bot.status())