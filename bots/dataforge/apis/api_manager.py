"""
bots/dataforge/apis/api_manager.py

APIManager – manages lifecycle and invocation of all registered API connectors.
"""

import logging
import time
import threading
from datetime import datetime, timezone
from typing import Any

from bots.dataforge.apis.connectors.base_connector import BaseAPIConnector

logger = logging.getLogger(__name__)

# Default rate-limit window in seconds.
_RATE_WINDOW = 60


class APIManager:
    """
    Manages registration, invocation, and health monitoring of API connectors.

    Provides a unified ``call_api()`` interface with per-connector rate limiting
    so that individual connectors never need to implement their own throttle logic
    beyond the counters in :class:`~bots.dataforge.apis.connectors.base_connector.BaseAPIConnector`.
    """

    def __init__(self) -> None:
        """Initialise the manager with an empty connector store."""
        self._connectors: dict[str, BaseAPIConnector] = {}
        self._call_log: list[dict[str, Any]] = []
        self._lock = threading.RLock()
        logger.info("APIManager initialised")

    # ------------------------------------------------------------------
    # Connector management
    # ------------------------------------------------------------------

    def register_connector(
        self, name: str, connector: BaseAPIConnector
    ) -> None:
        """
        Register a connector under a given name.

        Args:
            name: Unique key used to retrieve the connector later.
            connector: An instance of a :class:`~bots.dataforge.apis.connectors.base_connector.BaseAPIConnector` subclass.
        """
        with self._lock:
            self._connectors[name] = connector
        logger.info("Registered connector '%s'", name)

    def get_connector(self, name: str) -> BaseAPIConnector:
        """
        Retrieve a registered connector by name.

        Args:
            name: The connector's registered key.

        Returns:
            The connector instance.

        Raises:
            KeyError: If no connector is registered under *name*.
        """
        connector = self._connectors.get(name)
        if connector is None:
            raise KeyError(f"No connector registered under '{name}'")
        return connector

    def get_all_connectors(self) -> dict[str, BaseAPIConnector]:
        """
        Return a snapshot of all registered connectors.

        Returns:
            A dict mapping name to connector instance.
        """
        with self._lock:
            return dict(self._connectors)

    # ------------------------------------------------------------------
    # API invocation
    # ------------------------------------------------------------------

    def call_api(
        self,
        connector_name: str,
        method: str,
        endpoint: str = "/",
        data: dict | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Invoke a method on the named connector with rate-limit enforcement.

        Args:
            connector_name: Key of the connector to use.
            method: HTTP method string (``"GET"``, ``"POST"``, etc.).
            endpoint: API endpoint path.
            data: Optional request payload dict.
            **kwargs: Additional keyword arguments passed to the connector's
                      ``call()`` method (currently unused but reserved for
                      future extension).

        Returns:
            The response dict returned by the connector's ``call()`` method,
            wrapped with timing metadata.

        Raises:
            KeyError: If *connector_name* is not registered.
            RuntimeError: If the connector's rate limit has been exceeded.
        """
        connector = self.get_connector(connector_name)
        rl = connector.get_rate_limit_status()
        if rl["available_calls"] <= 0:
            raise RuntimeError(
                f"Rate limit exceeded for connector '{connector_name}' "
                f"({rl['calls_in_window']}/{rl['limit_per_minute']} calls in window)"
            )

        start = time.monotonic()
        try:
            response = connector.call(method, endpoint, data or {})
            elapsed = time.monotonic() - start
            log_entry: dict[str, Any] = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "connector": connector_name,
                "method": method,
                "endpoint": endpoint,
                "elapsed_ms": round(elapsed * 1000, 2),
                "success": True,
            }
            with self._lock:
                self._call_log.append(log_entry)
            return response
        except Exception as exc:
            elapsed = time.monotonic() - start
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "connector": connector_name,
                "method": method,
                "endpoint": endpoint,
                "elapsed_ms": round(elapsed * 1000, 2),
                "success": False,
                "error": str(exc),
            }
            with self._lock:
                self._call_log.append(log_entry)
            logger.warning(
                "API call to '%s %s' via connector '%s' failed: %s",
                method,
                endpoint,
                connector_name,
                exc,
            )
            raise

    # ------------------------------------------------------------------
    # Health monitoring
    # ------------------------------------------------------------------

    def health_check_all(self) -> dict[str, bool]:
        """
        Run health checks on every registered connector.

        Returns:
            A dict mapping connector name to its health-check result.
        """
        results: dict[str, bool] = {}
        for name, connector in list(self._connectors.items()):
            try:
                ok = connector.health_check()
            except Exception as exc:
                logger.warning("Health check for '%s' raised: %s", name, exc)
                ok = False
            results[name] = ok
        logger.info(
            "Health check complete: %d/%d connectors healthy",
            sum(results.values()),
            len(results),
        )
        return results

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_stats(self) -> dict[str, Any]:
        """
        Return aggregate call statistics for all connectors.

        Returns:
            A dict with total calls, success/failure counts, and per-connector summaries.
        """
        with self._lock:
            total = len(self._call_log)
            successes = sum(1 for e in self._call_log if e["success"])
            by_connector: dict[str, dict[str, int]] = {}
            for entry in self._call_log:
                cn = entry["connector"]
                if cn not in by_connector:
                    by_connector[cn] = {"total": 0, "success": 0, "failure": 0}
                by_connector[cn]["total"] += 1
                if entry["success"]:
                    by_connector[cn]["success"] += 1
                else:
                    by_connector[cn]["failure"] += 1

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "registered_connectors": len(self._connectors),
            "total_calls": total,
            "successful_calls": successes,
            "failed_calls": total - successes,
            "by_connector": by_connector,
        }
