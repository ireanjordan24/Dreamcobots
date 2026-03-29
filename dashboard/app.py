"""
DreamCo Revenue Dashboard

Aggregates bot results and revenue metrics into a single summary view.
Supports both a plain-Python API (for testing) and an optional Flask
HTTP endpoint on port 5001.

Metrics exposed
---------------
  - Per-bot revenue, leads, conversion rate
  - Total portfolio revenue
  - Top performers (by revenue and conversion rate)
  - Scaling events count
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timezone
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import GlobalAISourcesFlow  # noqa: F401
from core.dreamco_orchestrator import DreamCoOrchestrator


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class DashboardApp:
    """
    Revenue dashboard — aggregates and presents DreamCo bot performance.

    Usage
    -----
    dash = DashboardApp()
    view = dash.get_view()   # returns plain dict
    dash.run_server()        # start Flask (requires flask installed)
    """

    def __init__(self, orchestrator: DreamCoOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator or DreamCoOrchestrator()

    # ------------------------------------------------------------------
    # Core view
    # ------------------------------------------------------------------

    def get_view(self) -> dict:
        """
        Run all bots and return the dashboard data dictionary.

        Returns
        -------
        dict with keys: bots (list), total_revenue (float),
        top_performers (list), scaling_events (int), timestamp (str).
        """
        results = self.orchestrator.run_all_bots()

        total_revenue = sum(
            r.get("output", {}).get("revenue", 0)
            for r in results
            if r.get("error") is None
        )

        top_performers = sorted(
            [r for r in results if r.get("error") is None],
            key=lambda r: r.get("output", {}).get("revenue", 0),
            reverse=True,
        )[:5]

        scaling_events = sum(
            1
            for r in results
            if r.get("error") is None and r.get("validation", {}).get("scale", False)
        )

        return {
            "bots": results,
            "total_revenue": round(total_revenue, 2),
            "top_performers": [t.get("bot_name") for t in top_performers],
            "scaling_events": scaling_events,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_summary_stats(self) -> dict:
        """Return lightweight stats without re-running bots (uses history)."""
        return self.orchestrator.get_summary()

    # ------------------------------------------------------------------
    # Optional Flask server
    # ------------------------------------------------------------------

    def run_server(self, port: int = 5001, debug: bool = False) -> None:  # pragma: no cover
        """Start the Flask dashboard server."""
        from flask import Flask, jsonify  # type: ignore[import]

        flask_app = Flask(__name__)
        dash = self

        @flask_app.route("/")
        def index():
            return jsonify(dash.get_view())

        @flask_app.route("/stats")
        def stats():
            return jsonify(dash.get_summary_stats())

        flask_app.run(port=port, debug=debug)


if __name__ == "__main__":  # pragma: no cover
    DashboardApp().run_server()
