"""
DreamCo Empire OS — Main Entry Point
======================================

Starts the system, loads all bots, triggers the control center, and
runs the perpetual automation loop.

Usage
-----
    python main.py
"""

from __future__ import annotations

import time

from bots.control_center.controller import ControlCenter
from bots.bot_generator_bot.generator import BotGenerator
from bots.ai_learning_system.learning_loop import LearningLoop


def main() -> None:
    print("🚀 Starting DreamCo Empire OS...")

    # Initialise core systems
    control_center = ControlCenter()
    generator = BotGenerator(control_center)
    learning_loop = LearningLoop(control_center, generator)

    # Register built-in core bots
    control_center.register_core_bots()

    # Boot sequence
    print("✅ Core systems initialised")
    print("🤖 Loading bots...")
    control_center.load_bots()

    print("🔁 Entering automation loop...\n")

    # Main loop
    while True:
        try:
            # Execute every registered bot
            control_center.run_cycle()

            # Allow the system to expand itself
            generator.evaluate_and_expand()

            # Learn and optimise
            learning_loop.optimize()

            time.sleep(2)  # Prevent runaway CPU usage

        except KeyboardInterrupt:
            print("\n🛑 DreamCo shutting down gracefully...")
            summary = learning_loop.get_summary()
            gen_summary = generator.get_summary()
            print(f"📊 Learning summary: {summary}")
            print(f"🏭 Generator summary: {gen_summary}")
            break


if __name__ == "__main__":
    main()
