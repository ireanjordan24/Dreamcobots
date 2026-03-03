"""
bots/bot_base.py

Abstract base class for all DreamCobots bots.
Provides logging, thread safety, lifecycle management, and structured data export.
"""

import logging
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any


def _get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


class BotBase(ABC):
    """
    Abstract base class for all DreamCobots bots.

    Subclasses must implement :meth:`run` and :meth:`stop`.
    """

    def __init__(self, bot_name: str, bot_id: str) -> None:
        """
        Initialise the bot.

        Args:
            bot_name: Human-readable name for this bot instance.
            bot_id: Unique identifier for this bot instance.
        """
        self.bot_name: str = bot_name
        self.bot_id: str = bot_id

        self._running: bool = False
        self._lock: threading.RLock = threading.RLock()  # reentrant to allow nested acquisition
        self._activity_log: list[dict[str, Any]] = []
        self._error_log: list[dict[str, Any]] = []
        self._start_time: datetime | None = None

        self.logger: logging.Logger = _get_logger(f"{bot_name}[{bot_id}]")
        self.logger.info("Bot initialised: name=%s, id=%s", bot_name, bot_id)

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def run(self) -> None:
        """Start the bot's main processing loop."""

    @abstractmethod
    def stop(self) -> None:
        """Signal the bot to stop its processing loop."""

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def _set_running(self, state: bool) -> None:
        """Thread-safe setter for the running flag."""
        with self._lock:
            self._running = state

    @property
    def is_running(self) -> bool:
        """Return whether the bot is currently running."""
        with self._lock:
            return self._running

    # ------------------------------------------------------------------
    # Activity / error logging
    # ------------------------------------------------------------------

    def log_activity(self, activity: str) -> None:
        """
        Log an activity message for this bot.

        Args:
            activity: A human-readable description of the activity.
        """
        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bot_id": self.bot_id,
            "bot_name": self.bot_name,
            "activity": activity,
        }
        with self._lock:
            self._activity_log.append(entry)
        self.logger.info("Activity: %s", activity)

    def handle_error(self, error: Exception) -> None:
        """
        Record and log an exception encountered by this bot.

        Args:
            error: The exception to handle.
        """
        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bot_id": self.bot_id,
            "bot_name": self.bot_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
        }
        with self._lock:
            self._error_log.append(entry)
        self.logger.exception("Error encountered: %s", error)

    # ------------------------------------------------------------------
    # Status / data export
    # ------------------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """
        Return a status dictionary for this bot.

        Returns:
            A dict containing bot identity, running state, uptime,
            activity count, and error count.
        """
        uptime_seconds: float | None = None
        if self._start_time is not None:
            uptime_seconds = (
                datetime.now(timezone.utc) - self._start_time
            ).total_seconds()

        with self._lock:
            return {
                "bot_id": self.bot_id,
                "bot_name": self.bot_name,
                "running": self._running,
                "start_time": (
                    self._start_time.isoformat() if self._start_time else None
                ),
                "uptime_seconds": uptime_seconds,
                "activity_count": len(self._activity_log),
                "error_count": len(self._error_log),
            }

    def export_structured_data(self) -> dict[str, Any]:
        """
        Export all structured data produced by this bot for DataForge ingestion.

        Returns:
            A dict with bot metadata, activity log, and error log.
        """
        with self._lock:
            return {
                "bot_id": self.bot_id,
                "bot_name": self.bot_name,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "status": self.get_status(),
                "activity_log": list(self._activity_log),
                "error_log": list(self._error_log),
            }
