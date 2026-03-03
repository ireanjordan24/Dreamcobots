"""
core/watchdog.py

Watchdog that monitors running bots and automatically restarts any that crash.
"""

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any

from core.base_bot import BaseBotCore


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


class Watchdog:
    """
    Monitors a collection of :class:`~core.base_bot.BaseBotCore` instances and
    restarts any that have moved into an unhealthy or stopped state unexpectedly.
    """

    def __init__(
        self,
        check_interval_seconds: int = 30,
        max_restarts: int = 5,
    ) -> None:
        """
        Initialise the Watchdog.

        Args:
            check_interval_seconds: How often to poll bot health.
            max_restarts: Maximum restart attempts per bot before giving up.
        """
        self.check_interval_seconds: int = check_interval_seconds
        self.max_restarts: int = max_restarts

        self._bots: dict[str, BaseBotCore] = {}
        self._restart_counts: dict[str, int] = {}
        self._restart_history: list[dict[str, Any]] = []
        self._lock: threading.Lock = threading.Lock()
        self._stop_event: threading.Event = threading.Event()
        self._monitor_thread: threading.Thread | None = None

        self.logger: logging.Logger = _get_logger("Watchdog")

    # ------------------------------------------------------------------
    # Bot registration
    # ------------------------------------------------------------------

    def register_bot(self, bot_name: str, bot: BaseBotCore) -> None:
        """
        Register a bot to be monitored.

        Args:
            bot_name: A unique identifier for the bot.
            bot: The bot instance to monitor.
        """
        with self._lock:
            self._bots[bot_name] = bot
            self._restart_counts[bot_name] = 0
        self.logger.info("Registered bot for monitoring: %s", bot_name)

    def unregister_bot(self, bot_name: str) -> None:
        """Remove a bot from monitoring."""
        with self._lock:
            self._bots.pop(bot_name, None)
            self._restart_counts.pop(bot_name, None)
        self.logger.info("Unregistered bot: %s", bot_name)

    # ------------------------------------------------------------------
    # Health check & restart
    # ------------------------------------------------------------------

    def _check_bot(self, bot_name: str, bot: BaseBotCore) -> None:
        """Inspect a single bot and restart it if necessary."""
        try:
            healthy = bot.is_healthy()
            state = bot.state
        except Exception as exc:
            self.logger.warning(
                "Error checking bot %s health: %s", bot_name, exc
            )
            healthy = False
            state = "error"

        if not healthy or state in ("stopped", "error"):
            restart_count = self._restart_counts.get(bot_name, 0)
            if restart_count >= self.max_restarts:
                self.logger.error(
                    "Bot %s has reached max restarts (%d). Giving up.",
                    bot_name,
                    self.max_restarts,
                )
                return

            self.logger.warning(
                "Bot %s appears unhealthy (state=%s, healthy=%s). Restarting…",
                bot_name,
                state,
                healthy,
            )
            try:
                bot.restart()
                with self._lock:
                    self._restart_counts[bot_name] += 1
                entry: dict[str, Any] = {
                    "bot_name": bot_name,
                    "restarted_at": datetime.now(timezone.utc).isoformat(),
                    "restart_number": self._restart_counts[bot_name],
                    "reason": f"state={state}, healthy={healthy}",
                }
                self._restart_history.append(entry)
                self.logger.info(
                    "Bot %s restarted (attempt %d/%d).",
                    bot_name,
                    self._restart_counts[bot_name],
                    self.max_restarts,
                )
            except Exception as exc:
                self.logger.exception(
                    "Failed to restart bot %s: %s", bot_name, exc
                )

    def check_all_bots(self) -> None:
        """Run a single health-check pass over all registered bots."""
        with self._lock:
            snapshot = dict(self._bots)
        for bot_name, bot in snapshot.items():
            self._check_bot(bot_name, bot)

    # ------------------------------------------------------------------
    # Monitoring loop
    # ------------------------------------------------------------------

    def _monitoring_loop(self) -> None:
        """Background thread that periodically checks all bots."""
        self.logger.info(
            "Watchdog monitoring loop started (interval=%ds).",
            self.check_interval_seconds,
        )
        while not self._stop_event.is_set():
            self.check_all_bots()
            self._stop_event.wait(timeout=self.check_interval_seconds)
        self.logger.info("Watchdog monitoring loop stopped.")

    def start(self) -> None:
        """Start the watchdog's background monitoring thread."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self.logger.warning("Watchdog is already running.")
            return
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True, name="WatchdogThread"
        )
        self._monitor_thread.start()
        self.logger.info("Watchdog started.")

    def stop(self) -> None:
        """Stop the watchdog's background monitoring thread."""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=self.check_interval_seconds + 5)
        self.logger.info("Watchdog stopped.")

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_bot_health_report(self) -> dict[str, Any]:
        """
        Return a health report for all monitored bots.

        Returns:
            A dict with per-bot status and overall watchdog statistics.
        """
        with self._lock:
            snapshot = dict(self._bots)
            restart_counts = dict(self._restart_counts)

        per_bot: dict[str, Any] = {}
        for bot_name, bot in snapshot.items():
            try:
                status = bot.get_status()
                status["restart_count"] = restart_counts.get(bot_name, 0)
            except Exception as exc:
                status = {"error": str(exc), "restart_count": restart_counts.get(bot_name, 0)}
            per_bot[bot_name] = status

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "monitored_bot_count": len(snapshot),
            "bots": per_bot,
            "restart_history": list(self._restart_history),
        }
