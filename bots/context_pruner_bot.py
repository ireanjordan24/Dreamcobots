"""
Context Pruner Bot — Prevents knowledge base bloat by removing stale insights.

Over time the knowledge store accumulates low-quality, outdated, or
redundant entries that slow down inference. This bot trims entries with
zero confidence, keeps only the freshest records beyond a count cap, and
reports savings.

Usage
-----
    python bots/context_pruner_bot.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INSIGHTS_FILE = os.path.join(_ROOT, "knowledge", "pr_insights.json")
RANKED_FILE = os.path.join(_ROOT, "knowledge", "ranked_insights.json")
FEEDBACK_LOG = os.path.join(_ROOT, "knowledge", "feedback_log.json")
METRICS_FILE = os.path.join(_ROOT, "knowledge", "performance_metrics.json")

_CAPS: dict = {
    INSIGHTS_FILE: 500,
    RANKED_FILE: 100,
    FEEDBACK_LOG: 1000,
    METRICS_FILE: 500,
}


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


def prune_file(path: str, cap: int, remove_zero_confidence: bool = False) -> dict:
    """Prune a JSON list file.

    Parameters
    ----------
    path : str
        Absolute path to the JSON file.
    cap : int
        Maximum number of entries to retain (keeps the most recent).
    remove_zero_confidence : bool
        If True, also remove entries with ``confidence == 0``.

    Returns
    -------
    dict
        Keys: path, before, after, removed.
    """
    data = _load(path)
    before = len(data)

    if remove_zero_confidence:
        data = [d for d in data if d.get("confidence", 1) > 0]

    data = data[-cap:]
    after = len(data)

    if after < before:
        _save(data, path)

    return {"path": path, "before": before, "after": after, "removed": before - after}


def _prune_all() -> dict:
    """Prune all knowledge store files and return a summary report."""
    results: list[dict] = []

    for fpath, cap in _CAPS.items():
        zero_conf = fpath in (INSIGHTS_FILE, RANKED_FILE)
        results.append(prune_file(fpath, cap, remove_zero_confidence=zero_conf))

    total_removed = sum(r["removed"] for r in results)
    return {
        "files_pruned": len(results),
        "total_entries_removed": total_removed,
        "details": results,
        "status": "pruned" if total_removed else "already_clean",
    }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    return _prune_all()


if __name__ == "__main__":
    report = _prune_all()
    print(json.dumps(report, indent=2))
    print(
        f"\n🧹 Context pruned: {report['total_entries_removed']} stale "
        f"entr{'y' if report['total_entries_removed'] == 1 else 'ies'} removed."
    )
