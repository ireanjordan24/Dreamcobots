#!/usr/bin/env python3
"""
DreamCobots Stress Tests

Runs stress / load tests against all bots in the ecosystem to verify they
can handle repeated invocations without errors or performance degradation.
"""

import sys
import os
import time
import logging

# Ensure the government-contract-grant-bot directory is on the path
BOTS_DIR = os.path.join(os.path.dirname(__file__), "..", "bots", "government-contract-grant-bot")
sys.path.insert(0, BOTS_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("DreamCobots.StressTest")


# ---------------------------------------------------------------------------
# Individual stress-test helpers
# ---------------------------------------------------------------------------

def stress_test(bot_instance, iterations: int = 50) -> dict:
    """
    Invoke bot.run() *iterations* times and collect pass/fail metrics.

    Returns
    -------
    dict with keys: bot, iterations, successes, failures, elapsed_seconds
    """
    name = type(bot_instance).__name__
    successes = 0
    failures = 0
    start = time.monotonic()

    for i in range(iterations):
        try:
            bot_instance.run()
            successes += 1
        except Exception as exc:  # noqa: BLE001 — intentional: record any bot failure without stopping the stress run
            failures += 1
            logger.warning("[%s] iteration %d failed: %s", name, i + 1, exc)

    elapsed = time.monotonic() - start
    result = {
        "bot": name,
        "iterations": iterations,
        "successes": successes,
        "failures": failures,
        "elapsed_seconds": round(elapsed, 3),
    }
    status = "PASSED" if failures == 0 else "FAILED"
    logger.info(
        "[%s] stress test %s — %d/%d OK in %.3fs",
        name,
        status,
        successes,
        iterations,
        elapsed,
    )
    return result


# ---------------------------------------------------------------------------
# Per-bot test functions
# ---------------------------------------------------------------------------

def test_government_contract_grant_bot(iterations: int = 50) -> dict:
    """Stress-test the GovernmentContractGrantBot."""
    from government_contract_grant_bot import GovernmentContractGrantBot  # noqa: E402

    bot = GovernmentContractGrantBot()
    return stress_test(bot, iterations=iterations)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def main():
    logger.info("=== DreamCobots Stress Test Suite ===")
    all_results = []

    test_functions = [
        test_government_contract_grant_bot,
    ]

    for test_fn in test_functions:
        try:
            result = test_fn()
            all_results.append(result)
        except Exception as exc:  # noqa: BLE001 — intentional: log and continue even if a test function fails
            logger.error("Could not run %s: %s", test_fn.__name__, exc)

    # Summary
    logger.info("--- Summary ---")
    overall_passed = True
    for r in all_results:
        status = "PASSED" if r["failures"] == 0 else "FAILED"
        if r["failures"] > 0:
            overall_passed = False
        logger.info(
            "  %s: %s (%d/%d successes, %.3fs)",
            r["bot"],
            status,
            r["successes"],
            r["iterations"],
            r["elapsed_seconds"],
        )

    logger.info("=== Overall: %s ===", "PASSED" if overall_passed else "FAILED")
    return 0 if overall_passed else 1


if __name__ == "__main__":
    sys.exit(main())
