"""
DreamCo BaseEventBus — In-memory pub/sub for testing / offline environments.

Provides the same interface as RedisEventBus so code can switch between
implementations without change.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional


class BaseEventBus(ABC):
    """
    Abstract base event bus.

    Concrete implementations must provide ``publish`` and ``subscribe``.
    The in-memory fallback is provided via ``_subscribers`` / ``_event_log``
    attributes that subclasses can rely on.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Abstract Pub/Sub API (must be implemented by subclasses)
    # ------------------------------------------------------------------

    @abstractmethod
    def publish(self, event_type: str, data: Any = None) -> None:
        """Publish *data* to every subscriber registered for *event_type*."""

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Register *handler* to be called when *event_type* is published."""

    # ------------------------------------------------------------------
    # Concrete helpers (available to all subclasses)
    # ------------------------------------------------------------------

    def _publish_local(self, event_type: str, data: Any = None) -> None:
        """Publish to in-memory subscribers and log the event."""
        entry = {"event_type": event_type, "data": data}
        self._event_log.append(entry)
        for handler in list(self._subscribers.get(event_type, [])):
            handler(data)

    def _subscribe_local(self, event_type: str, handler: Callable) -> None:
        """Register handler only if not already subscribed (deduplicates)."""
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove *handler* from *event_type* subscriptions."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h is not handler
            ]

    def get_events(self, event_type: Optional[str] = None) -> List[Any]:
        """Return published event data, optionally filtered by *event_type*.

        Parameters
        ----------
        event_type : str | None
            If given, return only the ``data`` payloads of events matching
            this type.  If ``None``, return all raw event dicts.
        """
        if event_type is None:
            return list(self._event_log)
        return [e["data"] for e in self._event_log if e["event_type"] == event_type]

    def clear(self) -> None:
        """Clear subscriber list and event log."""
        self._subscribers.clear()
        self._event_log.clear()

    def subscriber_count(self, event_type: str) -> int:
        """Return the number of subscribers for *event_type*."""
        return len(self._subscribers.get(event_type, []))
