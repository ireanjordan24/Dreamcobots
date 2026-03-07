"""BuddyAI — central AI management package for the Dreamcobots platform."""

from BuddyAI.event_bus import EventBus
from BuddyAI.buddy_bot import BuddyBot

__all__ = ["BuddyBot", "EventBus"]
