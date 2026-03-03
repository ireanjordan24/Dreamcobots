"""
core/base_bot.py

Abstract core base class for all DreamCobots bots.
Provides lifecycle management, health checks, configuration loading,
and a lightweight synchronous event system.
"""

import json
import logging
import os
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable


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


class BaseBotCore(ABC):
    """
    Core abstract base class providing lifecycle management, health checks,
    configuration loading, and an event bus for all DreamCobots bots.
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        """
        Initialise the core bot.

        Args:
            name: Human-readable name for this bot.
            config: Optional pre-loaded configuration dict. If omitted the bot
                    starts with an empty configuration that can be populated via
                    :meth:`load_config`.
        """
        self.name: str = name
        self.config: dict[str, Any] = config or {}
        self.logger: logging.Logger = _get_logger(name)

        self._state: str = "created"  # created | initialised | running | stopped | error
        self._lock: threading.Lock = threading.Lock()
        self._start_time: datetime | None = None
        self._health_checks: dict[str, Callable[[], bool]] = {}
        self._event_handlers: dict[str, list[Callable[..., None]]] = {}

        self.logger.info("BaseBotCore created: name=%s", name)

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def initialize(self) -> None:
        """Perform one-time setup (e.g. open connections, load models)."""

    @abstractmethod
    def start(self) -> None:
        """Begin the bot's main processing work."""

    @abstractmethod
    def stop(self) -> None:
        """Signal the bot to cease processing gracefully."""

    # ------------------------------------------------------------------
    # Lifecycle management
    # ------------------------------------------------------------------

    def restart(self) -> None:
        """Stop and then re-start the bot."""
        self.logger.info("Restarting bot: %s", self.name)
        self.stop()
        time.sleep(1)
        self.initialize()
        self.start()

    def _set_state(self, state: str) -> None:
        with self._lock:
            self.logger.debug("State transition: %s -> %s", self._state, state)
            self._state = state

    @property
    def state(self) -> str:
        """Return the current lifecycle state of the bot."""
        with self._lock:
            return self._state

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def load_config(self, config_path: str) -> dict[str, Any]:
        """
        Load JSON configuration from *config_path*, applying environment-variable
        overrides for any key matching ``DREAMCOBOTS_<KEY>`` (upper-cased).

        Args:
            config_path: Absolute or relative path to a JSON config file.

        Returns:
            The merged configuration dict.

        Raises:
            FileNotFoundError: If *config_path* does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        self.logger.info("Loading config from %s", config_path)
        with open(config_path, "r", encoding="utf-8") as fh:
            loaded: dict[str, Any] = json.load(fh)

        # Apply environment-variable overrides
        for key in list(loaded.keys()):
            env_key = f"DREAMCOBOTS_{key.upper()}"
            env_val = os.environ.get(env_key)
            if env_val is not None:
                self.logger.debug(
                    "Config override from env: %s=%r", env_key, env_val
                )
                loaded[key] = env_val

        self.config.update(loaded)
        return self.config

    # ------------------------------------------------------------------
    # Health checks
    # ------------------------------------------------------------------

    def register_health_check(
        self, check_name: str, check_fn: Callable[[], bool]
    ) -> None:
        """
        Register a named health-check callable.

        Args:
            check_name: A unique identifier for this check.
            check_fn: A zero-argument callable that returns ``True`` if healthy.
        """
        self._health_checks[check_name] = check_fn
        self.logger.debug("Registered health check: %s", check_name)

    def run_health_checks(self) -> dict[str, bool]:
        """
        Execute all registered health checks.

        Returns:
            A dict mapping check name to boolean health status.
        """
        results: dict[str, bool] = {}
        for name, fn in self._health_checks.items():
            try:
                results[name] = fn()
            except Exception as exc:
                self.logger.warning("Health check %r raised: %s", name, exc)
                results[name] = False
        return results

    def is_healthy(self) -> bool:
        """Return ``True`` if all registered health checks pass."""
        checks = self.run_health_checks()
        return all(checks.values()) if checks else True

    # ------------------------------------------------------------------
    # Event system
    # ------------------------------------------------------------------

    def on_event(self, event_name: str, handler: Callable[..., None]) -> None:
        """
        Subscribe *handler* to *event_name*.

        Args:
            event_name: The event to listen for.
            handler: Callable invoked with keyword arguments when the event fires.
        """
        self._event_handlers.setdefault(event_name, []).append(handler)
        self.logger.debug("Event handler registered: event=%s", event_name)

    def emit_event(self, event_name: str, **kwargs: Any) -> None:
        """
        Emit *event_name*, invoking all registered handlers with *kwargs*.

        Args:
            event_name: The name of the event to emit.
            **kwargs: Arbitrary keyword arguments forwarded to each handler.
        """
        handlers = self._event_handlers.get(event_name, [])
        self.logger.debug(
            "Emitting event=%s to %d handler(s)", event_name, len(handlers)
        )
        for handler in handlers:
            try:
                handler(**kwargs)
            except Exception as exc:
                self.logger.warning(
                    "Event handler for %r raised: %s", event_name, exc
                )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """Return a status snapshot including state and uptime."""
        uptime: float | None = None
        if self._start_time is not None:
            uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
        return {
            "name": self.name,
            "state": self.state,
            "start_time": (
                self._start_time.isoformat() if self._start_time else None
            ),
            "uptime_seconds": uptime,
            "healthy": self.is_healthy(),
        }
