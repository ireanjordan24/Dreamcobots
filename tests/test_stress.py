"""
tests/test_stress.py

Stress tests for DreamCobots using the StressTester class.
"""

import unittest

from stress_test.stress_tester import StressTester


class _DummyBot:
    """Minimal bot stub for stress testing."""

    bot_id = "stress-dummy"
    bot_name = "StressDummy"
    _activity_log: list = []
    _error_log: list = []

    def get_status(self) -> dict:
        return {"bot_id": self.bot_id, "running": False}


class TestConcurrentBotExecution(unittest.TestCase):
    def setUp(self) -> None:
        self.tester = StressTester()

    def test_concurrent_bot_execution(self) -> None:
        result = self.tester.run_concurrent_bots(num_threads=4, duration_seconds=1)
        self.assertIn("threads", result)
        self.assertIn("total_tasks", result)
        self.assertEqual(result["threads"], 4)
        self.assertGreaterEqual(result["total_tasks"], 0)
        self.assertEqual(result["errors"], 0)

    def test_concurrent_single_thread(self) -> None:
        result = self.tester.run_concurrent_bots(num_threads=1, duration_seconds=1)
        self.assertEqual(result["threads"], 1)


class TestMemoryStability(unittest.TestCase):
    def setUp(self) -> None:
        self.tester = StressTester()
        self.bot = _DummyBot()

    def test_memory_stability(self) -> None:
        no_leak = self.tester.check_memory_leaks(self.bot)
        self.assertTrue(no_leak)


class TestThroughputMeasurement(unittest.TestCase):
    def setUp(self) -> None:
        self.tester = StressTester()
        self.bot = _DummyBot()

    def test_throughput_measurement(self) -> None:
        rps = self.tester.measure_throughput(self.bot, num_requests=100)
        self.assertIsInstance(rps, float)
        self.assertGreater(rps, 0)

    def test_throughput_returns_finite_value(self) -> None:
        rps = self.tester.measure_throughput(self.bot, num_requests=50)
        self.assertFalse(rps != rps)  # NaN check


class TestLatencyMeasurement(unittest.TestCase):
    def setUp(self) -> None:
        self.tester = StressTester()
        self.bot = _DummyBot()

    def test_latency_measurement(self) -> None:
        result = self.tester.measure_latency(self.bot, num_samples=20)
        self.assertIn("min_ms", result)
        self.assertIn("max_ms", result)
        self.assertIn("avg_ms", result)
        self.assertIn("samples", result)
        self.assertEqual(result["samples"], 20)
        self.assertLessEqual(result["min_ms"], result["max_ms"])
        self.assertGreater(result["avg_ms"], 0)

    def test_latency_samples_count(self) -> None:
        result = self.tester.measure_latency(self.bot, num_samples=5)
        self.assertEqual(result["samples"], 5)


class TestFullStressTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tester = StressTester()

    def test_full_stress_test_returns_all_keys(self) -> None:
        result = self.tester.run_full_stress_test()
        self.assertIn("concurrent", result)
        self.assertIn("throughput_rps", result)
        self.assertIn("memory_stable", result)
        self.assertIn("latency", result)

    def test_full_stress_test_memory_stable(self) -> None:
        result = self.tester.run_full_stress_test()
        self.assertTrue(result["memory_stable"])


if __name__ == "__main__":
    unittest.main()
