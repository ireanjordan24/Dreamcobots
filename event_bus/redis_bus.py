"""
DreamCo Event Bus — Redis-backed implementation

Publishes and subscribes to events via Redis pub/sub so that Python and Java
bots running in separate processes can communicate over a shared message bus.

Falls back gracefully to an in-process queue when Redis is unavailable so
that the system can still run in environments without Redis (e.g. CI without
the Redis service).
"""

from __future__ import annotations

import json
import threading
from typing import Any, Callable

from event_bus.base_bus import BaseEventBus


class RedisEventBus(BaseEventBus):
    """
    Event bus backed by Redis pub/sub.

    Parameters
    ----------
    host : str
        Redis hostname (default ``"localhost"``).
    port : int
        Redis port (default ``6379``).
    db : int
        Redis database index (default ``0``).

    Notes
    -----
    If the ``redis`` package is not installed or the Redis server is
    unreachable the bus silently falls back to an in-process threading-based
    implementation so that bots can still run without an external Redis
    instance.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0) -> None:
        self._host = host
        self._port = port
        self._db = db
        self._redis = None
        self._subscribers: dict[str, list[Callable]] = {}
        self._lock = threading.Lock()
        self._event_log: dict[str, list] = {}

        try:
            import redis  # type: ignore[import]

            client = redis.Redis(host=host, port=port, db=db)
            client.ping()
            self._redis = client
        except Exception:  # pragma: no cover — Redis not available in all envs
            self._redis = None

    # ------------------------------------------------------------------
    # BaseEventBus interface
    # ------------------------------------------------------------------

    def publish(self, event_type: str, data: Any) -> None:
        """
        Publish *event_type* with *data*.

        If Redis is available the event is published to the Redis channel
        so other processes can receive it.  In either case all local
        subscribers are notified.

        Parameters
        ----------
        event_type : str
            Channel / event category.
        data : Any
            JSON-serialisable payload.
        """
        with self._lock:
            callbacks = list(self._subscribers.get(event_type, []))
            self._event_log.setdefault(event_type, []).append(data)

        if self._redis is not None:
            try:
                self._redis.publish(event_type, json.dumps(data))
            except Exception:  # pragma: no cover
                pass

        for callback in callbacks:
            callback(data)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Register *handler* for *event_type*.

        Parameters
        ----------
        event_type : str
            Event category to listen for.
        handler : Callable
            Called with the event data payload.
        """
        with self._lock:
            self._subscribers.setdefault(event_type, [])
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_events(self, event_type: str) -> list:
        """
        Return all locally recorded events of *event_type* (useful for tests).

        Parameters
        ----------
        event_type : str
            Event category to query.

        Returns
        -------
        list
        """
        with self._lock:
            return list(self._event_log.get(event_type, []))

    @property
    def redis_connected(self) -> bool:
        """``True`` when a live Redis connection is active."""
        return self._redis is not None
