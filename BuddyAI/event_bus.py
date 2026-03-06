"""
event_bus.py – Lightweight synchronous publish/subscribe event bus.

Modules publish named events; other modules subscribe to those events
and are notified automatically.  This decouples the components so each
module can be developed and tested independently.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)


class EventBus:
    """Simple in-process publish/subscribe bus."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------

    def subscribe(self, event: str, handler: Callable[[Any], None]) -> None:
        """Register *handler* to be called whenever *event* is published."""
        self._handlers[event].append(handler)
        logger.debug("Subscribed %s to event '%s'", handler, event)

    def unsubscribe(self, event: str, handler: Callable[[Any], None]) -> None:
        """Remove a previously registered *handler* for *event*."""
        try:
            self._handlers[event].remove(handler)
        except ValueError:
            logger.warning("Handler %s was not subscribed to '%s'", handler, event)

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    def publish(self, event: str, data: Any = None) -> None:
        """Invoke all handlers registered for *event* with optional *data*."""
        handlers = self._handlers.get(event, [])
        logger.debug("Publishing event '%s' to %d handler(s)", event, len(handlers))
        for handler in handlers:
            try:
                handler(data)
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Error in handler %s for event '%s'", handler, event
                )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def events(self) -> list[str]:
        """Return a list of all event names that have at least one subscriber."""
        return [e for e, h in self._handlers.items() if h]


# Module-level singleton – importable directly.
bus = EventBus()
