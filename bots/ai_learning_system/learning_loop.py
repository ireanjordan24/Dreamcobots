"""
DreamCo AI Learning Loop — Evolution Layer

Tracks bot performance, identifies underperforming bots, suggests or
auto-generates improvements, and optimizes KPIs across the system.

GLOBAL AI SOURCES FLOW compliant.
"""

from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

if TYPE_CHECKING:
    from bots.control_center.controller import Controller
    from bots.bot_generator_bot.generator import Generator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# KPI defaults
# ---------------------------------------------------------------------------

DEFAULT_KPIS = {
    "min_efficiency": 0.6,      # minimum acceptable run-success rate (0–1)
    "min_revenue_usd": 0.0,     # minimum acceptable revenue per cycle
    "target_efficiency": 0.9,   # goal efficiency
    "target_revenue_usd": 100.0,  # goal revenue per cycle
}


class BotPerformanceRecord:
    """Snapshot of a single bot's performance metrics."""

    def __init__(self, bot_name: str) -> None:
        self.bot_name = bot_name
        self.total_runs: int = 0
        self.successful_runs: int = 0
        self.failed_runs: int = 0
        self.total_revenue_usd: float = 0.0
        self.last_updated: str = datetime.now(timezone.utc).isoformat()

    @property
    def efficiency(self) -> float:
        """Run-success rate (0–1)."""
        if self.total_runs == 0:
            return 1.0
        return self.successful_runs / self.total_runs

    @property
    def revenue_per_run(self) -> float:
        if self.total_runs == 0:
            return 0.0
        return round(self.total_revenue_usd / self.total_runs, 4)

    def record_run(self, success: bool, revenue: float = 0.0) -> None:
        self.total_runs += 1
        if success:
            self.successful_runs += 1
        else:
            self.failed_runs += 1
        self.total_revenue_usd += revenue
        self.last_updated = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "bot_name": self.bot_name,
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "efficiency": round(self.efficiency, 4),
            "total_revenue_usd": round(self.total_revenue_usd, 2),
            "revenue_per_run": self.revenue_per_run,
            "last_updated": self.last_updated,
        }


class LearningLoop:
    """
    DreamCo AI Learning Loop — system intelligence and self-improvement engine.

    Responsibilities
    ----------------
    * Track performance metrics (efficiency, revenue) for every registered bot.
    * Analyse underperforming bots and flag them for refactoring.
    * Identify functional gaps and suggest (or auto-generate) new bots.
    * Optimise KPIs and surface actionable insights to the operator.

    Parameters
    ----------
    controller : Controller, optional
        If provided, the loop can pull live run results from the controller's
        last automation cycle and push recommendations back.
    generator : Generator, optional
        If provided, the loop can automatically generate new bots to fill
        identified gaps.
    kpis : dict, optional
        Override default KPI thresholds.
    """

    def __init__(
        self,
        controller: "Controller | None" = None,
        generator: "Generator | None" = None,
        kpis: dict | None = None,
    ) -> None:
        self._controller = controller
        self._generator = generator
        self.kpis: dict = {**DEFAULT_KPIS, **(kpis or {})}
        self._performance: Dict[str, BotPerformanceRecord] = {}
        self._suggestions: List[dict] = []
        self._refactor_log: List[dict] = []
        self._cycle_count: int = 0

    # ------------------------------------------------------------------
    # Performance tracking
    # ------------------------------------------------------------------

    def record_run(self, bot_name: str, success: bool, revenue: float = 0.0) -> BotPerformanceRecord:
        """Record a single run result for *bot_name*."""
        if bot_name not in self._performance:
            self._performance[bot_name] = BotPerformanceRecord(bot_name)
        rec = self._performance[bot_name]
        rec.record_run(success=success, revenue=revenue)
        return rec

    def ingest_cycle_results(self, cycle_results: List[dict]) -> None:
        """
        Parse the output of :meth:`Controller.run_loop` and update tracking.

        Parameters
        ----------
        cycle_results : list[dict]
            Each element is one loop cycle as returned by
            :meth:`~bots.control_center.controller.Controller.run_loop`.
        """
        for cycle in cycle_results:
            bot_results = cycle.get("bot_results", {})
            for bot_name, result in bot_results.items():
                success = result.get("status") == "ok"
                self.record_run(bot_name, success=success)

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyse(self) -> dict:
        """
        Analyse all tracked bots and produce a performance report.

        Returns
        -------
        dict
            ``underperforming``, ``healthy``, ``suggestions``, and KPI summary.
        """
        underperforming: List[dict] = []
        healthy: List[dict] = []

        for bot_name, rec in self._performance.items():
            perf = rec.to_dict()
            issues: List[str] = []

            if rec.efficiency < self.kpis["min_efficiency"]:
                issues.append(
                    f"efficiency {rec.efficiency:.0%} < threshold {self.kpis['min_efficiency']:.0%}"
                )
            if rec.total_revenue_usd < self.kpis["min_revenue_usd"]:
                issues.append(
                    f"revenue ${rec.total_revenue_usd:.2f} < threshold ${self.kpis['min_revenue_usd']:.2f}"
                )

            if issues:
                underperforming.append({**perf, "issues": issues})
            else:
                healthy.append(perf)

        suggestions = self._identify_gaps(healthy, underperforming)
        self._suggestions = suggestions

        return {
            "cycle": self._cycle_count,
            "total_bots_tracked": len(self._performance),
            "underperforming": underperforming,
            "healthy": healthy,
            "suggestions": suggestions,
            "kpis": self.kpis,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _identify_gaps(self, healthy: list, underperforming: list) -> List[dict]:
        """Generate bot suggestions based on coverage gaps."""
        suggestions: List[dict] = []
        healthy_names = {r["bot_name"] for r in healthy}

        # Suggest replacement / refactoring for underperforming bots
        for rec in underperforming:
            suggestions.append({
                "type": "refactor",
                "bot_name": rec["bot_name"],
                "reason": "; ".join(rec.get("issues", ["underperforming"])),
                "action": f"Review and refactor bots/{rec['bot_name']}/ to improve metrics.",
            })

        # Suggest new bots when fewer than 3 healthy bots are tracked
        if len(healthy_names) < 3:
            suggestions.append({
                "type": "new_bot",
                "bot_name": "lead_scraper_bot",
                "reason": "System has fewer than 3 healthy bots — expand coverage.",
                "action": "Generate a new lead-scraping bot to increase revenue potential.",
            })

        return suggestions

    # ------------------------------------------------------------------
    # Auto-refactor / auto-generate
    # ------------------------------------------------------------------

    def refactor_underperforming(self, analysis: dict | None = None) -> List[dict]:
        """
        Log refactor actions for all underperforming bots.

        When a :class:`~bots.bot_generator_bot.generator.Generator` is
        attached, regenerates the bot with a fresh template.

        Parameters
        ----------
        analysis : dict, optional
            Output of :meth:`analyse`.  Runs a fresh analysis when omitted.

        Returns
        -------
        List[dict]
            Log entries for each refactor action taken.
        """
        if analysis is None:
            analysis = self.analyse()

        actions: List[dict] = []
        for rec in analysis.get("underperforming", []):
            bot_name = rec["bot_name"]
            action_entry: dict = {
                "bot_name": bot_name,
                "issues": rec.get("issues", []),
                "action": "refactor",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "result": "logged",
            }

            if self._generator is not None:
                try:
                    gen_result = self._generator.create_bot(
                        bot_name.replace("_", " ").title(),
                        dry_run=False,
                        register=True,
                    )
                    action_entry["result"] = "regenerated"
                    action_entry["gen_result"] = gen_result
                    logger.info("Regenerated underperforming bot: %s", bot_name)
                except Exception as exc:
                    action_entry["result"] = f"error: {exc}"
                    logger.warning("Failed to regenerate bot '%s': %s", bot_name, exc)

            self._refactor_log.append(action_entry)
            actions.append(action_entry)

        return actions

    def auto_generate_suggested_bots(self, analysis: dict | None = None) -> List[dict]:
        """
        Use the attached :class:`Generator` to create any suggested new bots.

        Parameters
        ----------
        analysis : dict, optional
            Output of :meth:`analyse`.  Runs a fresh analysis when omitted.

        Returns
        -------
        List[dict]
            Generation results for each suggested new bot.
        """
        if analysis is None:
            analysis = self.analyse()

        results: List[dict] = []
        for suggestion in analysis.get("suggestions", []):
            if suggestion.get("type") != "new_bot":
                continue
            bot_name = suggestion.get("bot_name", "unnamed_bot")
            if self._generator is not None:
                try:
                    gen_result = self._generator.create_bot(
                        bot_name.replace("_", " ").title(),
                        dry_run=False,
                        register=True,
                    )
                    results.append({"suggestion": suggestion, "result": gen_result, "status": "created"})
                    logger.info("Auto-generated suggested bot: %s", bot_name)
                except Exception as exc:
                    results.append({"suggestion": suggestion, "status": "error", "error": str(exc)})
            else:
                results.append({"suggestion": suggestion, "status": "no_generator"})

        return results

    # ------------------------------------------------------------------
    # Full learning cycle
    # ------------------------------------------------------------------

    def run_cycle(self) -> dict:
        """
        Execute one full learning cycle.

        Steps
        -----
        1. Pull latest run results from controller (if attached).
        2. Analyse all tracked bots.
        3. Refactor underperforming bots.
        4. Auto-generate any suggested new bots.

        Returns
        -------
        dict
            Summary of the cycle.
        """
        self._cycle_count += 1

        # Step 1 — ingest latest controller results
        if self._controller is not None:
            try:
                cycle_results = self._controller.run_loop(iterations=1)
                self.ingest_cycle_results(cycle_results)
            except Exception as exc:
                logger.warning("Could not pull controller results: %s", exc)

        # Step 2 — analyse
        analysis = self.analyse()

        # Step 3 — refactor
        refactor_actions = self.refactor_underperforming(analysis)

        # Step 4 — generate
        gen_results = self.auto_generate_suggested_bots(analysis)

        return {
            "cycle": self._cycle_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis": analysis,
            "refactor_actions": refactor_actions,
            "auto_generated_bots": gen_results,
        }

    # ------------------------------------------------------------------
    # Status / reporting
    # ------------------------------------------------------------------

    def get_performance_report(self) -> dict:
        """Return a full performance snapshot for all tracked bots."""
        return {
            "cycle_count": self._cycle_count,
            "kpis": self.kpis,
            "bots": {name: rec.to_dict() for name, rec in self._performance.items()},
            "refactor_log": list(self._refactor_log),
            "suggestions": list(self._suggestions),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def update_kpis(self, **kwargs: float) -> dict:
        """Update one or more KPI thresholds."""
        for key, value in kwargs.items():
            if key in self.kpis:
                self.kpis[key] = value
                logger.info("KPI updated: %s = %s", key, value)
        return dict(self.kpis)
