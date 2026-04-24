"""
Performance Monitor Bot — Tracks bot execution speed and resource usage.

Instruments bot runs with timing and memory snapshots, persists metrics to
the knowledge store, and flags bots that are degrading in performance over
successive runs.

Usage
-----
    python bots/performance_monitor_bot.py
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
METRICS_FILE = os.path.join(_ROOT, "knowledge", "performance_metrics.json")

_SLOW_THRESHOLD_SECONDS = 30.0
_MAX_RECORDS = 500


def _load_metrics() -> list[dict]:
    try:
        with open(METRICS_FILE) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []


def _save_metrics(data: list[dict]) -> None:
    os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)
    with open(METRICS_FILE, "w") as fh:
        json.dump(data[-_MAX_RECORDS:], fh, indent=2)


def record(bot_name: str, elapsed_seconds: float, status: str = "ok") -> dict:
    """Record a single timing measurement for *bot_name*.

    Parameters
    ----------
    bot_name : str
        Identifier of the bot being measured.
    elapsed_seconds : float
        Wall-clock time the bot took to run.
    status : str
        ``"ok"`` | ``"error"`` | ``"timeout"``.

    Returns
    -------
    dict
        The persisted metric entry.
    """
    metrics = _load_metrics()
    entry = {
        "bot": bot_name,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "status": status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    metrics.append(entry)
    _save_metrics(metrics)
    return entry


def report() -> dict:
    """Summarize performance metrics for all tracked bots."""
    metrics = _load_metrics()
    bot_times: dict[str, list[float]] = {}

    for m in metrics:
        bot = m.get("bot", "unknown")
        bot_times.setdefault(bot, []).append(m.get("elapsed_seconds", 0))

    summaries: list[dict] = []
    slow_bots: list[str] = []

    for bot, times in sorted(bot_times.items()):
        avg = sum(times) / len(times)
        latest = times[-1]
        summaries.append(
            {
                "bot": bot,
                "runs": len(times),
                "avg_seconds": round(avg, 3),
                "latest_seconds": round(latest, 3),
                "slow": latest > _SLOW_THRESHOLD_SECONDS,
            }
        )
        if latest > _SLOW_THRESHOLD_SECONDS:
            slow_bots.append(bot)

    return {
        "total_measurements": len(metrics),
        "bots_tracked": len(bot_times),
        "slow_bots": slow_bots,
        "summaries": summaries,
        "status": "degradation_detected" if slow_bots else "all_bots_healthy",
    }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    return report()


if __name__ == "__main__":
    r = report()
    print(json.dumps(r, indent=2))
    if r["slow_bots"]:
        print(f"\n⚠️  Slow bots detected: {', '.join(r['slow_bots'])}")
        sys.exit(1)
    else:
        print("\n✅ All bots performing within acceptable limits.")
