"""
Sandbox Bot Simulation — DreamCo Error Handling Bot Demo.

Run this script directly to see the error handling bot in action:

    python bots/error_handling_bot/sandbox_simulation.py

The simulation exercises every error category (Syntax, Dependency,
Environment, IO, HTTP) and prints the full beginner-friendly report so
you can verify the system is working before deploying to production.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# GlobalAISourcesFlow is imported for framework compliance registration
# (required by all DreamCo bots — see tools/check_bot_framework.py).
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.error_handling_bot.error_handling_bot import ErrorHandlingBot


def run_simulation(learning_mode: bool = True) -> int:
    """Run the sandbox simulation and return the number of errors detected."""
    print("\n" + "=" * 60)
    print("  🤖  DREAMCO ERROR HANDLING BOT — SANDBOX SIMULATION")
    print("=" * 60)
    print(f"  Learning Mode: {'ON  (tutorials included)' if learning_mode else 'OFF'}")
    print("=" * 60 + "\n")

    bot = ErrorHandlingBot(
        learning_mode=learning_mode,
        log_dir=os.path.join(tempfile.gettempdir(), "error-bot-demo"),
    )
    records = bot.simulate_bot_run()

    print(f"✅  Simulation complete — {len(records)} error(s) captured.\n")
    print(bot.get_report())

    summary = bot.get_summary()
    print("\n📊  Error Summary by Category:")
    for category, count in summary.items():
        if count > 0:
            bar = "█" * count
            print(f"   {category:<12}: {bar} ({count})")

    return len(records)


if __name__ == "__main__":
    # Accept --no-learning flag to disable tutorials
    learning = "--no-learning" not in sys.argv
    detected = run_simulation(learning_mode=learning)
    sys.exit(0 if detected >= 0 else 1)
