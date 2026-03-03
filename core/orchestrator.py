"""
core/orchestrator.py

BotOrchestrator manages the lifecycle of multiple bots, routes messages
between them, and aggregates exported data from all running instances.
"""

import logging
import queue
import threading
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase


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


class _Message:
    """Internal message envelope used by the orchestrator's message bus."""

    __slots__ = ("sender_id", "recipient_id", "topic", "payload", "sent_at")

    def __init__(
        self,
        sender_id: str,
        recipient_id: str,
        topic: str,
        payload: Any,
    ) -> None:
        self.sender_id: str = sender_id
        self.recipient_id: str = recipient_id
        self.topic: str = topic
        self.payload: Any = payload
        self.sent_at: str = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "topic": self.topic,
            "payload": self.payload,
            "sent_at": self.sent_at,
        }


class BotOrchestrator:
    """
    Manages a collection of :class:`~bots.bot_base.BotBase` instances:

    * Start / stop individual bots or all bots at once.
    * Route messages between bots via a central message bus.
    * Collect and aggregate structured data exported by each bot.
    """

    def __init__(self) -> None:
        self._bots: dict[str, BotBase] = {}
        self._bot_threads: dict[str, threading.Thread] = {}
        self._message_queues: dict[str, queue.Queue[_Message]] = {}
        self._message_history: list[dict[str, Any]] = []
        self._lock: threading.Lock = threading.Lock()
        self._router_stop: threading.Event = threading.Event()
        self._router_thread: threading.Thread | None = None

        self.logger: logging.Logger = _get_logger("BotOrchestrator")

    # ------------------------------------------------------------------
    # Bot registration
    # ------------------------------------------------------------------

    def register_bot(self, bot: BotBase) -> None:
        """
        Register a bot with the orchestrator.

        Args:
            bot: The bot instance to register. ``bot.bot_id`` is used as the key.
        """
        with self._lock:
            if bot.bot_id in self._bots:
                self.logger.warning(
                    "Bot already registered: %s. Skipping.", bot.bot_id
                )
                return
            self._bots[bot.bot_id] = bot
            self._message_queues[bot.bot_id] = queue.Queue()
        self.logger.info("Registered bot: %s (%s)", bot.bot_name, bot.bot_id)

    def unregister_bot(self, bot_id: str) -> None:
        """Remove a bot from the orchestrator (stops it first if running)."""
        self.stop_bot(bot_id)
        with self._lock:
            self._bots.pop(bot_id, None)
            self._message_queues.pop(bot_id, None)
        self.logger.info("Unregistered bot: %s", bot_id)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start_bot(self, bot_id: str) -> None:
        """
        Start a registered bot in its own daemon thread.

        Args:
            bot_id: The ID of the bot to start.

        Raises:
            KeyError: If no bot with *bot_id* is registered.
        """
        with self._lock:
            bot = self._bots.get(bot_id)
        if bot is None:
            raise KeyError(f"No bot registered with id={bot_id!r}")

        if bot_id in self._bot_threads and self._bot_threads[bot_id].is_alive():
            self.logger.warning("Bot %s is already running.", bot_id)
            return

        thread = threading.Thread(
            target=self._run_bot_safely,
            args=(bot,),
            daemon=True,
            name=f"Bot-{bot_id}",
        )
        with self._lock:
            self._bot_threads[bot_id] = thread
        thread.start()
        self.logger.info("Started bot: %s", bot_id)

    def _run_bot_safely(self, bot: BotBase) -> None:
        """Wrapper that catches exceptions from bot.run()."""
        try:
            bot.run()
        except Exception as exc:
            bot.handle_error(exc)
            self.logger.exception(
                "Unhandled exception in bot %s: %s", bot.bot_id, exc
            )

    def stop_bot(self, bot_id: str) -> None:
        """
        Signal a bot to stop and wait for its thread to finish.

        Args:
            bot_id: The ID of the bot to stop.
        """
        with self._lock:
            bot = self._bots.get(bot_id)
            thread = self._bot_threads.get(bot_id)

        if bot is None:
            self.logger.warning("stop_bot: no bot registered with id=%s", bot_id)
            return

        bot.stop()
        if thread and thread.is_alive():
            thread.join(timeout=10)
            if thread.is_alive():
                self.logger.warning(
                    "Bot %s thread did not exit within timeout.", bot_id
                )
        self.logger.info("Stopped bot: %s", bot_id)

    def start_all(self) -> None:
        """Start all registered bots."""
        with self._lock:
            bot_ids = list(self._bots.keys())
        for bot_id in bot_ids:
            self.start_bot(bot_id)

    def stop_all(self) -> None:
        """Stop all registered bots and the message router."""
        with self._lock:
            bot_ids = list(self._bots.keys())
        for bot_id in bot_ids:
            self.stop_bot(bot_id)
        self.stop_router()

    # ------------------------------------------------------------------
    # Message routing
    # ------------------------------------------------------------------

    def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        topic: str,
        payload: Any = None,
    ) -> None:
        """
        Enqueue a message from *sender_id* to *recipient_id*.

        Args:
            sender_id: The bot_id of the sending bot (or ``"orchestrator"``).
            recipient_id: The bot_id of the intended recipient.
            topic: A short string describing the message type.
            payload: Arbitrary data to include in the message.

        Raises:
            KeyError: If *recipient_id* is not registered.
        """
        with self._lock:
            q = self._message_queues.get(recipient_id)
        if q is None:
            raise KeyError(
                f"Cannot route message: recipient {recipient_id!r} not registered."
            )
        msg = _Message(sender_id, recipient_id, topic, payload)
        q.put(msg)
        with self._lock:
            self._message_history.append(msg.to_dict())
        self.logger.debug(
            "Message queued: %s -> %s [%s]", sender_id, recipient_id, topic
        )

    def receive_messages(self, bot_id: str) -> list[dict[str, Any]]:
        """
        Drain and return all pending messages for *bot_id*.

        Args:
            bot_id: The recipient bot's ID.

        Returns:
            A list of message dicts (may be empty).
        """
        with self._lock:
            q = self._message_queues.get(bot_id)
        if q is None:
            return []
        messages: list[dict[str, Any]] = []
        while not q.empty():
            try:
                messages.append(q.get_nowait().to_dict())
            except queue.Empty:
                break
        return messages

    def _router_loop(self) -> None:
        """Background thread: logs undelivered messages for observability."""
        self.logger.info("Message router started.")
        while not self._router_stop.is_set():
            self._router_stop.wait(timeout=5)
        self.logger.info("Message router stopped.")

    def start_router(self) -> None:
        """Start the background message router thread."""
        if self._router_thread and self._router_thread.is_alive():
            return
        self._router_stop.clear()
        self._router_thread = threading.Thread(
            target=self._router_loop, daemon=True, name="OrchestratorRouter"
        )
        self._router_thread.start()

    def stop_router(self) -> None:
        """Stop the background message router thread."""
        self._router_stop.set()
        if self._router_thread:
            self._router_thread.join(timeout=10)

    # ------------------------------------------------------------------
    # Data collection
    # ------------------------------------------------------------------

    def collect_all_data(self) -> dict[str, Any]:
        """
        Collect and aggregate structured data exported by every registered bot.

        Returns:
            A dict mapping each bot_id to its exported structured data,
            plus a top-level ``collected_at`` timestamp and bot count.
        """
        with self._lock:
            snapshot = dict(self._bots)

        all_data: dict[str, Any] = {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "bot_count": len(snapshot),
            "bots": {},
        }
        for bot_id, bot in snapshot.items():
            try:
                all_data["bots"][bot_id] = bot.export_structured_data()
            except Exception as exc:
                self.logger.warning(
                    "Failed to export data from bot %s: %s", bot_id, exc
                )
                all_data["bots"][bot_id] = {"error": str(exc)}

        return all_data

    def get_all_statuses(self) -> dict[str, Any]:
        """Return a status dict for every registered bot."""
        with self._lock:
            snapshot = dict(self._bots)
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "bots": {
                bot_id: bot.get_status()
                for bot_id, bot in snapshot.items()
            },
        }

    # ------------------------------------------------------------------
    # Message history
    # ------------------------------------------------------------------

    def get_message_history(self) -> list[dict[str, Any]]:
        """Return a copy of all messages that have been routed."""
        with self._lock:
            return list(self._message_history)
