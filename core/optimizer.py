"""
DreamCo Optimizer — Self-Improving Loop

Evaluates bot output and recommends the optimal next action:
  - "Change strategy"    → conversion rate too low
  - "Scale aggressively" → revenue above target
  - "Maintain"           → stable performance

Can also batch-evaluate a list of bot outputs and produce a
ranked recommendation report for the operator dashboard.
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Thresholds (tunable)
# ---------------------------------------------------------------------------

LOW_CONVERSION_THRESHOLD = 0.05
SCALE_REVENUE_THRESHOLD = 1_000.0
HIGH_LEAD_THRESHOLD = 10


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class OptimizationResult:
    """Result of evaluating a single bot output."""

    bot_name: str
    recommendation: str
    revenue: float
    conversion_rate: float
    leads_generated: int
    priority_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "bot_name": self.bot_name,
            "recommendation": self.recommendation,
            "revenue": round(self.revenue, 2),
            "conversion_rate": round(self.conversion_rate, 4),
            "leads_generated": self.leads_generated,
            "priority_score": round(self.priority_score, 4),
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Optimizer
# ---------------------------------------------------------------------------


class Optimizer:
    """
    Evaluates bot output dictionaries and recommends scaling decisions.

    Usage
    -----
    opt = Optimizer()
    recommendation = opt.improve({"revenue": 200, "conversion_rate": 0.4})
    report = opt.evaluate_all([...list of bot outputs...])
    """

    def __init__(
        self,
        low_conversion_threshold: float = LOW_CONVERSION_THRESHOLD,
        scale_revenue_threshold: float = SCALE_REVENUE_THRESHOLD,
        high_lead_threshold: int = HIGH_LEAD_THRESHOLD,
    ) -> None:
        self.low_conversion_threshold = low_conversion_threshold
        self.scale_revenue_threshold = scale_revenue_threshold
        self.high_lead_threshold = high_lead_threshold
        self._history: List[OptimizationResult] = []

    # ------------------------------------------------------------------
    # Core recommendation
    # ------------------------------------------------------------------

    def improve(self, bot_output: dict) -> str:
        """
        Return a single string recommendation for a bot output.

        Parameters
        ----------
        bot_output : dict with keys "revenue", "conversion_rate",
                     "leads_generated" (all optional, default 0).
        """
        revenue = float(bot_output.get("revenue", 0))
        conversion_rate = float(bot_output.get("conversion_rate", 0.0))

        if conversion_rate < self.low_conversion_threshold:
            return "Change strategy"
        elif revenue > self.scale_revenue_threshold:
            return "Scale aggressively"
        return "Maintain"

    def evaluate(self, bot_name: str, bot_output: dict) -> OptimizationResult:
        """
        Evaluate a named bot and return a full OptimizationResult.
        """
        revenue = float(bot_output.get("revenue", 0))
        conversion_rate = float(bot_output.get("conversion_rate", 0.0))
        leads_generated = int(bot_output.get("leads_generated", 0))

        recommendation = self.improve(bot_output)

        # Priority score: weighted combination for dashboard ranking
        priority_score = (
            (revenue / max(self.scale_revenue_threshold, 1)) * 0.5
            + conversion_rate * 0.3
            + (leads_generated / max(self.high_lead_threshold, 1)) * 0.2
        )

        result = OptimizationResult(
            bot_name=bot_name,
            recommendation=recommendation,
            revenue=revenue,
            conversion_rate=conversion_rate,
            leads_generated=leads_generated,
            priority_score=priority_score,
        )
        self._history.append(result)
        return result

    def evaluate_all(self, bot_outputs: List[Dict]) -> List[dict]:
        """
        Evaluate a list of ``{"bot_name": ..., "output": {...}}`` dicts.

        Returns results sorted by priority_score descending.
        """
        results = []
        for item in bot_outputs:
            bot_name = item.get("bot_name", "unknown")
            output = item.get("output", item)
            result = self.evaluate(bot_name, output)
            results.append(result.to_dict())
        results.sort(key=lambda r: r["priority_score"], reverse=True)
        return results

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def get_history(self) -> List[dict]:
        """Return all evaluation records."""
        return [r.to_dict() for r in self._history]

    def get_top_performers(self, n: int = 5) -> List[dict]:
        """Return the top-n bots by priority score."""
        return sorted(
            [r.to_dict() for r in self._history],
            key=lambda r: r["priority_score"],
            reverse=True,
        )[:n]
