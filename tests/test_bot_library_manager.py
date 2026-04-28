"""
Tests for bots/bot_library_manager/library_manager.py

Covers:
  1. Initialization
  2. Library registration and mastery updates
  3. Library summary
  4. Learning data storage and retention filtering
  5. Low-relevance purge
  6. Scraper run logging
  7. Close / cleanup
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.bot_library_manager import BotLibraryManager


# ===========================================================================
# 1. Initialization
# ===========================================================================

class TestInitialization:
    def test_creates_manager(self):
        mgr = BotLibraryManager()
        assert mgr is not None
        mgr.close()

    def test_empty_library_list(self):
        mgr = BotLibraryManager()
        assert mgr.get_bot_libraries("no_bot") == []
        mgr.close()

    def test_list_all_bots_empty(self):
        mgr = BotLibraryManager()
        assert mgr.list_all_bots() == []
        mgr.close()


# ===========================================================================
# 2. Library registration and mastery
# ===========================================================================

class TestLibraryRegistration:
    def setup_method(self):
        self.mgr = BotLibraryManager()

    def teardown_method(self):
        self.mgr.close()

    def test_register_returns_dict(self):
        rec = self.mgr.register_library("bot_a", "requests")
        assert isinstance(rec, dict)

    def test_register_sets_bot_name(self):
        rec = self.mgr.register_library("bot_a", "requests")
        assert rec["bot_name"] == "bot_a"

    def test_register_sets_library_name(self):
        rec = self.mgr.register_library("bot_a", "requests")
        assert rec["library_name"] == "requests"

    def test_register_default_mastery_zero(self):
        rec = self.mgr.register_library("bot_a", "requests")
        assert rec["mastery_score"] == pytest.approx(0.0)

    def test_register_default_status_learning(self):
        rec = self.mgr.register_library("bot_a", "requests")
        assert rec["status"] == "learning"

    def test_register_idempotent(self):
        self.mgr.register_library("bot_a", "requests")
        self.mgr.register_library("bot_a", "requests")  # should not raise
        libs = self.mgr.get_bot_libraries("bot_a")
        assert len(libs) == 1

    def test_register_multiple_libraries(self):
        self.mgr.register_library("bot_a", "requests")
        self.mgr.register_library("bot_a", "beautifulsoup4")
        libs = self.mgr.get_bot_libraries("bot_a")
        assert len(libs) == 2

    def test_update_mastery_proficient(self):
        self.mgr.register_library("bot_b", "numpy")
        rec = self.mgr.update_mastery("bot_b", "numpy", 70.0)
        assert rec["mastery_score"] == pytest.approx(70.0)
        assert rec["status"] == "proficient"

    def test_update_mastery_mastered(self):
        self.mgr.register_library("bot_b", "numpy")
        rec = self.mgr.update_mastery("bot_b", "numpy", 90.0)
        assert rec["status"] == "mastered"

    def test_update_mastery_capped_at_100(self):
        self.mgr.register_library("bot_b", "numpy")
        rec = self.mgr.update_mastery("bot_b", "numpy", 200.0)
        assert rec["mastery_score"] == pytest.approx(100.0)

    def test_get_library_unknown_returns_empty(self):
        result = self.mgr.get_library("no_bot", "no_lib")
        assert result == {}

    def test_list_all_bots_after_registration(self):
        self.mgr.register_library("bot_x", "requests")
        self.mgr.register_library("bot_y", "flask")
        bots = self.mgr.list_all_bots()
        assert "bot_x" in bots
        assert "bot_y" in bots


# ===========================================================================
# 3. Library summary
# ===========================================================================

class TestLibrarySummary:
    def setup_method(self):
        self.mgr = BotLibraryManager()

    def teardown_method(self):
        self.mgr.close()

    def test_summary_no_libraries(self):
        s = self.mgr.get_library_summary("empty_bot")
        assert s["total_libraries"] == 0
        assert s["avg_mastery"] == pytest.approx(0.0)

    def test_summary_counts(self):
        self.mgr.register_library("bot_c", "lib1")
        self.mgr.register_library("bot_c", "lib2")
        self.mgr.update_mastery("bot_c", "lib1", 90.0)
        s = self.mgr.get_library_summary("bot_c")
        assert s["total_libraries"] == 2
        assert s["mastered"] == 1
        assert s["learning"] == 1

    def test_summary_avg_mastery(self):
        self.mgr.register_library("bot_d", "a")
        self.mgr.register_library("bot_d", "b")
        self.mgr.update_mastery("bot_d", "a", 80.0)
        self.mgr.update_mastery("bot_d", "b", 60.0)
        s = self.mgr.get_library_summary("bot_d")
        assert s["avg_mastery"] == pytest.approx(70.0)


# ===========================================================================
# 4. Learning data
# ===========================================================================

class TestLearningData:
    def setup_method(self):
        self.mgr = BotLibraryManager(retention_threshold=50.0)

    def teardown_method(self):
        self.mgr.close()

    def test_store_returns_dict(self):
        entry = self.mgr.store_learning("bot_e", "workflow", "Use cache steps")
        assert isinstance(entry, dict)

    def test_store_retained_above_threshold(self):
        entry = self.mgr.store_learning(
            "bot_e", "tip", "Important tip", relevance_score=60.0
        )
        assert entry["retained"] == 1

    def test_store_discarded_below_threshold(self):
        entry = self.mgr.store_learning(
            "bot_e", "tip", "Irrelevant noise", relevance_score=10.0
        )
        assert entry["retained"] == 0

    def test_get_retained_returns_only_retained(self):
        self.mgr.store_learning("bot_f", "tip", "Good tip", relevance_score=80.0)
        self.mgr.store_learning("bot_f", "tip", "Bad tip", relevance_score=20.0)
        retained = self.mgr.get_retained_learning("bot_f")
        assert len(retained) == 1
        assert retained[0]["content"] == "Good tip"

    def test_get_retained_with_type_filter(self):
        self.mgr.store_learning("bot_g", "workflow", "W1", relevance_score=70.0)
        self.mgr.store_learning("bot_g", "client", "C1", relevance_score=70.0)
        wf = self.mgr.get_retained_learning("bot_g", data_type="workflow")
        assert all(r["data_type"] == "workflow" for r in wf)

    def test_learning_stats_counts(self):
        self.mgr.store_learning("bot_h", "t", "A", relevance_score=80.0)
        self.mgr.store_learning("bot_h", "t", "B", relevance_score=10.0)
        stats = self.mgr.get_learning_stats("bot_h")
        assert stats["total_entries"] == 2
        assert stats["retained_entries"] == 1
        assert stats["discarded_entries"] == 1


# ===========================================================================
# 5. Purge
# ===========================================================================

class TestPurge:
    def setup_method(self):
        self.mgr = BotLibraryManager(retention_threshold=0.0)

    def teardown_method(self):
        self.mgr.close()

    def test_purge_removes_low_relevance(self):
        # Store with retention_threshold=0 so everything is retained initially
        self.mgr.store_learning("bot_i", "t", "Low", relevance_score=20.0)
        self.mgr.store_learning("bot_i", "t", "High", relevance_score=80.0)
        purged = self.mgr.purge_low_relevance("bot_i", threshold=50.0)
        assert purged == 1
        retained = self.mgr.get_retained_learning("bot_i")
        assert len(retained) == 1
        assert retained[0]["content"] == "High"

    def test_purge_returns_zero_when_nothing_to_purge(self):
        self.mgr.store_learning("bot_j", "t", "High", relevance_score=80.0)
        purged = self.mgr.purge_low_relevance("bot_j", threshold=30.0)
        assert purged == 0


# ===========================================================================
# 6. Scraper run log
# ===========================================================================

class TestScraperRunLog:
    def setup_method(self):
        self.mgr = BotLibraryManager()

    def teardown_method(self):
        self.mgr.close()

    def test_log_scraper_run_returns_dict(self):
        rec = self.mgr.log_scraper_run("bot_k", "github workflows", 10, 6)
        assert isinstance(rec, dict)

    def test_log_scraper_run_discarded_computed(self):
        rec = self.mgr.log_scraper_run("bot_k", "query", 10, 6)
        assert rec["items_discarded"] == 4

    def test_get_scraper_history_is_list(self):
        self.mgr.log_scraper_run("bot_l", "q", 5, 3)
        history = self.mgr.get_scraper_history("bot_l")
        assert isinstance(history, list)
        assert len(history) == 1

    def test_get_scraper_history_empty_for_unknown_bot(self):
        assert self.mgr.get_scraper_history("no_bot") == []

    def test_log_multiple_runs(self):
        for _ in range(3):
            self.mgr.log_scraper_run("bot_m", "q", 5, 3)
        history = self.mgr.get_scraper_history("bot_m")
        assert len(history) == 3
