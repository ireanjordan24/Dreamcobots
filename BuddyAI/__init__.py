"""
__init__.py – BuddyAI package initialisation.

Expose the most commonly used public symbols at package level.
"""

from .buddy_bot import BuddyBot
from .config import load_config
from .event_bus import EventBus, bus
from .income_tracker import IncomeTracker
from .dashboard import Dashboard
from .content_automation import ContentAutomation
from .market_analysis import MarketAnalysis
from .ml_optimizer import IncomePredictor, OptimizationEngine

__all__ = [
    "BuddyBot",
    "load_config",
    "EventBus",
    "bus",
    "IncomeTracker",
    "Dashboard",
    "ContentAutomation",
    "MarketAnalysis",
    "IncomePredictor",
    "OptimizationEngine",
]
