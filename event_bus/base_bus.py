"""
DreamCo BaseEventBus — In-memory pub/sub for testing / offline environments.

Provides the same interface as RedisEventBus so code can switch between
implementations without change.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Dict, List


class BaseEventBus:
    """
    In-memory event bus.

    Suitable for unit tests and environments where Redis is unavailable.
    Handlers are called synchronously on publish.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Pub/Sub API
    # ------------------------------------------------------------------

    def publish(self, event_type: str, data: Any = None) -> None:
        """
        Publish *data* to every subscriber registered for *event_type*.

        Parameters
        ----------
        event_type : str
            The event channel name (e.g. ``"deal_found"``).
        data : Any
            Payload forwarded to each subscriber.
        """
        entry = {"event_type": event_type, "data": data}
        self._event_log.append(entry)
        for handler in list(self._subscribers.get(event_type, [])):
            handler(data)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Register *handler* to be called when *event_type* is published.

        Parameters
        ----------
        event_type : str
            The channel to subscribe to.
        handler : callable
            Function to invoke with the event data.
        """
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove *handler* from *event_type* subscriptions."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h is not handler
            ]

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def get_events(self) -> List[Dict[str, Any]]:
        """Return a copy of all published events in order."""
        return list(self._event_log)

    def clear(self) -> None:
        """Clear subscriber list and event log."""
        self._subscribers.clear()
        self._event_log.clear()

    def subscriber_count(self, event_type: str) -> int:
        """Return the number of subscribers for *event_type*."""
        return len(self._subscribers.get(event_type, []))
