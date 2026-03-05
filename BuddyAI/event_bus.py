"""
BuddyAI Event Bus
-----------------
A lightweight, synchronous publish/subscribe event bus for bot-to-bot
communication within the DreamCobots ecosystem.

Usage::

    bus = EventBus()

    def on_task(payload):
        print("Task received:", payload)

    bus.subscribe("task.assigned", on_task)
    bus.publish("task.assigned", {"task": "onboard_user"})
"""

from typing import Callable, Dict, List, Any


class EventBusError(Exception):
    """Raised when an event cannot be published or subscribed."""


class EventBus:
    """Central event bus for bot-to-bot messaging.

    Bots subscribe to named *events* by registering handler callables.
    When another bot publishes an event the handlers are invoked
    synchronously in subscription order.

    Parameters
    ----------
    error_handler:
        Optional callable ``(event, handler, exc) -> None`` that is
        called when a handler raises.  If ``None`` the exception is
        re-raised immediately.
    """

    def __init__(self, error_handler: Callable = None) -> None:
        self._handlers: Dict[str, List[Callable]] = {}
        self._error_handler = error_handler

    # ------------------------------------------------------------------
    # Subscribe / unsubscribe
    # ------------------------------------------------------------------

    def subscribe(self, event: str, handler: Callable) -> None:
        """Register *handler* to be called when *event* is published.

        Parameters
        ----------
        event:
            Event name string (e.g. ``"task.assigned"``).
        handler:
            A callable that accepts a single *payload* argument.
        """
        if not callable(handler):
            raise EventBusError("Handler must be callable")
        self._handlers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        """Remove *handler* from the list for *event* (no-op if absent)."""
        handlers = self._handlers.get(event, [])
        try:
            handlers.remove(handler)
        except ValueError:
            pass

    # ------------------------------------------------------------------
    # Publish
    # ------------------------------------------------------------------

    def publish(self, event: str, payload: Any = None) -> int:
        """Broadcast *payload* to all handlers registered for *event*.

        Parameters
        ----------
        event:
            Event name.
        payload:
            Arbitrary data to pass to each handler.

        Returns
        -------
        int
            The number of handlers that were called.
        """
        handlers = list(self._handlers.get(event, []))
        for handler in handlers:
            try:
                handler(payload)
            except Exception as exc:  # noqa: BLE001
                if self._error_handler is not None:
                    self._error_handler(event, handler, exc)
                else:
                    raise
        return len(handlers)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def events(self) -> List[str]:
        """Return a sorted list of all registered event names."""
        return sorted(self._handlers.keys())

    def handler_count(self, event: str) -> int:
        """Return the number of handlers registered for *event*."""
        return len(self._handlers.get(event, []))
