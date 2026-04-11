"""
DreamCo WorkflowEngine — Chains bots into sequential or parallel
execution pipelines.

A *workflow* is an ordered list of steps, each pointing to a ``BaseBot``
subclass and an optional task override.  Steps are executed in order;
the output of each step is available to subsequent steps via the shared
*context* dict.

Usage
-----
    from core.workflow import WorkflowEngine, WorkflowStep

    engine = WorkflowEngine()
    engine.add_step(WorkflowStep(bot=RealEstateBot(), task={"location": "austin"}))
    engine.add_step(WorkflowStep(bot=DealFinderBot(), task={}))
    result = engine.run()
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.base_bot import BaseBot, RESULT_STATUS_SUCCESS, RESULT_STATUS_FAILED
from core.executor import BotExecutor


# ---------------------------------------------------------------------------
# WorkflowStep
# ---------------------------------------------------------------------------


@dataclass
class WorkflowStep:
    """
    A single step in a workflow.

    Attributes
    ----------
    bot : BaseBot
        The bot instance to run for this step.
    task : dict
        Task payload forwarded to ``bot.run()``.
    name : str
        Optional human-readable step name.  Defaults to the bot's name.
    """

    bot: BaseBot
    task: dict = field(default_factory=dict)
    name: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.bot.name or self.bot.bot_id


# ---------------------------------------------------------------------------
# WorkflowResult
# ---------------------------------------------------------------------------


@dataclass
class WorkflowResult:
    """Aggregated result returned by :meth:`WorkflowEngine.run`."""

    steps: List[dict]
    status: str
    total_elapsed_ms: float
    context: Dict[str, Any]

    @property
    def succeeded(self) -> int:
        return sum(1 for s in self.steps if s["status"] == RESULT_STATUS_SUCCESS)

    @property
    def failed(self) -> int:
        return sum(1 for s in self.steps if s["status"] == RESULT_STATUS_FAILED)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "steps": self.steps,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "total_elapsed_ms": self.total_elapsed_ms,
            "context": self.context,
        }


# ---------------------------------------------------------------------------
# WorkflowEngine
# ---------------------------------------------------------------------------


class WorkflowEngine:
    """
    Chains ``BaseBot`` instances into a sequential execution pipeline.

    Parameters
    ----------
    name : str
        Human-readable workflow name (useful for logging).
    stop_on_failure : bool
        If ``True`` (default), halt the pipeline when a step fails.
        If ``False``, continue running remaining steps.
    """

    def __init__(
        self,
        name: str = "default_workflow",
        stop_on_failure: bool = True,
    ) -> None:
        self.name = name
        self.stop_on_failure = stop_on_failure
        self._steps: List[WorkflowStep] = []
        self._executor = BotExecutor()
        self._history: List[WorkflowResult] = []

    # ------------------------------------------------------------------
    # Step management
    # ------------------------------------------------------------------

    def add_step(self, step: WorkflowStep) -> "WorkflowEngine":
        """Append *step* to the workflow and return *self* for chaining."""
        self._steps.append(step)
        return self

    def add_bot(
        self,
        bot: BaseBot,
        task: dict | None = None,
        name: str = "",
    ) -> "WorkflowEngine":
        """Convenience method — wrap *bot* in a WorkflowStep and add it."""
        return self.add_step(WorkflowStep(bot=bot, task=task or {}, name=name))

    def clear_steps(self) -> None:
        """Remove all steps from the workflow."""
        self._steps.clear()

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(self, context: Dict[str, Any] | None = None) -> WorkflowResult:
        """
        Execute all steps in order.

        Parameters
        ----------
        context : dict | None
            Shared mutable context that each step can read and write.
            The result of each step is stored under the step name key.

        Returns
        -------
        WorkflowResult
        """
        if context is None:
            context = {}

        start = time.monotonic()
        step_results: List[dict] = []
        overall_status = RESULT_STATUS_SUCCESS

        for step in self._steps:
            # Merge context into the task so bots can read upstream results
            merged_task = {**step.task, "_context": context}
            entry = self._executor.execute(step.bot, task=merged_task)
            step_results.append({"step": step.name, **entry})

            # Store this step's result in context under its name
            context[step.name] = entry.get("result")

            if entry["status"] == RESULT_STATUS_FAILED:
                overall_status = RESULT_STATUS_FAILED
                if self.stop_on_failure:
                    break

        total_elapsed = round((time.monotonic() - start) * 1000, 2)
        result = WorkflowResult(
            steps=step_results,
            status=overall_status,
            total_elapsed_ms=total_elapsed,
            context=context,
        )
        self._history.append(result)
        return result

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def get_history(self) -> List[WorkflowResult]:
        """Return all past :class:`WorkflowResult` instances."""
        return list(self._history)

    def last_result(self) -> Optional[WorkflowResult]:
        """Return the most recent :class:`WorkflowResult`, or ``None``."""
        return self._history[-1] if self._history else None
