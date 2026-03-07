"""
BuddyBot — central dialogue hub for all Dreamcobots sector bots.

BuddyBot acts as the orchestrator that:
  • registers sector bots by name
  • routes user messages to the appropriate bot
  • provides a unified dialogue history across bots
  • emits lifecycle events on the shared EventBus

Usage
-----
    from BuddyAI.buddy_bot import BuddyBot

    buddy = BuddyBot()
    buddy.register_bot("finance", finance_bot_instance)
    response = buddy.chat("finance", "What is my portfolio balance?")
    print(response["message"])
"""

from __future__ import annotations

import time
from typing import Any, Protocol, runtime_checkable

from .event_bus import EventBus


class BuddyBotError(Exception):
    """Raised for configuration or routing errors inside BuddyBot."""


@runtime_checkable
class SectorBotProtocol(Protocol):
    """
    Minimal interface that every sector bot must implement to be registered
    with BuddyBot.
    """

    def chat(self, message: str, **kwargs: Any) -> dict:
        ...  # pragma: no cover

    def describe_tier(self) -> str:
        ...  # pragma: no cover


class BuddyBot:
    """
    Central dialogue hub for the Dreamcobots platform.

    Parameters
    ----------
    event_bus : EventBus | None
        Shared event bus.  A new bus is created if *None* is provided.

    Events published
    ----------------
    ``buddy.message_received``  -- fired before routing to a sector bot.
    ``buddy.message_responded`` -- fired after a successful bot response.
    ``buddy.bot_registered``    -- fired when a new sector bot is registered.
    ``buddy.bot_unregistered``  -- fired when a sector bot is removed.
    """

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._bus: EventBus = event_bus or EventBus()
        self._bots: dict[str, SectorBotProtocol] = {}
        self._history: list[dict] = []

    # ------------------------------------------------------------------
    # Bot registry
    # ------------------------------------------------------------------

    def register_bot(self, name: str, bot: SectorBotProtocol) -> None:
        """Register *bot* under *name*.  Raises if the name is taken."""
        if name in self._bots:
            raise BuddyBotError(
                f"A bot named '{name}' is already registered. "
                "Use unregister_bot() first."
            )
        if not isinstance(bot, SectorBotProtocol):
            raise BuddyBotError(
                f"Bot '{name}' does not implement the SectorBotProtocol "
                "(must have chat() and describe_tier() methods)."
            )
        self._bots[name] = bot
        self._bus.publish("buddy.bot_registered", {"name": name})

    def unregister_bot(self, name: str) -> None:
        """Remove a previously registered bot.  No-op if not registered."""
        if name in self._bots:
            del self._bots[name]
            self._bus.publish("buddy.bot_unregistered", {"name": name})

    def list_bots(self) -> list[str]:
        """Return the names of all registered sector bots."""
        return list(self._bots.keys())

    # ------------------------------------------------------------------
    # Dialogue routing
    # ------------------------------------------------------------------

    def chat(self, bot_name: str, message: str, **kwargs: Any) -> dict:
        """
        Route *message* to the registered bot called *bot_name*.

        Parameters
        ----------
        bot_name : str
            Name the target bot was registered under.
        message : str
            User's input text.
        **kwargs :
            Extra keyword arguments forwarded to the sector bot's ``chat()``
            method (e.g. ``model=`` overrides).

        Returns
        -------
        dict
            The response dict returned by the sector bot, augmented with
            ``"bot_name"`` and ``"timestamp"`` keys.
        """
        if bot_name not in self._bots:
            available = ", ".join(self._bots) or "(none)"
            raise BuddyBotError(
                f"No bot named '{bot_name}' is registered. "
                f"Available bots: {available}"
            )

        self._bus.publish(
            "buddy.message_received",
            {"bot": bot_name, "message": message},
        )

        response = self._bots[bot_name].chat(message, **kwargs)
        response.setdefault("bot_name", bot_name)
        response.setdefault("timestamp", time.time())

        self._history.append(
            {
                "bot": bot_name,
                "role": "user",
                "content": message,
                "timestamp": response["timestamp"],
            }
        )
        self._history.append(
            {
                "bot": bot_name,
                "role": "assistant",
                "content": response.get("message", ""),
                "timestamp": response["timestamp"],
            }
        )

        self._bus.publish(
            "buddy.message_responded",
            {"bot": bot_name, "response": response},
        )

        return response

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def get_history(self, bot_name: str | None = None) -> list[dict]:
        """
        Return the unified dialogue history.

        Parameters
        ----------
        bot_name : str | None
            If provided, return only entries for that bot.
        """
        if bot_name is None:
            return list(self._history)
        return [e for e in self._history if e["bot"] == bot_name]

    def clear_history(self, bot_name: str | None = None) -> None:
        """Clear dialogue history, optionally scoped to one bot."""
        if bot_name is None:
            self._history = []
        else:
            self._history = [e for e in self._history if e["bot"] != bot_name]

    # ------------------------------------------------------------------
    # Tier information passthrough
    # ------------------------------------------------------------------

    def describe_bot_tier(self, bot_name: str) -> str:
        """Delegate describe_tier() to the named sector bot."""
        if bot_name not in self._bots:
            raise BuddyBotError(f"No bot named '{bot_name}' is registered.")
        return self._bots[bot_name].describe_tier()

    # ------------------------------------------------------------------
    # Event bus access
    # ------------------------------------------------------------------

    @property
    def event_bus(self) -> EventBus:
        """The shared EventBus instance."""
        return self._bus
