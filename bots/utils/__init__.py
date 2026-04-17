"""
DreamCobots — Shared Utilities Package

Provides structured logging, centralized error handling, and
performance metrics helpers for all bots.
"""

from .error_handler import BotError, retry, safe_run
from .logger import BotLogger, get_logger

__all__ = [
    "get_logger",
    "BotLogger",
    "BotError",
    "retry",
    "safe_run",
]
