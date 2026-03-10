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

    # Or with hub ID (collaborative integration mode):
    hub = BuddyBot("MyHub")
    token = hub.register_bot("mybot")   # returns auth token
    hub.authenticate("mybot", token)    # verify token
"""

import sys
import os
import collections
from typing import Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bots', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from BuddyAI.event_bus import EventBus
from BuddyAI.auth import AuthModule, AuthError


class BuddyBotError(KeyError):
    """Raised for BuddyBot operational errors. Extends KeyError for compatibility."""


class SectorBotProtocol:
    """Protocol for sector bots that can be registered with BuddyBot."""
    def chat(self, message: str, **kwargs) -> dict: ...
    def process(self, message: str, **kwargs) -> dict: ...


class BuddyBot:
    """
    Central orchestrator that manages bot registrations and routes messages.

    Supports two registration modes:

    1. **Instance mode** (legacy): ``register_bot(name, bot_instance)``
       — stores the bot instance and enables ``route_message``.
    2. **Auth mode**: ``register_bot(name)``
       — issues an auth token and returns it.  Use :meth:`authenticate` to
       verify tokens from registered bots.

    Parameters
    ----------
    hub_id_or_tier : str or Tier, optional
        When a :class:`str`, treated as the hub identifier.
        When a :class:`~tiers.Tier`, treated as the subscription tier.
        Defaults to ``Tier.FREE`` when omitted.
    tier : Tier, optional
        Subscription tier, only used when *hub_id_or_tier* is a string.
    """

    def __init__(self, hub_id_or_tier=None, tier: Tier = Tier.FREE):
        if isinstance(hub_id_or_tier, str):
            self.hub_id: str = hub_id_or_tier
            self.tier: Tier = tier
        elif isinstance(hub_id_or_tier, Tier):
            self.hub_id = "BuddyBot"
            self.tier = hub_id_or_tier
        else:
            self.hub_id = "BuddyBot"
            self.tier = Tier.FREE

        self.config = get_tier_config(self.tier)
        self._event_bus = EventBus()
        self._registered_bots: dict[str, object] = {}
        self._auth = AuthModule()
        # Knowledge base: shared key-value store
        self._knowledge: dict[str, Any] = {}
        # Task queue (FIFO)
        self._task_queue: collections.deque = collections.deque()

    # ------------------------------------------------------------------
    # Bot registration
    # ------------------------------------------------------------------

    def register_bot(self, name: str, bot_instance: object = None) -> Optional[str]:
        """Register a bot under the given name.

        Parameters
        ----------
        name:
            Unique identifier for the bot.
        bot_instance:
            The bot object to register.  When *None*, the bot is registered
            in **auth mode** and an authentication token is returned.

        Returns
        -------
        str or None
            Authentication token in auth mode; ``None`` in instance mode.
        """
        if name in self._registered_bots:
            raise BuddyBotError(f"A bot named '{name}' is already registered.")
        if bot_instance is not None:
            self._registered_bots[name] = bot_instance
            self._event_bus.publish("bot_registered", {"name": name})
            self._event_bus.publish("bot.registered", {"name": name})
            return None
        else:
            # Auth mode: issue a token via AuthModule
            token = self._auth.register_bot(name)
            self._registered_bots[name] = {"_auth_bot": True}
            self._event_bus.publish("bot_registered", {"name": name})
            self._event_bus.publish("bot.registered", {"name": name})
            return token

    def unregister_bot(self, name: str) -> None:
        """Remove a registered bot."""
        if name not in self._registered_bots:
            raise BuddyBotError(f"No bot named '{name}' is registered.")
        del self._registered_bots[name]
        # Also remove from auth module if present
        try:
            self._auth.unregister_bot(name)
        except Exception:
            pass
        self._event_bus.publish("bot.unregistered", {"name": name})

    def get_bot(self, name: str) -> object:
        """Retrieve a registered bot by name."""
        if name not in self._registered_bots:
            raise BuddyBotError(f"No bot named '{name}' is registered.")
        return self._registered_bots[name]

    def list_bots(self) -> list[str]:
        """Return sorted list of registered bot names."""
        return sorted(self._registered_bots.keys())

    def connected_bots(self) -> list[str]:
        """Return sorted list of connected bot names (alias for :meth:`list_bots`)."""
        return self.list_bots()

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self, bot_id: str, token: str) -> bool:
        """Verify that *token* is valid for *bot_id*.

        Returns
        -------
        bool
            ``True`` if the token is valid.

        Raises
        ------
        AuthError
            If the token is invalid or the bot is not registered.
        """
        return self._auth.verify_token(bot_id, token)

    # ------------------------------------------------------------------
    # Message routing
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Knowledge base
    # ------------------------------------------------------------------

    def set_knowledge(self, key: str, value: Any) -> None:
        """Store *value* in the shared knowledge base under *key*."""
        self._knowledge[key] = value

    def get_knowledge(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the shared knowledge base.

        Returns *default* if *key* is not found.
        """
        return self._knowledge.get(key, default)

    def delete_knowledge(self, key: str) -> None:
        """Remove *key* from the shared knowledge base (noop if absent)."""
        self._knowledge.pop(key, None)

    def knowledge_keys(self) -> list[str]:
        """Return sorted list of keys in the shared knowledge base."""
        return sorted(self._knowledge.keys())

    # ------------------------------------------------------------------
    # Task queue
    # ------------------------------------------------------------------

    def push_task(self, task: dict) -> None:
        """Enqueue *task* (must be a dict).

        Raises
        ------
        BuddyBotError
            If *task* is not a dict.
        """
        if not isinstance(task, dict):
            raise BuddyBotError("Tasks must be dicts.")
        self._task_queue.append(task)

    def pop_task(self) -> Optional[dict]:
        """Dequeue and return the oldest task, or ``None`` if the queue is empty."""
        if not self._task_queue:
            return None
        return self._task_queue.popleft()

    def pending_tasks(self) -> int:
        """Return the number of tasks currently in the queue."""
        return len(self._task_queue)

    # ------------------------------------------------------------------
    # Event helpers
    # ------------------------------------------------------------------

    def subscribe_event(self, event_type: str, handler) -> None:
        """Subscribe *handler* to *event_type* on the internal event bus."""
        self._event_bus.subscribe(event_type, handler)

    def publish_event(self, event_type: str, payload: Any = None) -> int:
        """Publish *payload* to *event_type* on the internal event bus.

        Returns
        -------
        int
            Number of handlers invoked.
        """
        return self._event_bus.publish(event_type, payload)

    @property
    def event_bus(self) -> EventBus:
        """Return the internal EventBus instance."""
        return self._event_bus

    # ------------------------------------------------------------------
    # Tier helpers
    # ------------------------------------------------------------------

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
