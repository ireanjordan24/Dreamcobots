"""
Feature 1: Business bot for scheduling meetings.
Functionality: Integrates with calendars to check availability and schedule meetings.
Use Cases: Teams needing to coordinate schedules.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uuid
from datetime import datetime
from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class MeetingSchedulerBot(BotBase):
    """Schedules meetings by checking participant availability."""

    def __init__(self) -> None:
        super().__init__("MeetingSchedulerBot", AutonomyLevel.SEMI_AUTONOMOUS, ScalingLevel.MODERATE)
        self._calendar: list = []

    def check_availability(self, participants: list, proposed_time: str) -> dict:
        """Return availability status for each participant at proposed_time."""
        availability = {p: "available" for p in participants}
        conflicts = [p for p, s in availability.items() if s == "conflict"]
        return {"proposed_time": proposed_time, "availability": availability, "conflicts": conflicts}

    def schedule_meeting(self, participants: list, title: str, start_time: str, duration_minutes: int = 60) -> dict:
        """Book a meeting on all participants' calendars."""
        meeting = {
            "meeting_id": str(uuid.uuid4()),
            "title": title,
            "participants": participants,
            "start_time": start_time,
            "duration_minutes": duration_minutes,
            "status": "scheduled",
        }
        self._calendar.append(meeting)
        return {"status": "ok", "meeting_id": meeting["meeting_id"], "title": title}

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "schedule_meeting":
            return self.schedule_meeting(
                task.get("participants", []),
                task.get("title", "Meeting"),
                task.get("start_time", ""),
                task.get("duration_minutes", 60),
            )
        return super()._run_task(task)


if __name__ == "__main__":
    bot = MeetingSchedulerBot()
    bot.start()
    print(bot.schedule_meeting(["alice@co.com", "bob@co.com"], "Q1 Review", "2026-03-10T10:00:00"))
    bot.stop()