"""
Deep Learning System for DreamCobots
=====================================

Provides three coordinated engines:

  • APIScraperEngine        — catalogues and studies the top-1000 APIs per category
  • CompetitorAnalysisEngine — tracks competitor pricing, features, and user sentiment
  • SandboxTestingEngine    — safe isolated execution environment for bot candidates

All engines run until the June 22, 2026 go-live deadline and are orchestrated
by BuddyOrchestrator via :class:`DeepLearningCoordinator`.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.deep_learning_system import DeepLearningCoordinator

    coordinator = DeepLearningCoordinator()
    coordinator.register_bot("sales_bot", category="sales")
    coordinator.run_learning_cycle("sales_bot")
    status = coordinator.learning_status()
"""

from __future__ import annotations

import os
import sys
from datetime import date, datetime, timezone
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)
except ImportError:
    GlobalAISourcesFlow = None  # type: ignore[assignment,misc]

from bots.deep_learning_system.api_scraper import APIScraperEngine
from bots.deep_learning_system.competitor_analysis import CompetitorAnalysisEngine
from bots.deep_learning_system.sandbox_tester import SandboxTestingEngine

# ---------------------------------------------------------------------------
# Go-live deadline (shared with DataScrapeLifecycle)
# ---------------------------------------------------------------------------
LEARNING_DEADLINE: date = date(2026, 6, 22)


class DeepLearningCoordinator:
    """
    Central coordinator for all bot deep-learning activities.

    Registers bots across three specialised engines (API scraping,
    competitor analysis, sandbox testing), runs coordinated learning
    cycles, and exposes aggregated status / progress metrics for
    consumption by the React Dashboard and BuddyOrchestrator.

    Parameters
    ----------
    deadline : date
        Learning and scraping deadline.  Defaults to June 22, 2026.
    """

    def __init__(self, deadline: date = LEARNING_DEADLINE) -> None:
        self.deadline = deadline
        self.api_scraper = APIScraperEngine(deadline=deadline)
        self.competitor_analysis = CompetitorAnalysisEngine(deadline=deadline)
        self.sandbox_tester = SandboxTestingEngine(deadline=deadline)
        self._bot_categories: dict[str, str] = {}
        self._cycle_log: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_bot(self, bot_id: str, category: str = "general") -> dict:
        """Register a bot for deep learning across all engines.

        Parameters
        ----------
        bot_id : str
            Unique identifier for the bot.
        category : str
            Bot category (e.g. ``"sales"``, ``"fiverr"``, ``"marketing"``).
        """
        self._bot_categories[bot_id] = category
        self.api_scraper.register(bot_id, category)
        self.competitor_analysis.register(bot_id, category)
        self.sandbox_tester.register(bot_id)
        return {"bot_id": bot_id, "category": category, "status": "registered"}

    def unregister_bot(self, bot_id: str) -> bool:
        """Remove a bot from all learning engines."""
        if bot_id not in self._bot_categories:
            return False
        del self._bot_categories[bot_id]
        return True

    # ------------------------------------------------------------------
    # Learning cycle
    # ------------------------------------------------------------------

    def run_learning_cycle(self, bot_id: str) -> dict:
        """Run one full deep-learning cycle for *bot_id*.

        A cycle consists of:
          1. Scraping top-1000 APIs for the bot's category.
          2. Analysing competitors' pricing, features, and sentiment.
          3. Running a sandbox test to validate any new capabilities.

        Returns a summary dict with results from each engine.
        """
        if not self._learning_active():
            return {"status": "deadline_passed", "bot_id": bot_id}

        if bot_id not in self._bot_categories:
            self.register_bot(bot_id)

        category = self._bot_categories[bot_id]
        api_result = self.api_scraper.scrape_cycle(bot_id, category)
        competitor_result = self.competitor_analysis.analyse_cycle(bot_id, category)
        sandbox_result = self.sandbox_tester.run_test(bot_id)

        cycle = {
            "bot_id": bot_id,
            "category": category,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "api_scrape": api_result,
            "competitor_analysis": competitor_result,
            "sandbox_test": sandbox_result,
            "days_until_go_live": self._days_remaining(),
        }
        self._cycle_log.append(cycle)
        return cycle

    def run_all_cycles(self) -> list[dict]:
        """Run a learning cycle for every registered bot."""
        return [self.run_learning_cycle(bot_id) for bot_id in list(self._bot_categories)]

    # ------------------------------------------------------------------
    # Status / reporting
    # ------------------------------------------------------------------

    def learning_status(self) -> dict:
        """Return aggregated deep-learning status for the dashboard."""
        return {
            "active": self._learning_active(),
            "deadline": self.deadline.isoformat(),
            "days_remaining": self._days_remaining(),
            "registered_bots": len(self._bot_categories),
            "bots": list(self._bot_categories.keys()),
            "total_cycles_run": len(self._cycle_log),
            "api_scraper": self.api_scraper.status(),
            "competitor_analysis": self.competitor_analysis.status(),
            "sandbox_tester": self.sandbox_tester.status(),
        }

    def bot_progress(self, bot_id: str) -> dict:
        """Return progress summary for a specific bot."""
        cycles = [c for c in self._cycle_log if c["bot_id"] == bot_id]
        return {
            "bot_id": bot_id,
            "category": self._bot_categories.get(bot_id, "unknown"),
            "cycles_completed": len(cycles),
            "api_mastery": self.api_scraper.mastery_score(bot_id),
            "competitor_intel_score": self.competitor_analysis.intel_score(bot_id),
            "sandbox_pass_rate": self.sandbox_tester.pass_rate(bot_id),
            "last_cycle": cycles[-1]["timestamp"] if cycles else None,
        }

    def top_performing_bots(self, n: int = 5) -> list[dict]:
        """Return the *n* bots with the highest composite learning score."""
        scores = [
            {
                "bot_id": bid,
                "category": cat,
                "score": self._composite_score(bid),
            }
            for bid, cat in self._bot_categories.items()
        ]
        return sorted(scores, key=lambda x: x["score"], reverse=True)[:n]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _learning_active(self) -> bool:
        return date.today() <= self.deadline

    def _days_remaining(self) -> int:
        delta = (self.deadline - date.today()).days
        return max(0, delta)

    def _composite_score(self, bot_id: str) -> float:
        api_score = self.api_scraper.mastery_score(bot_id)
        intel = self.competitor_analysis.intel_score(bot_id)
        sr = self.sandbox_tester.pass_rate(bot_id)
        return round((api_score + intel + sr) / 3, 2)
