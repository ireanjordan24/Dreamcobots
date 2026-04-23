"""
PR Intelligence Bot — Analyzes pull request history to extract learning patterns.

Reads PR data from the knowledge store, identifies recurring bug types,
most-fixed components, and common failure patterns to help other bots
improve their accuracy.

Usage
-----
    python bots/pr_intelligence_bot.py
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INSIGHTS_FILE = os.path.join(_ROOT, "knowledge", "pr_insights.json")
RANKED_FILE = os.path.join(_ROOT, "knowledge", "ranked_insights.json")


def _load(path: str) -> list[dict]:
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []


def analyze_pr_patterns(insights: list[dict]) -> dict:
    """Extract statistical patterns from the insight list.

    Returns
    -------
    dict
        Keys: total_insights, top_bug_types, top_components,
        high_confidence_fixes, pattern_summary.
    """
    bug_types: Counter = Counter()
    components: Counter = Counter()
    high_conf: list[dict] = []

    for item in insights:
        itype = item.get("type", "unknown")
        bug_types[itype] += 1

        title = item.get("title", "")
        # Extract component from title heuristically (first "word" before space)
        if title:
            component = title.split()[0].lower()
            components[component] += 1

        if item.get("confidence", 0) >= 3:
            high_conf.append(
                {
                    "title": item.get("title", ""),
                    "lesson": item.get("lesson", ""),
                    "confidence": item.get("confidence", 0),
                }
            )

    return {
        "total_insights": len(insights),
        "top_bug_types": dict(bug_types.most_common(5)),
        "top_components": dict(components.most_common(5)),
        "high_confidence_fixes": high_conf[:10],
        "pattern_summary": (
            f"{len(insights)} insights analyzed; "
            f"{len(high_conf)} high-confidence fixes available."
        ),
    }


def ingest_pr(pr_data: dict) -> dict:
    """Record a new PR insight and persist it.

    Parameters
    ----------
    pr_data : dict
        Must contain: title (str), type (str), lesson (str).

    Returns
    -------
    dict
        Confirmation with the stored insight.
    """
    insights = _load(INSIGHTS_FILE)
    insight = {
        "title": pr_data.get("title", ""),
        "type": pr_data.get("type", "general"),
        "lesson": pr_data.get("lesson", ""),
        "confidence": 0,
    }
    insights.append(insight)
    # Keep only the most recent 500 raw insights
    insights = insights[-500:]
    os.makedirs(os.path.dirname(INSIGHTS_FILE), exist_ok=True)
    with open(INSIGHTS_FILE, "w") as fh:
        json.dump(insights, fh, indent=2)
    return {"status": "recorded", "insight": insight}


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    if context and "pr_data" in context:
        return ingest_pr(context["pr_data"])
    insights = _load(RANKED_FILE) or _load(INSIGHTS_FILE)
    return analyze_pr_patterns(insights)


if __name__ == "__main__":
    insights = _load(RANKED_FILE) or _load(INSIGHTS_FILE)
    report = analyze_pr_patterns(insights)
    print(json.dumps(report, indent=2))
