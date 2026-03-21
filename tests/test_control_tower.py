"""Tests for the DreamCo Control Tower modules.

Covers:
  - dreamco-control-tower/backend/bot_manager.py
  - dreamco-control-tower/backend/repo_manager.py
  - dreamco-control-tower/backend/auto_upgrader.py
  - dreamco-control-tower/backend/revenue_tracker.py
  - ControlCenter enhancements (heartbeat, repo monitoring, deploy, onboard)
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Path setup — make Control Tower modules importable
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
CT_BACKEND = os.path.join(REPO_ROOT, "dreamco-control-tower", "backend")
AI_MODELS = os.path.join(REPO_ROOT, "bots", "ai-models-integration")

sys.path.insert(0, CT_BACKEND)
sys.path.insert(0, AI_MODELS)
sys.path.insert(0, REPO_ROOT)

from bot_manager import (
    BotManager,
    STATUS_ACTIVE,
    STATUS_CONFLICT,
    STATUS_OFFLINE,
    STATUS_UPDATING,
    STATUS_ONBOARDING,
)
from repo_manager import RepoManager, GitHubClient
from auto_upgrader import AutoUpgrader
from revenue_tracker import RevenueTracker, StripeProvider, PayPalProvider, SquareProvider

from tiers import Tier
from bots.control_center.control_center import ControlCenter
from bots.affiliate_bot.affiliate_bot import AffiliateBot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tmp_json(data) -> str:
    """Write *data* to a temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as fh:
        json.dump(data, fh)
    return path


def _make_bot_manager(bots: Optional[List[Dict]] = None) -> tuple[BotManager, str]:
    """Create a BotManager backed by a temporary JSON file."""
    path = _tmp_json(bots or [])
    return BotManager(config_path=path), path


def _make_repo_manager(
    repos: Optional[List[Dict]] = None,
    client: Optional[GitHubClient] = None,
) -> tuple[RepoManager, str]:
    path = _tmp_json(repos or [])
    return RepoManager(config_path=path, github_client=client or MagicMock(spec=GitHubClient)), path


# ---------------------------------------------------------------------------
# BotManager tests
# ---------------------------------------------------------------------------

class TestBotManagerInstantiation:
    def test_creates_empty_registry(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        assert bm.total_bots() == 0

    def test_loads_existing_config(self):
        existing = [{"name": "test_bot", "repoName": "Repo", "repoPath": "bots/test", "tier": "free"}]
        bm, _ = _make_bot_manager(existing)
        assert bm.total_bots() == 1
        assert bm.get_bot("test_bot") is not None

    def test_handles_missing_config_gracefully(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "nonexistent.json"))
        assert bm.total_bots() == 0


class TestBotManagerRegister:
    def test_register_returns_entry(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        entry = bm.register_bot("bot_a", "Repo", "bots/a", tier="pro", description="Test")
        assert entry["name"] == "bot_a"
        assert entry["tier"] == "pro"

    def test_register_increases_total(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("bot_a", "Repo", "bots/a")
        bm.register_bot("bot_b", "Repo", "bots/b")
        assert bm.total_bots() == 2

    def test_registered_status_is_onboarding(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        entry = bm.register_bot("bot_a", "Repo", "bots/a")
        assert entry["status"] == STATUS_ONBOARDING

    def test_register_sets_registered_at(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        entry = bm.register_bot("bot_a", "Repo", "bots/a")
        assert "registeredAt" in entry


class TestBotManagerRemove:
    def test_remove_existing_bot(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("bot_a", "Repo", "bots/a")
        assert bm.remove_bot("bot_a") is True
        assert bm.total_bots() == 0

    def test_remove_nonexistent_returns_false(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        assert bm.remove_bot("ghost") is False


class TestBotManagerHeartbeat:
    def test_heartbeat_updates_timestamp(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("bot_a", "Repo", "bots/a")
        assert bm.update_heartbeat("bot_a") is True
        assert bm.get_bot("bot_a")["heartbeat"] is not None

    def test_heartbeat_unknown_bot_returns_false(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        assert bm.update_heartbeat("ghost") is False

    def test_heartbeat_revives_offline_bot(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("bot_a", "Repo", "bots/a")
        bm.set_status("bot_a", STATUS_OFFLINE)
        bm.update_heartbeat("bot_a")
        assert bm.get_bot("bot_a")["status"] == STATUS_ACTIVE


class TestBotManagerStatus:
    def test_set_valid_status(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("bot_a", "Repo", "bots/a")
        assert bm.set_status("bot_a", STATUS_ACTIVE) is True

    def test_set_invalid_status_returns_false(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("bot_a", "Repo", "bots/a")
        assert bm.set_status("bot_a", "flying") is False

    def test_set_status_unknown_bot_returns_false(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        assert bm.set_status("ghost", STATUS_ACTIVE) is False


class TestBotManagerConflict:
    def test_mark_conflict_sets_status(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("bot_a", "Repo", "bots/a")
        bm.mark_conflict("bot_a", True)
        assert bm.get_bot("bot_a")["status"] == STATUS_CONFLICT
        assert bm.get_bot("bot_a")["conflictsDetected"] is True

    def test_clear_conflict(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("bot_a", "Repo", "bots/a")
        bm.mark_conflict("bot_a", True)
        bm.mark_conflict("bot_a", False)
        assert bm.get_bot("bot_a")["conflictsDetected"] is False

    def test_get_conflicted_bots(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("bot_a", "Repo", "bots/a")
        bm.register_bot("bot_b", "Repo", "bots/b")
        bm.mark_conflict("bot_a", True)
        conflicted = bm.get_conflicted_bots()
        assert len(conflicted) == 1
        assert conflicted[0]["name"] == "bot_a"


class TestBotManagerRecordUpdate:
    def test_record_update_sets_active(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("bot_a", "Repo", "bots/a")
        bm.set_status("bot_a", STATUS_UPDATING)
        bm.record_update("bot_a")
        assert bm.get_bot("bot_a")["status"] == STATUS_ACTIVE

    def test_record_update_sets_timestamp(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("bot_a", "Repo", "bots/a")
        bm.record_update("bot_a")
        assert bm.get_bot("bot_a")["lastUpdate"] is not None


class TestBotManagerSummary:
    def test_summary_returns_dict(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        result = bm.get_summary()
        assert isinstance(result, dict)

    def test_summary_has_required_keys(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        for key in ("total", "by_status", "conflicts", "timestamp"):
            assert key in bm.get_summary()

    def test_summary_counts_total(self, tmp_path):
        bm = BotManager(config_path=str(tmp_path / "bots.json"))
        bm.register_bot("a", "R", "p")
        bm.register_bot("b", "R", "p")
        assert bm.get_summary()["total"] == 2


class TestBotManagerPersistence:
    def test_save_and_reload(self, tmp_path):
        path = str(tmp_path / "bots.json")
        bm = BotManager(config_path=path)
        bm.register_bot("bot_a", "Repo", "bots/a", tier="pro")
        bm.save()

        bm2 = BotManager(config_path=path)
        assert bm2.total_bots() == 1
        assert bm2.get_bot("bot_a")["tier"] == "pro"


# ---------------------------------------------------------------------------
# RepoManager tests
# ---------------------------------------------------------------------------

class TestRepoManagerInstantiation:
    def test_creates_empty_registry(self, tmp_path):
        client = MagicMock(spec=GitHubClient)
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=client)
        assert len(rm.list_repos()) == 0

    def test_loads_existing_config(self):
        existing = [{"name": "MyRepo", "owner": "user", "branch": "main"}]
        rm, _ = _make_repo_manager(existing)
        assert len(rm.list_repos()) == 1


class TestRepoManagerAddRemove:
    def test_add_repo(self, tmp_path):
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=MagicMock())
        entry = rm.add_repo("MyRepo", "user")
        assert entry["name"] == "MyRepo"
        assert entry["owner"] == "user"

    def test_add_repo_default_url(self, tmp_path):
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=MagicMock())
        entry = rm.add_repo("MyRepo", "user")
        assert entry["url"] == "https://github.com/user/MyRepo"

    def test_remove_existing_repo(self, tmp_path):
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=MagicMock())
        rm.add_repo("MyRepo", "user")
        assert rm.remove_repo("MyRepo") is True
        assert len(rm.list_repos()) == 0

    def test_remove_nonexistent_returns_false(self, tmp_path):
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=MagicMock())
        assert rm.remove_repo("ghost") is False


class TestRepoManagerSync:
    def _client_with_data(self) -> GitHubClient:
        client = MagicMock(spec=GitHubClient)
        client.get.side_effect = lambda path: (
            {"pushed_at": "2024-01-01T00:00:00Z", "open_issues_count": 3}
            if path.endswith("MyRepo")
            else [{"number": 1}, {"number": 2}]
            if "pulls" in path
            else {"workflow_runs": [{"status": "completed", "conclusion": "success",
                                     "name": "CI", "updated_at": "2024-01-01T00:00:00Z"}]}
        )
        return client

    def test_sync_unknown_repo_returns_error(self, tmp_path):
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=MagicMock())
        result = rm.sync_repo("ghost")
        assert "error" in result

    def test_sync_missing_owner_returns_error(self, tmp_path):
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=MagicMock())
        rm._repos["MyRepo"] = {"name": "MyRepo"}  # no owner
        result = rm.sync_repo("MyRepo")
        assert "error" in result

    def test_sync_updates_last_synced(self, tmp_path):
        client = self._client_with_data()
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=client)
        rm.add_repo("MyRepo", "user")
        result = rm.sync_repo("MyRepo")
        assert "lastSynced" in result

    def test_sync_all_returns_dict(self, tmp_path):
        client = self._client_with_data()
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=client)
        rm.add_repo("MyRepo", "user")
        results = rm.sync_all()
        assert "MyRepo" in results


class TestRepoManagerCreatePR:
    def test_create_pr_unknown_repo_returns_none(self, tmp_path):
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=MagicMock())
        assert rm.create_pr("ghost", "Title", "auto-update") is None

    def test_create_pr_calls_github_api(self, tmp_path):
        client = MagicMock(spec=GitHubClient)
        client.post.return_value = {"html_url": "https://github.com/user/Repo/pull/1", "number": 1}
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=client)
        rm.add_repo("Repo", "user")
        result = rm.create_pr("Repo", "🤖 Auto-upgrade", "auto-update")
        assert result is not None
        assert result.get("html_url")
        client.post.assert_called_once()

    def test_create_pr_records_last_pr(self, tmp_path):
        client = MagicMock(spec=GitHubClient)
        client.post.return_value = {"html_url": "https://github.com/user/Repo/pull/1"}
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=client)
        rm.add_repo("Repo", "user")
        rm.create_pr("Repo", "title", "auto-update")
        assert rm.get_repo("Repo")["lastPR"] is not None


class TestRepoManagerSummary:
    def test_summary_returns_dict(self, tmp_path):
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=MagicMock())
        result = rm.get_summary()
        assert isinstance(result, dict)

    def test_summary_has_required_keys(self, tmp_path):
        rm = RepoManager(config_path=str(tmp_path / "repos.json"), github_client=MagicMock())
        for key in ("total_repos", "total_open_prs", "total_open_issues", "conflicted_repos", "timestamp"):
            assert key in rm.get_summary()


# ---------------------------------------------------------------------------
# AutoUpgrader tests
# ---------------------------------------------------------------------------

def _make_upgrader(bots=None, repos=None, runner=None, run_tests=False):
    """Build an AutoUpgrader with stub managers and a mock runner."""
    bm, _ = _make_bot_manager(bots or [])
    rm, _ = _make_repo_manager(repos or [])
    mock_runner = runner or MagicMock(return_value=MagicMock(returncode=0, stdout="ok", stderr=""))
    return AutoUpgrader(
        bot_manager=bm,
        repo_manager=rm,
        repo_root="/fake/root",
        run_tests=run_tests,
        runner=mock_runner,
    ), bm, rm


class TestAutoUpgraderInit:
    def test_creates_instance(self):
        upgrader, _, _ = _make_upgrader()
        assert upgrader is not None

    def test_upgrade_log_starts_empty(self):
        upgrader, _, _ = _make_upgrader()
        assert upgrader.get_upgrade_log() == []


class TestAutoUpgraderUpgradeBot:
    def test_upgrade_unknown_bot_returns_error(self):
        upgrader, _, _ = _make_upgrader()
        result = upgrader.upgrade_bot("ghost")
        assert result["status"] == "error"
        assert "not found" in result["detail"]

    def test_upgrade_bot_success(self, tmp_path):
        bm, bpath = _make_bot_manager()
        bm.register_bot("bot_a", "Repo", "bots/a")
        rm, _ = _make_repo_manager([{"name": "Repo", "owner": "user", "branch": "main"}])
        rm._repos["Repo"]["owner"] = "user"
        mock_runner = MagicMock(return_value=MagicMock(returncode=0, stdout="ok", stderr=""))
        upgrader = AutoUpgrader(bm, rm, repo_root="/fake", run_tests=False, runner=mock_runner)
        result = upgrader.upgrade_bot("bot_a")
        assert result["status"] == "ok"

    def test_upgrade_bot_conflict_resolved(self, tmp_path):
        bm, _ = _make_bot_manager()
        bm.register_bot("bot_a", "Repo", "bots/a")
        rm, _ = _make_repo_manager([{"name": "Repo", "owner": "user", "branch": "main"}])
        # pull fails, merge succeeds
        fail = MagicMock(returncode=1, stdout="", stderr="conflict")
        success = MagicMock(returncode=0, stdout="merged", stderr="")
        mock_runner = MagicMock(side_effect=[fail, success])
        upgrader = AutoUpgrader(bm, rm, repo_root="/fake", run_tests=False, runner=mock_runner)
        result = upgrader.upgrade_bot("bot_a")
        assert result["status"] == "conflict_resolved"

    def test_upgrade_bot_error_on_both_failures(self, tmp_path):
        bm, _ = _make_bot_manager()
        bm.register_bot("bot_a", "Repo", "bots/a")
        rm, _ = _make_repo_manager([{"name": "Repo", "owner": "user", "branch": "main"}])
        fail = MagicMock(returncode=1, stdout="", stderr="error")
        mock_runner = MagicMock(return_value=fail)
        upgrader = AutoUpgrader(bm, rm, repo_root="/fake", run_tests=False, runner=mock_runner)
        result = upgrader.upgrade_bot("bot_a")
        assert result["status"] == "error"

    def test_upgrade_all_returns_dict_for_each_bot(self, tmp_path):
        bm, _ = _make_bot_manager()
        bm.register_bot("bot_a", "Repo", "bots/a")
        bm.register_bot("bot_b", "Repo", "bots/b")
        rm, _ = _make_repo_manager([{"name": "Repo", "owner": "user", "branch": "main"}])
        mock_runner = MagicMock(return_value=MagicMock(returncode=0, stdout="ok", stderr=""))
        upgrader = AutoUpgrader(bm, rm, repo_root="/fake", run_tests=False, runner=mock_runner)
        results = upgrader.upgrade_all()
        assert "bot_a" in results
        assert "bot_b" in results

    def test_upgrade_log_records_entries(self, tmp_path):
        bm, _ = _make_bot_manager()
        bm.register_bot("bot_a", "Repo", "bots/a")
        rm, _ = _make_repo_manager([{"name": "Repo", "owner": "user", "branch": "main"}])
        mock_runner = MagicMock(return_value=MagicMock(returncode=0, stdout="ok", stderr=""))
        upgrader = AutoUpgrader(bm, rm, repo_root="/fake", run_tests=False, runner=mock_runner)
        upgrader.upgrade_bot("bot_a")
        assert len(upgrader.get_upgrade_log()) == 1

    def test_upgrade_records_pr(self, tmp_path):
        bm, _ = _make_bot_manager()
        bm.register_bot("bot_a", "Repo", "bots/a")
        rm, _ = _make_repo_manager([{"name": "Repo", "owner": "user", "branch": "main"}])
        # Make the RM return a PR result
        rm._client = MagicMock(spec=GitHubClient)
        rm._client.post.return_value = {"html_url": "https://github.com/user/Repo/pull/1"}
        mock_runner = MagicMock(return_value=MagicMock(returncode=0, stdout="ok", stderr=""))
        upgrader = AutoUpgrader(bm, rm, repo_root="/fake", run_tests=False, runner=mock_runner)
        result = upgrader.upgrade_bot("bot_a")
        assert result.get("pr") is not None


# ---------------------------------------------------------------------------
# RevenueTracker tests
# ---------------------------------------------------------------------------

class TestRevenueTrackerInstantiation:
    def test_creates_with_default_providers(self):
        rt = RevenueTracker()
        assert rt is not None

    def test_creates_with_custom_provider(self):
        provider = MagicMock(spec=StripeProvider)
        provider.name = "mock_stripe"
        provider.fetch_payments.return_value = []
        rt = RevenueTracker(providers=[provider])
        assert rt is not None


class TestRevenueTrackerAddEntry:
    def test_add_entry_returns_dict(self):
        rt = RevenueTracker(providers=[])
        entry = rt.add_entry(99.99, bot_name="bot_a", provider="stripe")
        assert entry["amount_usd"] == 99.99
        assert entry["bot_name"] == "bot_a"

    def test_add_entry_appears_in_summary(self):
        rt = RevenueTracker(providers=[])
        rt.add_entry(100.0, bot_name="bot_a", provider="stripe")
        summary = rt.get_summary()
        assert summary["total_usd"] == 100.0

    def test_add_multiple_entries_accumulate(self):
        rt = RevenueTracker(providers=[])
        rt.add_entry(100.0, bot_name="bot_a", provider="stripe")
        rt.add_entry(50.0, bot_name="bot_a", provider="paypal")
        summary = rt.get_summary()
        assert abs(summary["total_usd"] - 150.0) < 0.01


class TestRevenueTrackerSummary:
    def test_summary_has_required_keys(self):
        rt = RevenueTracker(providers=[])
        for key in ("total_usd", "by_provider", "by_bot", "succeeded_count", "failed_count", "payment_count", "timestamp"):
            assert key in rt.get_summary()

    def test_by_provider_breakdown(self):
        rt = RevenueTracker(providers=[])
        rt.add_entry(100.0, bot_name="b", provider="stripe")
        rt.add_entry(50.0, bot_name="b", provider="paypal")
        summary = rt.get_summary()
        assert summary["by_provider"]["stripe"] == 100.0
        assert summary["by_provider"]["paypal"] == 50.0

    def test_by_bot_breakdown(self):
        rt = RevenueTracker(providers=[])
        rt.add_entry(200.0, bot_name="affiliate", provider="stripe")
        rt.add_entry(75.0, bot_name="mining", provider="stripe")
        summary = rt.get_summary()
        assert summary["by_bot"]["affiliate"] == 200.0
        assert summary["by_bot"]["mining"] == 75.0

    def test_failed_entry_not_counted_in_total(self):
        rt = RevenueTracker(providers=[])
        rt.add_entry(100.0, bot_name="b", provider="stripe", status="failed")
        summary = rt.get_summary()
        assert summary["total_usd"] == 0.0
        assert summary["failed_count"] == 1


class TestRevenueTrackerTopBots:
    def test_returns_list(self):
        rt = RevenueTracker(providers=[])
        assert isinstance(rt.get_top_bots(), list)

    def test_top_bots_ordered_by_revenue(self):
        rt = RevenueTracker(providers=[])
        rt.add_entry(300.0, bot_name="bot_c", provider="stripe")
        rt.add_entry(100.0, bot_name="bot_a", provider="stripe")
        rt.add_entry(200.0, bot_name="bot_b", provider="stripe")
        top = rt.get_top_bots(n=3)
        assert top[0]["bot"] == "bot_c"
        assert top[1]["bot"] == "bot_b"

    def test_get_provider_breakdown(self):
        rt = RevenueTracker(providers=[])
        rt.add_entry(100.0, bot_name="b", provider="stripe")
        breakdown = rt.get_provider_breakdown()
        assert isinstance(breakdown, list)
        assert breakdown[0]["provider"] == "stripe"


class TestStubProviders:
    def test_stripe_returns_empty_list(self):
        p = StripeProvider()
        assert p.fetch_payments() == []
        assert p.name == "stripe"

    def test_paypal_returns_empty_list(self):
        p = PayPalProvider()
        assert p.fetch_payments() == []
        assert p.name == "paypal"

    def test_square_returns_empty_list(self):
        p = SquareProvider()
        assert p.fetch_payments() == []
        assert p.name == "square"


# ---------------------------------------------------------------------------
# ControlCenter enhancement tests
# ---------------------------------------------------------------------------

class TestControlCenterHeartbeat:
    def test_record_heartbeat_known_bot(self):
        cc = ControlCenter()
        cc.register_bot("aff", AffiliateBot(tier=Tier.FREE))
        assert cc.record_heartbeat("aff") is True

    def test_record_heartbeat_unknown_bot(self):
        cc = ControlCenter()
        assert cc.record_heartbeat("ghost") is False

    def test_heartbeat_sets_timestamp(self):
        cc = ControlCenter()
        cc.register_bot("aff", AffiliateBot(tier=Tier.FREE))
        cc.record_heartbeat("aff")
        assert cc._bots["aff"]["last_heartbeat"] is not None

    def test_heartbeat_log_records_events(self):
        cc = ControlCenter()
        cc.register_bot("aff", AffiliateBot(tier=Tier.FREE))
        cc.record_heartbeat("aff")
        cc.record_heartbeat("aff")
        log = cc.get_heartbeat_log()
        assert len(log) == 2

    def test_heartbeat_revives_offline_bot(self):
        cc = ControlCenter()
        cc.register_bot("aff", AffiliateBot(tier=Tier.FREE))
        cc._bots["aff"]["status"] = "offline"
        cc.record_heartbeat("aff")
        assert cc._bots["aff"]["status"] != "offline"


class TestControlCenterRepoMonitoring:
    def test_register_repo(self):
        cc = ControlCenter()
        cc.register_repo("Dreamcobots", "ireanjordan24")
        repo = cc.get_repo_status("Dreamcobots")
        assert repo["name"] == "Dreamcobots"
        assert repo["owner"] == "ireanjordan24"

    def test_get_unknown_repo_returns_empty(self):
        cc = ControlCenter()
        assert cc.get_repo_status("ghost") == {}

    def test_update_repo_status_known_repo(self):
        cc = ControlCenter()
        cc.register_repo("Repo", "user")
        result = cc.update_repo_status("Repo", open_prs=3, open_issues=5)
        assert result is True
        repo = cc.get_repo_status("Repo")
        assert repo["open_prs"] == 3
        assert repo["open_issues"] == 5

    def test_update_repo_status_unknown_repo(self):
        cc = ControlCenter()
        assert cc.update_repo_status("ghost") is False

    def test_get_all_repo_status(self):
        cc = ControlCenter()
        cc.register_repo("Repo", "user")
        all_status = cc.get_all_repo_status()
        assert "total_repos" in all_status
        assert "Repo" in all_status["repos"]

    def test_conflict_alerts_empty_when_no_conflicts(self):
        cc = ControlCenter()
        cc.register_repo("Repo", "user")
        assert cc.get_conflict_alerts() == []

    def test_conflict_alerts_includes_conflicted_repo(self):
        cc = ControlCenter()
        cc.register_repo("Repo", "user")
        cc.update_repo_status("Repo", conflicts_detected=True)
        alerts = cc.get_conflict_alerts()
        assert any(a["name"] == "Repo" for a in alerts)

    def test_conflict_alerts_includes_errored_bot(self):
        cc = ControlCenter()
        cc.register_bot("aff", AffiliateBot(tier=Tier.FREE))
        cc._bots["aff"]["status"] = "error"
        alerts = cc.get_conflict_alerts()
        assert any(a["name"] == "aff" for a in alerts)


class TestControlCenterDeploy:
    def test_deploy_bot_known(self):
        cc = ControlCenter()
        cc.register_bot("aff", AffiliateBot(tier=Tier.FREE))
        result = cc.deploy_bot("aff")
        assert result["status"] == "deploying"
        assert result["bot"] == "aff"

    def test_deploy_bot_unknown(self):
        cc = ControlCenter()
        result = cc.deploy_bot("ghost")
        assert result["status"] == "error"

    def test_deploy_all(self):
        cc = ControlCenter()
        cc.register_bot("aff", AffiliateBot(tier=Tier.FREE))
        results = cc.deploy_all()
        assert "aff" in results
        assert results["aff"]["status"] == "deploying"

    def test_deploy_log_records_events(self):
        cc = ControlCenter()
        cc.register_bot("aff", AffiliateBot(tier=Tier.FREE))
        cc.deploy_bot("aff")
        assert len(cc.get_deploy_log()) == 1

    def test_deploy_assigns_deploy_id(self):
        cc = ControlCenter()
        cc.register_bot("aff", AffiliateBot(tier=Tier.FREE))
        result = cc.deploy_bot("aff")
        assert "deploy_id" in result


class TestControlCenterOnboarding:
    def test_onboard_registers_bot(self):
        cc = ControlCenter()
        bot = AffiliateBot(tier=Tier.FREE)
        result = cc.onboard_bot("aff", bot, tier=Tier.FREE)
        assert result["bot"] == "aff"
        assert result["onboarding_status"] in ("ok", "error")

    def test_onboard_sets_tier(self):
        cc = ControlCenter()
        bot = AffiliateBot(tier=Tier.PRO)
        cc.onboard_bot("aff", bot, tier=Tier.PRO)
        assert cc._bots["aff"]["tier_assigned"] == "pro"

    def test_onboard_bot_appears_in_status(self):
        cc = ControlCenter()
        bot = AffiliateBot(tier=Tier.FREE)
        cc.onboard_bot("aff", bot, tier=Tier.FREE)
        status = cc.get_status()
        assert "aff" in status["bots"]

    def test_onboard_error_bot_captures_detail(self):
        class BrokenBot:
            tier = Tier.FREE
            def run(self):
                raise RuntimeError("broken!")

        cc = ControlCenter()
        result = cc.onboard_bot("broken", BrokenBot(), tier=Tier.FREE)
        assert result["onboarding_status"] == "error"
        assert "broken" in result.get("detail", "")
