"""
knowledge_store.py — Persistent knowledge storage for Elite Scraper Bots.

Each bot's scraper team writes its findings to a local JSON store so that
learned knowledge accumulates over time and can be queried by the parent bot
for self-improvement, client acquisition, and monetisation.

Storage layout (relative to repo root):
    data/elite_scraper/<bot_name>/knowledge.json
    data/elite_scraper/<bot_name>/github_repos.json
    data/elite_scraper/<bot_name>/monetization.json
    data/elite_scraper/<bot_name>/clients.json

All files are created on first write and updated (not replaced) on subsequent
runs so that the knowledge base grows incrementally.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

_LOG = logging.getLogger(__name__)

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_DATA_ROOT = os.path.join(_REPO_ROOT, "data", "elite_scraper")


class KnowledgeStore:
    """
    Persistent, append-friendly JSON knowledge store for a single bot.

    Parameters
    ----------
    bot_name : str
        Canonical bot directory name.  Used as the storage sub-directory.
    data_root : str | None
        Override the default ``data/elite_scraper/<bot_name>`` path.
    """

    STORES = ("knowledge", "github_repos", "monetization", "clients")

    def __init__(self, bot_name: str, data_root: Optional[str] = None):
        self.bot_name = bot_name
        self._dir = os.path.join(data_root or _DATA_ROOT, bot_name)
        os.makedirs(self._dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def save(self, store: str, items: List[Dict[str, Any]]) -> None:
        """
        Append *items* to *store*, deduplicating on the ``url`` or ``id``
        field so the knowledge base only keeps unique entries.

        Parameters
        ----------
        store : str
            One of ``"knowledge"``, ``"github_repos"``, ``"monetization"``,
            or ``"clients"``.
        items : list[dict]
            New records to merge into the store.
        """
        if not items:
            return
        path = self._path(store)
        existing = self._load(path)
        merged = self._merge(existing, items)
        self._write(path, merged)
        _LOG.debug("[%s] %s: +%d items → %d total", self.bot_name, store, len(items), len(merged))

    def load(self, store: str) -> List[Dict[str, Any]]:
        """Return all records in *store*."""
        return self._load(self._path(store))

    def stats(self) -> Dict[str, int]:
        """Return record counts for all stores."""
        return {s: len(self.load(s)) for s in self.STORES}

    def prune(self, store: str, keep: int = 500) -> int:
        """
        Keep only the *keep* most-recently-added records in *store*.

        Returns the number of records removed.
        """
        path = self._path(store)
        existing = self._load(path)
        if len(existing) <= keep:
            return 0
        pruned = existing[-keep:]
        removed = len(existing) - len(pruned)
        self._write(path, pruned)
        _LOG.info("[%s] %s pruned %d old records", self.bot_name, store, removed)
        return removed

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _path(self, store: str) -> str:
        return os.path.join(self._dir, f"{store}.json")

    @staticmethod
    def _load(path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError) as exc:
            _LOG.warning("Failed to load %s: %s", path, exc)
            return []

    @staticmethod
    def _write(path: str, records: List[Dict[str, Any]]) -> None:
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(records, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            _LOG.error("Failed to write %s: %s", path, exc)

    @staticmethod
    def _merge(
        existing: List[Dict[str, Any]],
        new_items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Merge *new_items* into *existing*, deduplicating by ``url`` or ``id``.
        New items are appended with a ``scraped_at`` timestamp if missing.
        """
        seen: set[str] = set()
        result: List[Dict[str, Any]] = []
        now = datetime.now(tz=timezone.utc).isoformat()

        for item in existing:
            key = item.get("url") or item.get("id") or json.dumps(item, sort_keys=True)
            if key not in seen:
                seen.add(key)
                result.append(item)

        for item in new_items:
            item.setdefault("scraped_at", now)
            key = item.get("url") or item.get("id") or json.dumps(item, sort_keys=True)
            if key not in seen:
                seen.add(key)
                result.append(item)

        return result
