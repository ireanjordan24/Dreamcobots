"""
framework/base_bot.py

Concrete base bot class for the DreamCobots framework.
Unlike bots.bot_base.BotBase (which is abstract), this class provides
full default implementations so it can be instantiated directly or subclassed.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any


def _get_logger(name: str) -> logging.Logger:
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


class BaseBot:
    """
    Concrete base bot for the DreamCobots framework.

    Provides message processing, learning, capability management,
    statistics tracking, and lifecycle management out of the box.
    """

    def __init__(
        self,
        name: str,
        description: str,
        capabilities: list[str],
    ) -> None:
        """
        Initialise the bot.

        Args:
            name: Human-readable name.
            description: Short description of what this bot does.
            capabilities: List of capability tags (e.g. ``["nlp", "search"]``).
        """
        self.name: str = name
        self.description: str = description
        self.capabilities: list[str] = list(capabilities)

        self._running: bool = False
        self._lock: threading.RLock = threading.RLock()
        self._message_count: int = 0
        self._error_count: int = 0
        self._learn_count: int = 0
        self._knowledge_base: dict[str, Any] = {}
        self._created_at: str = datetime.now(timezone.utc).isoformat()
        self._started_at: str | None = None

        self.logger: logging.Logger = _get_logger(f"BaseBot[{name}]")
        self.logger.info("Initialised bot '%s': %s", name, description)

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def process_message(self, message: str) -> str:
        """
        Process an incoming text message and return a response.

        Args:
            message: The raw message string.

        Returns:
            A response string.
        """
        with self._lock:
            self._message_count += 1
        self.logger.debug("Processing message #%d: %r", self._message_count, message)

        # Simple keyword reflection; subclasses should override for richer logic.
        lowered = message.lower().strip()
        if not lowered:
            return f"[{self.name}] Please send a non-empty message."
        if lowered in ("hello", "hi", "hey"):
            return f"[{self.name}] Hello! How can I assist you today?"
        if "help" in lowered:
            caps = ", ".join(self.capabilities) if self.capabilities else "none"
            return f"[{self.name}] I can help with: {caps}."
        if "status" in lowered:
            stats = self.get_stats()
            return (
                f"[{self.name}] Running: {stats['running']}, "
                f"Messages processed: {stats['message_count']}."
            )
        return f"[{self.name}] Received: {message}"

    def learn(self, data: dict[str, Any]) -> None:
        """
        Incorporate new knowledge into the bot's knowledge base.

        Args:
            data: A dictionary of key-value pairs to learn.
        """
        if not isinstance(data, dict):
            self.logger.warning("learn() expects a dict, got %s", type(data).__name__)
            return
        with self._lock:
            self._knowledge_base.update(data)
            self._learn_count += 1
        self.logger.debug("Learned %d new items (total cycles: %d)", len(data), self._learn_count)

    def get_capabilities(self) -> list[str]:
        """Return the list of capability tags for this bot."""
        with self._lock:
            return list(self.capabilities)

    def get_stats(self) -> dict[str, Any]:
        """
        Return runtime statistics for this bot.

        Returns:
            A dict with ``name``, ``description``, ``running``,
            ``message_count``, ``learn_count``, ``error_count``,
            ``knowledge_size``, ``created_at``, ``started_at``.
        """
        with self._lock:
            return {
                "name": self.name,
                "description": self.description,
                "running": self._running,
                "message_count": self._message_count,
                "learn_count": self._learn_count,
                "error_count": self._error_count,
                "knowledge_size": len(self._knowledge_base),
                "created_at": self._created_at,
                "started_at": self._started_at,
            }

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Mark the bot as running and record the start time."""
        with self._lock:
            if self._running:
                self.logger.warning("Bot '%s' is already running.", self.name)
                return
            self._running = True
            self._started_at = datetime.now(timezone.utc).isoformat()
        self.logger.info("Bot '%s' started.", self.name)

    def stop(self) -> None:
        """Mark the bot as stopped."""
        with self._lock:
            if not self._running:
                self.logger.warning("Bot '%s' is not running.", self.name)
                return
            self._running = False
        self.logger.info("Bot '%s' stopped.", self.name)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_structured_data(self) -> dict[str, Any]:
        """Export a snapshot of the bot's state for external consumption."""
        return {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "stats": self.get_stats(),
            "capabilities": self.get_capabilities(),
            "knowledge_base_keys": list(self._knowledge_base.keys()),
        }
