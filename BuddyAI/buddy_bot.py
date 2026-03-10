"""
BuddyAI BuddyBot — central orchestrator for the Dreamcobots bot platform.

Usage
-----
    from BuddyAI.buddy_bot import BuddyBot
    from bots.ai_chatbot.chatbot import Chatbot
    from tiers import Tier

    hub = BuddyBot(tier=Tier.PRO)
    hub.register_bot("chatbot", Chatbot(tier=Tier.PRO))
    result = hub.route_message("chatbot", "Hello!")
    print(result)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bots', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from BuddyAI.event_bus import EventBus


class BuddyBotError(KeyError):
    """Raised for BuddyBot operational errors. Extends KeyError for compatibility."""


class BuddyBot:
    """
    Central orchestrator that manages bot registrations and routes messages.

    Parameters
    ----------
    tier : Tier
        Subscription tier for the BuddyBot hub itself.
    """

    def __init__(self, tier: Tier = Tier.FREE, enable_scheduler: bool = True):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._event_bus = EventBus()
        self._registered_bots: dict[str, object] = {}
        self._running: bool = False
        self._todos: list[str] = []

        # Task engine integration (from add-buddy-saas-bot)
        try:
            from BuddyAI.task_engine import TaskEngine
            from BuddyAI.library_manager import LibraryManager
            from BuddyAI.benchmarks import Benchmarks
            self.task_engine = TaskEngine()
            self.library_manager = LibraryManager()
            self.benchmarks = Benchmarks()
        except ImportError:
            self.task_engine = None
            self.library_manager = None
            self.benchmarks = None

    def start(self) -> None:
        """Start the BuddyBot and load plugins."""
        self._running = True
        if self.task_engine is not None:
            self._load_plugins()
        self._event_bus.publish("buddy.started", {"version": "1.0.0"})

    def stop(self) -> None:
        """Stop the BuddyBot."""
        self._running = False

    def _load_plugins(self) -> None:
        """Load all built-in plugins and register their capabilities."""
        try:
            from BuddyAI.plugins import productivity, data_entry, api_integrator
            productivity.register(self.task_engine)
            data_entry.register(self.task_engine)
            api_integrator.register(self.task_engine)
        except ImportError:
            pass
        if self.task_engine:
            self.task_engine.register_capability(
                "install_library", lambda p: self.install_capability(p.get("package", ""))
            )

    def chat(self, text: str) -> dict:
        """Handle a text message and return a response dict."""
        self._event_bus.publish("buddy.input.text", {"text": text})
        if self.task_engine is not None:
            result = self.task_engine.process_text(text)
        else:
            result = self._simple_chat(text)
        self._event_bus.publish("buddy.output", result)
        return result

    def _simple_chat(self, text: str) -> dict:
        """Fallback simple chat handler."""
        if not text or not text.strip():
            return {"success": False, "message": "Empty input received."}
        text_lower = text.lower()
        if "help" in text_lower:
            return {"success": True, "message": "I can help with todos, status, and bot routing. Try 'add todo <item>'."}
        if "add todo" in text_lower:
            item = text_lower.replace("add todo", "").strip()
            self._todos.append(item)
            return {"success": True, "message": f"Added todo: {item}"}
        if "list" in text_lower and "todo" in text_lower:
            return {"success": True, "message": "Todos: " + ", ".join(self._todos), "items": self._todos[:]}
        return {"success": False, "message": f"Unknown command: {text}"}

    def benchmark_task(self, task: str, iterations: int = 5) -> dict:
        """Benchmark a task by running it multiple times."""
        import time
        times = []
        for _ in range(iterations):
            start = time.time()
            self.chat(task)
            times.append(time.time() - start)
        avg = sum(times) / len(times)
        return {
            "success": True,
            "message": f"Benchmarked '{task}' over {iterations} iterations. Avg: {avg:.4f}s",
            "benchmark": {
                "task": task,
                "iterations": iterations,
                "avg_time_s": avg,
                "min_time_s": min(times),
                "max_time_s": max(times),
            }
        }

    def install_capability(self, package: str) -> dict:
        """Install a new capability (blocked for security)."""
        BLOCKED = {"os", "sys", "subprocess", "shutil", "socket"}
        if not package:
            return {"success": False, "message": "No package specified."}
        if package in BLOCKED:
            return {"success": False, "message": f"Package '{package}' is blocked for security reasons."}
        if self.library_manager is not None:
            try:
                self.library_manager.install_library(package)
                return {"success": True, "message": f"Package '{package}' installed."}
            except Exception as e:
                return {"success": False, "message": str(e)}
        return {"success": False, "message": "Library manager not available."}

    def register_bot(self, name: str, bot_instance: object) -> None:
        """Register a bot under the given name."""
        if name in self._registered_bots:
            raise BuddyBotError(f"A bot named '{name}' is already registered.")
        self._registered_bots[name] = bot_instance
        self._event_bus.publish("bot_registered", {"name": name})
        self._event_bus.publish("bot.registered", {"name": name})

    def unregister_bot(self, name: str) -> None:
        """Remove a registered bot."""
        if name not in self._registered_bots:
            raise BuddyBotError(f"No bot named '{name}' is registered.")
        del self._registered_bots[name]
        self._event_bus.publish("bot.unregistered", {"name": name})

    def get_bot(self, name: str) -> object:
        """Retrieve a registered bot by name."""
        if name not in self._registered_bots:
            raise BuddyBotError(f"No bot named '{name}' is registered.")
        return self._registered_bots[name]

    def list_bots(self) -> list[str]:
        """Return sorted list of registered bot names."""
        return sorted(self._registered_bots.keys())

    def route_message(self, bot_name: str, message: str, **kwargs) -> dict:
        """
        Route a message to a registered bot.

        Tries the bot's ``chat()`` method first; falls back to ``process()``.

        Parameters
        ----------
        bot_name : str
            Name of the registered bot.
        message : str
            Message to route.
        **kwargs
            Additional keyword arguments forwarded to the bot's method.

        Returns
        -------
        dict
            Result from the bot's chat() or process() call.
        """
        bot = self.get_bot(bot_name)
        if hasattr(bot, "chat"):
            result = bot.chat(message, **kwargs)
        elif hasattr(bot, "process"):
            result = bot.process(message, **kwargs)
        else:
            raise BuddyBotError(
                f"Bot '{bot_name}' does not implement a chat() or process() method."
            )
        self._event_bus.publish("message.routed", {
            "bot_name": bot_name,
            "message": message,
            "result": result,
        })
        return result

    def broadcast(self, message: str, **kwargs) -> dict:
        """
        Send a message to all registered bots.

        Parameters
        ----------
        message : str
            Message to broadcast.
        **kwargs
            Additional keyword arguments forwarded to each bot's method.

        Returns
        -------
        dict
            Mapping of bot_name -> result for each registered bot.
        """
        results = {}
        for name in self._registered_bots:
            try:
                results[name] = self.route_message(name, message, **kwargs)
            except BuddyBotError:
                results[name] = {"error": f"Bot '{name}' could not process message"}
        return results

    @property
    def event_bus(self) -> EventBus:
        """Return the internal EventBus instance."""
        return self._event_bus

    def describe_tier(self) -> str:
        """Print and return a description of the current BuddyBot tier."""
        limit = (
            "Unlimited"
            if self.config.requests_per_month is None
            else f"{self.config.requests_per_month:,}"
        )
        lines = [
            f"=== {self.config.name} BuddyBot Tier ===",
            f"Price   : ${self.config.price_usd_monthly:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {self.config.support_level}",
            "",
            "Platform features:",
        ]
        for feat in self.config.features:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        lines.append(f"\nRegistered bots: {len(self._registered_bots)}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg
        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New platform features:",
        ]
        current_feats = set(self.config.features)
        for feat in next_cfg.features:
            if feat not in current_feats:
                lines.append(f"  + {feat.replace('_', ' ').title()}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing BuddyBot or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output
