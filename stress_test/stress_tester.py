"""
stress_test/stress_tester.py

Concurrent load testing and performance measurement for DreamCobots bots.
"""

import threading
import time
import tracemalloc
from typing import Any


class StressTester:
    """Runs concurrent load tests, throughput/latency measurements, and memory checks."""

    def run_concurrent_bots(self, num_threads: int, duration_seconds: int) -> dict:
        """
        Spawn *num_threads* worker threads that each call a no-op task for
        *duration_seconds* and return aggregate statistics.

        Args:
            num_threads: Number of concurrent threads to launch.
            duration_seconds: How long each thread runs (seconds).

        Returns:
            dict with keys: threads, duration_seconds, total_tasks, errors.
        """
        results: list[dict[str, Any]] = []
        lock = threading.Lock()

        def _worker() -> None:
            count = 0
            errors = 0
            deadline = time.monotonic() + duration_seconds
            while time.monotonic() < deadline:
                try:
                    time.sleep(0)  # yield; simulate lightweight work
                    count += 1
                except Exception:  # pragma: no cover
                    errors += 1
            with lock:
                results.append({"tasks": count, "errors": errors})

        threads = [threading.Thread(target=_worker, daemon=True) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        total_tasks = sum(r["tasks"] for r in results)
        total_errors = sum(r["errors"] for r in results)
        return {
            "threads": num_threads,
            "duration_seconds": duration_seconds,
            "total_tasks": total_tasks,
            "errors": total_errors,
        }

    def measure_throughput(self, bot_instance: Any, num_requests: int) -> float:
        """
        Call *bot_instance.get_status()* *num_requests* times and return
        requests per second.

        Args:
            bot_instance: Any object with a callable ``get_status`` method.
            num_requests: Number of calls to make.

        Returns:
            Throughput in requests per second (float).
        """
        start = time.monotonic()
        for _ in range(num_requests):
            if hasattr(bot_instance, "get_status"):
                bot_instance.get_status()
        elapsed = time.monotonic() - start
        return num_requests / elapsed if elapsed > 0 else float("inf")

    def check_memory_leaks(self, bot_instance: Any) -> bool:
        """
        Run *bot_instance.get_status()* in a loop and check whether memory
        grows significantly using :mod:`tracemalloc`.

        Args:
            bot_instance: Any object with a callable ``get_status`` method.

        Returns:
            ``True`` if no significant leak detected, ``False`` otherwise.
        """
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()

        for _ in range(100):
            if hasattr(bot_instance, "get_status"):
                bot_instance.get_status()

        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats = snapshot2.compare_to(snapshot1, "lineno")
        total_growth = sum(s.size_diff for s in stats)
        # Allow up to 1 MB of growth before flagging as a potential leak
        return total_growth < 1_000_000

    def measure_latency(self, bot_instance: Any, num_samples: int) -> dict:
        """
        Measure per-call latency of *bot_instance.get_status()*.

        Args:
            bot_instance: Any object with a callable ``get_status`` method.
            num_samples: Number of latency samples to collect.

        Returns:
            dict with keys: min_ms, max_ms, avg_ms, samples.
        """
        latencies: list[float] = []
        for _ in range(num_samples):
            t0 = time.monotonic()
            if hasattr(bot_instance, "get_status"):
                bot_instance.get_status()
            latencies.append((time.monotonic() - t0) * 1000)

        return {
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "avg_ms": sum(latencies) / len(latencies),
            "samples": num_samples,
        }

    def run_full_stress_test(self) -> dict:
        """
        Execute all stress-test routines with conservative defaults and return
        a consolidated report.

        Returns:
            dict containing results from concurrent, throughput, memory, and
            latency sub-tests.
        """

        class _DummyBot:
            bot_id = "stress-dummy"
            bot_name = "StressDummy"

            def get_status(self) -> dict:
                return {"bot_id": self.bot_id, "running": False}

        dummy = _DummyBot()

        concurrent = self.run_concurrent_bots(num_threads=4, duration_seconds=1)
        throughput = self.measure_throughput(dummy, num_requests=200)
        no_leak = self.check_memory_leaks(dummy)
        latency = self.measure_latency(dummy, num_samples=50)

        return {
            "concurrent": concurrent,
            "throughput_rps": throughput,
            "memory_stable": no_leak,
            "latency": latency,
        }
