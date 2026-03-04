"""
Feature 2: Real estate bot for scheduling viewings.
Functionality: Allows users to schedule property viewings via chat.
Use Cases: Prospective buyers wanting to view properties.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uuid
from datetime import date
from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class ViewingSchedulerBot(BotBase):
    """Schedules property viewings for prospective buyers and renters."""

    def __init__(self) -> None:
        super().__init__("ViewingSchedulerBot", AutonomyLevel.SEMI_AUTONOMOUS, ScalingLevel.MODERATE)
        self._viewings: list = []

    def schedule_viewing(self, property_id: str, buyer_name: str, viewing_date: str, time_slot: str) -> dict:
        """Book a viewing slot for a property."""
        viewing = {
            "viewing_id": str(uuid.uuid4()),
            "property_id": property_id,
            "buyer_name": buyer_name,
            "viewing_date": viewing_date,
            "time_slot": time_slot,
            "status": "confirmed",
        }
        self._viewings.append(viewing)
        return {"status": "ok", "viewing_id": viewing["viewing_id"], "confirmed": True}

    def cancel_viewing(self, viewing_id: str) -> dict:
        """Cancel an existing viewing."""
        for v in self._viewings:
            if v["viewing_id"] == viewing_id:
                v["status"] = "cancelled"
                return {"status": "ok", "message": "Viewing cancelled"}
        return {"status": "error", "message": "Viewing not found"}

    def get_viewings(self, property_id: str = None) -> list:
        """Return all (or property-filtered) viewings."""
        if property_id:
            return [v for v in self._viewings if v["property_id"] == property_id]
        return list(self._viewings)

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "schedule_viewing":
            return self.schedule_viewing(
                task.get("property_id", ""), task.get("buyer_name", ""),
                task.get("viewing_date", ""), task.get("time_slot", ""),
            )
        return super()._run_task(task)


if __name__ == "__main__":
    bot = ViewingSchedulerBot()
    bot.start()
    result = bot.schedule_viewing("prop-001", "Alice Brown", "2026-03-15", "10:00 AM")
    print(result)
    bot.stop()