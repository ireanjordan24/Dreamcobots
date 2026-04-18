"""
DreamCo Sandbox — Report Generator

Collects :class:`BotRating` objects produced by
:class:`~sandbox.performance_rating.PerformanceRatingSystem` and renders
human-readable (plain-text) and machine-readable (JSON) reports suitable for:

  * CI/CD pipeline logs
  * Client-facing post-test summaries
  * Performance-trend storage

Usage
-----
::

    from sandbox.performance_rating import PerformanceRatingSystem, TaskResult
    from sandbox.report_generator import SandboxReportGenerator

    rg = SandboxReportGenerator(test_duration_hours=24)
    for bot_name, results in per_bot_results.items():
        prs = PerformanceRatingSystem(bot_name)
        prs.record_many(results)
        rg.add_rating(prs.compute_rating())

    print(rg.render_text())
    rg.save_json("/path/to/report.json")
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sandbox.performance_rating import BotRating


# ---------------------------------------------------------------------------
# SandboxReportGenerator
# ---------------------------------------------------------------------------


class SandboxReportGenerator:
    """
    Aggregates :class:`BotRating` results and produces formatted reports.

    Parameters
    ----------
    test_duration_hours : float
        Duration of the sandbox run (for display purposes).
    report_title : str
        Optional custom title printed at the top of the report.
    """

    def __init__(
        self,
        test_duration_hours: float = 24.0,
        report_title: str = "DreamCo Sandbox — Performance Report",
    ) -> None:
        self.test_duration_hours = test_duration_hours
        self.report_title = report_title
        self._ratings: List[BotRating] = []
        self._generated_at: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def add_rating(self, rating: BotRating) -> None:
        """Append a :class:`BotRating` to the report."""
        self._ratings.append(rating)

    def add_ratings(self, ratings: List[BotRating]) -> None:
        """Bulk-add a list of :class:`BotRating` objects."""
        self._ratings.extend(ratings)

    def clear(self) -> None:
        """Remove all ratings and reset the report."""
        self._ratings.clear()
        self._generated_at = None

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render_text(self) -> str:
        """
        Return a multi-line ASCII report string.

        Suitable for printing to a terminal or appending to CI logs.
        """
        self._generated_at = datetime.now(timezone.utc)
        lines = [
            "╔══════════════════════════════════════════════════════════════════╗",
            f"║  {self.report_title:<64}║",
            f"║  Generated : {self._generated_at.strftime('%Y-%m-%d %H:%M:%S UTC'):<52}║",
            f"║  Test duration : {self.test_duration_hours:.1f} hours{'':<46}║",
            f"║  Bots evaluated : {len(self._ratings):<47}║",
            "╠══════════════════════════════════════════════════════════════════╣",
        ]

        if not self._ratings:
            lines += [
                "║  No bot ratings available.                                       ║",
                "╚══════════════════════════════════════════════════════════════════╝",
            ]
            return "\n".join(lines)

        for rating in sorted(self._ratings, key=lambda r: r.star_rating, reverse=True):
            stars_str = "★" * int(rating.star_rating) + "☆" * (5 - int(rating.star_rating))
            lines += [
                f"║  Bot       : {rating.bot_name:<53}║",
                f"║  Rating    : {stars_str}  {rating.label:<45}║",
                f"║  Score     : {rating.weighted_score:>6.2f} / 100{'':<46}║",
                f"║  Tasks     : {rating.total_tasks} total, "
                f"{rating.successful_tasks} passed, "
                f"{rating.failed_tasks} failed{'':<27}║",
                f"║  Success % : {rating.success_rate * 100:>6.2f}%{'':<52}║",
                f"║  Error   % : {rating.error_rate * 100:>6.2f}%{'':<52}║",
                "╠══════════════════════════════════════════════════════════════════╣",
            ]

        lines[-1] = "╚══════════════════════════════════════════════════════════════════╝"
        return "\n".join(lines)

    def render_json(self) -> str:
        """Return the report as a formatted JSON string."""
        self._generated_at = datetime.now(timezone.utc)
        data = self._build_dict()
        return json.dumps(data, indent=2)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_text(self, path: str) -> None:
        """Write the text report to *path*."""
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.render_text())

    def save_json(self, path: str) -> None:
        """Write the JSON report to *path*."""
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.render_json())

    # ------------------------------------------------------------------
    # Summary helpers
    # ------------------------------------------------------------------

    def summary(self) -> Dict:
        """Return a lightweight summary dict (no full per-bot breakdown)."""
        if not self._ratings:
            return {"bots_evaluated": 0, "average_score": 0.0, "average_stars": 0.0}
        avg_score = sum(r.weighted_score for r in self._ratings) / len(self._ratings)
        avg_stars = sum(r.star_rating for r in self._ratings) / len(self._ratings)
        top_bot = max(self._ratings, key=lambda r: r.weighted_score)
        return {
            "bots_evaluated": len(self._ratings),
            "average_score": round(avg_score, 2),
            "average_stars": round(avg_stars, 2),
            "top_bot": top_bot.bot_name,
            "top_bot_score": round(top_bot.weighted_score, 2),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_dict(self) -> Dict:
        ts = self._generated_at or datetime.now(timezone.utc)
        return {
            "report_title": self.report_title,
            "generated_at": ts.isoformat(),
            "test_duration_hours": self.test_duration_hours,
            "summary": self.summary(),
            "bot_ratings": [r.as_dict() for r in self._ratings],
        }
