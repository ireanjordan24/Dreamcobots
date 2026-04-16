"""
DreamCo RedisEventBus — Production Redis pub/sub + queue bus.

Falls back gracefully to the in-memory BaseEventBus when Redis is
unavailable so the rest of the system keeps running.

Environment variables
---------------------
REDIS_HOST   Redis hostname (default: localhost)
REDIS_PORT   Redis port     (default: 6379)
REDIS_DB     Redis DB index (default: 0)
"""
# GlobalAISourcesFlow — GLOBAL AI SOURCES FLOW

from __future__ import annotations

import json
import os
from typing import Any, Callable, Optional

from event_bus.base_bus import BaseEventBus

# ---------------------------------------------------------------------------
# Optional Redis import — graceful degradation
# ---------------------------------------------------------------------------

try:
    import redis as _redis  # type: ignore[import]
    _REDIS_AVAILABLE = True
except ImportError:
    _redis = None  # type: ignore[assignment]
    _REDIS_AVAILABLE = False


def _get_redis_client() -> Any:
    """Return a Redis client using env-configured connection settings."""
    host = os.environ.get("REDIS_HOST", "localhost")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    db = int(os.environ.get("REDIS_DB", "0"))
    return _redis.Redis(host=host, port=port, db=db, decode_responses=True)


# ---------------------------------------------------------------------------
# RedisEventBus
# ---------------------------------------------------------------------------


class RedisEventBus(BaseEventBus):
    """
    Redis pub/sub event bus.

    Falls back to in-memory mode if Redis is unavailable (ImportError or
    ConnectionError), making it safe to use in all environments.
    """

    def __init__(self, host: str = None, port: int = None) -> None:
        super().__init__()
        self._redis: Optional[Any] = None
        if _REDIS_AVAILABLE:
            try:
                self._redis = _get_redis_client()
                self._redis.ping()
            except Exception:
                self._redis = None

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Register handler, preventing duplicates."""
        handlers = self._subscribers[event_type]
        if handler not in handlers:
            handlers.append(handler)

    def publish(self, event_type: str, data: Any = None) -> None:
        """
        Publish event in-memory (synchronous handlers) and to Redis.
        """
        self._event_log[event_type].append(data)
        for handler in list(self._subscribers.get(event_type, [])):
            try:
                handler(data)
            except Exception:
                pass
        if self._redis is not None:
            try:
                payload = json.dumps({"event_type": event_type, "data": data})
                self._redis.publish(event_type, payload)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def redis_connected(self) -> bool:
        """Return True if Redis is connected."""
        return self._redis is not None

    @property
    def redis_available(self) -> bool:
        """Alias for redis_connected (backwards compat)."""
        return self._redis is not None


# ---------------------------------------------------------------------------
# RedisQueueBus — Job queue for worker-based bot execution
# ---------------------------------------------------------------------------

_DEFAULT_QUEUE = "dreamco:bot_jobs"


class RedisQueueBus:
    """Redis list-based job queue with in-memory fallback."""

    def __init__(self, queue_name: str = _DEFAULT_QUEUE) -> None:
        self.queue_name = queue_name
        self._redis: Optional[Any] = None
        self._fallback_queue: list = []

        if _REDIS_AVAILABLE:
            try:
                self._redis = _get_redis_client()
                self._redis.ping()
            except Exception:
                self._redis = None

    def enqueue(self, job: dict) -> None:
        """Push a bot job onto the queue."""
        if self._redis is not None:
            try:
                self._redis.lpush(self.queue_name, json.dumps(job))
                return
            except Exception:
                pass
        self._fallback_queue.insert(0, job)

    def dequeue(self, timeout: int = 0) -> Optional[dict]:
        """Pop the next job from the queue."""
        if self._redis is not None:
            try:
                if timeout > 0:
                    item = self._redis.brpop(self.queue_name, timeout=timeout)
                else:
                    item = self._redis.rpop(self.queue_name)
                if item is None:
                    return None
                raw = item[1] if isinstance(item, (list, tuple)) else item
                return json.loads(raw)
            except Exception:
                pass
        if self._fallback_queue:
            return self._fallback_queue.pop()
        return None

    def queue_length(self) -> int:
        """Return the number of jobs currently in the queue."""
        if self._redis is not None:
            try:
                return int(self._redis.llen(self.queue_name))
            except Exception:
                pass
        return len(self._fallback_queue)

    def clear(self) -> None:
        """Remove all jobs from the queue."""
        if self._redis is not None:
            try:
                self._redis.delete(self.queue_name)
                return
            except Exception:
                pass
        self._fallback_queue.clear()

    @property
    def redis_available(self) -> bool:
        """Return True if Redis is connected."""
        return self._redis is not None
