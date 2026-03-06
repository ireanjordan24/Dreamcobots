"""
EventBus - Event-driven pub/sub architecture for Buddy.

Provides decoupled communication between Buddy's modules.
"""

import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventBus:
    """Lightweight publish/subscribe event bus.

    Modules publish events by name; other modules subscribe
    to those events with callback handlers.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def subscribe(self, event: str, handler: Callable) -> None:
        """Register *handler* to be called whenever *event* is published.

        Args:
            event: Event name string (e.g. ``"task.scheduled"``).
            handler: Callable that accepts a single ``data`` argument.
        """
        self._subscribers[event].append(handler)
        logger.debug("Subscribed %s to event '%s'", handler, event)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        """Remove *handler* from the subscribers list for *event*.

        Args:
            event: Event name string.
            handler: Previously registered callable.
        """
        try:
            self._subscribers[event].remove(handler)
            logger.debug("Unsubscribed %s from event '%s'", handler, event)
        except ValueError:
            logger.warning("Handler %s was not subscribed to '%s'", handler, event)

    def publish(self, event: str, data: Any = None) -> None:
        """Publish *event* to all registered subscribers.

        Args:
            event: Event name string.
            data: Optional payload delivered to each subscriber.
        """
        logger.debug("Publishing event '%s' with data: %s", event, data)
        for handler in list(self._subscribers.get(event, [])):
            try:
                handler(data)
            except Exception as exc:  # pylint: disable=broad-except
                logger.error(
                    "Handler %s raised an exception for event '%s': %s",
                    handler,
                    event,
                    exc,
                )

    # Alias so callers can use either ``publish`` or ``emit``
    emit = publish

    def clear(self, event: Optional[str] = None) -> None:
        """Remove all subscribers.

        Args:
            event: If given, only clear subscribers for that event.
                   If ``None``, clear every event.
        """
        if event is not None:
            self._subscribers.pop(event, None)
        else:
            self._subscribers.clear()

    def subscriber_count(self, event: str) -> int:
        """Return the number of subscribers for *event*."""
        return len(self._subscribers.get(event, []))
