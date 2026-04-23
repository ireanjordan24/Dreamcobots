"""
Proactive Task Planner Bot — Anticipates future tasks and schedules them intelligently.

Analyzes the current state of the repository (pending bots, knowledge gaps,
failing tests) and generates a prioritized action plan for the next sprint.

Usage
-----
    python bots/proactive_task_planner.py
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

_PRIORITY_BOTS = [
    "debug_bot",
    "testing_bot",
    "bot_validator",
    "insight_ranker",
    "buddy_bot",
    "optimizer_bot",
    "security_auditor_bot",
    "pr_intelligence_bot",
    "deployment_review_bot",
    "code_coverage_bot",
    "skill_generation_bot",
    "task_execution_controller",
    "proactive_task_planner",
    "feedback_loop_bot",
    "adaptive_learning_bot",
]


def _bot_exists(name: str) -> bool:
    return os.path.isfile(os.path.join(_ROOT, "bots", f"{name}.py"))


def _doc_exists(name: str) -> bool:
    return os.path.isfile(os.path.join(_ROOT, "docs", "bots", f"{name}.md"))


def generate_plan() -> dict:
    """Inspect the repo and produce a prioritized task plan.

    Returns
    -------
    dict
        Keys: generated_at, tasks (list), summary.
    """
    tasks: list[dict] = []
    priority = 1

    for bot in _PRIORITY_BOTS:
        if not _bot_exists(bot):
            tasks.append(
                {
                    "priority": priority,
                    "task": f"Create missing bot: {bot}.py",
                    "category": "bot_creation",
                    "effort": "medium",
                }
            )
            priority += 1

        if not _doc_exists(bot):
            tasks.append(
                {
                    "priority": priority,
                    "task": f"Write portfolio doc: docs/bots/{bot}.md",
                    "category": "documentation",
                    "effort": "low",
                }
            )
            priority += 1

    # Check for missing knowledge files
    for fname in ("pr_insights.json", "ranked_insights.json"):
        fpath = os.path.join(_ROOT, "knowledge", fname)
        if not os.path.isfile(fpath):
            tasks.append(
                {
                    "priority": priority,
                    "task": f"Initialize knowledge file: knowledge/{fname}",
                    "category": "infrastructure",
                    "effort": "low",
                }
            )
            priority += 1

    # Check for missing workflows
    ci_path = os.path.join(_ROOT, ".github", "workflows", "dreamco-bots.yml")
    if not os.path.isfile(ci_path):
        tasks.append(
            {
                "priority": 0,  # highest
                "task": "Create staged CI workflow: .github/workflows/dreamco-bots.yml",
                "category": "ci_cd",
                "effort": "medium",
            }
        )

    tasks.sort(key=lambda x: x["priority"])

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_tasks": len(tasks),
        "tasks": tasks[:20],
        "summary": (
            f"{len(tasks)} pending tasks identified. "
            "Run this bot regularly to keep the plan up to date."
        ),
    }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    return generate_plan()


if __name__ == "__main__":
    plan = generate_plan()
    print(json.dumps(plan, indent=2))
    print(f"\n📋 {plan['summary']}")
