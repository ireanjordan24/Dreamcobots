"""
Feedback Loop Bot — Collects bot execution results and feeds improvements back.

Aggregates run reports from all bots, identifies recurring failures, and
writes actionable feedback into the PR insights knowledge base so future
runs are more accurate.

Usage
-----
    python bots/feedback_loop_bot.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INSIGHTS_FILE = os.path.join(_ROOT, "knowledge", "pr_insights.json")
FEEDBACK_LOG = os.path.join(_ROOT, "knowledge", "feedback_log.json")


def _load(path: str) -> list[dict]:
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []


def _save(data: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def record_run_result(bot_name: str, status: str, error: str = "") -> dict:
    """Persist a single bot run result to the feedback log.

    Parameters
    ----------
    bot_name : str
        Name of the bot that ran.
    status : str
        Outcome: ``"ok"`` | ``"error"`` | ``"warning"``.
    error : str
        Error message (if any).

    Returns
    -------
    dict
        The saved feedback entry.
    """
    log = _load(FEEDBACK_LOG)
    entry = {
        "bot": bot_name,
        "status": status,
        "error": error,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    log.append(entry)
    log = log[-1000:]  # anti-context rot
    _save(log, FEEDBACK_LOG)
    return entry


def analyze_feedback() -> dict:
    """Analyze the feedback log and surface recurring failures."""
    log = _load(FEEDBACK_LOG)
    failure_counts: dict = defaultdict(int)
    error_samples: dict = defaultdict(str)

    for entry in log:
        if entry.get("status") in ("error", "warning"):
            bot = entry.get("bot", "unknown")
            failure_counts[bot] += 1
            if entry.get("error"):
                error_samples[bot] = entry["error"]

    recurring = [
        {"bot": b, "failures": c, "last_error": error_samples.get(b, "")}
        for b, c in sorted(failure_counts.items(), key=lambda x: -x[1])
        if c >= 2
    ]

    return {
        "total_runs_analyzed": len(log),
        "recurring_failures": recurring,
        "status": "feedback_ready",
    }


def inject_learnings(failures: list[dict]) -> int:
    """Convert recurring failures into PR insights for the knowledge base.

    Returns
    -------
    int
        Number of new insights added.
    """
    insights = _load(INSIGHTS_FILE)
    added = 0
    existing_titles = {i.get("title", "") for i in insights}

    for failure in failures:
        title = f"{failure['bot']} recurring failure"
        if title not in existing_titles:
            insights.append(
                {
                    "title": title,
                    "type": "bug_fix",
                    "lesson": (
                        f"Investigate {failure['bot']}: "
                        f"failed {failure['failures']} times. "
                        f"Last error: {failure['last_error'][:200]}"
                    ),
                    "confidence": 0,
                }
            )
            added += 1

    insights = insights[-500:]
    _save(insights, INSIGHTS_FILE)
    return added


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    feedback = analyze_feedback()
    added = inject_learnings(feedback["recurring_failures"])
    return {**feedback, "learnings_injected": added}


if __name__ == "__main__":
    feedback = analyze_feedback()
    print(json.dumps(feedback, indent=2))
    added = inject_learnings(feedback["recurring_failures"])
    if added:
        print(f"\n💡 {added} new learning(s) added to knowledge base.")
    else:
        print("\n✅ No new learnings to inject.")
