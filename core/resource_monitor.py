"""
core/resource_monitor.py

Monitors system resource utilisation (CPU, memory, disk) using psutil,
generates periodic reports, and emits alerts when thresholds are exceeded.
"""

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any, Callable

import psutil


def _get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


class ResourceMonitor:
    """
    Periodically samples CPU, memory, and disk usage.
    Fires alert callbacks when configurable thresholds are exceeded
    and maintains a rolling history of resource snapshots.
    """

    DEFAULT_CPU_THRESHOLD: float = 85.0   # percent
    DEFAULT_MEM_THRESHOLD: float = 85.0   # percent
    DEFAULT_DISK_THRESHOLD: float = 90.0  # percent

    def __init__(
        self,
        sample_interval_seconds: int = 10,
        history_limit: int = 360,
        cpu_threshold: float = DEFAULT_CPU_THRESHOLD,
        mem_threshold: float = DEFAULT_MEM_THRESHOLD,
        disk_threshold: float = DEFAULT_DISK_THRESHOLD,
        disk_path: str = "/",
    ) -> None:
        """
        Initialise the ResourceMonitor.

        Args:
            sample_interval_seconds: Seconds between each sampling cycle.
            history_limit: Maximum number of snapshots to retain in memory.
            cpu_threshold: CPU usage % that triggers an alert.
            mem_threshold: Memory usage % that triggers an alert.
            disk_threshold: Disk usage % that triggers an alert.
            disk_path: Filesystem path to monitor for disk usage.
        """
        self.sample_interval_seconds: int = sample_interval_seconds
        self.history_limit: int = history_limit
        self.cpu_threshold: float = cpu_threshold
        self.mem_threshold: float = mem_threshold
        self.disk_threshold: float = disk_threshold
        self.disk_path: str = disk_path

        self._history: list[dict[str, Any]] = []
        self._alert_callbacks: list[Callable[[dict[str, Any]], None]] = []
        self._lock: threading.Lock = threading.Lock()
        self._stop_event: threading.Event = threading.Event()
        self._monitor_thread: threading.Thread | None = None

        self.logger: logging.Logger = _get_logger("ResourceMonitor")

    # ------------------------------------------------------------------
    # Alert registration
    # ------------------------------------------------------------------

    def register_alert_callback(
        self, callback: Callable[[dict[str, Any]], None]
    ) -> None:
        """
        Register a callable to be invoked whenever a resource threshold is exceeded.

        Args:
            callback: A function that receives an alert dict with keys
                      ``resource``, ``value``, ``threshold``, and ``timestamp``.
        """
        self._alert_callbacks.append(callback)
        self.logger.debug("Alert callback registered.")

    def _fire_alert(self, resource: str, value: float, threshold: float) -> None:
        """Build and dispatch an alert to all registered callbacks."""
        alert: dict[str, Any] = {
            "resource": resource,
            "value": round(value, 2),
            "threshold": threshold,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.logger.warning(
            "ALERT: %s usage %.1f%% exceeds threshold %.1f%%",
            resource,
            value,
            threshold,
        )
        for cb in self._alert_callbacks:
            try:
                cb(alert)
            except Exception as exc:
                self.logger.warning("Alert callback raised: %s", exc)

    # ------------------------------------------------------------------
    # Sampling
    # ------------------------------------------------------------------

    def sample(self) -> dict[str, Any]:
        """
        Take a single resource snapshot.

        Returns:
            A dict with current CPU, memory, and disk metrics.
        """
        cpu_percent: float = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(self.disk_path)

        snapshot: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count_logical": psutil.cpu_count(logical=True),
                "count_physical": psutil.cpu_count(logical=False),
            },
            "memory": {
                "total_bytes": mem.total,
                "available_bytes": mem.available,
                "used_bytes": mem.used,
                "percent": mem.percent,
            },
            "disk": {
                "path": self.disk_path,
                "total_bytes": disk.total,
                "used_bytes": disk.used,
                "free_bytes": disk.free,
                "percent": disk.percent,
            },
        }

        # Check thresholds
        if cpu_percent >= self.cpu_threshold:
            self._fire_alert("CPU", cpu_percent, self.cpu_threshold)
        if mem.percent >= self.mem_threshold:
            self._fire_alert("Memory", mem.percent, self.mem_threshold)
        if disk.percent >= self.disk_threshold:
            self._fire_alert("Disk", disk.percent, self.disk_threshold)

        with self._lock:
            self._history.append(snapshot)
            if len(self._history) > self.history_limit:
                self._history = self._history[-self.history_limit :]

        return snapshot

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_report(self) -> dict[str, Any]:
        """
        Generate a summary report from the retained history.

        Returns:
            A dict with ``generated_at``, ``sample_count``, and per-resource
            ``min``, ``max``, and ``avg`` statistics.
        """
        with self._lock:
            history = list(self._history)

        if not history:
            return {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "sample_count": 0,
                "message": "No samples collected yet.",
            }

        cpu_vals = [s["cpu"]["percent"] for s in history]
        mem_vals = [s["memory"]["percent"] for s in history]
        disk_vals = [s["disk"]["percent"] for s in history]

        def _stats(vals: list[float]) -> dict[str, float]:
            return {
                "min": round(min(vals), 2),
                "max": round(max(vals), 2),
                "avg": round(sum(vals) / len(vals), 2),
                "latest": round(vals[-1], 2),
            }

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sample_count": len(history),
            "cpu_percent": _stats(cpu_vals),
            "memory_percent": _stats(mem_vals),
            "disk_percent": _stats(disk_vals),
            "thresholds": {
                "cpu": self.cpu_threshold,
                "memory": self.mem_threshold,
                "disk": self.disk_threshold,
            },
        }

    def get_latest_snapshot(self) -> dict[str, Any] | None:
        """Return the most recent resource snapshot, or ``None`` if empty."""
        with self._lock:
            return dict(self._history[-1]) if self._history else None

    # ------------------------------------------------------------------
    # Background monitoring loop
    # ------------------------------------------------------------------

    def _monitoring_loop(self) -> None:
        self.logger.info(
            "ResourceMonitor loop started (interval=%ds).",
            self.sample_interval_seconds,
        )
        while not self._stop_event.is_set():
            try:
                self.sample()
            except Exception as exc:
                self.logger.exception("Error during resource sampling: %s", exc)
            self._stop_event.wait(timeout=self.sample_interval_seconds)
        self.logger.info("ResourceMonitor loop stopped.")

    def start(self) -> None:
        """Start the background sampling thread."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self.logger.warning("ResourceMonitor is already running.")
            return
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="ResourceMonitorThread",
        )
        self._monitor_thread.start()
        self.logger.info("ResourceMonitor started.")

    def stop(self) -> None:
        """Stop the background sampling thread."""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=self.sample_interval_seconds + 5)
        self.logger.info("ResourceMonitor stopped.")
