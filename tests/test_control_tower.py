"""
Tests for the DreamCo Control Tower Python modules:
  - bots/control_center/github_integration.py
  - bots/control_center/heartbeat.py
  - bots/control_center/bot_registry.py
  - bots/control_center/auto_upgrade.py
  - Updated bots/control_center/control_center.py
  - Updated ui/web_dashboard.py (new endpoints)
"""

import sys
import os
import time
import json
import tempfile

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, "models"))
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.control_center.heartbeat import HeartbeatMonitor
from bots.control_center.bot_registry import BotRegistry
from bots.control_center.github_integration import GitHubIntegration
from bots.control_center.auto_upgrade import AutoUpgradeEngine
from bots.control_center.control_center import ControlCenter


# ===========================================================================
# HeartbeatMonitor
# ===========================================================================

class TestHeartbeatMonitor:
    def test_instantiate(self):
        hb = HeartbeatMonitor()
        assert hb is not None

    def test_ping_returns_live(self):
        hb = HeartbeatMonitor()
        result = hb.ping("bot_a")
        assert result["status"] == "live"
        assert result["bot_name"] == "bot_a"

    def test_get_status_live(self):
        hb = HeartbeatMonitor()
        hb.ping("bot_b")
        status = hb.get_status("bot_b")
        assert status["status"] == "live"
        assert status["seconds_since_ping"] is not None

    def test_get_status_unknown_bot(self):
        hb = HeartbeatMonitor()
        status = hb.get_status("ghost_bot")
        assert status["status"] == "offline"
        assert status["pinged_at"] is None

    def test_offline_after_timeout(self):
        hb = HeartbeatMonitor(timeout_seconds=0)
        hb.ping("bot_c")
        time.sleep(0.05)
        status = hb.get_status("bot_c")
        assert status["status"] == "offline"

    def test_get_all_status(self):
        hb = HeartbeatMonitor()
        hb.ping("x")
        hb.ping("y")
        all_s = hb.get_all_status()
        assert "x" in all_s
        assert "y" in all_s

    def test_summary(self):
        hb = HeartbeatMonitor()
        hb.ping("a")
        hb.ping("b")
        s = hb.summary()
        assert s["total_monitored"] == 2
        assert s["live"] == 2
        assert s["offline"] == 0

    def test_reset_single(self):
        hb = HeartbeatMonitor()
        hb.ping("del_me")
        hb.reset("del_me")
        assert hb.get_status("del_me")["status"] == "offline"

    def test_reset_all(self):
        hb = HeartbeatMonitor()
        hb.ping("p")
        hb.ping("q")
        hb.reset()
        assert hb.summary()["total_monitored"] == 0

    def test_ping_with_metadata(self):
        hb = HeartbeatMonitor()
        r = hb.ping("meta_bot", metadata={"version": "1.0"})
        assert r["metadata"]["version"] == "1.0"


# ===========================================================================
# BotRegistry
# ===========================================================================

class TestBotRegistry:
    def test_instantiate(self):
        reg = BotRegistry()
        assert reg.count() == 0

    def test_register_bot(self):
        reg = BotRegistry()
        entry = reg.register("real_estate_bot", repo_name="Dreamcobots")
        assert entry["bot_name"] == "real_estate_bot"
        assert entry["repo_name"] == "Dreamcobots"

    def test_register_returns_entry(self):
        reg = BotRegistry()
        e = reg.register("sales_bot")
        assert "registered_at" in e
        assert "status" in e

    def test_get_all(self):
        reg = BotRegistry()
        reg.register("a")
        reg.register("b")
        all_bots = reg.get_all()
        assert len(all_bots) == 2

    def test_get_single(self):
        reg = BotRegistry()
        reg.register("solo_bot", repo_name="my_repo")
        entry = reg.get("solo_bot")
        assert entry is not None
        assert entry["repo_name"] == "my_repo"

    def test_get_missing_returns_none(self):
        reg = BotRegistry()
        assert reg.get("nonexistent") is None

    def test_update_status(self):
        reg = BotRegistry()
        reg.register("status_bot")
        reg.update_status("status_bot", "running")
        assert reg.get("status_bot")["status"] == "running"

    def test_deregister(self):
        reg = BotRegistry()
        reg.register("to_remove")
        removed = reg.deregister("to_remove")
        assert removed is True
        assert reg.count() == 0

    def test_deregister_nonexistent(self):
        reg = BotRegistry()
        assert reg.deregister("ghost") is False

    def test_record_heartbeat(self):
        reg = BotRegistry()
        reg.register("hb_bot")
        reg.record_heartbeat("hb_bot")
        assert reg.get("hb_bot")["last_heartbeat"] is not None

    def test_record_pr(self):
        reg = BotRegistry()
        reg.register("pr_bot")
        reg.record_pr("pr_bot", "https://github.com/pr/1")
        assert reg.get("pr_bot")["last_pr"] == "https://github.com/pr/1"

    def test_record_commit(self):
        reg = BotRegistry()
        reg.register("commit_bot")
        reg.record_commit("commit_bot", "abc1234")
        assert reg.get("commit_bot")["last_commit"] == "abc1234"

    def test_summary(self):
        reg = BotRegistry()
        reg.register("a")
        reg.register("b")
        reg.update_status("a", "running")
        s = reg.summary()
        assert s["total_bots"] == 2
        assert "running" in s["by_status"] or "idle" in s["by_status"]

    def test_get_by_status(self):
        reg = BotRegistry()
        reg.register("active_bot")
        reg.update_status("active_bot", "running")
        reg.register("idle_bot")
        running = reg.get_by_status("running")
        assert len(running) == 1
        assert running[0]["bot_name"] == "active_bot"

    def test_export_json(self):
        reg = BotRegistry()
        reg.register("json_bot")
        exported = reg.export_json()
        data = json.loads(exported)
        assert "bots" in data
        assert data["bots"][0]["bot_name"] == "json_bot"

    def test_persist_and_load(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            reg = BotRegistry(persist_path=path)
            reg.register("persisted_bot", repo_name="PersistRepo")
            reg2 = BotRegistry(persist_path=path)
            assert reg2.get("persisted_bot") is not None
            assert reg2.get("persisted_bot")["repo_name"] == "PersistRepo"
        finally:
            os.unlink(path)

    def test_config_preserved_on_update(self):
        reg = BotRegistry()
        reg.register("cfg_bot", config={"niche": "real_estate"})
        reg.update_status("cfg_bot", "running")
        assert reg.get("cfg_bot")["config"]["niche"] == "real_estate"


# ===========================================================================
# GitHubIntegration
# ===========================================================================

class TestGitHubIntegration:
    def test_instantiate(self):
        gh = GitHubIntegration()
        assert gh is not None

    def test_get_repo_status_offline(self):
        # No token → API call will fail, return offline status
        gh = GitHubIntegration(token="invalid_token_for_test")
        status = gh.get_repo_status("nonexistent_repo_xyz_12345")
        assert isinstance(status, dict)
        assert "repo" in status
        assert "online" in status
        assert "timestamp" in status

    def test_get_repo_status_has_required_keys(self):
        gh = GitHubIntegration()
        status = gh.get_repo_status("test_repo")
        required = {"repo", "owner", "online", "timestamp", "open_prs", "last_workflow_status"}
        assert required.issubset(status.keys())

    def test_pull_latest_bad_path(self):
        gh = GitHubIntegration()
        result = gh.pull_latest("/nonexistent/path/xyz")
        assert result["success"] is False
        assert "error" in result

    def test_auto_merge_bad_path(self):
        gh = GitHubIntegration()
        result = gh.auto_merge("/nonexistent/path/xyz")
        assert result["success"] is False

    def test_create_pr_no_token(self):
        gh = GitHubIntegration(token="")
        result = gh.create_pull_request("test_repo", "auto-upgrade", "Test PR")
        assert result["success"] is False
        assert "GITHUB_TOKEN" in result.get("error", "")

    def test_event_log_records(self):
        gh = GitHubIntegration()
        gh.get_repo_status("some_repo")
        log = gh.get_event_log()
        assert len(log) >= 1
        assert log[-1]["action"] == "get_repo_status"

    def test_event_log_limit(self):
        gh = GitHubIntegration()
        for i in range(10):
            gh.get_repo_status(f"repo_{i}")
        log = gh.get_event_log(limit=5)
        assert len(log) == 5

    def test_clear_event_log(self):
        gh = GitHubIntegration()
        gh.get_repo_status("r")
        gh.clear_event_log()
        assert gh.get_event_log() == []

    def test_pull_bad_path_records_in_log(self):
        gh = GitHubIntegration()
        gh.pull_latest("/bad/path")
        log = gh.get_event_log()
        assert any(e["action"] == "pull_latest" for e in log)


# ===========================================================================
# AutoUpgradeEngine
# ===========================================================================

class TestAutoUpgradeEngine:
    def test_instantiate(self):
        engine = AutoUpgradeEngine()
        assert engine is not None

    def test_dry_run_all_empty_registry(self):
        reg = BotRegistry()
        engine = AutoUpgradeEngine(registry=reg, dry_run=True)
        result = engine.run_all()
        assert result["total"] == 0
        assert result["succeeded"] == 0

    def test_dry_run_single_bot(self):
        reg = BotRegistry()
        reg.register("upgrade_bot", repo_name="Dreamcobots")
        engine = AutoUpgradeEngine(registry=reg, dry_run=True)
        result = engine.run_all()
        assert result["total"] == 1
        assert result["succeeded"] == 1

    def test_upgrade_bot_has_steps(self):
        reg = BotRegistry()
        reg.register("step_bot")
        engine = AutoUpgradeEngine(registry=reg, dry_run=True)
        bot_result = engine.upgrade_bot(reg.get("step_bot"))
        assert "steps" in bot_result
        assert "pull" in bot_result["steps"]
        assert "pr" in bot_result["steps"]

    def test_upgrade_updates_registry_status(self):
        reg = BotRegistry()
        reg.register("status_update_bot")
        engine = AutoUpgradeEngine(registry=reg, dry_run=True)
        engine.upgrade_bot(reg.get("status_update_bot"))
        # Status should be updated to "updated"
        assert reg.get("status_update_bot")["status"] in ("updated", "conflict_detected")

    def test_upgrade_log_recorded(self):
        reg = BotRegistry()
        reg.register("log_bot")
        engine = AutoUpgradeEngine(registry=reg, dry_run=True)
        engine.run_all()
        log = engine.get_upgrade_log()
        assert len(log) == 1

    def test_upgrade_log_limit(self):
        reg = BotRegistry()
        for i in range(5):
            reg.register(f"bot_{i}")
        engine = AutoUpgradeEngine(registry=reg, dry_run=True)
        engine.run_all()
        limited = engine.get_upgrade_log(limit=3)
        assert len(limited) == 3

    def test_test_bot_import_error(self):
        engine = AutoUpgradeEngine()
        result = engine.test_bot("nonexistent_bot_xyz")
        assert result["success"] is False
        assert "error" in result

    def test_run_all_summary_keys(self):
        reg = BotRegistry()
        reg.register("summary_bot")
        engine = AutoUpgradeEngine(registry=reg, dry_run=True)
        result = engine.run_all()
        assert "total" in result
        assert "succeeded" in result
        assert "failed" in result
        assert "timestamp" in result
        assert "results" in result


# ===========================================================================
# ControlCenter — extended with Control Tower features
# ===========================================================================

class TestControlCenterExtended:
    def test_instantiate_with_defaults(self):
        cc = ControlCenter()
        assert cc.registry is not None
        assert cc.heartbeat is not None
        assert cc.github is not None

    def test_register_bot_updates_registry(self):
        cc = ControlCenter()

        class _DummyBot:
            tier = None

        cc.register_bot("dummy", _DummyBot(), repo_name="test_repo")
        entry = cc.registry.get("dummy")
        assert entry is not None
        assert entry["repo_name"] == "test_repo"

    def test_ping_bot_records_heartbeat(self):
        cc = ControlCenter()

        class _DummyBot:
            tier = None

        cc.register_bot("pingable", _DummyBot())
        result = cc.ping_bot("pingable")
        assert result["status"] == "live"

    def test_monitoring_dashboard_has_heartbeat(self):
        cc = ControlCenter()
        dash = cc.get_monitoring_dashboard()
        assert "heartbeat" in dash
        assert "registry" in dash

    def test_deploy_bot(self):
        cc = ControlCenter()
        result = cc.deploy_bot("new_bot", repo_name="NewRepo", tier="pro")
        assert result["bot_name"] == "new_bot"
        assert result["status"] == "registered"
        assert cc.registry.get("new_bot") is not None

    def test_get_github_repo_status_returns_dict(self):
        cc = ControlCenter()
        status = cc.get_github_repo_status("Dreamcobots")
        assert isinstance(status, dict)
        assert "repo" in status
        assert "online" in status

    def test_inject_custom_registry(self):
        reg = BotRegistry()
        reg.register("pre_registered", repo_name="SomeRepo")
        cc = ControlCenter(registry=reg)
        assert cc.registry.get("pre_registered") is not None

    def test_inject_custom_heartbeat(self):
        from bots.control_center.heartbeat import HeartbeatMonitor
        hb = HeartbeatMonitor(timeout_seconds=999)
        cc = ControlCenter(heartbeat=hb)
        cc.ping_bot("injected_bot")
        assert cc.heartbeat.get_status("injected_bot")["status"] == "live"


# ===========================================================================
# Web Dashboard — new Control Tower endpoints
# ===========================================================================

try:
    from flask import Flask
    _FLASK_AVAILABLE = True
except ImportError:
    _FLASK_AVAILABLE = False


@pytest.mark.skipif(not _FLASK_AVAILABLE, reason="Flask not installed")
class TestControlTowerDashboardEndpoints:
    """Tests for the new Control Tower API endpoints in web_dashboard.py."""

    @pytest.fixture
    def client(self):
        from ui.web_dashboard import create_app
        app = create_app()
        app.config["TESTING"] = True
        with app.test_client() as c:
            yield c

    # -- Heartbeat --

    def test_heartbeat_returns_200(self, client):
        resp = client.get("/api/heartbeat")
        assert resp.status_code == 200

    def test_heartbeat_has_summary_keys(self, client):
        data = client.get("/api/heartbeat").get_json()
        assert "live" in data
        assert "offline" in data
        assert "bots" in data

    def test_heartbeat_ping_returns_200(self, client):
        resp = client.post("/api/heartbeat/ping", json={"bot_name": "test_bot"})
        assert resp.status_code == 200

    def test_heartbeat_ping_missing_name_returns_400(self, client):
        resp = client.post("/api/heartbeat/ping", json={})
        assert resp.status_code == 400

    def test_heartbeat_bot_appears_live_after_ping(self, client):
        client.post("/api/heartbeat/ping", json={"bot_name": "live_bot"})
        data = client.get("/api/heartbeat").get_json()
        assert "live_bot" in data["bots"]
        assert data["bots"]["live_bot"]["status"] == "live"

    # -- Registry --

    def test_registry_returns_200(self, client):
        resp = client.get("/api/registry")
        assert resp.status_code == 200

    def test_registry_has_summary(self, client):
        data = client.get("/api/registry").get_json()
        assert "summary" in data
        assert "bots" in data

    # -- GitHub --

    def test_github_endpoint_returns_200(self, client):
        resp = client.get("/api/github/Dreamcobots")
        assert resp.status_code == 200

    def test_github_endpoint_returns_repo_name(self, client):
        data = client.get("/api/github/Dreamcobots").get_json()
        assert data["repo"] == "Dreamcobots"

    def test_github_endpoint_has_required_keys(self, client):
        data = client.get("/api/github/TestRepo").get_json()
        assert "online" in data
        assert "timestamp" in data

    # -- Deploy --

    def test_deploy_returns_201(self, client):
        resp = client.post("/api/deploy", json={"bot_name": "deploy_test_bot"})
        assert resp.status_code == 201

    def test_deploy_missing_name_returns_400(self, client):
        resp = client.post("/api/deploy", json={})
        assert resp.status_code == 400

    def test_deploy_registers_in_registry(self, client):
        client.post("/api/deploy", json={"bot_name": "reg_bot", "repo_name": "SomeRepo"})
        data = client.get("/api/registry").get_json()
        names = [b["bot_name"] for b in data["bots"]]
        assert "reg_bot" in names

    def test_deploy_response_has_expected_keys(self, client):
        resp = client.post("/api/deploy", json={"bot_name": "key_bot", "tier": "pro"})
        data = resp.get_json()
        assert "bot_name" in data
        assert "status" in data
        assert "timestamp" in data

    # -- Upgrade-all --

    def test_upgrade_all_returns_200(self, client):
        resp = client.post("/api/upgrade-all")
        assert resp.status_code == 200

    def test_upgrade_all_has_summary_keys(self, client):
        data = client.post("/api/upgrade-all").get_json()
        assert "total" in data
        assert "succeeded" in data
        assert "failed" in data
        assert "results" in data

    def test_upgrade_all_dry_run_for_registered_bot(self, client):
        # Register a bot first, then run upgrade-all
        client.post("/api/deploy", json={"bot_name": "upgrade_bot_x"})
        data = client.post("/api/upgrade-all").get_json()
        assert data["total"] >= 1
