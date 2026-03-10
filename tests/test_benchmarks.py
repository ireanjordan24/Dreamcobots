"""Tests for Benchmarks."""

import time
import pytest
from BuddyAI.benchmarks import Benchmarks, BenchmarkResult


@pytest.fixture
def bm():
    return Benchmarks()


def test_benchmark_returns_result(bm):
    result = bm.benchmark(lambda: None, iterations=5, name="noop")
    assert isinstance(result, BenchmarkResult)
    assert result.name == "noop"
    assert result.iterations == 5
    assert len(result.timings) == 5


def test_benchmark_timing_reasonable(bm):
    def slow():
        time.sleep(0.01)

    result = bm.benchmark(slow, iterations=3)
    # Each iteration should take at least 10ms
    assert result.mean >= 0.009


def test_benchmark_summary_string(bm):
    result = bm.benchmark(lambda: None, iterations=2, name="test")
    summary = result.summary()
    assert "test" in summary
    assert "iterations=2" in summary
    assert "mean=" in summary


def test_compare_returns_winner(bm):
    fast = lambda: None
    slow = lambda: time.sleep(0.01)
    report = bm.compare(fast, slow, iterations=3)
    assert "winner" in report
    assert "speedup" in report
    assert report["speedup"] > 0
    # fast should win
    assert report["winner"] == "Buddy"


def test_timed_decorator(bm):
    called = []

    @Benchmarks.timed
    def my_func():
        called.append(1)
        return 42

    result = my_func()
    assert result == 42
    assert called == [1]


def test_benchmark_with_exception(bm):
    def raises():
        raise ValueError("oops")

    # Should not raise; exceptions are logged
    result = bm.benchmark(raises, iterations=3, name="error_fn")
    assert result.iterations == 3
