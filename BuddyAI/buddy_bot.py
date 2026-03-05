"""
BuddyAI – Buddy Bot Core
------------------------
``BuddyBot`` is the central hub for the DreamCobots ecosystem.  It:

* Manages bot registration and authentication (:mod:`BuddyAI.auth`).
* Provides a shared event bus for bot-to-bot messaging
  (:mod:`BuddyAI.event_bus`).
* Maintains a shared knowledge base (key/value store).
* Exposes a shared task queue that any connected bot may push to and
  pull from.

Connected bots interact through the public API rather than directly
accessing each other, keeping the architecture modular and extensible.

Example::

    buddy = BuddyBot()
    token = buddy.register_bot("dreamcobot", permissions=["task:run", "knowledge:read"])

    buddy.publish_event("user.joined", {"user_id": 42})
    buddy.push_task({"type": "onboard", "user_id": 42})
    task = buddy.pop_task()
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from BuddyAI.auth import AuthModule, AuthError
from BuddyAI.event_bus import EventBus


class BuddyBotError(Exception):
    """General Buddy Bot error."""


class BuddyBot:
    """Central hub for the DreamCobots bot ecosystem.

    Parameters
    ----------
    name:
        Human-readable name for this Buddy Bot instance.
    """

    def __init__(self, name: str = "BuddyBot") -> None:
        self.name = name
        self._auth = AuthModule()
        self._event_bus = EventBus(error_handler=self._handle_event_error)
        self._knowledge_base: Dict[str, Any] = {}
        self._task_queue: List[Dict[str, Any]] = []
        self._connected_bots: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Bot registration
    # ------------------------------------------------------------------

    def register_bot(self, bot_id: str, permissions: Optional[List[str]] = None) -> str:
        """Register *bot_id* and return its authentication token.

        Parameters
        ----------
        bot_id:
            Unique identifier for the bot being registered.
        permissions:
            Permission list granted to the bot, e.g.
            ``["task:run", "knowledge:read"]``.

        Returns
        -------
        str
            Secret token the bot uses to authenticate future requests.

        Raises
        ------
        BuddyBotError
            If *bot_id* is already registered.
        """
        if bot_id in self._connected_bots:
            raise BuddyBotError(f"Bot '{bot_id}' is already registered")
        token = self._auth.register_bot(bot_id, permissions)
        self._connected_bots[bot_id] = {"permissions": permissions or []}
        self._event_bus.publish("bot.registered", {"bot_id": bot_id})
        return token

    def unregister_bot(self, bot_id: str) -> None:
        """Remove *bot_id* from the ecosystem."""
        self._auth.unregister_bot(bot_id)
        self._connected_bots.pop(bot_id, None)
        self._event_bus.publish("bot.unregistered", {"bot_id": bot_id})

    def authenticate(self, bot_id: str, token: str) -> bool:
        """Verify that *token* belongs to *bot_id*.

        Raises
        ------
        AuthError
            If verification fails.
        """
        return self._auth.verify_token(bot_id, token)

    def connected_bots(self) -> List[str]:
        """Return a list of all currently registered bot IDs."""
        return list(self._connected_bots.keys())

    # ------------------------------------------------------------------
    # Event bus API
    # ------------------------------------------------------------------

    def subscribe_event(self, event: str, handler: Callable) -> None:
        """Subscribe *handler* to *event* on the shared event bus."""
        self._event_bus.subscribe(event, handler)

    def unsubscribe_event(self, event: str, handler: Callable) -> None:
        """Unsubscribe *handler* from *event*."""
        self._event_bus.unsubscribe(event, handler)

    def publish_event(self, event: str, payload: Any = None) -> int:
        """Publish *payload* for *event*; returns the handler call count."""
        return self._event_bus.publish(event, payload)

    # ------------------------------------------------------------------
    # Shared knowledge base
    # ------------------------------------------------------------------

    def set_knowledge(self, key: str, value: Any) -> None:
        """Store *value* in the shared knowledge base under *key*."""
        self._knowledge_base[key] = value

    def get_knowledge(self, key: str, default: Any = None) -> Any:
        """Retrieve the value stored under *key* (or *default*)."""
        return self._knowledge_base.get(key, default)

    def delete_knowledge(self, key: str) -> None:
        """Remove *key* from the knowledge base (no-op if absent)."""
        self._knowledge_base.pop(key, None)

    def knowledge_keys(self) -> List[str]:
        """Return a sorted list of all knowledge base keys."""
        return sorted(self._knowledge_base.keys())

    # ------------------------------------------------------------------
    # Shared task queue
    # ------------------------------------------------------------------

    def push_task(self, task: Dict[str, Any]) -> None:
        """Append *task* to the shared task queue.

        Parameters
        ----------
        task:
            A dict describing the task, e.g.
            ``{"type": "onboard", "user_id": 42}``.
        """
        if not isinstance(task, dict):
            raise BuddyBotError("Task must be a dict")
        self._task_queue.append(task)
        self._event_bus.publish("task.queued", task)

    def pop_task(self) -> Optional[Dict[str, Any]]:
        """Remove and return the next task, or ``None`` if the queue is empty."""
        if not self._task_queue:
            return None
        return self._task_queue.pop(0)

    def pending_tasks(self) -> int:
        """Return the number of tasks currently in the queue."""
        return len(self._task_queue)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _handle_event_error(event: str, handler: Callable, exc: Exception) -> None:
        """Default event-error handler: print a warning and continue."""
        print(
            f"[BuddyBot] Warning: handler {handler!r} raised while "
            f"processing event '{event}': {exc}"
        )
