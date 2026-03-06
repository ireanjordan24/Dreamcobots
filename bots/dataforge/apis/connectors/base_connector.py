"""
bots/dataforge/apis/connectors/base_connector.py

BaseAPIConnector – abstract base class for all DataForge API connectors.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseAPIConnector(ABC):
    """
    Abstract base class for all DataForge API connectors.

    Concrete subclasses must implement :meth:`connect`, :meth:`disconnect`,
    and :meth:`call`.  Rate limiting is handled generically here.
    """

    def __init__(
        self,
        name: str,
        api_key: str = "SIMULATED_KEY",
        base_url: str = "https://api.example.com",
    ) -> None:
        """
        Initialise the connector.

        Args:
            name: Human-readable name for this connector.
            api_key: API key (simulated – never validated against a real service).
            base_url: Base URL for the API.
        """
        self.name = name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._connected = False
        self._call_count = 0
        self._error_count = 0
        self._rate_limit: int = 60          # calls per minute
        self._rate_window_start: float = time.time()
        self._rate_window_calls: int = 0
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.logger.info("Connector '%s' initialised (base_url=%s)", name, base_url)

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish a connection to the API.

        Returns:
            ``True`` if the connection was (simulated as) successful.
        """

    @abstractmethod
    def disconnect(self) -> None:
        """Close the connection to the API."""

    @abstractmethod
    def call(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, Any]:
        """
        Execute an API call.

        Args:
            method: HTTP method (``"GET"``, ``"POST"``, etc.).
            endpoint: Path relative to :attr:`base_url`.
            data: Optional request payload.

        Returns:
            A dict containing the simulated API response.
        """

    # ------------------------------------------------------------------
    # Concrete helpers
    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Perform a lightweight health check against the API.

        Returns:
            ``True`` if the API is reachable (simulated).
        """
        try:
            response = self.call("GET", "/health")
            ok = response.get("status") in ("ok", "healthy", "up", 200)
            self.logger.debug("Health check result: %s", ok)
            return bool(ok)
        except Exception as exc:
            self.logger.warning("Health check failed: %s", exc)
            return False

    def get_rate_limit_status(self) -> dict[str, Any]:
        """
        Return current rate-limit counters.

        Returns:
            A dict with ``calls_in_window``, ``limit``, ``window_seconds``,
            and ``available`` fields.
        """
        elapsed = time.time() - self._rate_window_start
        if elapsed >= 60:
            self._rate_window_calls = 0
            self._rate_window_start = time.time()

        available = max(0, self._rate_limit - self._rate_window_calls)
        return {
            "connector": self.name,
            "calls_in_window": self._rate_window_calls,
            "limit_per_minute": self._rate_limit,
            "window_seconds_elapsed": round(elapsed, 2),
            "available_calls": available,
            "total_calls": self._call_count,
            "total_errors": self._error_count,
        }

    def _record_call(self, success: bool = True) -> None:
        """Update internal call counters."""
        self._call_count += 1
        self._rate_window_calls += 1
        if not success:
            self._error_count += 1
