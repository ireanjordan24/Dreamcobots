"""
DreamCo Orchestrator — Central Brain

Connects all DreamCo bots into one unified loop:
  BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE

Every bot registered here must return a standard revenue output:
    {
        "revenue": float,
        "leads_generated": int,
        "conversion_rate": float,
        "action": str,
    }

The orchestrator validates each result and triggers auto-scaling for
high-performing bots.
"""

from __future__ import annotations

import importlib
import sys
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Revenue output schema
# ---------------------------------------------------------------------------

REVENUE_OUTPUT_KEYS = ("revenue", "leads_generated", "conversion_rate", "action")

# Default revenue thresholds for validation
SCALE_REVENUE_THRESHOLD = 100.0
MIN_CONVERSION_RATE = 0.05


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class BotRunResult:
    """Result of a single bot execution cycle."""

    bot_name: str
    output: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "bot_name": self.bot_name,
            "output": self.output,
            "validation": self.validation,
            "error": self.error,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# DreamCoOrchestrator
# ---------------------------------------------------------------------------


class DreamCoOrchestrator:
    """
    Central orchestrator that wires all DreamCo bots into the Money OS.

    Usage
    -----
    orch = DreamCoOrchestrator()
    result = orch.process_bot("side_hustle_bot", {"revenue": 200, "conversion_rate": 0.4})
    all_results = orch.run_all_bots()
    """

    # Default bot registry: (import_path, bot_name)
    DEFAULT_BOTS: List[tuple] = [
        ("bots.government-contract-grant-bot.government_contract_grant_bot", "gov_bot"),
        ("bots.home_buyer_bot.home_buyer_bot", "real_estate_bot"),
        ("bots.ai-side-hustle-bots.bot", "side_hustle_bot"),
        ("bots.selenium-job-application-bot.bot", "job_bot"),
    ]

    def __init__(
        self,
        revenue_threshold: float = SCALE_REVENUE_THRESHOLD,
        min_conversion_rate: float = MIN_CONVERSION_RATE,
    ) -> None:
        self.revenue_threshold = revenue_threshold
        self.min_conversion_rate = min_conversion_rate
        self._run_history: List[BotRunResult] = []
        self._registered_bots: List[tuple] = list(self.DEFAULT_BOTS)

    # ------------------------------------------------------------------
    # Bot registration
    # ------------------------------------------------------------------

    def register_bot(self, import_path: str, bot_name: str) -> None:
        """Register a custom bot with the orchestrator."""
        self._registered_bots.append((import_path, bot_name))

    # ------------------------------------------------------------------
    # Core processing
    # ------------------------------------------------------------------

    def process_bot(self, bot_name: str, bot_output: dict) -> dict:
        """
        Validate a bot's output dictionary and decide whether to scale.

        Parameters
        ----------
        bot_name  : Human-readable bot identifier.
        bot_output: Dict with at minimum "revenue" and "conversion_rate" keys.

        Returns
        -------
        dict with keys: scale (bool), revenue (float), recommendation (str),
        conversion_rate (float), leads_generated (int).
        """
        result = self._validate(bot_output)
        print(f"[{bot_name}] → {result}")

        if result["scale"]:
            print(f"[{bot_name}] ✅ Scaling triggered — cloning bot into new niche.")

        run_result = BotRunResult(
            bot_name=bot_name,
            output=dict(bot_output),
            validation=result,
        )
        self._run_history.append(run_result)
        return result

    def run_bot(self, bot_path: str, bot_name: str) -> dict:
        """
        Dynamically import and execute a bot module, then validate output.

        The bot module must expose a ``run()`` function that returns a
        revenue output dictionary.
        """
        try:
            module = importlib.import_module(bot_path)
            bot_output = module.run()
            result = self._validate(bot_output)
            print(f"[{bot_name}] RESULT:", result)
            if result["scale"]:
                print(f"[{bot_name}] ✅ Scaling triggered.")
            run_result = BotRunResult(
                bot_name=bot_name,
                output=bot_output,
                validation=result,
            )
            self._run_history.append(run_result)
            return run_result.to_dict()
        except Exception as exc:
            error_result = BotRunResult(bot_name=bot_name, error=str(exc))
            self._run_history.append(error_result)
            return error_result.to_dict()

    def run_all_bots(self) -> List[dict]:
        """Execute every registered bot and collect results."""
        results = []
        for bot_path, bot_name in self._registered_bots:
            results.append(self.run_bot(bot_path, bot_name))
        return results

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_run_history(self) -> List[dict]:
        """Return all historical bot run results."""
        return [r.to_dict() for r in self._run_history]

    def get_summary(self) -> dict:
        """Summarise total revenue and scaling events across all runs."""
        total_revenue = sum(
            r.output.get("revenue", 0)
            for r in self._run_history
            if r.error is None
        )
        scaled = sum(
            1
            for r in self._run_history
            if r.error is None and r.validation.get("scale", False)
        )
        return {
            "total_runs": len(self._run_history),
            "total_revenue_usd": round(total_revenue, 2),
            "scaling_events": scaled,
            "registered_bots": len(self._registered_bots),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Internal validation
    # ------------------------------------------------------------------

    def _validate(self, bot_output: dict) -> dict:
        """Evaluate a bot output and produce a validation result."""
        revenue = float(bot_output.get("revenue", 0))
        conversion_rate = float(bot_output.get("conversion_rate", 0.0))
        leads_generated = int(bot_output.get("leads_generated", 0))

        should_scale = revenue >= self.revenue_threshold
        if conversion_rate < self.min_conversion_rate and revenue < self.revenue_threshold:
            recommendation = "Change strategy"
        elif should_scale:
            recommendation = "Scale aggressively"
        else:
            recommendation = "Maintain"

        return {
            "scale": should_scale,
            "revenue": round(revenue, 2),
            "conversion_rate": round(conversion_rate, 4),
            "leads_generated": leads_generated,
            "recommendation": recommendation,
        }
