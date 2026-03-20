"""
DreamCo Auto-Bot Factory — Learning Loop

Monitors bot performance, identifies underperformers, and triggers
autonomous optimization cycles.  Integrates with the control center,
bot generator, and revenue tracker to form a continuous improvement loop.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Learning Loop
# ---------------------------------------------------------------------------

class LearningLoopError(Exception):
    """Raised when the learning loop encounters an unrecoverable state."""


class LearningLoop:
    """
    DreamCo Auto-Bot Factory — Learning Loop.

    Tracks per-bot performance scores, detects underperformers, and
    triggers the generator to create optimized replacement bots.

    Parameters
    ----------
    control_center : any
        Reference to the main DreamCo control center (duck-typed).
    generator : any
        Bot generator with a ``create_bot(name)`` method.
    underperform_threshold : int
        Bots scoring below this value (0–100) are flagged as
        underperformers and queued for optimization.

    Usage::

        loop = LearningLoop(control_center, generator, underperform_threshold=30)
        loop.track_performance("lead_gen_bot", score=25)
        loop.optimize()  # creates "lead_gen_bot_optimized"
    """

    def __init__(
        self,
        control_center: Any,
        generator: Any,
        underperform_threshold: int = 30,
    ) -> None:
        self._control_center = control_center
        self._generator = generator
        self.underperform_threshold = underperform_threshold
        self._performance_log: List[Dict] = []
        self._optimization_history: List[Dict] = []

    # ------------------------------------------------------------------
    # Performance tracking
    # ------------------------------------------------------------------

    def track_performance(self, bot_name: str, score: float) -> dict:
        """
        Record a performance score for *bot_name*.

        Parameters
        ----------
        bot_name : str
            Name of the bot being tracked.
        score : float
            Performance score in [0, 100].

        Returns
        -------
        dict
            Log entry with bot_name, score, status, and timestamp.
        """
        if not (0 <= score <= 100):
            raise LearningLoopError(f"score must be in [0, 100], got {score}")

        status = (
            "underperforming"
            if score < self.underperform_threshold
            else "healthy"
        )
        entry: Dict = {
            "bot_name": bot_name,
            "score": score,
            "status": status,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        self._performance_log.append(entry)
        return entry

    def get_underperformers(self) -> List[str]:
        """
        Return bot names whose latest score is below the threshold.
        Only the most recent score per bot is considered.
        """
        latest: Dict[str, float] = {}
        for entry in self._performance_log:
            latest[entry["bot_name"]] = entry["score"]
        return [
            name for name, score in latest.items()
            if score < self.underperform_threshold
        ]

    def get_performance_log(self) -> List[Dict]:
        """Return all recorded performance entries."""
        return list(self._performance_log)

    # ------------------------------------------------------------------
    # Optimization
    # ------------------------------------------------------------------

    def optimize(self) -> List[Dict]:
        """
        Trigger optimization for all current underperformers.

        For each underperforming bot, calls
        ``generator.create_bot("{bot}_optimized")`` and logs the result.

        Returns
        -------
        list[dict]
            One optimization record per underperformer.
        """
        underperformers = self.get_underperformers()
        records: List[Dict] = []
        for bot_name in underperformers:
            optimized_name = f"{bot_name}_optimized"
            try:
                self._generator.create_bot(optimized_name)
                status = "optimized"
            except Exception as exc:  # pragma: no cover
                status = f"optimization_failed: {exc}"

            record = {
                "original_bot": bot_name,
                "optimized_bot": optimized_name,
                "status": status,
                "optimized_at": datetime.now(timezone.utc).isoformat(),
            }
            self._optimization_history.append(record)
            records.append(record)
        return records

    def get_optimization_history(self) -> List[Dict]:
        """Return the full history of optimization actions."""
        return list(self._optimization_history)

    # ------------------------------------------------------------------
    # Revenue helpers (used by decision_engine integration)
    # ------------------------------------------------------------------

    def track_revenue(self) -> float:
        """
        Return total revenue tracked by the control center.

        Falls back to reading ``data/revenue.json`` if the control center
        does not expose a ``get_total_revenue`` method.
        """
        if hasattr(self._control_center, "get_total_revenue"):
            return float(self._control_center.get_total_revenue())
        # Fallback: read from persistent store
        revenue_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "revenue.json"
        )
        try:
            with open(revenue_path, encoding="utf-8") as fh:
                data = json.load(fh)
            return float(data.get("total_revenue_usd", 0.0))
        except (OSError, json.JSONDecodeError, ValueError):
            return 0.0

    def count_leads(self) -> int:
        """
        Return the number of tracked leads.

        Falls back to reading ``data/leads.json`` (one JSON object per line)
        if the control center does not expose a ``count_leads`` method.
        """
        if hasattr(self._control_center, "count_leads"):
            return int(self._control_center.count_leads())
        leads_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "leads.json"
        )
        try:
            with open(leads_path, encoding="utf-8") as fh:
                lines = [l for l in fh.readlines() if l.strip()]
            return len(lines)
        except OSError:
            return 0

    # ------------------------------------------------------------------
    # Framework entry point
    # ------------------------------------------------------------------

    def run(self) -> str:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        underperformers = self.get_underperformers()
        return (
            f"LearningLoop active — "
            f"{len(self._performance_log)} performance log entries, "
            f"{len(underperformers)} underperformer(s) detected."
        )
