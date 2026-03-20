"""
Decision Engine — replaces random AI decisions with real data-driven logic
based on revenue and leads metrics.

Logic:
  - leads < 20  → "scale_leads"
  - revenue < 200 → "increase_outreach"
  - revenue > 1000 → "scale_system"
  - else → "optimize"

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Decision constants
# ---------------------------------------------------------------------------

DECISION_SCALE_LEADS = "scale_leads"
DECISION_INCREASE_OUTREACH = "increase_outreach"
DECISION_SCALE_SYSTEM = "scale_system"
DECISION_OPTIMIZE = "optimize"
DECISION_CREATE_SCALING_BOT = "create_scaling_bot"
DECISION_CREATE_RECOVERY_BOT = "create_recovery_bot"

# Thresholds
LEADS_THRESHOLD_LOW: int = 20
REVENUE_THRESHOLD_LOW: float = 200.0
REVENUE_THRESHOLD_HIGH: float = 1000.0
REVENUE_THRESHOLD_SCALE: float = 1000.0
REVENUE_THRESHOLD_RECOVERY: float = 100.0


# ---------------------------------------------------------------------------
# Decision Engine
# ---------------------------------------------------------------------------

class DecisionEngine:
    """
    Real data-driven decision engine for DreamCo bots.

    Replaces random/fake decisions with logic grounded in real revenue
    and lead metrics.

    Parameters
    ----------
    auto_generate_bots : bool
        When True, the engine recommends creating new bots based on conditions.
    """

    def __init__(self, auto_generate_bots: bool = False) -> None:
        self.auto_generate_bots = auto_generate_bots
        self._decision_log: list[dict] = []

    def run(self, metrics: dict) -> str:
        """
        Evaluate metrics and return the recommended action.

        Parameters
        ----------
        metrics : dict
            Must contain:
            - ``revenue`` (float): Current revenue figure.
            - ``leads`` (int): Current number of leads.

        Returns
        -------
        str
            One of: ``scale_leads``, ``increase_outreach``, ``scale_system``,
            ``optimize``, ``create_scaling_bot``, or ``create_recovery_bot``.
        """
        revenue = float(metrics.get("revenue", 0))
        leads = int(metrics.get("leads", 0))

        decision = self._evaluate(revenue, leads)

        self._decision_log.append({
            "decision": decision,
            "revenue": revenue,
            "leads": leads,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return decision

    def _evaluate(self, revenue: float, leads: int) -> str:
        """Core decision logic."""
        if leads < LEADS_THRESHOLD_LOW:
            return DECISION_SCALE_LEADS

        if revenue < REVENUE_THRESHOLD_LOW:
            return DECISION_INCREASE_OUTREACH

        if revenue > REVENUE_THRESHOLD_HIGH:
            if self.auto_generate_bots:
                return DECISION_CREATE_SCALING_BOT
            return DECISION_SCALE_SYSTEM

        return DECISION_OPTIMIZE

    def evaluate_for_bot_creation(self, revenue: float) -> Optional[str]:
        """
        Determine if a new bot should be created based on revenue.

        Returns
        -------
        str or None
            Bot type to create, or None if no action needed.
        """
        if revenue > REVENUE_THRESHOLD_SCALE:
            return "scaling_bot"
        if revenue < REVENUE_THRESHOLD_RECOVERY:
            return "recovery_bot"
        return None

    def get_decision_log(self) -> list[dict]:
        """Return the full decision history."""
        return list(self._decision_log)

    def get_latest_decision(self) -> Optional[dict]:
        """Return the most recent decision entry."""
        return self._decision_log[-1] if self._decision_log else None

    def get_decision_summary(self) -> dict:
        """Return a summary of all decisions made."""
        if not self._decision_log:
            return {"total": 0, "decisions": {}}
        counts: dict[str, int] = {}
        for entry in self._decision_log:
            d = entry["decision"]
            counts[d] = counts.get(d, 0) + 1
        return {
            "total": len(self._decision_log),
            "decisions": counts,
            "latest": self._decision_log[-1]["decision"],
        }
