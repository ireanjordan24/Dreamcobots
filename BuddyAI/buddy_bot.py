"""
BuddyAI — Buddy Bot

Orchestrator bot that registers, routes messages to, and broadcasts across
all DreamCo ecosystem bots.  Any bot that exposes a ``chat(message)`` method
can be registered.

Buddy Bot rules
---------------
1. Every message routed to a bot deducts tokens from the requesting user's
   billing account (when a BillingSystem is attached).
2. Free-tier users get a daily token allowance; paid subscribers get higher
   limits or unlimited tokens.
3. Consumption is tracked per user and per bot so the platform remains
   cost-neutral — all AI model costs are attributed to clients.
4. Community contributions are encouraged via event notifications.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from BuddyAI.event_bus import EventBus
from BuddyAI.task_engine import TaskEngine
from BuddyAI.library_manager import LibraryManager
from BuddyAI.plugins import productivity as _productivity_plugin
from BuddyAI.plugins import api_integrator as _api_integrator_plugin
from BuddyAI.plugins import data_entry as _data_entry_plugin

if TYPE_CHECKING:
    from bots.token_billing.billing_system import BillingSystem


class BuddyBot:
    """
    Central orchestrator for the DreamCo bot ecosystem.

    Registered bots must expose a ``chat(message: str) -> dict`` method.
    BuddyBot routes messages to individual bots or broadcasts to all of them.

    Attributes
    ----------
    event_bus : EventBus
        Shared event bus for inter-bot communication.
    billing : BillingSystem or None
        Optional billing system for token consumption tracking.
    default_token_cost : int
        Default token cost per routed message when billing is enabled.
    task_engine : TaskEngine
        Core task engine with registered capabilities.
    """

    def __init__(self, billing: Optional["BillingSystem"] = None, default_token_cost: int = 1, enable_scheduler: bool = True) -> None:
        self.event_bus: EventBus = EventBus()
        self._bots: dict[str, object] = {}
        self.billing: Optional["BillingSystem"] = billing
        self.default_token_cost: int = default_token_cost
        self._consumption: dict[str, dict] = {}
        self._running: bool = False
        self._library_manager = LibraryManager()

        # Set up task engine with all plugins
        self.task_engine = TaskEngine()
        _productivity_plugin.register(self.task_engine)
        _api_integrator_plugin.register(self.task_engine)
        _data_entry_plugin.register(self.task_engine)
        # Register install_library capability
        self.task_engine.register_capability("install_library", self._handle_install_library)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the BuddyBot."""
        self._running = True

    def stop(self) -> None:
        """Stop the BuddyBot."""
        self._running = False

    # ------------------------------------------------------------------
    # Bot registry
    # ------------------------------------------------------------------

    def _handle_install_library(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle install_library capability."""
        package = params.get("package", "")
        return self.install_capability(package)

    def chat(self, text: str) -> Dict[str, Any]:
        """Process a user text command and return a result dict."""
        # Publish input event
        self.event_bus.publish("buddy.input.text", {"text": text})
        result = self.task_engine.process_text(text)
        if "success" not in result:
            result["success"] = True
        return result

    def benchmark_task(self, task: str, iterations: int = 5) -> Dict[str, Any]:
        """Run *task* *iterations* times and return benchmark results."""
        timings: List[float] = []
        last_result: Dict[str, Any] = {}
        for _ in range(iterations):
            t0 = time.perf_counter()
            last_result = self.chat(task)
            timings.append(time.perf_counter() - t0)
        mean_time = sum(timings) / len(timings) if timings else 0.0
        return {
            "success": True,
            "benchmark": {
                "iterations": iterations,
                "mean_time_ms": round(mean_time * 1000, 3),
                "timings": timings,
            },
            **{k: v for k, v in last_result.items() if k != "success"},
        }

    def install_capability(self, package: str) -> Dict[str, Any]:
        """Install a Python package as a new capability."""
        if package in self._library_manager._BLOCKED_PACKAGES:
            return {"success": False, "message": f"Package '{package}' is blocked for security reasons."}
        try:
            self._library_manager.install_library(package)
            return {"success": True, "message": f"Package '{package}' installed successfully."}
        except Exception as exc:
            return {"success": False, "message": str(exc)}

    # ------------------------------------------------------------------
    # Bot registry
    # ------------------------------------------------------------------

    def register_bot(self, name: str, bot_instance: object) -> None:
        """
        Register a bot under *name*.

        Parameters
        ----------
        name : str
            Unique identifier for the bot (e.g. 'dreamco_payments').
        bot_instance : object
            Bot instance exposing a ``chat()`` method.
        """
        self._bots[name] = bot_instance
        self.event_bus.publish("bot_registered", {"name": name})

    def unregister_bot(self, name: str) -> None:
        """
        Remove a previously registered bot.

        Parameters
        ----------
        name : str
            Name of the bot to remove.
        """
        if name in self._bots:
            del self._bots[name]
            self.event_bus.publish("bot_unregistered", {"name": name})

    def list_bots(self) -> list:
        """
        Return the names of all registered bots.

        Returns
        -------
        list[str]
            Sorted list of registered bot names.
        """
        return sorted(self._bots.keys())

    # ------------------------------------------------------------------
    # Message routing
    # ------------------------------------------------------------------

    def route_message(self, bot_name: str, message: str) -> dict:
        """
        Route *message* to a specific registered bot.

        Parameters
        ----------
        bot_name : str
            Target bot name.
        message : str
            Message to send.

        Returns
        -------
        dict
            Response from the target bot's ``chat()`` method.

        Raises
        ------
        KeyError
            If *bot_name* is not registered.
        AttributeError
            If the registered bot does not expose a ``chat()`` method.
        """
        if bot_name not in self._bots:
            raise KeyError(f"Bot '{bot_name}' is not registered.")

        bot = self._bots[bot_name]
        if not callable(getattr(bot, "chat", None)):
            raise AttributeError(
                f"Bot '{bot_name}' does not expose a chat() method."
            )

        response = bot.chat(message)
        self.event_bus.publish(
            "message_routed", {"bot_name": bot_name, "message": message}
        )
        return response

    def broadcast(self, message: str) -> dict:
        """
        Send *message* to all registered bots that expose ``chat()``.

        Parameters
        ----------
        message : str
            Message to broadcast.

        Returns
        -------
        dict
            Mapping of bot_name -> response dict from each bot's ``chat()``.
        """
        results: dict[str, dict] = {}
        for name, bot in self._bots.items():
            if callable(getattr(bot, "chat", None)):
                results[name] = bot.chat(message)

        self.event_bus.publish("broadcast_sent", {"message": message})
        return results

    # ------------------------------------------------------------------
    # Subscription & consumption tracking (Buddy Bot rules)
    # ------------------------------------------------------------------

    def track_usage(
        self,
        user_id: str,
        bot_name: str,
        tokens_used: int,
        description: str = "AI model usage",
    ) -> dict:
        """Record token consumption for *user_id* from *bot_name*.

        If a BillingSystem is attached the tokens are deducted from the user's
        balance.  Consumption is always recorded in the local registry regardless.

        Parameters
        ----------
        user_id : str
            The user being charged.
        bot_name : str
            The bot that performed the work.
        tokens_used : int
            Number of tokens consumed.
        description : str
            Human-readable description of the usage event.

        Returns
        -------
        dict
            Updated consumption summary for *user_id*.
        """
        if user_id not in self._consumption:
            self._consumption[user_id] = {"total_tokens": 0, "by_bot": {}}
        record = self._consumption[user_id]
        record["total_tokens"] += tokens_used
        record["by_bot"][bot_name] = record["by_bot"].get(bot_name, 0) + tokens_used

        if self.billing is not None:
            self.billing.deduct_tokens(user_id, tokens_used, description)

        self.event_bus.publish(
            "usage_tracked",
            {
                "user_id": user_id,
                "bot_name": bot_name,
                "tokens_used": tokens_used,
                "description": description,
            },
        )
        return self.get_consumption_report(user_id)

    def get_consumption_report(self, user_id: str) -> dict:
        """Return a consumption summary for *user_id*.

        Returns
        -------
        dict
            Keys: ``user_id``, ``total_tokens``, ``by_bot``, ``balance``
            (only present when billing is attached).
        """
        report: dict = {
            "user_id": user_id,
            **self._consumption.get(user_id, {"total_tokens": 0, "by_bot": {}}),
        }
        if self.billing is not None:
            try:
                report["balance"] = self.billing.get_balance(user_id)
            except KeyError:
                pass
        return report
