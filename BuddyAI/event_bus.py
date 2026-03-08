"""
BuddyAI — Event Bus

Thread-safe publish/subscribe event bus for inter-bot communication within
the DreamCo ecosystem.
"""

import threading
from typing import Callable, Any


class EventBus:
    """
    Thread-safe publish/subscribe event bus.

    Subscribers register callbacks for specific event types.  When an event
    is published, all registered callbacks for that type are invoked
    synchronously in the calling thread.

    Additionally, all published events are stored in an internal log so that
    tests can inspect them via ``get_events()``.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._subscribers: dict[str, list[Callable]] = {}
        self._event_log: dict[str, list] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Register *callback* to be called when *event_type* is published.

        Parameters
        ----------
        event_type : str
            The event category to listen for.
        callback : Callable
            Function to call with the event data as its sole argument.
        """
        with self._lock:
            self._subscribers.setdefault(event_type, [])
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Remove *callback* from the subscriber list for *event_type*.

        Parameters
        ----------
        event_type : str
            The event category to stop listening for.
        callback : Callable
            The previously registered callback to remove.
        """
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                except ValueError:
                    pass

    def publish(self, event_type: str, data: Any) -> None:
        """
        Publish an event, invoking all registered callbacks.

        Parameters
        ----------
        event_type : str
            The event category.
        data : Any
            Payload passed to each subscriber callback.
        """
        with self._lock:
            callbacks = list(self._subscribers.get(event_type, []))
            self._event_log.setdefault(event_type, []).append(data)

        for callback in callbacks:
            callback(data)

    def get_events(self, event_type: str) -> list:
        """
        Return all published events of *event_type* (for testing).

        Parameters
        ----------
        event_type : str
            The event category to query.

        Returns
        -------
        list
            Copies of all data payloads published under *event_type*.
        """
        with self._lock:
            return list(self._event_log.get(event_type, []))
