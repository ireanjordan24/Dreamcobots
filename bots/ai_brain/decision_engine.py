"""
DreamCo AI Brain — Decision Engine

Replaces the original random-choice decision logic with a weighted,
data-driven decision engine.  The engine analyses three sources of
truth before committing to an action:

  1. Revenue data   — prioritise areas where revenue is lowest.
  2. CRM trends     — surface top-performing and under-performing bots.
  3. Workflow data  — detect bottlenecks (errors / slow cycles) and
                      resolve them first.

The resulting decision is deterministic and explainable: each candidate
action receives a numeric score, and the highest scorer wins.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import logging
import sys
import os
from datetime import datetime, timezone
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, get_tier_config  # noqa: E402

from bots.ai_brain.tiers import BOT_FEATURES, get_bot_tier_info  # noqa: E402
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Action catalogue — each entry describes one possible system action.
# ---------------------------------------------------------------------------

ACTIONS: list[dict[str, Any]] = [
    {
        "key": "scale_leads",
        "label": "Scale lead generation",
        "description": "Create additional lead-generation bots to increase top-of-funnel.",
        "base_score": 0,
    },
    {
        "key": "increase_outreach",
        "label": "Increase sales outreach",
        "description": "Launch more outreach bots to contact existing leads faster.",
        "base_score": 0,
    },
    {
        "key": "build_new_bot",
        "label": "Build a new specialist bot",
        "description": "Generate a new bot to fill an identified capability gap.",
        "base_score": 0,
    },
    {
        "key": "focus_real_estate",
        "label": "Focus on real estate deals",
        "description": "Increase real estate deal-finding activity to capture investment opportunities.",
        "base_score": 0,
    },
    {
        "key": "optimize_sales",
        "label": "Optimize sales pipeline",
        "description": "Tune existing sales bots based on CRM conversion data.",
        "base_score": 0,
    },
    {
        "key": "fix_bottleneck",
        "label": "Fix workflow bottleneck",
        "description": "Resolve detected failure or inefficiency in the current workflow.",
        "base_score": 0,
    },
]

# Revenue threshold (USD) below which lead generation is boosted.
LOW_REVENUE_THRESHOLD = 200.0
# Revenue threshold (USD) above which sales scaling is boosted.
HIGH_REVENUE_THRESHOLD = 1000.0
# Bottleneck error-rate threshold above which fix_bottleneck is boosted.
BOTTLENECK_ERROR_RATE_THRESHOLD = 0.10


class DecisionEngineTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class DecisionEngine:
    """
    Weighted decision engine for the DreamCo AI Brain.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self._decision_history: list[dict[str, Any]] = []

        # GLOBAL AI SOURCES FLOW — mandatory pipeline
        self._flow = GlobalAISourcesFlow(bot_name="DecisionEngine")

        logger.info("DecisionEngine initialised (tier=%s)", tier.value)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Run one decision cycle using default/empty context and return a summary."""
        result = self.make_decision()
        action = result["decision"]["key"]
        reason = result["decision"]["reason"]
        logger.info("Decision: %s — %s", action, reason)
        return f"🧠 Decision: {action} — {reason}"

    def analyze_revenue(self, revenue_data: dict[str, float]) -> dict[str, Any]:
        """
        Analyse per-source revenue figures and return priority signals.

        Parameters
        ----------
        revenue_data : dict[str, float]
            Mapping of revenue source name → USD amount.  For example::

                {"lead_gen": 50.0, "sales": 800.0, "real_estate": 120.0}

        Returns
        -------
        dict with keys:
          - ``total``    : float — sum of all revenue.
          - ``lowest``   : dict  — ``{source, amount}`` for the lowest source.
          - ``highest``  : dict  — ``{source, amount}`` for the highest source.
          - ``signals``  : list  — action keys that should be up-weighted.
        """
        if not revenue_data:
            return {"total": 0.0, "lowest": None, "highest": None, "signals": ["scale_leads"]}

        total = sum(revenue_data.values())
        sorted_sources = sorted(revenue_data.items(), key=lambda kv: kv[1])
        lowest_src, lowest_amt = sorted_sources[0]
        highest_src, highest_amt = sorted_sources[-1]

        signals: list[str] = []

        if total < LOW_REVENUE_THRESHOLD:
            signals.append("scale_leads")
            signals.append("increase_outreach")
        elif total > HIGH_REVENUE_THRESHOLD:
            signals.append("optimize_sales")
            signals.append("build_new_bot")

        if lowest_amt < LOW_REVENUE_THRESHOLD * 0.5 and lowest_src == "lead_gen":
            if "scale_leads" not in signals:
                signals.append("scale_leads")
        if lowest_src == "real_estate" and lowest_amt < LOW_REVENUE_THRESHOLD:
            signals.append("focus_real_estate")

        return {
            "total": round(total, 2),
            "lowest": {"source": lowest_src, "amount": lowest_amt},
            "highest": {"source": highest_src, "amount": highest_amt},
            "signals": signals,
        }

    def analyze_crm_trends(self, crm_data: dict[str, dict]) -> dict[str, Any]:
        """
        Analyse CRM bot-performance data and return trend signals.

        Parameters
        ----------
        crm_data : dict[str, dict]
            Mapping of bot name → performance metrics dict.  Each metrics
            dict should contain at least a ``"conversion_rate"`` key
            (float, 0–1) and optionally ``"leads_generated"`` (int).

            Example::

                {
                    "lead_gen_bot":  {"conversion_rate": 0.08, "leads_generated": 120},
                    "sales_bot":     {"conversion_rate": 0.25, "leads_generated": 40},
                }

        Returns
        -------
        dict with keys:
          - ``top_bot``       : str  — name of the best-performing bot.
          - ``bottom_bot``    : str  — name of the lowest-performing bot.
          - ``signals``       : list — action keys that should be up-weighted.
        """
        if not crm_data:
            return {"top_bot": None, "bottom_bot": None, "signals": []}

        ranked = sorted(
            crm_data.items(),
            key=lambda kv: kv[1].get("conversion_rate", 0.0),
        )
        bottom_name, _ = ranked[0]
        top_name, _ = ranked[-1]

        signals: list[str] = []
        if "lead" in bottom_name.lower():
            signals.append("scale_leads")
        if "sales" in bottom_name.lower():
            signals.append("increase_outreach")
        if "real_estate" in bottom_name.lower():
            signals.append("focus_real_estate")
        # Top performer indicates we should keep the same focus
        if "sales" in top_name.lower():
            if "optimize_sales" not in signals:
                signals.append("optimize_sales")

        return {"top_bot": top_name, "bottom_bot": bottom_name, "signals": signals}

    def detect_bottlenecks(self, workflow_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Detect bottlenecks (errors / slow steps) in workflow execution data.

        Parameters
        ----------
        workflow_data : dict
            Mapping of step name → metrics dict.  Each metrics dict should
            contain at least ``"error_rate"`` (float, 0–1) and optionally
            ``"avg_duration_seconds"`` (float).

            Example::

                {
                    "lead_scraping": {"error_rate": 0.02, "avg_duration_seconds": 3.1},
                    "sms_outreach":  {"error_rate": 0.18, "avg_duration_seconds": 1.2},
                }

        Returns
        -------
        list[dict]
            List of bottleneck entries, each with ``step``, ``error_rate``,
            and ``severity`` (``"high"`` | ``"medium"``).
        """
        bottlenecks: list[dict[str, Any]] = []
        for step, metrics in workflow_data.items():
            error_rate = metrics.get("error_rate", 0.0)
            if error_rate >= BOTTLENECK_ERROR_RATE_THRESHOLD:
                severity = "high" if error_rate >= 0.25 else "medium"
                bottlenecks.append(
                    {"step": step, "error_rate": round(error_rate, 4), "severity": severity}
                )
        return bottlenecks

    def make_decision(
        self,
        revenue_data: dict[str, float] | None = None,
        crm_data: dict[str, dict] | None = None,
        workflow_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Run the weighted decision algorithm and return the top-scored action.

        Each ACTIONS entry starts at ``base_score = 0``.  Signals from the
        three analysis passes each add +10 to the matching action key.
        Detected bottlenecks add +20 to ``fix_bottleneck`` per bottleneck
        found (ensuring it takes priority when the system is broken).

        Parameters
        ----------
        revenue_data : dict, optional
        crm_data : dict, optional
        workflow_data : dict, optional

        Returns
        -------
        dict with keys:
          - ``decision``        : dict with ``key``, ``label``, ``reason``, ``score``.
          - ``all_scores``      : list of ``{key, score}`` sorted descending.
          - ``revenue_analysis``: result of :meth:`analyze_revenue`.
          - ``crm_analysis``    : result of :meth:`analyze_crm_trends`.
          - ``bottlenecks``     : list from :meth:`detect_bottlenecks`.
          - ``timestamp``       : ISO-8601 UTC string.
        """
        revenue_data = revenue_data or {}
        crm_data = crm_data or {}
        workflow_data = workflow_data or {}

        rev_analysis = self.analyze_revenue(revenue_data)
        crm_analysis = self.analyze_crm_trends(crm_data)
        bottlenecks = self.detect_bottlenecks(workflow_data)

        # PRO/ENTERPRISE tiers gain access to CRM and bottleneck analysis.
        use_crm = self.tier in (Tier.PRO, Tier.ENTERPRISE)
        use_bottleneck = self.tier in (Tier.PRO, Tier.ENTERPRISE)

        # Build score map
        scores: dict[str, float] = {a["key"]: 0.0 for a in ACTIONS}

        # Revenue signals
        for sig in rev_analysis.get("signals", []):
            if sig in scores:
                scores[sig] += 10.0

        # CRM signals (PRO+)
        if use_crm:
            for sig in crm_analysis.get("signals", []):
                if sig in scores:
                    scores[sig] += 10.0

        # Bottleneck signals (PRO+) — each bottleneck adds weight
        if use_bottleneck and bottlenecks:
            scores["fix_bottleneck"] += 20.0 * len(bottlenecks)

        # Determine winning action
        best_key = max(scores, key=lambda k: scores[k])

        # Resolve ties deterministically using the canonical ACTIONS order
        max_score = scores[best_key]
        for action in ACTIONS:
            if scores[action["key"]] == max_score:
                best_key = action["key"]
                break

        best_action = next(a for a in ACTIONS if a["key"] == best_key)

        # Build human-readable reason
        reason_parts: list[str] = []
        if best_key in rev_analysis.get("signals", []):
            rev_total = rev_analysis.get("total", 0)
            reason_parts.append(f"revenue=${rev_total:.0f}")
        if use_crm and best_key in crm_analysis.get("signals", []):
            reason_parts.append(f"CRM bottom-bot={crm_analysis.get('bottom_bot', 'n/a')}")
        if use_bottleneck and best_key == "fix_bottleneck" and bottlenecks:
            steps = ", ".join(b["step"] for b in bottlenecks)
            reason_parts.append(f"bottlenecks=[{steps}]")
        reason = "; ".join(reason_parts) if reason_parts else "no specific signal — default action"

        all_scores = sorted(
            [{"key": k, "score": v} for k, v in scores.items()],
            key=lambda x: x["score"],
            reverse=True,
        )

        result = {
            "decision": {
                "key": best_action["key"],
                "label": best_action["label"],
                "description": best_action["description"],
                "score": max_score,
                "reason": reason,
            },
            "all_scores": all_scores,
            "revenue_analysis": rev_analysis,
            "crm_analysis": crm_analysis,
            "bottlenecks": bottlenecks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._decision_history.append(result)
        logger.info(
            "Decision made: %s (score=%.1f) — %s",
            best_key,
            max_score,
            reason,
        )
        return result

    def get_decision_history(self) -> list[dict[str, Any]]:
        """Return all past decisions (newest last)."""
        if self.tier == Tier.FREE:
            raise DecisionEngineTierError(
                "Decision history requires PRO or ENTERPRISE tier."
            )
        return list(self._decision_history)

    def get_tier_info(self) -> dict:
        """Return tier capabilities."""
        return get_bot_tier_info(self.tier)
