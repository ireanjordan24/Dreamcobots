"""
Learning Loop — Self-Improvement Trigger

Evaluates the performance of every registered bot during each cycle, flags
underperforming bots based on metrics, and automatically creates optimized
replacements for weak bots.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import sys
import random
from typing import TYPE_CHECKING

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

if TYPE_CHECKING:  # pragma: no cover
    from bots.control_center.control_center import ControlCenter


# ---------------------------------------------------------------------------
# Default thresholds
# ---------------------------------------------------------------------------

DEFAULT_UNDERPERFORM_THRESHOLD: int = 30
DEFAULT_SCORE_MIN: int = 1
DEFAULT_SCORE_MAX: int = 100


class LearningLoop:
    """Continuous self-improvement loop for the DreamCo bot ecosystem.

    On each call to :meth:`optimize`, every registered bot is assigned a
    performance score.  Bots whose score falls below
    ``underperform_threshold`` are flagged and an optimised replacement is
    created automatically via the supplied *generator*.

    Parameters
    ----------
    control_center : ControlCenter
        The central control center that holds all registered bots.
    generator : object
        Any object that exposes a ``create_bot(name: str)`` method — typically
        a :class:`~bots.bot_generator_bot.bot_generator_bot.BotGeneratorBot`
        instance.
    underperform_threshold : int
        Score below which a bot is considered underperforming.  Defaults to
        ``DEFAULT_UNDERPERFORM_THRESHOLD`` (30).
    """

    def __init__(
        self,
        control_center: "ControlCenter",
        generator: object,
        underperform_threshold: int = DEFAULT_UNDERPERFORM_THRESHOLD,
    ) -> None:
        self.control_center = control_center
        self.generator = generator
        self.underperform_threshold = underperform_threshold
        self.performance_log: dict[str, int] = {}

    # ------------------------------------------------------------------
    # Performance tracking
    # ------------------------------------------------------------------

    def track_performance(self) -> dict[str, int]:
        """Assign a performance score to every registered bot.

        Scores are random integers in [DEFAULT_SCORE_MIN, DEFAULT_SCORE_MAX].
        # TODO: Replace random scores with real bot performance metrics
        # (e.g. from the bot performance database at
        # bots/ai_learning_system/database.py) when available.

        Returns
        -------
        dict[str, int]
            Mapping of bot name → performance score.
        """
        bots = (
            self.control_center.bots
            if hasattr(self.control_center, "bots")
            else self.control_center._bots  # noqa: SLF001
        )
        for name in bots:
            self.performance_log[name] = random.randint(
                DEFAULT_SCORE_MIN, DEFAULT_SCORE_MAX
            )
        return dict(self.performance_log)

    # ------------------------------------------------------------------
    # Optimisation
    # ------------------------------------------------------------------

    def optimize(self) -> list[str]:
        """Run one optimization cycle.

        1. Tracks performance for all bots.
        2. Flags bots below :attr:`underperform_threshold`.
        3. Creates an optimized replacement via :attr:`generator`.

        Returns
        -------
        list[str]
            Names of all optimized (replacement) bots that were created.
        """
        print("🧠 Optimizing system...")
        self.track_performance()

        created: list[str] = []
        for bot, score in self.performance_log.items():
            if score < self.underperform_threshold:
                print(f"🔧 Improving {bot} (score: {score})")
                optimized_name = f"{bot}_optimized"
                self.generator.create_bot(optimized_name)
                created.append(optimized_name)
                print(f"✅ Replacement bot created: {optimized_name}")

        return created

    # ------------------------------------------------------------------
    # Informational helpers
    # ------------------------------------------------------------------

    def get_performance_log(self) -> dict[str, int]:
        """Return the most recent performance log."""
        return dict(self.performance_log)

    def get_underperformers(self) -> dict[str, int]:
        """Return bots whose score is below the threshold."""
        return {
            name: score
            for name, score in self.performance_log.items()
            if score < self.underperform_threshold
        }
