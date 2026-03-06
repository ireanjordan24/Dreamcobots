"""
SQLite-backed storage for leads, demo analytics, and quote requests.
"""

import sqlite3
import os
import datetime

DB_PATH = os.environ.get("SAAS_BOT_DB", os.path.join(os.path.dirname(__file__), "saas_bot.db"))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                email       TEXT NOT NULL,
                company     TEXT,
                service     TEXT,
                message     TEXT,
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS demo_events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                demo_name   TEXT NOT NULL,
                user_input  TEXT,
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                created_at   TEXT NOT NULL
            );
            """
        )


def save_lead(name: str, email: str, company: str, service: str, message: str) -> int:
    """Insert a new lead and return its id."""
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO leads (name, email, company, service, message, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, company, service, message, _now()),
        )
        return cur.lastrowid


def record_demo(demo_name: str, user_input: str = "") -> None:
    """Record that a demo was run."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO demo_events (demo_name, user_input, created_at) VALUES (?, ?, ?)",
            (demo_name, user_input, _now()),
        )


def record_chat(user_message: str, bot_response: str) -> None:
    """Record a chatbot exchange."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_events (user_message, bot_response, created_at) VALUES (?, ?, ?)",
            (user_message, bot_response, _now()),
        )


def get_analytics() -> dict:
    """Return simple analytics counts."""
    with get_connection() as conn:
        leads_count = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        demo_rows = conn.execute(
            "SELECT demo_name, COUNT(*) as cnt FROM demo_events GROUP BY demo_name"
        ).fetchall()
        chat_count = conn.execute("SELECT COUNT(*) FROM chat_events").fetchone()[0]
    return {
        "total_leads": leads_count,
        "demo_runs": {row["demo_name"]: row["cnt"] for row in demo_rows},
        "chat_interactions": chat_count,
    }


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
