"""
bots/hustle-bot/hustle_bot.py

HustleBot — tracks side hustles, goals, and revenue opportunities.
"""

from __future__ import annotations

import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

logger = logging.getLogger(__name__)

_OPPORTUNITY_CATALOG: dict[str, list[dict[str, Any]]] = {
    "freelance": [
        {"name": "Freelance Writing", "platform": "Upwork", "avg_hourly": 35},
        {"name": "Graphic Design", "platform": "Fiverr", "avg_hourly": 45},
        {"name": "Web Development", "platform": "Toptal", "avg_hourly": 80},
    ],
    "ecommerce": [
        {"name": "Dropshipping", "platform": "Shopify", "startup_cost": 300},
        {"name": "Print-on-Demand", "platform": "Printful", "startup_cost": 0},
        {"name": "Handmade Crafts", "platform": "Etsy", "startup_cost": 50},
    ],
    "content": [
        {"name": "YouTube Channel", "platform": "YouTube", "avg_monthly": 500},
        {"name": "Blogging", "platform": "WordPress", "avg_monthly": 200},
        {"name": "Podcast", "platform": "Spotify", "avg_monthly": 150},
    ],
    "investing": [
        {"name": "Dividend Stocks", "platform": "Robinhood", "min_investment": 100},
        {"name": "Real Estate Crowdfunding", "platform": "Fundrise", "min_investment": 10},
        {"name": "Peer-to-Peer Lending", "platform": "LendingClub", "min_investment": 25},
    ],
}


class HustleBot(BotBase):
    """
    Tracks side hustles, goals, and revenue opportunities.

    Extends :class:`~bots.bot_base.BotBase` with hustle-specific operations.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="HustleBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._goals: dict[str, dict[str, Any]] = {}
        self._progress: dict[str, list[dict[str, Any]]] = {}
        self._lock_extra: threading.RLock = threading.RLock()

    # ------------------------------------------------------------------
    # BotBase abstract methods
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Mark bot as running."""
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("HustleBot started.")

    def stop(self) -> None:
        """Mark bot as stopped."""
        self._set_running(False)
        self.log_activity("HustleBot stopped.")

    # ------------------------------------------------------------------
    # Hustle-specific API
    # ------------------------------------------------------------------

    def find_opportunities(self, category: str) -> list[dict[str, Any]]:
        """
        Return a list of side-hustle opportunities for *category*.

        Args:
            category: One of ``freelance``, ``ecommerce``, ``content``,
                      ``investing``, or ``all``.

        Returns:
            List of opportunity dicts.
        """
        cat = category.lower().strip()
        if cat == "all":
            all_opps: list[dict[str, Any]] = []
            for opps in _OPPORTUNITY_CATALOG.values():
                all_opps.extend(opps)
            self.log_activity(f"Found {len(all_opps)} opportunities (all categories).")
            return all_opps
        opps = _OPPORTUNITY_CATALOG.get(cat, [])
        self.log_activity(f"Found {len(opps)} opportunities in category '{cat}'.")
        return list(opps)

    def set_goal(self, goal: str, target_amount: float) -> str:
        """
        Create a new hustle goal.

        Args:
            goal: Goal description.
            target_amount: Monetary target.

        Returns:
            The generated goal ID.
        """
        goal_id = str(uuid.uuid4())
        with self._lock_extra:
            self._goals[goal_id] = {
                "id": goal_id,
                "description": goal,
                "target_amount": float(target_amount),
                "current_amount": 0.0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
            }
            self._progress[goal_id] = []
        self.log_activity(f"Goal '{goal}' created (target: {target_amount}).")
        return goal_id

    def track_progress(self, goal_id: str) -> dict[str, Any]:
        """
        Return progress details for a goal.

        Args:
            goal_id: The goal's ID.

        Returns:
            Dict with goal details and progress history.

        Raises:
            KeyError: If *goal_id* is unknown.
        """
        with self._lock_extra:
            goal = self._goals.get(goal_id)
            if goal is None:
                raise KeyError(f"Goal '{goal_id}' not found.")
            progress = list(self._progress.get(goal_id, []))
            pct = (
                round(goal["current_amount"] / goal["target_amount"] * 100, 2)
                if goal["target_amount"] > 0
                else 0.0
            )
            return {
                **goal,
                "progress_pct": pct,
                "progress_history": progress,
            }

    def record_earning(self, goal_id: str, amount: float, note: str = "") -> None:
        """
        Record earnings towards a goal.

        Args:
            goal_id: Target goal ID.
            amount: Amount earned.
            note: Optional note.
        """
        with self._lock_extra:
            goal = self._goals.get(goal_id)
            if goal is None:
                raise KeyError(f"Goal '{goal_id}' not found.")
            goal["current_amount"] = round(goal["current_amount"] + amount, 2)
            if goal["current_amount"] >= goal["target_amount"]:
                goal["status"] = "completed"
            self._progress[goal_id].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "amount": amount,
                "note": note,
                "running_total": goal["current_amount"],
            })
        self.log_activity(f"Earned {amount} towards goal '{goal_id}'.")

    def generate_action_plan(self, goal_id: str) -> list[str]:
        """
        Generate a step-by-step action plan for reaching a goal.

        Args:
            goal_id: Goal ID.

        Returns:
            Ordered list of action-step strings.

        Raises:
            KeyError: If *goal_id* is unknown.
        """
        with self._lock_extra:
            goal = self._goals.get(goal_id)
        if goal is None:
            raise KeyError(f"Goal '{goal_id}' not found.")
        target = goal["target_amount"]
        description = goal["description"]
        remaining = max(0.0, target - goal["current_amount"])
        plan = [
            f"1. Define your '{description}' success metrics clearly.",
            f"2. Research the best income streams to reach ${target:.2f}.",
            f"3. Allocate 2 hours per day to hustle activities.",
            f"4. Build an online presence related to '{description}'.",
            f"5. Set weekly milestones (${remaining / 4:.2f} per week if 4 weeks).",
            f"6. Network with others in the same hustle space.",
            f"7. Track every dollar earned and adjust strategy monthly.",
            f"8. Reinvest 20% of earnings to scale the hustle.",
            f"9. Review and celebrate progress at each ${target / 4:.2f} milestone.",
            f"10. Reach goal of ${target:.2f} and set the next challenge.",
        ]
        self.log_activity(f"Action plan generated for goal '{goal_id}'.")
        return plan
