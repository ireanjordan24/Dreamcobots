"""
Tests for bots/deep_learning_system/.

Covers:
  - APIScraperEngine
  - CompetitorAnalysisEngine
  - SandboxTestingEngine
  - DeepLearningCoordinator
  - BuddyOrchestrator deep learning integration
"""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bots.deep_learning_system.api_scraper import APIScraperEngine
from bots.deep_learning_system.competitor_analysis import CompetitorAnalysisEngine
from bots.deep_learning_system.sandbox_tester import SandboxTestingEngine
from bots.deep_learning_system import DeepLearningCoordinator, LEARNING_DEADLINE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def future_deadline() -> date:
    return date.today() + timedelta(days=60)


def past_deadline() -> date:
    return date.today() - timedelta(days=1)


# ===========================================================================
# APIScraperEngine
# ===========================================================================

class TestAPIScraperEngine:
    def setup_method(self):
        self.engine = APIScraperEngine(deadline=future_deadline())

    def test_register_adds_bot(self):
        self.engine.register("bot_a", "sales")
        assert "bot_a" in self.engine._records

    def test_register_idempotent(self):
        self.engine.register("bot_a", "sales")
        self.engine.register("bot_a", "sales")
        assert len(self.engine._records) == 1

    def test_scrape_cycle_returns_dict(self):
        result = self.engine.scrape_cycle("bot_a", "sales")
        assert isinstance(result, dict)

    def test_scrape_cycle_status_scraped(self):
        result = self.engine.scrape_cycle("bot_a", "sales")
        assert result["status"] == "scraped"

    def test_scrape_cycle_increments_studied(self):
        self.engine.scrape_cycle("bot_a", "sales")
        assert self.engine._records["bot_a"]["studied"] != []

    def test_mastery_score_starts_zero(self):
        self.engine.register("bot_a", "sales")
        assert self.engine.mastery_score("bot_a") == 0.0

    def test_mastery_score_increases_after_scrape(self):
        self.engine.scrape_cycle("bot_a", "sales")
        assert self.engine.mastery_score("bot_a") > 0.0

    def test_mastery_score_unknown_bot_is_zero(self):
        assert self.engine.mastery_score("nonexistent") == 0.0

    def test_studied_apis_empty_initially(self):
        self.engine.register("bot_a", "general")
        assert self.engine.studied_apis("bot_a") == []

    def test_studied_apis_after_scrape(self):
        self.engine.scrape_cycle("bot_a", "general")
        assert len(self.engine.studied_apis("bot_a")) >= 1

    def test_status_keys(self):
        s = self.engine.status()
        assert "registered_bots" in s
        assert "total_apis_studied" in s
        assert "average_mastery_score" in s
        assert "scraping_active" in s

    def test_status_scraping_active_true_when_before_deadline(self):
        assert self.engine.status()["scraping_active"] is True

    def test_scrape_cycle_inactive_after_deadline(self):
        engine = APIScraperEngine(deadline=past_deadline())
        result = engine.scrape_cycle("bot_a", "sales")
        assert result["status"] == "deadline_passed"

    def test_auto_registers_on_scrape(self):
        self.engine.scrape_cycle("new_bot", "ai")
        assert "new_bot" in self.engine._records

    def test_multiple_cycles_increase_mastery(self):
        for _ in range(3):
            self.engine.scrape_cycle("bot_a", "general")
        assert self.engine.mastery_score("bot_a") > 0.0

    def test_unknown_category_falls_back_to_default(self):
        self.engine.register("bot_a", "unknown_category_xyz")
        assert self.engine._records["bot_a"]["target_apis"] != []


# ===========================================================================
# CompetitorAnalysisEngine
# ===========================================================================

class TestCompetitorAnalysisEngine:
    def setup_method(self):
        self.engine = CompetitorAnalysisEngine(deadline=future_deadline())

    def test_register_adds_bot(self):
        self.engine.register("bot_a", "marketing")
        assert "bot_a" in self.engine._records

    def test_analyse_cycle_returns_dict(self):
        result = self.engine.analyse_cycle("bot_a", "marketing")
        assert isinstance(result, dict)

    def test_analyse_cycle_status_analysed(self):
        result = self.engine.analyse_cycle("bot_a", "marketing")
        assert result["status"] == "analysed"

    def test_intel_score_starts_zero(self):
        self.engine.register("bot_a", "marketing")
        assert self.engine.intel_score("bot_a") == 0.0

    def test_intel_score_increases_after_analysis(self):
        self.engine.analyse_cycle("bot_a", "marketing")
        assert self.engine.intel_score("bot_a") > 0.0

    def test_intel_score_unknown_bot_is_zero(self):
        assert self.engine.intel_score("nonexistent") == 0.0

    def test_pricing_benchmark_after_analysis(self):
        self.engine.analyse_cycle("bot_a", "marketing")
        assert self.engine.pricing_benchmark("bot_a") >= 0.0

    def test_sentiment_summary_keys(self):
        self.engine.analyse_cycle("bot_a", "sales")
        s = self.engine.sentiment_summary("bot_a")
        assert "avg_sentiment" in s
        assert "competitors_analysed" in s

    def test_status_keys(self):
        s = self.engine.status()
        assert "registered_bots" in s
        assert "average_intel_score" in s
        assert "analysis_active" in s

    def test_analysis_inactive_after_deadline(self):
        engine = CompetitorAnalysisEngine(deadline=past_deadline())
        result = engine.analyse_cycle("bot_a", "sales")
        assert result["status"] == "deadline_passed"

    def test_auto_registers_on_analyse(self):
        self.engine.analyse_cycle("new_bot", "ai")
        assert "new_bot" in self.engine._records

    def test_competitor_data_populated(self):
        result = self.engine.analyse_cycle("bot_a", "sales")
        assert result["competitors_analysed"] >= 1


# ===========================================================================
# SandboxTestingEngine
# ===========================================================================

class TestSandboxTestingEngine:
    def setup_method(self):
        self.engine = SandboxTestingEngine(deadline=future_deadline())

    def test_register_adds_bot(self):
        self.engine.register("bot_a")
        assert "bot_a" in self.engine._records

    def test_run_test_returns_dict(self):
        result = self.engine.run_test("bot_a")
        assert isinstance(result, dict)

    def test_run_test_status_completed(self):
        result = self.engine.run_test("bot_a")
        assert result["status"] == "completed"

    def test_run_test_has_pass_rate(self):
        result = self.engine.run_test("bot_a")
        assert "pass_rate" in result
        assert isinstance(result["pass_rate"], float)

    def test_pass_rate_starts_zero(self):
        self.engine.register("bot_a")
        assert self.engine.pass_rate("bot_a") == 0.0

    def test_pass_rate_after_test(self):
        self.engine.run_test("bot_a")
        assert self.engine.pass_rate("bot_a") >= 0.0

    def test_pass_rate_unknown_bot_is_zero(self):
        assert self.engine.pass_rate("nonexistent") == 0.0

    def test_all_tasks_pass_by_default(self):
        result = self.engine.run_test("bot_a")
        assert result["failed"] == 0
        assert result["passed"] == result["tasks_run"]

    def test_custom_tasks(self):
        tasks = [
            {"id": "task_1", "description": "Custom task A", "weight": 1.0},
            {"id": "task_2", "description": "Custom task B", "weight": 1.0},
        ]
        result = self.engine.run_test("bot_a", tasks=tasks)
        assert result["tasks_run"] == 2

    def test_test_history_keys(self):
        self.engine.run_test("bot_a")
        h = self.engine.test_history("bot_a")
        assert "tests_run" in h
        assert "tests_passed" in h

    def test_status_keys(self):
        s = self.engine.status()
        assert "registered_bots" in s
        assert "total_tests_run" in s
        assert "average_pass_rate" in s

    def test_testing_inactive_after_deadline(self):
        engine = SandboxTestingEngine(deadline=past_deadline())
        result = engine.run_test("bot_a")
        assert result["status"] == "deadline_passed"

    def test_auto_registers_on_test(self):
        self.engine.run_test("new_bot")
        assert "new_bot" in self.engine._records


# ===========================================================================
# DeepLearningCoordinator
# ===========================================================================

class TestDeepLearningCoordinator:
    def setup_method(self):
        self.coordinator = DeepLearningCoordinator(deadline=future_deadline())

    def test_register_bot_returns_dict(self):
        result = self.coordinator.register_bot("sales_bot", "sales")
        assert result["bot_id"] == "sales_bot"
        assert result["status"] == "registered"

    def test_register_sets_category(self):
        self.coordinator.register_bot("marketing_bot", "marketing")
        assert self.coordinator._bot_categories["marketing_bot"] == "marketing"

    def test_unregister_removes_bot(self):
        self.coordinator.register_bot("bot_a")
        assert self.coordinator.unregister_bot("bot_a") is True
        assert "bot_a" not in self.coordinator._bot_categories

    def test_unregister_unknown_returns_false(self):
        assert self.coordinator.unregister_bot("nonexistent") is False

    def test_run_learning_cycle_returns_dict(self):
        result = self.coordinator.run_learning_cycle("sales_bot")
        assert isinstance(result, dict)

    def test_run_learning_cycle_has_required_keys(self):
        result = self.coordinator.run_learning_cycle("sales_bot")
        assert "api_scrape" in result
        assert "competitor_analysis" in result
        assert "sandbox_test" in result
        assert "days_until_go_live" in result

    def test_run_learning_cycle_logs_entry(self):
        self.coordinator.run_learning_cycle("sales_bot")
        assert len(self.coordinator._cycle_log) == 1

    def test_run_all_cycles_trains_all_bots(self):
        self.coordinator.register_bot("bot_a", "sales")
        self.coordinator.register_bot("bot_b", "marketing")
        results = self.coordinator.run_all_cycles()
        assert len(results) == 2

    def test_learning_status_keys(self):
        s = self.coordinator.learning_status()
        assert "active" in s
        assert "deadline" in s
        assert "days_remaining" in s
        assert "registered_bots" in s
        assert "api_scraper" in s
        assert "competitor_analysis" in s
        assert "sandbox_tester" in s

    def test_learning_status_active_before_deadline(self):
        assert self.coordinator.learning_status()["active"] is True

    def test_learning_status_inactive_after_deadline(self):
        c = DeepLearningCoordinator(deadline=past_deadline())
        assert c.learning_status()["active"] is False

    def test_bot_progress_keys(self):
        self.coordinator.run_learning_cycle("sales_bot")
        p = self.coordinator.bot_progress("sales_bot")
        assert "api_mastery" in p
        assert "competitor_intel_score" in p
        assert "sandbox_pass_rate" in p
        assert "cycles_completed" in p

    def test_bot_progress_cycles_counted(self):
        self.coordinator.run_learning_cycle("sales_bot")
        self.coordinator.run_learning_cycle("sales_bot")
        p = self.coordinator.bot_progress("sales_bot")
        assert p["cycles_completed"] == 2

    def test_top_performing_bots_returns_list(self):
        self.coordinator.register_bot("bot_a", "sales")
        self.coordinator.register_bot("bot_b", "marketing")
        top = self.coordinator.top_performing_bots(n=5)
        assert isinstance(top, list)

    def test_top_performing_bots_has_score(self):
        self.coordinator.register_bot("bot_a", "sales")
        top = self.coordinator.top_performing_bots(n=1)
        assert "score" in top[0]

    def test_deadline_constant_is_june_22_2026(self):
        assert LEARNING_DEADLINE == date(2026, 6, 22)

    def test_deadline_passed_returns_early(self):
        c = DeepLearningCoordinator(deadline=past_deadline())
        result = c.run_learning_cycle("bot_a")
        assert result["status"] == "deadline_passed"

    def test_run_cycle_auto_registers_unknown_bot(self):
        self.coordinator.run_learning_cycle("unknown_bot")
        assert "unknown_bot" in self.coordinator._bot_categories


# ===========================================================================
# BuddyOrchestrator deep learning integration
# ===========================================================================

class TestBuddyOrchestratorDeepLearning:
    def setup_method(self):
        from bots.buddy_orchestrator import BuddyOrchestrator
        self.orch = BuddyOrchestrator()
        self.orch.register_bot("sales_bot", category="sales")
        self.orch.register_bot("marketing_bot", category="marketing")

    def test_run_deep_learning_cycle_single_bot(self):
        result = self.orch.run_deep_learning_cycle("sales_bot")
        assert isinstance(result, dict)
        assert "api_scrape" in result

    def test_run_deep_learning_cycle_all_bots(self):
        result = self.orch.run_deep_learning_cycle()
        assert "cycles" in result
        assert isinstance(result["cycles"], list)

    def test_deep_learning_status_keys(self):
        s = self.orch.deep_learning_status()
        assert "active" in s
        assert "registered_bots" in s
        assert "days_remaining" in s

    def test_deep_learning_bot_progress(self):
        self.orch.run_deep_learning_cycle("sales_bot")
        p = self.orch.deep_learning_bot_progress("sales_bot")
        assert "api_mastery" in p
        assert "cycles_completed" in p

    def test_top_learning_bots_returns_list(self):
        top = self.orch.top_learning_bots(n=2)
        assert isinstance(top, list)
