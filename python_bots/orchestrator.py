"""
DreamCo Python Bot Orchestrator
================================

Centralized orchestrator for DreamCo Python bots.  Manages a registry
of sub-bots, dispatches runs, collects results, and drives the learning
loop for continuous improvement.

The orchestrator follows the event-bus pattern from ``python_bots/base_bot.py``
and integrates with:
  * ``bots.ai_learning_system.learning_loop.LearningLoop`` — performance tracking
  * ``bots.bot_library_manager.BotLibraryManager`` — library/knowledge storage

Usage
-----
    from python_bots.orchestrator import PythonBotOrchestrator
    from python_bots.base_bot import BaseBot
    from event_bus.base_bus import BaseEventBus

    class MyBot(BaseBot):
        def run(self, event_bus):
            event_bus.publish("my_bot.done", {"revenue": 42.0})

    orch = PythonBotOrchestrator()
    orch.register(MyBot("my_bot"))
    summary = orch.run_all()
    print(summary)
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from event_bus.base_bus import BaseEventBus
from python_bots.base_bot import BaseBot


# ---------------------------------------------------------------------------
# Orchestrator uses the existing BaseEventBus directly
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# PythonBotOrchestrator
# ---------------------------------------------------------------------------

class PythonBotOrchestrator:
    """
    Centralized orchestrator that manages and runs Python sub-bots.

    Each sub-bot is a :class:`~python_bots.base_bot.BaseBot` subclass
    registered via :meth:`register`.  The orchestrator creates a fresh
    ``_InMemoryEventBus`` per run, dispatches all bots, and collects
    their results.

    Parameters
    ----------
    learning_loop : optional
        A ``LearningLoop`` instance for performance tracking.  When
        provided, each bot run is recorded automatically.
    db_manager : optional
        A ``BotLibraryManager`` instance for library/knowledge tracking.
    """

    def __init__(
        self,
        learning_loop=None,
        db_manager=None,
    ) -> None:
        self._bots: Dict[str, BaseBot] = {}
        self._learning_loop = learning_loop
        self._db = db_manager
        self._run_history: List[dict] = []

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, bot: BaseBot) -> None:
        """Register a sub-bot with the orchestrator.

        Parameters
        ----------
        bot : BaseBot
            The bot instance to register.
        """
        self._bots[bot.name] = bot

    def unregister(self, bot_name: str) -> bool:
        """Remove a registered bot by name.

        Returns
        -------
        bool
            True if the bot was found and removed, False otherwise.
        """
        if bot_name in self._bots:
            del self._bots[bot_name]
            return True
        return False

    @property
    def registered_bots(self) -> List[str]:
        """Return names of all registered sub-bots."""
        return list(self._bots.keys())

    # ------------------------------------------------------------------
    # Running bots
    # ------------------------------------------------------------------

    def run_bot(self, bot_name: str) -> dict:
        """Run a single registered bot by name.

        Parameters
        ----------
        bot_name : str
            Name of the bot to run.

        Returns
        -------
        dict
            Result dict with keys ``bot``, ``status``, ``events``,
            and optionally ``error``.
        """
        bot = self._bots.get(bot_name)
        if bot is None:
            return {"bot": bot_name, "status": "error", "error": "Bot not registered"}

        bus = BaseEventBus()
        result: dict = {"bot": bot_name, "status": "ok", "events": []}
        try:
            bot.run(bus)
            result["events"] = bus.get_events()
        except Exception as exc:  # noqa: BLE001
            result["status"] = "error"
            result["error"] = str(exc)

        # Track in learning loop
        if self._learning_loop is not None:
            revenue = self._extract_revenue(bus.get_events())
            self._learning_loop.record_run(
                bot_name,
                success=(result["status"] == "ok"),
                revenue=revenue,
            )

        self._run_history.append(result)
        return result

    def run_all(self) -> dict:
        """Run all registered sub-bots and return a consolidated summary.

        Returns
        -------
        dict
            Keys: ``bots_run``, ``successful``, ``failed``, ``results``,
            ``timestamp``.
        """
        results = [self.run_bot(name) for name in list(self._bots.keys())]
        successful = [r for r in results if r["status"] == "ok"]
        failed = [r for r in results if r["status"] == "error"]

        # Trigger a learning-loop cycle after all bots have run
        if self._learning_loop is not None:
            self._learning_loop.run_cycle()

        return {
            "bots_run": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Return a summary of all runs since this orchestrator was created."""
        total = len(self._run_history)
        ok = sum(1 for r in self._run_history if r["status"] == "ok")
        return {
            "total_runs": total,
            "successful_runs": ok,
            "failed_runs": total - ok,
            "registered_bots": len(self._bots),
            "bot_names": list(self._bots.keys()),
        }

    def get_run_history(self) -> List[dict]:
        """Return all historical run records."""
        return list(self._run_history)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_revenue(events: List[dict]) -> float:
        """Sum revenue values from bus events."""
        total = 0.0
        for ev in events:
            payload = ev.get("data") or {}
            if isinstance(payload, dict):
                total += float(payload.get("revenue", 0))
        return total
