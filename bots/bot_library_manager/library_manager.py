"""
Bot Library Manager
===================

SQL-backed manager for per-bot library catalogues and learning-data folders.

Each bot can:
  * Register the libraries it uses and track its mastery level.
  * Store learning data (scraped facts, strategies, client leads).
  * Discard low-relevance entries to keep the knowledge base lean.
  * Query its own leaderboard and mastery progression.

Backed by SQLite (default: in-memory for tests; pass a file path for
persistence).  The schema mirrors the extended ``database/schema.sql``
but runs independently so any module can embed it without PostgreSQL.

Usage
-----
    from bots.bot_library_manager import BotLibraryManager

    mgr = BotLibraryManager("bot_libraries.db")
    mgr.register_library("scraper_bot", "requests", category="http")
    mgr.update_mastery("scraper_bot", "requests", 85.0)
    mgr.store_learning("scraper_bot", "github_workflow",
                       "Use matrix strategy for parallel scraping",
                       source="github", relevance_score=90.0)
    print(mgr.get_library_summary("scraper_bot"))
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS bot_libraries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    bot_name        TEXT    NOT NULL,
    library_name    TEXT    NOT NULL,
    version         TEXT    DEFAULT '',
    category        TEXT    NOT NULL DEFAULT 'general',
    mastery_score   REAL    NOT NULL DEFAULT 0.0,
    status          TEXT    NOT NULL DEFAULT 'learning',
    notes           TEXT    DEFAULT '',
    registered_at   TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL,
    UNIQUE (bot_name, library_name)
);

CREATE TABLE IF NOT EXISTS bot_learning_data (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    bot_name        TEXT    NOT NULL,
    data_type       TEXT    NOT NULL DEFAULT 'generic',
    source          TEXT    NOT NULL DEFAULT 'manual',
    content         TEXT    NOT NULL,
    relevance_score REAL    NOT NULL DEFAULT 50.0,
    retained        INTEGER NOT NULL DEFAULT 1,
    tags            TEXT    DEFAULT '',
    scraped_at      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS scraper_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    bot_name        TEXT    NOT NULL,
    scraper_type    TEXT    NOT NULL DEFAULT 'github',
    query           TEXT    NOT NULL,
    items_found     INTEGER NOT NULL DEFAULT 0,
    items_retained  INTEGER NOT NULL DEFAULT 0,
    items_discarded INTEGER NOT NULL DEFAULT 0,
    status          TEXT    NOT NULL DEFAULT 'success',
    duration_ms     INTEGER NOT NULL DEFAULT 0,
    ran_at          TEXT    NOT NULL
);
"""

# Mastery thresholds
_MASTERY_PROFICIENT = 60.0
_MASTERY_MASTERED = 85.0

# Minimum relevance score to retain a learning-data entry automatically.
DEFAULT_RETENTION_THRESHOLD: float = 40.0


# ---------------------------------------------------------------------------
# BotLibraryManager
# ---------------------------------------------------------------------------

class BotLibraryManager:
    """
    Manages per-bot library registrations and learning data in SQLite.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file.  Defaults to ``:memory:`` for
        tests.
    retention_threshold : float
        Minimum relevance score (0–100) for a learning entry to be kept
        automatically.  Entries below this score are marked as discarded.
    """

    def __init__(
        self,
        db_path: str = ":memory:",
        retention_threshold: float = DEFAULT_RETENTION_THRESHOLD,
    ) -> None:
        self._db_path = db_path
        self._retention_threshold = retention_threshold
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_schema(self) -> None:
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _mastery_status(score: float) -> str:
        if score >= _MASTERY_MASTERED:
            return "mastered"
        if score >= _MASTERY_PROFICIENT:
            return "proficient"
        return "learning"

    # ------------------------------------------------------------------
    # Library management
    # ------------------------------------------------------------------

    def register_library(
        self,
        bot_name: str,
        library_name: str,
        version: str = "",
        category: str = "general",
        notes: str = "",
    ) -> dict:
        """Register a library for a bot (upsert — safe to call multiple times).

        Returns
        -------
        dict
            The library record as stored.
        """
        now = self._now()
        self._conn.execute(
            """INSERT INTO bot_libraries
               (bot_name, library_name, version, category, mastery_score,
                status, notes, registered_at, updated_at)
               VALUES (?, ?, ?, ?, 0.0, 'learning', ?, ?, ?)
               ON CONFLICT (bot_name, library_name) DO UPDATE SET
                   version    = excluded.version,
                   category   = excluded.category,
                   notes      = excluded.notes,
                   updated_at = excluded.updated_at""",
            (bot_name, library_name, version, category, notes, now, now),
        )
        self._conn.commit()
        return self.get_library(bot_name, library_name)

    def update_mastery(
        self, bot_name: str, library_name: str, mastery_score: float
    ) -> dict:
        """Set the mastery score (0–100) for a bot's library.

        The ``status`` field is updated automatically based on the score.
        """
        mastery_score = max(0.0, min(100.0, float(mastery_score)))
        status = self._mastery_status(mastery_score)
        now = self._now()
        self._conn.execute(
            """UPDATE bot_libraries
               SET mastery_score = ?, status = ?, updated_at = ?
               WHERE bot_name = ? AND library_name = ?""",
            (mastery_score, status, now, bot_name, library_name),
        )
        self._conn.commit()
        return self.get_library(bot_name, library_name)

    def get_library(self, bot_name: str, library_name: str) -> dict:
        """Return a single library record, or an empty dict if not found."""
        row = self._conn.execute(
            "SELECT * FROM bot_libraries WHERE bot_name = ? AND library_name = ?",
            (bot_name, library_name),
        ).fetchone()
        return dict(row) if row else {}

    def get_bot_libraries(self, bot_name: str) -> List[dict]:
        """Return all library records for a bot, ordered by mastery descending."""
        rows = self._conn.execute(
            "SELECT * FROM bot_libraries WHERE bot_name = ? "
            "ORDER BY mastery_score DESC",
            (bot_name,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_library_summary(self, bot_name: str) -> dict:
        """Return aggregate library stats for a bot."""
        rows = self.get_bot_libraries(bot_name)
        if not rows:
            return {
                "bot_name": bot_name,
                "total_libraries": 0,
                "mastered": 0,
                "proficient": 0,
                "learning": 0,
                "avg_mastery": 0.0,
            }
        mastered = sum(1 for r in rows if r["status"] == "mastered")
        proficient = sum(1 for r in rows if r["status"] == "proficient")
        learning = sum(1 for r in rows if r["status"] == "learning")
        avg = sum(r["mastery_score"] for r in rows) / len(rows)
        return {
            "bot_name": bot_name,
            "total_libraries": len(rows),
            "mastered": mastered,
            "proficient": proficient,
            "learning": learning,
            "avg_mastery": round(avg, 2),
        }

    def list_all_bots(self) -> List[str]:
        """Return the names of all bots that have registered at least one library."""
        rows = self._conn.execute(
            "SELECT DISTINCT bot_name FROM bot_libraries ORDER BY bot_name"
        ).fetchall()
        return [r["bot_name"] for r in rows]

    # ------------------------------------------------------------------
    # Learning data
    # ------------------------------------------------------------------

    def store_learning(
        self,
        bot_name: str,
        data_type: str,
        content: str,
        source: str = "manual",
        relevance_score: float = 50.0,
        tags: Optional[str] = None,
    ) -> dict:
        """Store a learning data entry for a bot.

        Entries below the ``retention_threshold`` are automatically marked
        as discarded (``retained=False``) so they do not pollute the
        active knowledge base.

        Returns
        -------
        dict
            The stored entry.
        """
        relevance_score = max(0.0, min(100.0, float(relevance_score)))
        retained = 1 if relevance_score >= self._retention_threshold else 0
        now = self._now()
        cursor = self._conn.execute(
            """INSERT INTO bot_learning_data
               (bot_name, data_type, source, content,
                relevance_score, retained, tags, scraped_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (bot_name, data_type, source, content,
             relevance_score, retained, tags or "", now),
        )
        self._conn.commit()
        row_id = cursor.lastrowid
        row = self._conn.execute(
            "SELECT * FROM bot_learning_data WHERE id = ?", (row_id,)
        ).fetchone()
        return dict(row)

    def get_retained_learning(
        self,
        bot_name: str,
        data_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[dict]:
        """Return retained learning entries for a bot.

        Parameters
        ----------
        bot_name : str
        data_type : str, optional
            Filter by data type.
        limit : int
            Maximum number of entries to return (most recent first).
        """
        if data_type:
            rows = self._conn.execute(
                "SELECT * FROM bot_learning_data "
                "WHERE bot_name = ? AND data_type = ? AND retained = 1 "
                "ORDER BY scraped_at DESC LIMIT ?",
                (bot_name, data_type, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM bot_learning_data "
                "WHERE bot_name = ? AND retained = 1 "
                "ORDER BY scraped_at DESC LIMIT ?",
                (bot_name, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def purge_low_relevance(
        self, bot_name: str, threshold: Optional[float] = None
    ) -> int:
        """Mark entries below *threshold* as discarded.

        Returns
        -------
        int
            Number of entries purged.
        """
        cutoff = threshold if threshold is not None else self._retention_threshold
        cursor = self._conn.execute(
            "UPDATE bot_learning_data SET retained = 0 "
            "WHERE bot_name = ? AND relevance_score < ? AND retained = 1",
            (bot_name, cutoff),
        )
        self._conn.commit()
        return cursor.rowcount

    def get_learning_stats(self, bot_name: str) -> dict:
        """Return learning-data stats for a bot."""
        total = self._conn.execute(
            "SELECT COUNT(*) FROM bot_learning_data WHERE bot_name = ?",
            (bot_name,),
        ).fetchone()[0]
        retained = self._conn.execute(
            "SELECT COUNT(*) FROM bot_learning_data WHERE bot_name = ? AND retained = 1",
            (bot_name,),
        ).fetchone()[0]
        avg_rel = (
            self._conn.execute(
                "SELECT AVG(relevance_score) FROM bot_learning_data WHERE bot_name = ?",
                (bot_name,),
            ).fetchone()[0]
            or 0.0
        )
        return {
            "bot_name": bot_name,
            "total_entries": total,
            "retained_entries": retained,
            "discarded_entries": total - retained,
            "avg_relevance": round(avg_rel, 2),
        }

    # ------------------------------------------------------------------
    # Scraper run log
    # ------------------------------------------------------------------

    def log_scraper_run(
        self,
        bot_name: str,
        query: str,
        items_found: int,
        items_retained: int,
        scraper_type: str = "github",
        status: str = "success",
        duration_ms: int = 0,
    ) -> dict:
        """Log one Elite Scraper run result."""
        items_discarded = max(0, items_found - items_retained)
        now = self._now()
        cursor = self._conn.execute(
            """INSERT INTO scraper_runs
               (bot_name, scraper_type, query, items_found, items_retained,
                items_discarded, status, duration_ms, ran_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (bot_name, scraper_type, query, items_found, items_retained,
             items_discarded, status, duration_ms, now),
        )
        self._conn.commit()
        row = self._conn.execute(
            "SELECT * FROM scraper_runs WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)

    def get_scraper_history(self, bot_name: str, limit: int = 20) -> List[dict]:
        """Return recent scraper runs for a bot (most recent first)."""
        rows = self._conn.execute(
            "SELECT * FROM scraper_runs WHERE bot_name = ? "
            "ORDER BY ran_at DESC LIMIT ?",
            (bot_name, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying database connection."""
        self._conn.close()
