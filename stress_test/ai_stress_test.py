"""AI bot stress testing for DreamCobots platform."""
import sys
import os
import time
import threading
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class AIStressTest:
    """Stress tests the DreamCobots AI bot ecosystem under load."""

    def __init__(self):
        """Initialize the AI stress test suite."""
        self._results = []

    def run_bot_stress_test(self, bots: list, duration_seconds: int = 30) -> dict:
        """Run multiple bots simultaneously for a given duration and collect metrics."""
        print(f"[StressTest] Running {len(bots)} bots for {duration_seconds}s...")
        start_time = time.time()
        errors = []
        invocations = [0] * len(bots)
        lock = threading.Lock()

        def run_bot_continuously(bot, idx):
            """Run a single bot in a loop until duration expires."""
            while time.time() - start_time < duration_seconds:
                try:
                    if hasattr(bot, "get_status"):
                        bot.get_status()
                    with lock:
                        invocations[idx] += 1
                except Exception as e:
                    with lock:
                        errors.append(str(e))

        threads = []
        for i, bot in enumerate(bots):
            t = threading.Thread(target=run_bot_continuously, args=(bot, i), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=duration_seconds + 5)

        total_time = time.time() - start_time
        total_calls = sum(invocations)
        result = {
            "test_type": "bot_stress_test",
            "bots_tested": len(bots),
            "duration_seconds": round(total_time, 2),
            "total_invocations": total_calls,
            "invocations_per_second": round(total_calls / total_time, 2) if total_time > 0 else 0,
            "errors_count": len(errors),
            "errors_sample": errors[:5],
            "per_bot_invocations": dict(zip([getattr(b, "name", f"bot_{i}") for i, b in enumerate(bots)], invocations)),
            "status": "PASSED" if len(errors) == 0 else "FAILED" if len(errors) > total_calls * 0.1 else "WARNING",
        }
        self._results.append(result)
        print(f"[StressTest] Completed: {total_calls} calls in {total_time:.1f}s ({result['status']})")
        return result

    def test_response_time(self, bot, num_requests: int = 100) -> dict:
        """Measure response time of a bot over multiple requests."""
        print(f"[ResponseTime] Testing {getattr(bot, 'name', 'bot')} with {num_requests} requests...")
        times = []
        errors = []
        for _ in range(num_requests):
            start = time.time()
            try:
                if hasattr(bot, "get_status"):
                    bot.get_status()
            except Exception as e:
                errors.append(str(e))
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        result = {
            "test_type": "response_time",
            "bot": getattr(bot, "name", "unknown"),
            "num_requests": num_requests,
            "min_ms": round(min(times), 3) if times else 0,
            "max_ms": round(max(times), 3) if times else 0,
            "avg_ms": round(statistics.mean(times), 3) if times else 0,
            "median_ms": round(statistics.median(times), 3) if times else 0,
            "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 3) if times else 0,
            "p99_ms": round(sorted(times)[int(len(times) * 0.99)], 3) if times else 0,
            "errors": len(errors),
            "status": "PASSED" if not errors else "WARNING",
        }
        self._results.append(result)
        print(f"[ResponseTime] avg={result['avg_ms']}ms p95={result['p95_ms']}ms ({result['status']})")
        return result

    def test_memory_usage(self, bot) -> dict:
        """Test memory usage of a bot under repeated calls."""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            before_mb = process.memory_info().rss / (1024 * 1024)
            for _ in range(1000):
                if hasattr(bot, "get_status"):
                    bot.get_status()
            after_mb = process.memory_info().rss / (1024 * 1024)
            delta_mb = after_mb - before_mb
        except ImportError:
            before_mb = 0
            after_mb = 0
            delta_mb = 0

        result = {
            "test_type": "memory_usage",
            "bot": getattr(bot, "name", "unknown"),
            "memory_before_mb": round(before_mb, 2),
            "memory_after_mb": round(after_mb, 2),
            "memory_delta_mb": round(delta_mb, 2),
            "status": "PASSED" if delta_mb < 50 else "WARNING",
        }
        self._results.append(result)
        return result

    def generate_report(self, results: list = None) -> str:
        """Generate a formatted stress test report."""
        results = results or self._results
        lines = [
            "=" * 60,
            "  DREAMCOBOTS AI STRESS TEST REPORT",
            f"  Total Test Suites: {len(results)}",
            "=" * 60,
        ]
        for i, r in enumerate(results, 1):
            lines.append(f"\n[Test {i}] {r.get('test_type', 'unknown').upper()}")
            for k, v in r.items():
                if k != "test_type":
                    lines.append(f"  {k}: {v}")
        passed = sum(1 for r in results if r.get("status") == "PASSED")
        failed = sum(1 for r in results if r.get("status") == "FAILED")
        lines.extend([
            "\n" + "=" * 60,
            f"  SUMMARY: {passed} PASSED | {failed} FAILED | {len(results) - passed - failed} WARNINGS",
            "=" * 60,
        ])
        return "\n".join(lines)
