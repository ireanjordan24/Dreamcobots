"""Learning Loop — revenue-aware bot optimiser for the DreamCo AI system.

Monitors estimated revenue and dynamically instructs the bot generator to
create new specialist bots when performance is low or to scale successful
bots when performance is high.

Usage
-----
    from bots.ai_learning_system.learning_loop import LearningLoop
    from bots.bot_generator_bot.bot_generator_bot import BotGeneratorBot
    from bots.control_center.control_center import ControlCenter

    cc = ControlCenter()
    gen = BotGeneratorBot()
    loop = LearningLoop(control_center=cc, generator=gen)
    loop.track_performance("lead_scraper", 95)
    loop.optimize()
"""

from __future__ import annotations

import os
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class LearningLoop:
    """Revenue-aware optimisation loop.

    Parameters
    ----------
    control_center:
        Any object that provides a ``get_bot_scores()`` method returning a
        ``dict[str, float]``.  May be ``None`` in standalone / test use.
    generator:
        Any object that provides a ``create_bot(name: str)`` method.
        May be ``None`` in standalone / test use.
    underperform_threshold:
        Bots whose performance score falls below this value are considered
        underperformers and will be replaced.
    """

    LOW_REVENUE_THRESHOLD = 100
    HIGH_REVENUE_THRESHOLD = 500

    def __init__(
        self,
        control_center=None,
        generator=None,
        underperform_threshold: int = 30,
    ) -> None:
        self.control_center = control_center
        self.generator = generator
        self.underperform_threshold = underperform_threshold
        self._performance_log: dict[str, float] = {}

    # ------------------------------------------------------------------
    # Performance tracking
    # ------------------------------------------------------------------

    def track_performance(self, bot_name: str, score: float) -> None:
        """Record a performance *score* for *bot_name*.

        Parameters
        ----------
        bot_name:
            Identifier for the bot being tracked.
        score:
            Numeric performance score (higher is better).
        """
        self._performance_log[bot_name] = score

    def get_performance_log(self) -> dict[str, float]:
        """Return a copy of the current performance log."""
        return dict(self._performance_log)

    def get_underperformers(self) -> list[str]:
        """Return bot names whose score is below *underperform_threshold*."""
        return [
            name
            for name, score in self._performance_log.items()
            if score < self.underperform_threshold
        ]

    # ------------------------------------------------------------------
    # Revenue estimation
    # ------------------------------------------------------------------

    def track_revenue(self) -> float:
        """Estimate current revenue from the leads data file.

        Returns $10 per lead line found in ``data/leads.json``.  Override
        this method (or replace the data source) to connect to real revenue
        tracking.
        """
        try:
            with open("data/leads.json") as f:
                leads = sum(1 for line in f if line.strip())
            return leads * 10.0
        except (FileNotFoundError, OSError):
            return 0.0

    # ------------------------------------------------------------------
    # Optimisation
    # ------------------------------------------------------------------

    def optimize(self) -> None:
        """Analyse system performance and generate or scale bots as needed.

        Logic
        -----
        * If estimated revenue < LOW_REVENUE_THRESHOLD  →  create a
          ``lead_booster_bot`` to drive more top-of-funnel activity.
        * If estimated revenue > HIGH_REVENUE_THRESHOLD →  create a
          ``sales_scaler_bot`` to capitalise on strong lead flow.
        * Any bot with a recorded score below *underperform_threshold* will
          have an ``<name>_optimized`` replacement bot created.
        """
        print("🧠 AI analyzing system...")

        revenue = self.track_revenue()
        print(f"💰 Revenue: ${revenue}")

        if revenue < self.LOW_REVENUE_THRESHOLD:
            print("📉 Low revenue → generating more lead bots")
            if self.generator is not None:
                self.generator.create_bot("lead_booster_bot")

        elif revenue > self.HIGH_REVENUE_THRESHOLD:
            print("📈 High performance → scaling sales bots")
            if self.generator is not None:
                self.generator.create_bot("sales_scaler_bot")

        # Replace underperforming bots
        for bot in self.get_underperformers():
            print(f"🔄 Replacing underperformer: {bot}")
            if self.generator is not None:
                self.generator.create_bot(f"{bot}_optimized")
