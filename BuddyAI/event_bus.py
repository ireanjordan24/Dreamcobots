"""
BuddyAI EventBus — lightweight publish-subscribe event system.

Usage
-----
    from BuddyAI.event_bus import EventBus

    bus = EventBus()
    bus.subscribe("user.message", lambda payload: print(payload))
    bus.publish("user.message", {"text": "Hello"})
"""
from typing import Callable, Any, Optional
import threading
import datetime


class EventBusError(Exception):
    """Raised for EventBus operational errors."""


class EventBus:
    """
    Thread-safe publish-subscribe event bus.

    Parameters
    ----------
    error_handler : callable, optional
        Called as ``error_handler(event_type, handler, exc)`` when a handler
        raises an exception during :meth:`publish`.  When not provided,
        exceptions propagate to the caller.
    """

    def __init__(self, error_handler: Optional[Callable] = None):
        self._subscribers: dict[str, list[Callable]] = {}
        self._lock = threading.Lock()
        self._event_log: list[dict] = []
        self._error_handler = error_handler

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Register a handler for an event type.

        Raises
        ------
        EventBusError
            If *handler* is not callable.
        """
        if not callable(handler):
            raise EventBusError(
                f"Handler must be callable, got {type(handler).__name__!r}."
            )
        with self._lock:
            self._subscribers.setdefault(event_type, [])
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove a previously registered handler.

        Raises
        ------
        EventBusError
            If *event_type* has no registered handlers or *handler* is not
            found among them.
        """
        with self._lock:
            if event_type not in self._subscribers:
                raise EventBusError(f"No handlers registered for event type '{event_type}'.")
            try:
                self._subscribers[event_type].remove(handler)
            except ValueError:
                raise EventBusError(
                    f"Handler not found for event type '{event_type}'."
                )

    def publish(self, event_type: str, payload: Any = None) -> int:
        """
        Dispatch payload to all handlers registered for event_type.

        When an ``error_handler`` was supplied at construction time, handler
        exceptions are caught and forwarded to it.  Otherwise they propagate.

        Returns
        -------
        int
            Number of handlers invoked (including those that raised when an
            error_handler is installed).
        """
        with self._lock:
            handlers = list(self._subscribers.get(event_type, []))
        count = 0
        for handler in handlers:
            try:
                handler(payload)
                count += 1
            except Exception as exc:
                if self._error_handler is not None:
                    self._error_handler(event_type, handler, exc)
                    count += 1
                else:
                    raise
        with self._lock:
            self._event_log.append({
                "event_type": event_type,
                "payload": payload,
                "handlers_invoked": count,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            })
        return count

    def get_event_log(self) -> list[dict]:
        """Return a copy of the full event log."""
        with self._lock:
            return list(self._event_log)

    def get_events(self, event_type: str) -> list[Any]:
        """Return list of payloads published for the given event_type."""
        with self._lock:
            return [
                entry["payload"]
                for entry in self._event_log
                if entry["event_type"] == event_type
            ]

    def clear_log(self) -> None:
        """Clear the event log."""
        with self._lock:
            self._event_log = []

    def list_event_types(self) -> list[str]:
        """Return sorted list of registered event types."""
        with self._lock:
            return sorted(self._subscribers.keys())

    def events(self) -> list[str]:
        """Return sorted list of registered event types (alias for :meth:`list_event_types`)."""
        return self.list_event_types()

    def handler_count(self, event_type: str) -> int:
        """Return the number of handlers registered for *event_type*.

        Returns 0 if no handlers are registered for the given event type.
        """
        with self._lock:
            return len(self._subscribers.get(event_type, []))
