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


class BuddyBotError(Exception):
    """Raised for BuddyBot operational errors."""


class BuddyBot:
    """
    Central orchestrator that manages bot registrations and routes messages.

    Parameters
    ----------
    tier : Tier
        Subscription tier for the BuddyBot hub itself.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._event_bus = EventBus()
        self._registered_bots: dict[str, object] = {}

    def register_bot(self, name: str, bot_instance: object) -> None:
        """Register a bot under the given name."""
        if name in self._registered_bots:
            raise BuddyBotError(f"A bot named '{name}' is already registered.")
        self._registered_bots[name] = bot_instance
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
        Route a message to a registered bot's process() method.

        Parameters
        ----------
        bot_name : str
            Name of the registered bot.
        message : str
            Message to route.
        **kwargs
            Additional keyword arguments forwarded to the bot's process().

        Returns
        -------
        dict
            Result from the bot's process() call.
        """
        bot = self.get_bot(bot_name)
        if not hasattr(bot, "process"):
            raise BuddyBotError(
                f"Bot '{bot_name}' does not implement a process() method."
            )
        result = bot.process(message, **kwargs)
        self._event_bus.publish("message.routed", {
            "bot_name": bot_name,
            "message": message,
            "result": result,
        })
        return result

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
