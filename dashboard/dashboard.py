"""
dashboard/dashboard.py

Metrics collection and reporting dashboard for DreamCobots.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any


class Dashboard:
    """Collects metrics from bots and generates reports."""

    def collect_metrics(self, bots: list) -> dict:
        """
        Collect status metrics from a list of bot instances.

        Args:
            bots: List of bot objects (must implement ``get_status()``).

        Returns:
            dict with keys: collected_at, bot_count, bots (list of statuses),
            running_count, error_total.
        """
        statuses = []
        for bot in bots:
            if hasattr(bot, "get_status"):
                statuses.append(bot.get_status())

        running_count = sum(1 for s in statuses if s.get("running", False))
        error_total = sum(s.get("error_count", 0) for s in statuses)

        return {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "bot_count": len(bots),
            "bots": statuses,
            "running_count": running_count,
            "error_total": error_total,
        }

    def display_summary(self, metrics: dict) -> str:
        """
        Return a human-readable summary string for *metrics*.

        Args:
            metrics: dict as returned by :meth:`collect_metrics`.

        Returns:
            Multi-line summary string.
        """
        lines = [
            "=== DreamCobots Dashboard ===",
            f"Collected at : {metrics.get('collected_at', 'N/A')}",
            f"Total bots   : {metrics.get('bot_count', 0)}",
            f"Running      : {metrics.get('running_count', 0)}",
            f"Total errors : {metrics.get('error_total', 0)}",
        ]
        return "\n".join(lines)

    def get_bot_status_table(self, bots: list) -> list:
        """
        Return a list of dicts suitable for tabular display.

        Args:
            bots: List of bot objects.

        Returns:
            List of dicts with keys: bot_id, bot_name, running, uptime_seconds,
            activity_count, error_count.
        """
        rows = []
        for bot in bots:
            status = bot.get_status() if hasattr(bot, "get_status") else {}
            rows.append({
                "bot_id": status.get("bot_id", getattr(bot, "bot_id", "?")),
                "bot_name": status.get("bot_name", getattr(bot, "bot_name", "?")),
                "running": status.get("running", False),
                "uptime_seconds": status.get("uptime_seconds"),
                "activity_count": status.get("activity_count", 0),
                "error_count": status.get("error_count", 0),
            })
        return rows

    def generate_html_report(self, metrics: dict) -> str:
        """
        Generate a minimal HTML report from *metrics*.

        Args:
            metrics: dict as returned by :meth:`collect_metrics`.

        Returns:
            HTML string.
        """
        bot_rows = ""
        for bot in metrics.get("bots", []):
            bot_rows += (
                f"<tr><td>{bot.get('bot_id', '')}</td>"
                f"<td>{bot.get('bot_name', '')}</td>"
                f"<td>{'✓' if bot.get('running') else '✗'}</td>"
                f"<td>{bot.get('error_count', 0)}</td></tr>\n"
            )

        return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>DreamCobots Dashboard</title></head>
<body>
<h1>DreamCobots Dashboard</h1>
<p>Collected at: {metrics.get('collected_at', 'N/A')}</p>
<p>Total bots: {metrics.get('bot_count', 0)} &nbsp;|&nbsp;
   Running: {metrics.get('running_count', 0)} &nbsp;|&nbsp;
   Errors: {metrics.get('error_total', 0)}</p>
<table border="1" cellpadding="4" cellspacing="0">
<thead><tr><th>ID</th><th>Name</th><th>Running</th><th>Errors</th></tr></thead>
<tbody>
{bot_rows}</tbody>
</table>
</body>
</html>"""

    def export_metrics_json(self, metrics: dict, path: str) -> None:
        """
        Write *metrics* as JSON to *path*.

        Args:
            metrics: Metrics dict to serialise.
            path: Destination file path.
        """
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(metrics, fh, indent=2, default=str)
