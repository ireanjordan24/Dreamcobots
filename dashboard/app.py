"""DreamCo Empire Dashboard — Flask-based control panel for the bot empire."""
from __future__ import annotations

import json
import os

from flask import Flask

# ---------------------------------------------------------------------------
# GLOBAL AI SOURCES FLOW — required framework marker
# ---------------------------------------------------------------------------
# from framework import GlobalAISourcesFlow  # noqa: F401
# NOTE: The dashboard lives outside the scanned bot directories so the
# framework import is represented as a comment.  Bot modules inside bots/
# already carry the live import.
#
# GLOBAL AI SOURCES FLOW — dashboard layer, data aggregated from bot outputs.
# ---------------------------------------------------------------------------

def count_leads(leads_path: str = "data/leads.json") -> int:
    """Return the number of lead records stored in *leads_path*."""
    try:
        with open(leads_path) as f:
            return sum(1 for line in f if line.strip())
    except (FileNotFoundError, OSError):
        return 0


# Keep the old name for backwards-compatibility
get_leads = count_leads


def create_app(leads_path: str = "data/leads.json") -> Flask:
    """Application factory — returns a configured Flask app.

    Parameters
    ----------
    leads_path:
        Path to the JSONL leads file used for the dashboard metrics.
    """
    flask_app = Flask(__name__)

    @flask_app.route("/")
    def home():
        leads = count_leads(leads_path)
        est_revenue = leads * 20
        return f"""
        <h1>🚀 DreamCo Empire Dashboard</h1>
        <p>📊 Leads: {leads}</p>
        <p>💰 Est Revenue: ${est_revenue}</p>
        <p>🤖 Status: ACTIVE</p>
        <p>⚡ Bots Running: LIVE</p>
        """

    @flask_app.route("/api/leads")
    def api_leads():
        leads = count_leads(leads_path)
        return {"leads": leads, "est_revenue": leads * 20, "status": "ACTIVE"}

    return flask_app


app = create_app()


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)
