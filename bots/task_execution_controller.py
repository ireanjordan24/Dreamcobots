"""
Task Execution Controller Bot — Orchestrates bot pipelines and sequences tasks.

Accepts a list of bot tasks, resolves their dependencies, and runs them in
the correct order while collecting results and halting on critical failures.

Usage
-----
    python bots/task_execution_controller.py
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import time
from typing import Callable

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_BOTS_PKG_DIR = os.path.join(os.path.dirname(__file__))


def _load_bot_run(bot_module_name: str) -> Callable | None:
    """Dynamically load the ``run`` function from a bot module."""
    try:
        spec_path = os.path.join(_BOTS_PKG_DIR, f"{bot_module_name}.py")
        if not os.path.isfile(spec_path):
            return None
        import importlib.util
        spec = importlib.util.spec_from_file_location(bot_module_name, spec_path)
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return getattr(module, "run", None)
    except Exception:
        return None


class TaskExecutionController:
    """Orchestrates sequential bot task execution with dependency awareness."""

    def __init__(self, tasks: list[dict] | None = None) -> None:
        """
        Parameters
        ----------
        tasks : list[dict]
            Each task dict must have:
              - name (str): display name
              - bot (str): bot module name (e.g. ``"testing_bot"``)
              - critical (bool): if True, pipeline halts on failure
              - context (dict): optional runtime arguments
        """
        self.tasks = tasks or self._default_pipeline()
        self.results: list[dict] = []

    @staticmethod
    def _default_pipeline() -> list[dict]:
        return [
            {"name": "Validate Code", "bot": "bot_validator", "critical": False, "context": {}},
            {"name": "Run Tests", "bot": "testing_bot", "critical": True, "context": {}},
            {"name": "Security Audit", "bot": "security_auditor_bot", "critical": False, "context": {}},
            {"name": "Optimize", "bot": "optimizer_bot", "critical": False, "context": {}},
            {"name": "Deploy Review", "bot": "deployment_review_bot", "critical": False, "context": {}},
        ]

    def run(self) -> dict:
        """Execute all tasks in order and return the full pipeline report."""
        start = time.time()
        passed = failed = 0

        for task in self.tasks:
            bot_name = task.get("bot", "")
            context = task.get("context", {})
            critical = task.get("critical", False)

            run_fn = _load_bot_run(bot_name)
            task_result: dict = {
                "name": task.get("name", bot_name),
                "bot": bot_name,
                "critical": critical,
            }

            if run_fn is None:
                task_result["status"] = "bot_not_found"
                task_result["output"] = f"Bot module '{bot_name}' not found or has no run()."
                failed += 1
            else:
                try:
                    output = run_fn(context)
                    task_result["status"] = "ok"
                    task_result["output"] = output
                    passed += 1
                except Exception as exc:
                    task_result["status"] = "error"
                    task_result["output"] = str(exc)
                    failed += 1

            self.results.append(task_result)

            if critical and task_result["status"] in ("error", "bot_not_found"):
                task_result["pipeline_halted"] = True
                break

        elapsed = round(time.time() - start, 2)
        return {
            "tasks_run": len(self.results),
            "passed": passed,
            "failed": failed,
            "elapsed_seconds": elapsed,
            "results": self.results,
            "status": "pipeline_passed" if failed == 0 else "pipeline_failed",
        }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller (module-level wrapper)."""
    controller = TaskExecutionController()
    return controller.run()


if __name__ == "__main__":
    controller = TaskExecutionController()
    report = controller.run()
    print(json.dumps(report, indent=2))
    if report["status"] == "pipeline_failed":
        sys.exit(1)
