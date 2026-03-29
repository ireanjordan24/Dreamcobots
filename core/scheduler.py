"""
DreamCo Scheduler — Auto-Run System

Runs all registered bots on a configurable interval (default: 3600 s).
Keeps a log of every cycle's results for audit and reinvestment decisions.

Usage
-----
    scheduler = Scheduler(interval_seconds=3600)
    scheduler.run_once()       # run one cycle immediately
    scheduler.run_forever()    # loop indefinitely (blocks)
    scheduler.stop()           # signal the loop to stop
"""

from __future__ import annotations

import sys
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import GlobalAISourcesFlow  # noqa: F401
from core.dreamco_orchestrator import DreamCoOrchestrator


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class CycleRecord:
    """Record of one orchestration cycle."""

    cycle_id: int
    started_at: str
    finished_at: Optional[str] = None
    results: List[dict] = field(default_factory=list)
    total_revenue: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "cycle_id": self.cycle_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "results": self.results,
            "total_revenue": round(self.total_revenue, 2),
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------


class Scheduler:
    """
    Runs DreamCo bots on a fixed interval and logs every cycle.

    Parameters
    ----------
    orchestrator     : DreamCoOrchestrator instance (created if None).
    interval_seconds : Seconds between cycles (default 3600 = 1 hour).
    max_cycles       : Stop after this many cycles (None = unlimited).
    """

    def __init__(
        self,
        orchestrator: Optional[DreamCoOrchestrator] = None,
        interval_seconds: int = 3600,
        max_cycles: Optional[int] = None,
    ) -> None:
        self.orchestrator = orchestrator or DreamCoOrchestrator()
        self.interval_seconds = interval_seconds
        self.max_cycles = max_cycles
        self._running = False
        self._cycle_count = 0
        self._cycle_log: List[CycleRecord] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_once(self) -> CycleRecord:
        """Execute a single orchestration cycle and return its record."""
        self._cycle_count += 1
        record = CycleRecord(
            cycle_id=self._cycle_count,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        print(f"[Scheduler] Running DreamCo cycle #{self._cycle_count}…")
        try:
            results = self.orchestrator.run_all_bots()
            record.results = results
            record.total_revenue = sum(
                r.get("output", {}).get("revenue", 0)
                for r in results
                if r.get("error") is None
            )
        except Exception as exc:
            record.error = str(exc)
        finally:
            record.finished_at = datetime.now(timezone.utc).isoformat()

        self._cycle_log.append(record)
        print(f"[Scheduler] Cycle #{self._cycle_count} complete. Revenue: ${record.total_revenue:.2f}")
        return record

    def run_forever(self) -> None:
        """
        Loop indefinitely, running one cycle per interval.

        Call ``stop()`` from another thread to exit the loop cleanly.
        """
        self._running = True
        while self._running:
            self.run_once()
            if self.max_cycles and self._cycle_count >= self.max_cycles:
                print(f"[Scheduler] Reached max_cycles={self.max_cycles}. Stopping.")
                break
            if self._running:
                print(f"[Scheduler] Sleeping {self.interval_seconds}s until next cycle…")
                time.sleep(self.interval_seconds)
        self._running = False

    def stop(self) -> None:
        """Signal the run_forever loop to stop after the current cycle."""
        self._running = False

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_cycle_log(self) -> List[dict]:
        """Return all cycle records as plain dicts."""
        return [c.to_dict() for c in self._cycle_log]

    def get_summary(self) -> dict:
        """High-level summary across all cycles."""
        total_revenue = sum(c.total_revenue for c in self._cycle_log)
        errors = sum(1 for c in self._cycle_log if c.error)
        return {
            "total_cycles": self._cycle_count,
            "total_revenue_usd": round(total_revenue, 2),
            "error_cycles": errors,
            "interval_seconds": self.interval_seconds,
            "is_running": self._running,
        }
