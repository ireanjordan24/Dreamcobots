"""
BuddyAI — central dialogue integration layer for all Dreamcobots sector bots.

Import the main interface:
    from BuddyAI import BuddyBot, EventBus
"""

from .buddy_bot import BuddyBot, BuddyBotError
from .event_bus import EventBus

__all__ = ["BuddyBot", "BuddyBotError", "EventBus"]
