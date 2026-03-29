"""Tests for core/dreamco_orchestrator.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from core.dreamco_orchestrator import DreamCoOrchestrator, BotRunResult


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestInstantiation:
    def test_default_init(self):
        orch = DreamCoOrchestrator()
        assert orch.revenue_threshold > 0
        assert orch.min_conversion_rate >= 0

    def test_custom_thresholds(self):
        orch = DreamCoOrchestrator(revenue_threshold=500.0, min_conversion_rate=0.1)
        assert orch.revenue_threshold == 500.0
        assert orch.min_conversion_rate == 0.1


# ---------------------------------------------------------------------------
# process_bot
# ---------------------------------------------------------------------------

class TestProcessBot:
    def setup_method(self):
        self.orch = DreamCoOrchestrator(revenue_threshold=100.0)

    def test_scale_triggered_when_revenue_above_threshold(self):
        result = self.orch.process_bot("test_bot", {"revenue": 200, "conversion_rate": 0.2})
        assert result["scale"] is True
        assert result["recommendation"] == "Scale aggressively"

    def test_scale_not_triggered_below_threshold(self):
        result = self.orch.process_bot("test_bot", {"revenue": 50, "conversion_rate": 0.2})
        assert result["scale"] is False

    def test_change_strategy_when_low_conversion(self):
        result = self.orch.process_bot("test_bot", {"revenue": 10, "conversion_rate": 0.01})
        assert result["recommendation"] == "Change strategy"

    def test_maintain_recommendation(self):
        result = self.orch.process_bot("test_bot", {"revenue": 50, "conversion_rate": 0.2})
        assert result["recommendation"] == "Maintain"

    def test_revenue_in_result(self):
        result = self.orch.process_bot("test_bot", {"revenue": 150.5, "conversion_rate": 0.3})
        assert result["revenue"] == pytest.approx(150.5)

    def test_leads_generated_in_result(self):
        result = self.orch.process_bot("test_bot", {"revenue": 50, "leads_generated": 7})
        assert result["leads_generated"] == 7

    def test_missing_keys_use_defaults(self):
        result = self.orch.process_bot("test_bot", {})
        assert result["revenue"] == 0.0
        assert result["conversion_rate"] == 0.0
        assert result["leads_generated"] == 0

    def test_run_history_appended(self):
        self.orch.process_bot("bot_a", {"revenue": 50})
        self.orch.process_bot("bot_b", {"revenue": 200})
        history = self.orch.get_run_history()
        assert len(history) == 2
        assert history[0]["bot_name"] == "bot_a"
        assert history[1]["bot_name"] == "bot_b"


# ---------------------------------------------------------------------------
# run_bot (dynamic import)
# ---------------------------------------------------------------------------

class TestRunBot:
    def setup_method(self):
        self.orch = DreamCoOrchestrator()

    def test_run_bot_missing_module_returns_error(self):
        result = self.orch.run_bot("nonexistent.module.path", "bad_bot")
        assert "error" in result
        assert result["bot_name"] == "bad_bot"

    def test_run_bot_error_appended_to_history(self):
        self.orch.run_bot("nonexistent.path", "err_bot")
        history = self.orch.get_run_history()
        assert any(r["bot_name"] == "err_bot" for r in history)


# ---------------------------------------------------------------------------
# run_all_bots
# ---------------------------------------------------------------------------

class TestRunAllBots:
    def test_run_all_bots_returns_list(self):
        orch = DreamCoOrchestrator()
        results = orch.run_all_bots()
        assert isinstance(results, list)

    def test_all_results_have_bot_name(self):
        orch = DreamCoOrchestrator()
        results = orch.run_all_bots()
        for r in results:
            assert "bot_name" in r


# ---------------------------------------------------------------------------
# Bot registration
# ---------------------------------------------------------------------------

class TestBotRegistration:
    def test_register_bot_increases_registry(self):
        orch = DreamCoOrchestrator()
        initial = len(orch._registered_bots)
        orch.register_bot("some.module", "my_bot")
        assert len(orch._registered_bots) == initial + 1


# ---------------------------------------------------------------------------
# get_summary
# ---------------------------------------------------------------------------

class TestSummary:
    def test_summary_keys(self):
        orch = DreamCoOrchestrator()
        orch.process_bot("a", {"revenue": 200, "conversion_rate": 0.5})
        summary = orch.get_summary()
        assert "total_runs" in summary
        assert "total_revenue_usd" in summary
        assert "scaling_events" in summary
        assert "registered_bots" in summary

    def test_summary_revenue_accumulates(self):
        orch = DreamCoOrchestrator(revenue_threshold=10.0)
        orch.process_bot("a", {"revenue": 300})
        orch.process_bot("b", {"revenue": 200})
        summary = orch.get_summary()
        assert summary["total_revenue_usd"] == pytest.approx(500.0)

    def test_summary_scaling_events_counted(self):
        orch = DreamCoOrchestrator(revenue_threshold=100.0)
        orch.process_bot("a", {"revenue": 200})
        orch.process_bot("b", {"revenue": 50})
        summary = orch.get_summary()
        assert summary["scaling_events"] == 1


# ---------------------------------------------------------------------------
# BotRunResult
# ---------------------------------------------------------------------------

class TestBotRunResult:
    def test_to_dict_has_required_keys(self):
        r = BotRunResult(bot_name="test")
        d = r.to_dict()
        assert "bot_name" in d
        assert "output" in d
        assert "validation" in d
        assert "error" in d
        assert "timestamp" in d
