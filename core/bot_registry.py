"""
DreamCo Core — Bot Registry

Tracks all bots that have been approved and registered within the DreamCo OS
runtime so they can be discovered, scheduled, and wired to the event bus.
"""

from __future__ import annotations

from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# In-process registry (global singleton list)
# ---------------------------------------------------------------------------

REGISTERED_BOTS: List[Dict[str, Any]] = []


def register_bot(bot_info: Dict[str, Any]) -> None:
    """
    Add *bot_info* to the global bot registry.

    Parameters
    ----------
    bot_info : dict
        Arbitrary metadata dict describing the bot.  Recommended keys:
        ``name``, ``path``, ``type``, ``status``.
    """
    REGISTERED_BOTS.append(bot_info)


def get_registered_bots() -> List[Dict[str, Any]]:
    """Return a copy of the current registry."""
    return list(REGISTERED_BOTS)


def clear_registry() -> None:
    """Clear all entries from the registry (useful for testing)."""
    REGISTERED_BOTS.clear()


# ---------------------------------------------------------------------------
# BotRegistry class (object-oriented facade over the module-level registry)
# ---------------------------------------------------------------------------

class BotRegistry:
    """
    Object-oriented wrapper around the module-level bot registry.

    Example
    -------
    >>> registry = BotRegistry()
    >>> registry.register({"name": "my_bot", "status": "active"})
    >>> bots = registry.list_bots()
    """

    def register(self, bot_info: Dict[str, Any]) -> None:
        """Add *bot_info* to the global registry."""
        register_bot(bot_info)

    def list_bots(self) -> List[Dict[str, Any]]:
        """Return all registered bots."""
        return get_registered_bots()

    def clear(self) -> None:
        """Clear all entries (useful for testing)."""
        clear_registry()
