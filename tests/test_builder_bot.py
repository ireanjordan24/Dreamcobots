"""
Tests for bots/builder_bot/builder_bot.py

Covers:
  1. SubBotTask / SubBotResult dataclasses
  2. Individual built-in sub-bot handlers
  3. BuilderBot registration and listing
  4. BuilderBot.run_task — success and failure
  5. BuilderBot.run_parallel — parallel execution
  6. BuilderBot.run_pipeline — sequential with context propagation
  7. BuilderBot.summary
  8. BuilderBot.get_capabilities
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.builder_bot.builder_bot import (
    BuilderBot,
    SubBotTask,
    SubBotResult,
    SubBotStatus,
    TaskPriority,
    _sandbox_config_bot,
    _feature_validator,
    _code_tester,
    _deployment_bot,
    _conflict_resolver,
    _dedup_bot,
    _pr_tracker,
    _library_scout,
)


# ---------------------------------------------------------------------------
# SubBotTask and SubBotResult
# ---------------------------------------------------------------------------


class TestDataModels:
    def test_task_default_priority(self):
        task = SubBotTask(name="test", payload={})
        assert task.priority == TaskPriority.NORMAL

    def test_task_has_id(self):
        task = SubBotTask(name="test", payload={})
        assert task.task_id
        assert len(task.task_id) > 0

    def test_result_to_dict_keys(self):
        result = SubBotResult(
            task_id="abc",
            sub_bot_name="test_bot",
            status=SubBotStatus.COMPLETE,
            output={"key": "value"},
            duration_seconds=0.5,
        )
        d = result.to_dict()
        for key in ("task_id", "sub_bot_name", "status", "output", "duration_seconds", "error"):
            assert key in d

    def test_result_to_dict_status_value(self):
        result = SubBotResult(
            task_id="x",
            sub_bot_name="b",
            status=SubBotStatus.FAILED,
            output={},
        )
        assert result.to_dict()["status"] == "failed"


# ---------------------------------------------------------------------------
# Individual sub-bot handlers
# ---------------------------------------------------------------------------


class TestBuiltinSubBots:
    def _make_task(self, payload: dict) -> SubBotTask:
        return SubBotTask(name="test", payload=payload)

    def test_sandbox_config_bot_returns_container_id(self):
        result = _sandbox_config_bot(self._make_task({"repo": "my-repo", "branch": "main"}))
        assert "container_id" in result
        assert result["status"] == "ready"

    def test_feature_validator_approved(self):
        result = _feature_validator(self._make_task({"feature": "new-auth"}))
        assert result["verdict"] == "approved"
        assert "checks" in result

    def test_code_tester_all_passed(self):
        result = _code_tester(self._make_task({"target": "bots/"}))
        assert result["verdict"] == "all_passed"
        assert result["unit_tests"]["failed"] == 0

    def test_deployment_bot_deployed(self):
        result = _deployment_bot(self._make_task({"environment": "staging"}))
        assert result["status"] == "deployed"
        assert "deploy_url" in result

    def test_conflict_resolver_resolves_all(self):
        files = ["main.py", "config.yaml"]
        result = _conflict_resolver(self._make_task({"pr_number": 42, "conflicting_files": files}))
        assert result["status"] == "resolved"
        assert result["remaining_conflicts"] == 0
        assert len(result["resolved"]) == 2

    def test_dedup_bot_clean(self):
        result = _dedup_bot(self._make_task({"scope": "repo", "simulated_duplicates": 3}))
        assert result["duplicates_found"] == 3
        assert result["removed"] == 3
        assert result["status"] == "clean"

    def test_pr_tracker_returns_statuses(self):
        prs = [{"number": 1, "title": "Add feature", "status": "open", "ci": "passing"}]
        result = _pr_tracker(self._make_task({"pr_list": prs}))
        assert result["tracked_prs"] == 1
        assert 1 in result["statuses"]

    def test_library_scout_returns_results(self):
        result = _library_scout(self._make_task({"query": "requests", "language": "python"}))
        assert "results" in result
        assert len(result["results"]) > 0
        assert result["language"] == "python"


# ---------------------------------------------------------------------------
# BuilderBot
# ---------------------------------------------------------------------------


class TestBuilderBot:
    def setup_method(self):
        self.bot = BuilderBot(max_workers=2)

    def test_list_sub_bots_includes_builtins(self):
        bots = self.bot.list_sub_bots()
        for expected in ("sandbox_config_bot", "feature_validator", "code_tester", "deployment_bot"):
            assert expected in bots

    def test_register_custom_sub_bot(self):
        self.bot.register_sub_bot("my_custom_bot", lambda t: {"ok": True})
        assert "my_custom_bot" in self.bot.list_sub_bots()

    def test_register_duplicate_raises_without_overwrite(self):
        with pytest.raises(ValueError, match="already registered"):
            self.bot.register_sub_bot("sandbox_config_bot", lambda t: {})

    def test_register_duplicate_with_overwrite(self):
        self.bot.register_sub_bot("sandbox_config_bot", lambda t: {"replaced": True}, overwrite=True)
        result = self.bot.run_task("sandbox_config_bot", {})
        assert result.output.get("replaced") is True

    def test_run_task_success(self):
        result = self.bot.run_task("feature_validator", {"feature": "login"})
        assert result.status == SubBotStatus.COMPLETE
        assert result.output["verdict"] == "approved"

    def test_run_task_unknown_bot(self):
        result = self.bot.run_task("nonexistent_bot", {})
        assert result.status == SubBotStatus.FAILED
        assert "not found" in (result.error or "")

    def test_run_task_duration_positive(self):
        result = self.bot.run_task("code_tester", {"target": "tests/"})
        assert result.duration_seconds >= 0

    def test_run_parallel_all_complete(self):
        tasks = [
            SubBotTask(name="sandbox_config_bot", payload={}),
            SubBotTask(name="feature_validator", payload={"feature": "x"}),
            SubBotTask(name="code_tester", payload={}),
        ]
        results = self.bot.run_parallel(tasks)
        assert len(results) == 3
        for r in results:
            assert r.status == SubBotStatus.COMPLETE

    def test_run_parallel_stores_history(self):
        tasks = [SubBotTask(name="dedup_bot", payload={})]
        before = len(self.bot._history)
        self.bot.run_parallel(tasks)
        assert len(self.bot._history) == before + 1

    def test_run_pipeline_success(self):
        pipeline = [
            {"sub_bot": "sandbox_config_bot", "payload": {"repo": "dreamco", "branch": "main"}},
            {"sub_bot": "code_tester", "payload": {"target": "all"}},
            {"sub_bot": "deployment_bot", "payload": {"environment": "staging"}},
        ]
        result = self.bot.run_pipeline(pipeline)
        assert result["steps_run"] == 3
        assert "final_output" in result

    def test_run_pipeline_halts_on_failure(self):
        pipeline = [
            {"sub_bot": "nonexistent", "payload": {}},
            {"sub_bot": "code_tester", "payload": {}},
        ]
        result = self.bot.run_pipeline(pipeline)
        # Should stop after first failed step
        assert result["steps_run"] == 1

    def test_summary_keys(self):
        self.bot.run_task("library_scout", {"query": "numpy", "language": "python"})
        summary = self.bot.summary()
        for key in ("session_id", "registered_sub_bots", "tasks_run", "tasks_passed", "tasks_failed"):
            assert key in summary

    def test_summary_tasks_count(self):
        self.bot.run_task("pr_tracker", {"pr_list": []})
        summary = self.bot.summary()
        assert summary["tasks_run"] >= 1

    def test_get_capabilities_keys(self):
        caps = self.bot.get_capabilities()
        assert caps["bot_id"] == "builder_bot"
        assert "built_in_sub_bots" in caps
        assert len(caps["features"]) > 0

    def test_exception_in_handler_returns_failed(self):
        def bad_handler(task):
            raise RuntimeError("Intentional test error")
        self.bot.register_sub_bot("bad_bot", bad_handler)
        result = self.bot.run_task("bad_bot", {})
        assert result.status == SubBotStatus.FAILED
        assert "Intentional test error" in (result.error or "")
