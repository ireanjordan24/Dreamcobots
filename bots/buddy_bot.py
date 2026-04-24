"""
Buddy Bot — System intelligence distributor.

Reads the top-ranked insights from the knowledge store and broadcasts
the best practices to all registered bots through a simple in-process
recommendation API.

Usage
-----
    python bots/buddy_bot.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KNOWLEDGE_FILE = os.path.join(_ROOT, "knowledge", "ranked_insights.json")

_MIN_CONFIDENCE = 3
_TOP_N = 5


def _load_insights() -> list[dict]:
    try:
        with open(KNOWLEDGE_FILE) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []


def get_top_recommendations(
    min_confidence: int = _MIN_CONFIDENCE,
    top_n: int = _TOP_N,
) -> list[str]:
    """Return the top *top_n* lessons from insights above *min_confidence*.

    Parameters
    ----------
    min_confidence : int
        Minimum confidence score required.
    top_n : int
        Maximum number of recommendations to return.

    Returns
    -------
    list[str]
        Actionable lesson strings.
    """
    insights = _load_insights()
    recs: list[str] = []
    for item in insights:
        if item.get("confidence", 0) >= min_confidence:
            lesson = item.get("lesson", "")
            if lesson:
                recs.append(lesson)
        if len(recs) >= top_n:
            break
    return recs


def distribute(bots: list[str] | None = None) -> dict:
    """Distribute recommendations to *bots* (currently logged only).

    Parameters
    ----------
    bots : list[str] | None
        Names of bots to receive the recommendations.

    Returns
    -------
    dict
        Report containing recommendations and target bots.
    """
    recs = get_top_recommendations()
    target_bots = bots or [
        "debug_bot",
        "testing_bot",
        "bot_validator",
        "optimizer_bot",
        "security_auditor_bot",
    ]
    return {
        "recommendations": recs,
        "distributed_to": target_bots,
        "status": "ok" if recs else "no_recommendations_available",
    }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    return distribute(bots=context.get("bots") if context else None)


if __name__ == "__main__":
    recs = get_top_recommendations()
    print("🤝 Top System Recommendations:")
    if recs:
        for rec in recs:
            print(f"  - {rec}")
    else:
        print("  (No ranked insights yet — run insight_ranker.py first)")

    report = distribute()
    print(f"\n📡 Distributed to: {', '.join(report['distributed_to'])}")
