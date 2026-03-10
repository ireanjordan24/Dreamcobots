"""
Base bot class for Dreamcobots platform.

Provides three configurable autonomy levels and three scaling levels
that all bots in the platform inherit from.
"""

import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional


class BotStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class AutonomyLevel(Enum):
    """Three configurable levels of bot autonomy."""
    MANUAL = "manual"
    SEMI_AUTONOMOUS = "semi_autonomous"
    FULLY_AUTONOMOUS = "fully_autonomous"


class ScalingLevel(Enum):
    """Adjustable scaling levels for bot operations."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


# Scaling multipliers applied to bot operation capacity
SCALING_MULTIPLIERS: Dict[ScalingLevel, float] = {
    ScalingLevel.CONSERVATIVE: 1.0,
    ScalingLevel.MODERATE: 2.5,
    ScalingLevel.AGGRESSIVE: 5.0,
}


class BotBase:
    """
    Base class for all Dreamcobots bots.

    Each bot operates autonomously with configurable autonomy and scaling levels.
    Subclasses implement ``execute_task`` to provide domain-specific behaviour.

    Args:
        name: Human-readable bot name.
        autonomy: Initial autonomy level (defaults to MANUAL).
        scaling: Initial scaling level (defaults to MODERATE).
    """

    def __init__(
        self,
        name: str,
        autonomy: AutonomyLevel = AutonomyLevel.MANUAL,
        scaling: ScalingLevel = ScalingLevel.MODERATE,
    ) -> None:
        self.name = name
        self.autonomy = autonomy
        self.scaling = scaling
        self._running = False
        self.status: BotStatus = BotStatus.IDLE
        self._task_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_autonomy(self, level: AutonomyLevel) -> None:
        """Update the autonomy level."""
        self.logger.info("%s autonomy changed: %s → %s", self.name, self.autonomy.value, level.value)
        self.autonomy = level

    def set_scaling(self, level: ScalingLevel) -> None:
        """Update the scaling level."""
        self.logger.info("%s scaling changed: %s → %s", self.name, self.scaling.value, level.value)
        self.scaling = level

    @property
    def scaling_multiplier(self) -> float:
        """Return the numeric multiplier for the current scaling level."""
        return SCALING_MULTIPLIERS[self.scaling]

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        """Hook called when bot starts. Override in subclasses."""

    def on_stop(self) -> None:
        """Hook called when bot stops. Override in subclasses."""

    def execute(self) -> None:
        """Main execution logic. Override in subclasses."""

    def start(self) -> None:
        """Start the bot."""
        self._running = True
        self.status = BotStatus.RUNNING
        self.logger.info("%s started (autonomy=%s, scaling=%s)", self.name, self.autonomy.value, self.scaling.value)
        self.on_start()

    def stop(self) -> None:
        """Stop the bot."""
        self._running = False
        self.status = BotStatus.STOPPED
        self.logger.info("%s stopped", self.name)
        self.on_stop()

    def run(self) -> None:
        """Run the full bot lifecycle: start, execute, stop."""
        self.start()
        try:
            self.execute()
        except Exception:
            self.status = BotStatus.ERROR
            raise
        finally:
            if self.status != BotStatus.ERROR:
                self.stop()

    @property
    def is_running(self) -> bool:
        """Return True when the bot is active."""
        return self._running


    # ------------------------------------------------------------------
    # Task execution
    # ------------------------------------------------------------------

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task and record it in history.

        Subclasses should override ``_run_task`` to provide actual behaviour.
        In MANUAL mode the call is delegated directly; in SEMI_AUTONOMOUS and
        FULLY_AUTONOMOUS modes additional validation / retry logic is applied.

        Args:
            task: Arbitrary task descriptor understood by the subclass.

        Returns:
            Result dictionary with at least a ``status`` key.
        """
        if not self._running:
            return {"status": "error", "message": "Bot is not running"}

        start_time = time.monotonic()
        try:
            if self.autonomy == AutonomyLevel.MANUAL:
                result = self._run_task(task)
            elif self.autonomy == AutonomyLevel.SEMI_AUTONOMOUS:
                result = self._semi_autonomous_run(task)
            else:
                result = self._fully_autonomous_run(task)
        except Exception as exc:  # pragma: no cover – propagate unexpected errors
            result = {"status": "error", "message": str(exc)}

        elapsed = time.monotonic() - start_time
        record = {
            "task": task,
            "result": result,
            "elapsed_seconds": round(elapsed, 4),
            "autonomy": self.autonomy.value,
            "scaling": self.scaling.value,
        }
        self._task_history.append(record)
        return result

    def _run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclasses to implement task logic."""
        return {"status": "ok", "message": f"{self.name} processed task: {task.get('type', 'unknown')}"}

    def _semi_autonomous_run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with human-confirmation gate before acting."""
        validated = task.get("validated", False)
        if not validated:
            return {"status": "pending_confirmation", "message": "Task requires human confirmation"}
        return self._run_task(task)

    def _fully_autonomous_run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with automatic retry on transient failures."""
        max_retries = max(1, int(self.scaling_multiplier))
        for attempt in range(1, max_retries + 1):
            result = self._run_task(task)
            if result.get("status") != "transient_error":
                return result
            self.logger.warning("%s retry %d/%d for task %s", self.name, attempt, max_retries, task.get("type"))
        return result  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        """Return a snapshot of the bot's current state."""
        return {
            "name": self.name,
            "running": self._running,
            "autonomy": self.autonomy.value,
            "scaling": self.scaling.value,
            "scaling_multiplier": self.scaling_multiplier,
            "tasks_completed": len(self._task_history),
        }

    def get_task_history(self) -> List[Dict[str, Any]]:
        """Return a copy of the task execution history."""
        return list(self._task_history)
