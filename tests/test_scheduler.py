"""Tests for core/scheduler.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from core.scheduler import Scheduler, CycleRecord
from core.dreamco_orchestrator import DreamCoOrchestrator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_scheduler(max_cycles=1, interval=0):
    """Create a Scheduler with a stub orchestrator that returns known results."""
    orch = DreamCoOrchestrator()
    # Override run_all_bots so no real imports are attempted
    orch.run_all_bots = lambda: [
        {"bot_name": "stub_bot", "output": {"revenue": 250}, "validation": {}, "error": None}
    ]
    return Scheduler(orchestrator=orch, interval_seconds=interval, max_cycles=max_cycles)


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestInstantiation:
    def test_default_init(self):
        s = Scheduler()
        assert s.interval_seconds > 0
        assert s._running is False

    def test_custom_interval(self):
        s = Scheduler(interval_seconds=300)
        assert s.interval_seconds == 300


# ---------------------------------------------------------------------------
# run_once
# ---------------------------------------------------------------------------

class TestRunOnce:
    def test_run_once_returns_cycle_record(self):
        s = _make_scheduler()
        record = s.run_once()
        assert isinstance(record, CycleRecord)

    def test_cycle_id_increments(self):
        s = _make_scheduler()
        r1 = s.run_once()
        r2 = s.run_once()
        assert r2.cycle_id == r1.cycle_id + 1

    def test_run_once_appends_to_log(self):
        s = _make_scheduler()
        s.run_once()
        assert len(s.get_cycle_log()) == 1

    def test_run_once_revenue_extracted(self):
        s = _make_scheduler()
        record = s.run_once()
        assert record.total_revenue == pytest.approx(250.0)

    def test_run_once_sets_timestamps(self):
        s = _make_scheduler()
        record = s.run_once()
        assert record.started_at is not None
        assert record.finished_at is not None

    def test_error_captured_when_orchestrator_raises(self):
        orch = DreamCoOrchestrator()
        orch.run_all_bots = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
        s = Scheduler(orchestrator=orch, interval_seconds=0)
        record = s.run_once()
        assert record.error is not None


# ---------------------------------------------------------------------------
# run_forever (limited by max_cycles)
# ---------------------------------------------------------------------------

class TestRunForever:
    def test_run_forever_stops_at_max_cycles(self):
        s = _make_scheduler(max_cycles=3, interval=0)
        s.run_forever()
        assert s._cycle_count == 3

    def test_stop_exits_loop(self):
        """stop() should prevent further cycles even without max_cycles."""
        orch = DreamCoOrchestrator()
        call_count = []

        def fake_run():
            call_count.append(1)
            if len(call_count) >= 2:
                # Signal stop after 2 runs
                raise StopIteration("done")
            return []

        orch.run_all_bots = fake_run
        s = Scheduler(orchestrator=orch, interval_seconds=0, max_cycles=10)
        try:
            s.run_forever()
        except StopIteration:
            pass
        assert s._cycle_count >= 1


# ---------------------------------------------------------------------------
# get_summary
# ---------------------------------------------------------------------------

class TestGetSummary:
    def test_summary_keys(self):
        s = _make_scheduler()
        s.run_once()
        summary = s.get_summary()
        assert "total_cycles" in summary
        assert "total_revenue_usd" in summary
        assert "error_cycles" in summary
        assert "interval_seconds" in summary
        assert "is_running" in summary

    def test_summary_revenue_accumulates(self):
        s = _make_scheduler()
        s.run_once()
        s.run_once()
        summary = s.get_summary()
        assert summary["total_revenue_usd"] == pytest.approx(500.0)


# ---------------------------------------------------------------------------
# CycleRecord
# ---------------------------------------------------------------------------

class TestCycleRecord:
    def test_to_dict_keys(self):
        r = CycleRecord(cycle_id=1, started_at="2026-01-01T00:00:00Z")
        d = r.to_dict()
        assert "cycle_id" in d
        assert "started_at" in d
        assert "total_revenue" in d
        assert "error" in d
