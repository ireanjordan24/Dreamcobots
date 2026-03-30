"""
DreamCo Optimizer — Self-Improving Bot System

Analyses bot output and recommends strategic adjustments:
  * Drop what doesn't work (conversion_rate < threshold)
  * Scale what's winning (revenue > threshold)
  * Maintain everything in between

Usage
-----
    from core.optimizer import Optimizer

    opt = Optimizer()
    recommendation = opt.improve(bot_output)
"""

from __future__ import annotations

from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

LOW_CONVERSION_THRESHOLD: float = 0.05   # below 5% → change strategy
HIGH_REVENUE_THRESHOLD: float = 1000.0   # above $1,000 → scale aggressively
MIN_LEADS_THRESHOLD: int = 3             # fewer than 3 leads → expand reach


class Optimizer:
    """
    Analyses bot performance and recommends the next action.

    Methods
    -------
    improve(bot_output) -> str
        Return a single-sentence recommendation for a bot.
    analyse_all(results) -> list of dict
        Analyse a list of bot results and return enriched recommendations.
    """

    def improve(self, bot_output: Dict[str, Any]) -> str:
        """
        Return a strategic recommendation for a single bot output.

        Parameters
        ----------
        bot_output : dict
            Must contain at least one of: ``revenue``, ``conversion_rate``,
            ``leads_generated``.

        Returns
        -------
        str
            One of: "Scale aggressively", "Maintain", "Expand reach",
            "Change strategy", or "Insufficient data".
        """
        revenue: float = float(bot_output.get("revenue", 0))
        conversion_rate: float = float(bot_output.get("conversion_rate", 0.0))
        leads_generated: int = int(bot_output.get("leads_generated", 0))

        if revenue > HIGH_REVENUE_THRESHOLD:
            return "Scale aggressively"

        if leads_generated < MIN_LEADS_THRESHOLD:
            return "Expand reach"

        if conversion_rate < LOW_CONVERSION_THRESHOLD:
            return "Change strategy"

        if revenue > 0:
            return "Maintain"

        return "Expand reach"

    def analyse_all(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyse a list of bot result dicts (as returned by the orchestrator).

        Parameters
        ----------
        results : list of dict
            Each dict should have ``bot`` and ``output`` keys.

        Returns
        -------
        list of dict
            Each element contains ``bot``, ``recommendation``, and
            ``output`` (passthrough).
        """
        enriched: List[Dict[str, Any]] = []
        for result in results:
            bot_name = result.get("bot", "unknown")
            output = result.get("output") or {}
            recommendation = self.improve(output) if output else "Insufficient data"
            enriched.append(
                {
                    "bot": bot_name,
                    "recommendation": recommendation,
                    "output": output,
                }
            )
        return enriched
