"""
DreamCo AI Learning Loop — Evolution Layer
===========================================

Continuously tracks bot performance, identifies underperforming bots,
triggers optimisation strategies, and — where performance cannot be
recovered — requests replacement bots from the BotGenerator.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import random
import sys
import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

if TYPE_CHECKING:
    from bots.control_center.controller import ControlCenter
    from bots.bot_generator_bot.generator import BotGenerator

# Score below which a bot is flagged as underperforming.
_UNDERPERFORM_THRESHOLD = 30

# Score above which a bot is considered high-performing.
_OUTPERFORM_THRESHOLD = 80


class LearningLoop:
    """
    DreamCo Evolution Layer.

    In every ``optimize()`` call the loop:
    1. Scores every registered bot (simulated metric in MVP; replace with
       real KPIs when external data is available).
    2. Flags bots below the underperformance threshold.
    3. Attempts a soft optimisation (logs the issue and increments a
       retry counter).
    4. After three consecutive underperformance strikes, requests a v2
       replacement bot from the generator.
    5. Records high-performers for future reference.

    Parameters
    ----------
    control_center : ControlCenter
        The running ControlCenter instance to inspect and update.
    generator : BotGenerator
        The generator instance used to create replacement bots.
    """

    def __init__(
        self,
        control_center: "ControlCenter",
        generator: "BotGenerator",
    ) -> None:
        self.control_center = control_center
        self.generator = generator
        self.performance_log: Dict[str, int] = {}
        self._strike_counter: Dict[str, int] = {}
        self._optimisation_log: List[dict] = []

    # ------------------------------------------------------------------
    # Performance tracking
    # ------------------------------------------------------------------

    def track_performance(self) -> Dict[str, int]:
        """
        Collect a performance score for every registered bot.

        In the MVP the score is simulated.  Replace the random call with
        real metrics (API latency, lead count, revenue generated, etc.)
        once telemetry is wired up.

        Returns
        -------
        dict
            Mapping of bot name → score (0–100).
        """
        scores: Dict[str, int] = {}
        for name in self.control_center.bots:
            bot = self.control_center.bots[name]
            # Prefer a real get_status() score if the bot exposes one.
            if hasattr(bot, "get_status"):
                try:
                    status = bot.get_status()
                    if isinstance(status, dict) and "score" in status:
                        scores[name] = int(status["score"])
                        continue
                except Exception:  # noqa: BLE001
                    pass
            scores[name] = random.randint(1, 100)

        self.performance_log.update(scores)
        return scores

    # ------------------------------------------------------------------
    # Optimisation
    # ------------------------------------------------------------------

    def optimize(self) -> List[dict]:
        """
        Run one optimisation pass across all registered bots.

        Returns
        -------
        list[dict]
            A list of actions taken during this pass.
        """
        print("🧠 Optimizing system...")
        self.track_performance()

        actions: List[dict] = []
        timestamp = datetime.now(timezone.utc).isoformat()

        for bot_name, score in self.performance_log.items():
            if score < _UNDERPERFORM_THRESHOLD:
                self._strike_counter[bot_name] = self._strike_counter.get(bot_name, 0) + 1
                strikes = self._strike_counter[bot_name]
                print(f"⚠️  {bot_name} underperforming (score: {score}, strikes: {strikes})")

                if strikes >= 3:
                    # Request a replacement bot
                    replacement_name = f"{bot_name}_v{strikes}"
                    self.generator.create_bot(replacement_name)
                    self._strike_counter[bot_name] = 0
                    action = {
                        "action": "replace",
                        "bot": bot_name,
                        "replacement": replacement_name,
                        "score": score,
                        "timestamp": timestamp,
                    }
                else:
                    action = {
                        "action": "flag",
                        "bot": bot_name,
                        "score": score,
                        "strikes": strikes,
                        "timestamp": timestamp,
                    }
                actions.append(action)

            elif score >= _OUTPERFORM_THRESHOLD:
                print(f"⭐ {bot_name} performing well (score: {score})")
                actions.append({
                    "action": "high_performer",
                    "bot": bot_name,
                    "score": score,
                    "timestamp": timestamp,
                })

        self._optimisation_log.extend(actions)
        return actions

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def suggest_new_bots(self) -> List[str]:
        """
        Suggest new bot names based on current performance gaps.

        Returns
        -------
        list[str]
            Candidate bot names addressing identified gaps.
        """
        suggestions = []
        for bot_name, score in self.performance_log.items():
            if score < _UNDERPERFORM_THRESHOLD:
                suggestions.append(f"{bot_name}_optimizer")
        return suggestions

    def get_optimisation_log(self) -> List[dict]:
        """Return a full history of all optimisation actions."""
        return list(self._optimisation_log)

    def get_summary(self) -> dict:
        """Return a summary of the current learning loop state."""
        return {
            "bots_tracked": len(self.performance_log),
            "avg_score": (
                round(sum(self.performance_log.values()) / len(self.performance_log), 1)
                if self.performance_log
                else 0
            ),
            "underperforming": [
                b for b, s in self.performance_log.items()
                if s < _UNDERPERFORM_THRESHOLD
            ],
            "high_performing": [
                b for b, s in self.performance_log.items()
                if s >= _OUTPERFORM_THRESHOLD
            ],
            "optimisation_actions": len(self._optimisation_log),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
