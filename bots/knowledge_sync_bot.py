"""
Knowledge Sync Bot — Keeps the knowledge base clean, de-duplicated, and fresh.

Merges raw PR insights with ranked insights, removes duplicates, prunes
stale entries, and re-indexes the knowledge store for fast lookup by all
other bots.

Usage
-----
    python bots/knowledge_sync_bot.py
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_FILE = os.path.join(_ROOT, "knowledge", "pr_insights.json")
RANKED_FILE = os.path.join(_ROOT, "knowledge", "ranked_insights.json")
INDEX_FILE = os.path.join(_ROOT, "knowledge", "index.json")

_MAX_RAW = 500
_MAX_RANKED = 100


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


def deduplicate(items: list[dict]) -> list[dict]:
    """Remove exact duplicate insights (same title + lesson)."""
    seen: set[tuple] = set()
    unique: list[dict] = []
    for item in items:
        key = (item.get("title", ""), item.get("lesson", ""))
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def build_index(items: list[dict]) -> dict:
    """Build a title → insight lookup index."""
    index: dict = {}
    for i, item in enumerate(items):
        title = item.get("title", "").lower()
        if title:
            index[title] = i
    return index


def sync() -> dict:
    """Synchronize and clean the knowledge base.

    Returns
    -------
    dict
        Keys: raw_before, raw_after, ranked_before, ranked_after, status.
    """
    raw = _load(RAW_FILE)
    ranked = _load(RANKED_FILE)

    raw_before = len(raw)
    ranked_before = len(ranked)

    # Merge — add any ranked insights not already in raw
    raw_titles = {i.get("title", "") for i in raw}
    for item in ranked:
        if item.get("title", "") not in raw_titles:
            raw.append(item)

    # Deduplicate and trim
    raw = deduplicate(raw)[-_MAX_RAW:]
    ranked = deduplicate(ranked)[-_MAX_RANKED:]

    _save(raw, RAW_FILE)
    _save(ranked, RANKED_FILE)

    # Rebuild index
    index = build_index(ranked)
    _save(
        [
            {
                "synced_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "total_raw": len(raw),
                "total_ranked": len(ranked),
                "index": index,
            }
        ],
        INDEX_FILE,
    )

    return {
        "raw_before": raw_before,
        "raw_after": len(raw),
        "ranked_before": ranked_before,
        "ranked_after": len(ranked),
        "status": "synced",
    }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    return sync()


if __name__ == "__main__":
    result = sync()
    print(json.dumps(result, indent=2))
    print("\n🔄 Knowledge base synchronized.")
