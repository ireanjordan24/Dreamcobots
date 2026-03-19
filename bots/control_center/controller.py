"""
DreamCo Empire OS — Control Center Controller
==============================================

Central orchestration hub for the entire DreamCo bot network.
Registers bots, assigns tasks, enables inter-bot communication,
and runs the main automation loop.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import importlib
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


class ControlCenter:
    """
    Central mission control for the DreamCo Empire OS.

    Responsibilities
    ----------------
    - Register and track all bot instances.
    - Load bots dynamically from the bots directory.
    - Route tasks to the appropriate bots.
    - Enable inter-bot communication via a shared message bus.
    - Run the main automation loop each cycle.
    """

    def __init__(self) -> None:
        self.bots: Dict[str, Any] = {}
        self.tasks: List[dict] = []
        self._message_bus: List[dict] = []
        self._run_log: List[dict] = []

    # ------------------------------------------------------------------
    # Bot registration
    # ------------------------------------------------------------------

    def register_bot(self, name: str, bot_instance: Any) -> None:
        """Register a bot instance under the given name."""
        self.bots[name] = bot_instance
        print(f"✅ Registered bot: {name}")

    def register_core_bots(self) -> None:
        """Register built-in core bots that ship with the DreamCo OS."""
        print("📌 Registering core bots...")

        core_bot_paths = [
            ("dreamco_empire_os", "bots.dreamco_empire_os.empire_os", "DreamCoEmpireOS"),
            ("ai_learning_system", "bots.ai_learning_system.ai_learning_system", "AILearningSystem"),
            ("bot_generator_bot", "bots.bot_generator_bot.bot_generator_bot", "BotGeneratorBot"),
        ]

        for bot_name, module_path, class_name in core_bot_paths:
            try:
                module = importlib.import_module(module_path)
                cls = getattr(module, class_name, None)
                if cls is not None:
                    self.register_bot(bot_name, cls())
            except Exception as exc:  # noqa: BLE001
                print(f"⚠️  Could not load core bot {bot_name}: {exc}")

    # ------------------------------------------------------------------
    # Dynamic bot loading
    # ------------------------------------------------------------------

    def load_bots(self) -> None:
        """
        Walk the ``bots/`` directory and auto-load any module that exposes
        a ``Bot`` class with a ``run()`` method.
        """
        bots_path = os.path.join(os.path.dirname(__file__), "..")
        bots_path = os.path.abspath(bots_path)

        for root, _dirs, files in os.walk(bots_path):
            for file in files:
                if not file.endswith(".py") or file.startswith("__"):
                    continue
                if file in {"tiers.py", "registry.py"}:
                    continue

                rel = os.path.relpath(os.path.join(root, file), os.path.join(bots_path, ".."))
                module_path = rel.replace(os.sep, ".")[:-3]

                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, "Bot"):
                        bot_name = file[:-3]
                        if bot_name not in self.bots:
                            self.bots[bot_name] = module.Bot()
                            print(f"🔌 Auto-loaded bot: {bot_name}")
                except Exception:  # noqa: BLE001
                    pass

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def assign_task(self, task: dict) -> None:
        """Queue a task for execution in the next cycle."""
        self.tasks.append({**task, "queued_at": datetime.now(timezone.utc).isoformat()})

    # ------------------------------------------------------------------
    # Inter-bot communication
    # ------------------------------------------------------------------

    def send_message(self, sender: str, recipient: str, payload: Any) -> None:
        """Post a message from one bot to another via the shared message bus."""
        self._message_bus.append({
            "sender": sender,
            "recipient": recipient,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_messages(self, recipient: str) -> List[dict]:
        """Return and clear all messages addressed to *recipient*."""
        messages = [m for m in self._message_bus if m["recipient"] == recipient]
        self._message_bus = [m for m in self._message_bus if m["recipient"] != recipient]
        return messages

    # ------------------------------------------------------------------
    # Automation loop
    # ------------------------------------------------------------------

    def run_cycle(self) -> Dict[str, Any]:
        """
        Execute one automation cycle:
        1. Run every registered bot that exposes a ``run()`` method.
        2. Drain the task queue.
        3. Log results.

        Returns
        -------
        dict
            A summary of what ran during this cycle.
        """
        print("\n🔄 Running system cycle...")
        results: Dict[str, Any] = {}

        for name, bot in self.bots.items():
            if not hasattr(bot, "run"):
                continue
            try:
                result = bot.run()
                results[name] = {"status": "ok", "result": result}
                print(f"🤖 {name} executed: {result}")
            except Exception as exc:  # noqa: BLE001
                error_msg = f"{type(exc).__name__}: {exc}"
                results[name] = {"status": "error", "error": error_msg}
                print(f"❌ Error in {name}: {error_msg}")

        # Drain tasks
        while self.tasks:
            task = self.tasks.pop(0)
            target = task.get("bot")
            if target and target in self.bots:
                bot = self.bots[target]
                if hasattr(bot, "run"):
                    try:
                        bot.run()
                    except Exception:  # noqa: BLE001
                        pass

        self._run_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bots_run": len(results),
            "results": results,
        })

        return results

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return a snapshot of the control center state."""
        return {
            "total_bots": len(self.bots),
            "registered_bots": list(self.bots.keys()),
            "queued_tasks": len(self.tasks),
            "total_cycles": len(self._run_log),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
