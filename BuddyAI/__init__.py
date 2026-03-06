"""
BuddyAI - Central AI package for the Buddy SaaS bot.

Buddy understands and executes user commands dynamically,
eliminating the need for specialized apps.
"""

from BuddyAI.buddy_bot import BuddyBot
from BuddyAI.event_bus import EventBus
from BuddyAI.task_engine import TaskEngine
from BuddyAI.library_manager import LibraryManager

__all__ = ["BuddyBot", "EventBus", "TaskEngine", "LibraryManager"]
__version__ = "0.1.0"
