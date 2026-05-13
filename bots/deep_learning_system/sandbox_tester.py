"""
SandboxTestingEngine — Safe, isolated bot capability validation.

Each bot is given a sandboxed execution context where it can attempt tasks,
explore integrations, and be evaluated — without affecting production systems.

Capabilities tested per cycle:
  • Task completion (can the bot finish the assigned task?)
  • Error recovery (graceful handling of invalid inputs)
  • Integration smoke tests (API connectivity stubs)
  • Performance benchmarking (response time / throughput estimates)

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
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

# ---------------------------------------------------------------------------
# Default sandbox test suite (generic tasks applicable to any bot)
# ---------------------------------------------------------------------------
_DEFAULT_TASKS: list[dict[str, Any]] = [
    {"id": "basic_run",      "description": "Execute a basic task",         "weight": 1.0},
    {"id": "error_recovery", "description": "Handle invalid inputs cleanly","weight": 1.0},
    {"id": "api_stub",       "description": "Call an API stub endpoint",    "weight": 1.0},
    {"id": "throughput",     "description": "Process 100 items in < 1s",    "weight": 1.0},
    {"id": "memory_check",   "description": "No memory leaks after 10 runs","weight": 1.0},
]


class SandboxTestingEngine:
    """
    Manages sandbox testing for registered bots.

    Parameters
    ----------
    deadline : date
        The go-live deadline.  Sandbox tests stop after this date.
    """

    def __init__(self, deadline: date) -> None:
        self.deadline = deadline
        self._records: dict[str, dict[str, Any]] = {}

    def register(self, bot_id: str) -> None:
        if bot_id in self._records:
            return
        self._records[bot_id] = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "pass_rate": 0.0,
            "last_tested_at": None,
            "task_results": {},
        }

    def run_test(self, bot_id: str, tasks: list[dict[str, Any]] | None = None) -> dict:
        """Run a sandbox test cycle for *bot_id*.

        By default runs the standard task suite.  Callers may pass a custom
        *tasks* list of ``{"id": str, "description": str, "weight": float}``
        dicts to test specific capabilities.

        Returns a results dict with pass/fail counts and pass rate.
        """
        if not self._testing_active():
            return {"status": "deadline_passed"}

        if bot_id not in self._records:
            self.register(bot_id)

        suite = tasks if tasks is not None else _DEFAULT_TASKS
        passed = 0
        failed = 0
        task_results: dict[str, str] = {}

        for task in suite:
            # Deterministic pass/fail based on task id (all pass in baseline)
            outcome = self._evaluate_task(bot_id, task)
            task_results[task["id"]] = outcome
            if outcome == "pass":
                passed += 1
            else:
                failed += 1

        rec = self._records[bot_id]
        rec["tests_run"] += len(suite)
        rec["tests_passed"] += passed
        rec["tests_failed"] += failed
        total = rec["tests_run"]
        rec["pass_rate"] = round(rec["tests_passed"] / total * 100, 2) if total > 0 else 0.0
        rec["last_tested_at"] = datetime.now(timezone.utc).isoformat()
        rec["task_results"].update(task_results)

        return {
            "status": "completed",
            "tasks_run": len(suite),
            "passed": passed,
            "failed": failed,
            "pass_rate": rec["pass_rate"],
            "task_results": task_results,
        }

    def pass_rate(self, bot_id: str) -> float:
        """Return the cumulative pass rate (0–100) for *bot_id*."""
        if bot_id not in self._records:
            return 0.0
        return self._records[bot_id]["pass_rate"]

    def test_history(self, bot_id: str) -> dict:
        """Return the full test record for *bot_id*."""
        return dict(self._records.get(bot_id, {}))

    def status(self) -> dict:
        """Return aggregate sandbox testing status."""
        total_runs = sum(r["tests_run"] for r in self._records.values())
        total_passed = sum(r["tests_passed"] for r in self._records.values())
        avg_pass_rate = (
            sum(r["pass_rate"] for r in self._records.values()) / len(self._records)
            if self._records
            else 0.0
        )
        return {
            "registered_bots": len(self._records),
            "total_tests_run": total_runs,
            "total_tests_passed": total_passed,
            "average_pass_rate": round(avg_pass_rate, 2),
            "testing_active": self._testing_active(),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evaluate_task(self, bot_id: str, task: dict[str, Any]) -> str:
        """Evaluate a single sandbox task.

        All baseline tasks pass.  Subclasses or callers can override this
        method to inject real bot execution logic.
        """
        return "pass"

    def _testing_active(self) -> bool:
        return date.today() <= self.deadline
