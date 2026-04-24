"""
Debug Bot — AI-powered error detection and fix suggestion using PR learning data.

Reads ranked insights from knowledge/ranked_insights.json and matches known
error patterns against the provided error string to produce actionable
suggestions.

Usage
-----
    python bots/debug_bot.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

KNOWLEDGE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "knowledge", "ranked_insights.json"
)


def load_insights() -> list[dict]:
    """Load ranked insights from disk, returning an empty list on failure."""
    try:
        with open(KNOWLEDGE_FILE, "r") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []


def suggest_fixes(error: str, min_confidence: int = 2) -> list[str]:
    """Return up to three fix suggestions for *error* based on ranked insights.

    Parameters
    ----------
    error : str
        The error message or description to match against known patterns.
    min_confidence : int
        Minimum confidence score an insight must have to be considered.

    Returns
    -------
    list[str]
        Up to three fix suggestions (may be empty if no matches found).
    """
    insights = load_insights()
    suggestions: list[str] = []
    error_lower = error.lower()

    for item in insights:
        if item.get("confidence", 0) < min_confidence:
            continue
        if item.get("type") == "bug_fix" and item.get("title", "").lower() in error_lower:
            lesson = item.get("lesson", "")
            if lesson:
                suggestions.append(lesson)

    return suggestions[:3]


def analyze(error: str) -> dict:
    """Analyze *error* and return a structured debug report."""
    fixes = suggest_fixes(error)
    return {
        "error": error,
        "fixes_found": len(fixes),
        "suggestions": fixes,
        "status": "fixes_available" if fixes else "no_known_fix",
    }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    context = context or {}
    error = context.get("error", "CI workflow failed")
    return analyze(error)


if __name__ == "__main__":
    sample_error = sys.argv[1] if len(sys.argv) > 1 else "CI workflow failed"
    report = analyze(sample_error)
    print(json.dumps(report, indent=2))
    if report["status"] == "no_known_fix":
        print("\n⚠️  No known fix found. Consider opening a PR to document the solution.")
