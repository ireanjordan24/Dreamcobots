"""
Insight Ranker — Scores and ranks PR learning insights by confidence.

Reads pr_insights.json, assigns a confidence score to each insight based
on heuristics (bug fixes, key terms, recency), trims the list to the most
valuable 100 items, and writes the result to ranked_insights.json.

Usage
-----
    python bots/insight_ranker.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FILE = os.path.join(_ROOT, "knowledge", "pr_insights.json")
OUTPUT_FILE = os.path.join(_ROOT, "knowledge", "ranked_insights.json")

_MAX_ITEMS = 100

_BOOST_TERMS: list[tuple[str, int]] = [
    ("bug_fix", 3),
    ("fix", 2),
    ("ci", 1),
    ("security", 2),
    ("performance", 1),
    ("test", 1),
]


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


def score_insight(item: dict) -> int:
    """Compute a confidence score for a single insight dictionary."""
    score = 0
    item_type = item.get("type", "")
    title_lower = item.get("title", "").lower()

    for term, boost in _BOOST_TERMS:
        if term == item_type or term in title_lower:
            score += boost

    return score


def rank_insights(data: list[dict]) -> list[dict]:
    """Assign confidence scores and return sorted, trimmed insight list."""
    for item in data:
        item["confidence"] = score_insight(item)
    ranked = sorted(data, key=lambda x: x["confidence"], reverse=True)
    return ranked[:_MAX_ITEMS]


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    raw = _load(INPUT_FILE)
    ranked = rank_insights(raw)
    _save(ranked, OUTPUT_FILE)
    return {"ranked": len(ranked), "status": "ok"}


if __name__ == "__main__":
    raw = _load(INPUT_FILE)
    ranked = rank_insights(raw)
    _save(ranked, OUTPUT_FILE)
    print(f"✅ Ranked {len(ranked)} insights → {OUTPUT_FILE}")
