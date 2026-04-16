"""
DreamCo BaseEventBus — Abstract base class for event bus implementations.

Defines the pub/sub interface that all event bus implementations must satisfy.
"""

from __future__ import annotations

import abc
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional


class BaseEventBus(abc.ABC):
    """
    Abstract base event bus.

    Subclasses must implement :meth:`publish` and :meth:`subscribe`.
    A default in-memory implementation of :meth:`get_events` is provided.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_log: Dict[str, List[Any]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Abstract API (must be implemented by subclasses)
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def publish(self, event_type: str, data: Any = None) -> None:
        """Publish *data* to every subscriber registered for *event_type*."""

    @abc.abstractmethod
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Register *handler* to be called when *event_type* is published."""

    # ------------------------------------------------------------------
    # Concrete helpers (available to all subclasses)
    # ------------------------------------------------------------------

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove *handler* from *event_type* subscriptions."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h is not handler
            ]

    def get_events(self, event_type: Optional[str] = None) -> List[Any]:
        """
        Return published events, optionally filtered by *event_type*.

        Parameters
        ----------
        event_type : str or None
            If provided, return only events of this type.
            If None, return all events as ``{event_type, data}`` dicts.
        """
        if event_type is not None:
            return list(self._event_log.get(event_type, []))
        result = []
        for et, events in self._event_log.items():
            for data in events:
                result.append({"event_type": et, "data": data})
        return result

    def clear(self) -> None:
        """Clear subscriber list and event log."""
        self._subscribers.clear()
        self._event_log.clear()

    def subscriber_count(self, event_type: str) -> int:
        """Return the number of subscribers for *event_type*."""
        return len(self._subscribers.get(event_type, []))
