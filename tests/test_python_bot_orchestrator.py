"""
Tests for python_bots/orchestrator.py

Covers:
  1. Registration and unregistration of sub-bots
  2. run_bot — success, error, not found
  3. run_all — aggregation
  4. summary and run_history
  5. Integration with LearningLoop
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from python_bots.orchestrator import PythonBotOrchestrator
from python_bots.base_bot import BaseBot
from event_bus.base_bus import BaseEventBus


# ---------------------------------------------------------------------------
# Test bot implementations
# ---------------------------------------------------------------------------

class _OkBot(BaseBot):
    """A bot that publishes a revenue event successfully."""

    def run(self, event_bus: BaseEventBus) -> None:
        event_bus.publish("revenue_event", {"revenue": 100.0})


class _FailBot(BaseBot):
    """A bot that always raises an exception."""

    def run(self, event_bus: BaseEventBus) -> None:
        raise RuntimeError("intentional failure")


class _SilentBot(BaseBot):
    """A bot that runs without publishing any events."""

    def run(self, event_bus: BaseEventBus) -> None:
        pass  # no events


# ===========================================================================
# 1. Registration
# ===========================================================================

class TestRegistration:
    def test_register_bot(self):
        orch = PythonBotOrchestrator()
        orch.register(_OkBot("bot_a"))
        assert "bot_a" in orch.registered_bots

    def test_register_multiple_bots(self):
        orch = PythonBotOrchestrator()
        orch.register(_OkBot("bot_a"))
        orch.register(_OkBot("bot_b"))
        assert len(orch.registered_bots) == 2

    def test_unregister_existing(self):
        orch = PythonBotOrchestrator()
        orch.register(_OkBot("bot_a"))
        removed = orch.unregister("bot_a")
        assert removed is True
        assert "bot_a" not in orch.registered_bots

    def test_unregister_nonexistent(self):
        orch = PythonBotOrchestrator()
        removed = orch.unregister("ghost_bot")
        assert removed is False

    def test_registered_bots_empty_initially(self):
        orch = PythonBotOrchestrator()
        assert orch.registered_bots == []


# ===========================================================================
# 2. run_bot
# ===========================================================================

class TestRunBot:
    def test_run_bot_ok_status(self):
        orch = PythonBotOrchestrator()
        orch.register(_OkBot("ok_bot"))
        result = orch.run_bot("ok_bot")
        assert result["status"] == "ok"

    def test_run_bot_returns_events(self):
        orch = PythonBotOrchestrator()
        orch.register(_OkBot("ok_bot"))
        result = orch.run_bot("ok_bot")
        assert isinstance(result["events"], list)
        assert len(result["events"]) == 1

    def test_run_bot_error_captured(self):
        orch = PythonBotOrchestrator()
        orch.register(_FailBot("fail_bot"))
        result = orch.run_bot("fail_bot")
        assert result["status"] == "error"
        assert "error" in result
        assert "intentional failure" in result["error"]

    def test_run_bot_not_registered(self):
        orch = PythonBotOrchestrator()
        result = orch.run_bot("ghost")
        assert result["status"] == "error"

    def test_run_bot_contains_bot_name(self):
        orch = PythonBotOrchestrator()
        orch.register(_OkBot("named_bot"))
        result = orch.run_bot("named_bot")
        assert result["bot"] == "named_bot"

    def test_run_silent_bot_ok(self):
        orch = PythonBotOrchestrator()
        orch.register(_SilentBot("silent_bot"))
        result = orch.run_bot("silent_bot")
        assert result["status"] == "ok"
        assert result["events"] == []


# ===========================================================================
# 3. run_all
# ===========================================================================

class TestRunAll:
    def test_run_all_returns_dict(self):
        orch = PythonBotOrchestrator()
        orch.register(_OkBot("a"))
        result = orch.run_all()
        assert isinstance(result, dict)

    def test_run_all_bots_run_count(self):
        orch = PythonBotOrchestrator()
        orch.register(_OkBot("a"))
        orch.register(_OkBot("b"))
        result = orch.run_all()
        assert result["bots_run"] == 2

    def test_run_all_successful_count(self):
        orch = PythonBotOrchestrator()
        orch.register(_OkBot("ok"))
        orch.register(_FailBot("fail"))
        result = orch.run_all()
        assert result["successful"] == 1
        assert result["failed"] == 1

    def test_run_all_empty_registry(self):
        orch = PythonBotOrchestrator()
        result = orch.run_all()
        assert result["bots_run"] == 0

    def test_run_all_has_timestamp(self):
        orch = PythonBotOrchestrator()
        result = orch.run_all()
        assert "timestamp" in result

    def test_run_all_results_list(self):
        orch = PythonBotOrchestrator()
        orch.register(_OkBot("a"))
        result = orch.run_all()
        assert isinstance(result["results"], list)


# ===========================================================================
# 4. summary and history
# ===========================================================================

class TestSummaryAndHistory:
    def test_summary_keys(self):
        orch = PythonBotOrchestrator()
        s = orch.summary()
        for key in ("total_runs", "successful_runs", "failed_runs",
                    "registered_bots", "bot_names"):
            assert key in s

    def test_summary_empty_initially(self):
        orch = PythonBotOrchestrator()
        s = orch.summary()
        assert s["total_runs"] == 0

    def test_history_accumulates(self):
        orch = PythonBotOrchestrator()
        orch.register(_OkBot("x"))
        orch.run_bot("x")
        orch.run_bot("x")
        assert len(orch.get_run_history()) == 2

    def test_history_empty_initially(self):
        orch = PythonBotOrchestrator()
        assert orch.get_run_history() == []


# ===========================================================================
# 5. Integration with LearningLoop
# ===========================================================================

class TestLearningLoopIntegration:
    def test_learning_loop_records_run(self):
        from bots.ai_learning_system.learning_loop import LearningLoop
        ll = LearningLoop()
        orch = PythonBotOrchestrator(learning_loop=ll)
        orch.register(_OkBot("ll_bot"))
        orch.run_bot("ll_bot")
        assert "ll_bot" in ll._performance

    def test_learning_loop_records_failure(self):
        from bots.ai_learning_system.learning_loop import LearningLoop
        ll = LearningLoop()
        orch = PythonBotOrchestrator(learning_loop=ll)
        orch.register(_FailBot("fail_bot"))
        orch.run_bot("fail_bot")
        assert ll._performance["fail_bot"].failed_runs == 1
