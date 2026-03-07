"""
EventBus — lightweight publish/subscribe bus for inter-bot communication.

Usage
-----
    from BuddyAI.event_bus import EventBus

    bus = EventBus()
    bus.subscribe("lead_captured", lambda data: print("New lead:", data))
    bus.publish("lead_captured", {"name": "Alice", "email": "alice@example.com"})
"""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Any


class EventBus:
    """
    Simple synchronous publish/subscribe event bus.

    Methods
    -------
    subscribe(event, handler) -- register a callable for *event*.
    unsubscribe(event, handler) -- remove a previously registered handler.
    publish(event, data) -- fire *event*, calling all registered handlers.
    clear(event) -- remove all handlers for *event*.
    clear_all() -- remove every handler on the bus.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def subscribe(self, event: str, handler: Callable[[Any], None]) -> None:
        """Register *handler* to be called whenever *event* is published."""
        if handler not in self._handlers[event]:
            self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: Callable[[Any], None]) -> None:
        """Remove *handler* from *event*.  No-op if not registered."""
        handlers = self._handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event: str, data: Any = None) -> int:
        """
        Call every handler subscribed to *event*.

        Returns the number of handlers that were invoked.
        """
        handlers = list(self._handlers.get(event, []))
        for handler in handlers:
            handler(data)
        return len(handlers)

    def clear(self, event: str) -> None:
        """Remove all handlers for *event*."""
        self._handlers.pop(event, None)

    def clear_all(self) -> None:
        """Remove every handler on the bus."""
        self._handlers.clear()

    def list_events(self) -> list[str]:
        """Return the list of events that have at least one subscriber."""
        return [e for e, h in self._handlers.items() if h]
