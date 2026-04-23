"""
Parallel Execution Bot — Runs multiple bots concurrently to maximize throughput.

Accepts a list of bot modules and executes them simultaneously using
Python's ``concurrent.futures.ThreadPoolExecutor``, collecting results
and handling timeouts gracefully.

Usage
-----
    python bots/parallel_execution_bot.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeout

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_BOTS_DIR = os.path.dirname(__file__)
_DEFAULT_TIMEOUT = 60  # seconds per bot
_DEFAULT_WORKERS = 4


def _load_run(bot_name: str):
    """Dynamically load the ``run()`` function from a bot module."""
    path = os.path.join(_BOTS_DIR, f"{bot_name}.py")
    if not os.path.isfile(path):
        return None
    spec = importlib.util.spec_from_file_location(bot_name, path)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "run", None)


def run_parallel(
    bot_names: list[str],
    context: dict | None = None,
    max_workers: int = _DEFAULT_WORKERS,
    timeout: float = _DEFAULT_TIMEOUT,
) -> dict:
    """Execute *bot_names* concurrently and aggregate results.

    Parameters
    ----------
    bot_names : list[str]
        Bot module names to run (e.g. ``["optimizer_bot", "security_auditor_bot"]``).
    context : dict | None
        Shared context forwarded to each bot's ``run()`` function.
    max_workers : int
        Thread pool size.
    timeout : float
        Per-bot timeout in seconds.

    Returns
    -------
    dict
        Keys: total, passed, failed, timed_out, results, elapsed_seconds.
    """
    context = context or {}
    start = time.time()
    results: list[dict] = []
    passed = failed = timed_out = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(_load_and_run, name, context): name
            for name in bot_names
        }
        for future in as_completed(future_map, timeout=timeout * len(bot_names)):
            name = future_map[future]
            try:
                output = future.result(timeout=timeout)
                results.append({"bot": name, "status": "ok", "output": output})
                passed += 1
            except FuturesTimeout:
                results.append({"bot": name, "status": "timeout"})
                timed_out += 1
            except Exception as exc:
                results.append({"bot": name, "status": "error", "error": str(exc)})
                failed += 1

    elapsed = round(time.time() - start, 2)
    return {
        "total": len(bot_names),
        "passed": passed,
        "failed": failed,
        "timed_out": timed_out,
        "elapsed_seconds": elapsed,
        "results": results,
        "status": "all_passed" if failed == 0 and timed_out == 0 else "some_failed",
    }


def _load_and_run(bot_name: str, context: dict):
    """Helper that loads and calls a bot's run() in a thread."""
    run_fn = _load_run(bot_name)
    if run_fn is None:
        raise RuntimeError(f"Bot '{bot_name}' not found or has no run()")
    return run_fn(context)


# Default batch for parallel execution
_DEFAULT_BATCH = [
    "insight_ranker",
    "buddy_bot",
    "feedback_loop_bot",
    "context_pruner_bot",
    "knowledge_sync_bot",
]

def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    context = context or {}
    bots = context.get("bots", _DEFAULT_BATCH)
    return run_parallel(bots, context=context)


if __name__ == "__main__":
    report = run_parallel(_DEFAULT_BATCH)
    print(json.dumps(report, indent=2))
    print(
        f"\n⚡ Parallel run: {report['passed']}/{report['total']} passed "
        f"in {report['elapsed_seconds']}s"
    )
    if report["status"] != "all_passed":
        sys.exit(1)
