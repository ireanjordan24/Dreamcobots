"""
Tests for the new DreamCo bot scripts.

These tests verify that each bot module:
1. Imports without errors
2. Exposes a callable ``run()`` function
3. Returns a dict with a ``status`` key when called
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import types
from typing import Callable

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BOTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bots"))
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load_bot(name: str) -> types.ModuleType:
    path = os.path.join(_BOTS_DIR, f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ---------------------------------------------------------------------------
# Core bots
# ---------------------------------------------------------------------------

class TestDebugBot:
    def setup_method(self):
        self.mod = _load_bot("debug_bot")

    def test_imports(self):
        assert self.mod is not None

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)
        assert "status" in result

    def test_analyze_no_crash(self):
        result = self.mod.analyze("random error message")
        assert result["fixes_found"] == 0  # empty knowledge base
        assert result["status"] == "no_known_fix"


class TestTestingBot:
    def setup_method(self):
        self.mod = _load_bot("testing_bot")

    def test_imports(self):
        assert self.mod is not None

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)
        assert "success" in result


class TestBotValidator:
    def setup_method(self):
        self.mod = _load_bot("bot_validator")

    def test_imports(self):
        assert self.mod is not None

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_validate_clean_code(self):
        result = self.mod.validate_code("def hello(): return 'world'")
        assert result["score"] == 100
        assert result["status"] == "pass"

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)
        assert "status" in result


# ---------------------------------------------------------------------------
# Intelligence bots
# ---------------------------------------------------------------------------

class TestInsightRanker:
    def setup_method(self):
        self.mod = _load_bot("insight_ranker")

    def test_imports(self):
        assert self.mod is not None

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_rank_empty(self):
        result = self.mod.rank_insights([])
        assert result == []

    def test_rank_assigns_confidence(self):
        items = [{"title": "fix ci workflow", "type": "bug_fix", "lesson": "test"}]
        ranked = self.mod.rank_insights(items)
        assert ranked[0]["confidence"] >= 1

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)
        assert result["status"] == "ok"


class TestBuddyBot:
    def setup_method(self):
        self.mod = _load_bot("buddy_bot")

    def test_imports(self):
        assert self.mod is not None

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)
        assert "status" in result

    def test_get_recommendations_empty_kb(self):
        recs = self.mod.get_top_recommendations()
        assert isinstance(recs, list)


class TestFeedbackLoopBot:
    def setup_method(self):
        self.mod = _load_bot("feedback_loop_bot")

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_analyze_empty(self):
        result = self.mod.analyze_feedback()
        assert "total_runs_analyzed" in result
        assert isinstance(result["recurring_failures"], list)

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)
        assert "status" in result


class TestAdaptiveLearningBot:
    def setup_method(self):
        self.mod = _load_bot("adaptive_learning_bot")

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_adapt_empty_insights(self):
        defaults = dict(self.mod._DEFAULTS)
        updated = self.mod.adapt([], defaults)
        assert updated["min_confidence"] == 1

    def test_adapt_rich_insights(self):
        insights = [{"confidence": 5}] * 20
        defaults = dict(self.mod._DEFAULTS)
        updated = self.mod.adapt(insights, defaults)
        assert updated["min_confidence"] >= defaults["min_confidence"]


# ---------------------------------------------------------------------------
# Analytics bots
# ---------------------------------------------------------------------------

class TestOptimizerBot:
    def setup_method(self):
        self.mod = _load_bot("optimizer_bot")

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_analyze_nonexistent_path(self):
        result = self.mod.analyze_path("/nonexistent/path")
        assert len(result) == 1
        assert result[0]["status"] == "error"

    def test_run_returns_dict(self):
        result = self.mod.run({"path": "bots/debug_bot.py"})
        assert isinstance(result, dict)
        assert "status" in result


class TestDeploymentReviewBot:
    def setup_method(self):
        self.mod = _load_bot("deployment_review_bot")

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_review_passes(self):
        result = self.mod.review()
        assert isinstance(result, dict)
        assert "passed" in result
        assert result["passed"] is True  # all required files exist

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Infrastructure bots
# ---------------------------------------------------------------------------

class TestContextPrunerBot:
    def setup_method(self):
        self.mod = _load_bot("context_pruner_bot")

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)
        assert "status" in result

    def test_prune_does_not_corrupt(self):
        result = self.mod.run({})
        assert result["total_entries_removed"] >= 0


class TestKnowledgeSyncBot:
    def setup_method(self):
        self.mod = _load_bot("knowledge_sync_bot")

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_deduplicate_removes_dupes(self):
        items = [
            {"title": "fix", "lesson": "a"},
            {"title": "fix", "lesson": "a"},
            {"title": "other", "lesson": "b"},
        ]
        unique = self.mod.deduplicate(items)
        assert len(unique) == 2

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)
        assert result["status"] == "synced"


class TestProactiveTaskPlanner:
    def setup_method(self):
        self.mod = _load_bot("proactive_task_planner")

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_generate_plan(self):
        plan = self.mod.generate_plan()
        assert "tasks" in plan
        assert "total_tasks" in plan
        assert isinstance(plan["tasks"], list)

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)


class TestPerformanceMonitorBot:
    def setup_method(self):
        self.mod = _load_bot("performance_monitor_bot")

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_report_empty(self):
        r = self.mod.report()
        assert r["total_measurements"] >= 0
        assert isinstance(r["slow_bots"], list)

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)
        assert "status" in result


class TestBotRegistry:
    def setup_method(self):
        self.mod = _load_bot("bot_registry")

    def test_has_run(self):
        assert callable(getattr(self.mod, "run", None))

    def test_scan_returns_list(self):
        entries = self.mod.scan()
        assert isinstance(entries, list)
        assert len(entries) > 0

    def test_entries_have_required_keys(self):
        entries = self.mod.scan()
        for e in entries:
            assert "name" in e
            assert "category" in e
            assert "has_run_fn" in e

    def test_run_returns_dict(self):
        result = self.mod.run({})
        assert isinstance(result, dict)
        assert result["total"] > 0
