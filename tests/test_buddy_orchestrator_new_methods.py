"""
Tests for new BuddyOrchestrator methods:
  - run_all_async()
  - analytics()
  - white_label_bot()
"""

from __future__ import annotations

import asyncio
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bots.buddy_orchestrator.buddy_orchestrator import (
    BuddyOrchestrator,
    OrchestratorError,
)


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def orch():
    return BuddyOrchestrator(github_repo="test-owner/test-repo")


# ===========================================================================
# run_all_async()
# ===========================================================================

class TestRunAllAsync:
    def test_run_all_async_returns_list(self, orch):
        orch.register_bot("bot_a")
        orch.register_bot("bot_b")
        results = asyncio.run(orch.run_all_async())
        assert isinstance(results, list)

    def test_run_all_async_result_count_matches_catalog(self, orch):
        orch.register_bot("bot_a")
        orch.register_bot("bot_b")
        orch.register_bot("bot_c")
        results = asyncio.run(orch.run_all_async())
        assert len(results) == 3

    def test_run_all_async_each_result_has_bot_id(self, orch):
        orch.register_bot("bot_x")
        results = asyncio.run(orch.run_all_async())
        assert all("bot_id" in r for r in results)

    def test_run_all_async_empty_catalog_returns_empty_list(self, orch):
        results = asyncio.run(orch.run_all_async())
        assert results == []

    def test_run_all_async_updates_run_history(self, orch):
        orch.register_bot("bot_a")
        orch.register_bot("bot_b")
        asyncio.run(orch.run_all_async())
        assert len(orch._run_history) >= 2

    def test_run_all_async_with_custom_runner(self, orch):
        orch.register_bot("bot_a")

        def my_runner(bot_id, task):
            return {"custom": True, "bot_id": bot_id}

        results = asyncio.run(orch.run_all_async(runner=my_runner))
        assert len(results) == 1
        assert results[0]["bot_id"] == "bot_a"


# ===========================================================================
# analytics()
# ===========================================================================

class TestAnalytics:
    def test_analytics_returns_dict(self, orch):
        assert isinstance(orch.analytics(), dict)

    def test_analytics_contains_required_keys(self, orch):
        a = orch.analytics()
        for key in ("mau", "api_cost_usd", "bot_uptime", "task_efficiency", "total_revenue_usd", "snapshot_at"):
            assert key in a

    def test_analytics_mau_default_zero(self, orch):
        assert orch.analytics()["mau"] == 0

    def test_analytics_mau_after_ingest(self, orch):
        orch.ingest("active_users", 1500)
        assert orch.analytics()["mau"] == 1500

    def test_analytics_api_cost_default_zero(self, orch):
        assert orch.analytics()["api_cost_usd"] == 0.0

    def test_analytics_api_cost_after_ingest(self, orch):
        orch.ingest("api_cost_usd", 42.5)
        assert orch.analytics()["api_cost_usd"] == 42.5

    def test_analytics_task_efficiency_zero_runs(self, orch):
        assert orch.analytics()["task_efficiency"] == 0.0

    def test_analytics_task_efficiency_all_success(self, orch):
        orch.register_bot("bot_a")
        orch.run_bot("bot_a")
        orch.run_bot("bot_a")
        a = orch.analytics()
        assert a["task_efficiency"] == 100.0

    def test_analytics_bot_uptime_empty_when_no_runs(self, orch):
        assert orch.analytics()["bot_uptime"] == {}

    def test_analytics_bot_uptime_populated_after_runs(self, orch):
        orch.register_bot("bot_a")
        orch.run_bot("bot_a")
        a = orch.analytics()
        assert "bot_a" in a["bot_uptime"]

    def test_analytics_total_revenue_usd(self, orch):
        orch.register_bot("bot_a")
        orch.run_bot("bot_a", revenue_usd=100.0)
        a = orch.analytics()
        assert a["total_revenue_usd"] == 100.0

    def test_analytics_snapshot_at_is_string(self, orch):
        a = orch.analytics()
        assert isinstance(a["snapshot_at"], str)

    def test_analytics_bot_uptime_100_when_all_success(self, orch):
        orch.register_bot("bot_a")
        orch.run_bot("bot_a")
        a = orch.analytics()
        assert a["bot_uptime"]["bot_a"] == 100.0


# ===========================================================================
# white_label_bot()
# ===========================================================================

class TestWhiteLabelBot:
    def test_white_label_returns_dict(self, orch):
        orch.register_bot("source_bot", price_usd=100.0)
        result = orch.white_label_bot("source_bot", "acme")
        assert isinstance(result, dict)

    def test_white_label_contains_required_keys(self, orch):
        orch.register_bot("source_bot", price_usd=100.0)
        result = orch.white_label_bot("source_bot", "acme")
        for key in ("white_label_id", "source_bot_id", "client_name", "price_usd", "display_name"):
            assert key in result

    def test_white_label_id_format(self, orch):
        orch.register_bot("source_bot")
        result = orch.white_label_bot("source_bot", "client_x")
        assert result["white_label_id"] == "client_x/source_bot"

    def test_white_label_source_bot_id(self, orch):
        orch.register_bot("source_bot")
        result = orch.white_label_bot("source_bot", "client_x")
        assert result["source_bot_id"] == "source_bot"

    def test_white_label_client_name(self, orch):
        orch.register_bot("source_bot")
        result = orch.white_label_bot("source_bot", "acme_corp")
        assert result["client_name"] == "acme_corp"

    def test_white_label_price_markup(self, orch):
        orch.register_bot("source_bot", price_usd=100.0)
        result = orch.white_label_bot("source_bot", "acme", markup_pct=20)
        assert result["price_usd"] == 120.0

    def test_white_label_no_markup(self, orch):
        orch.register_bot("source_bot", price_usd=50.0)
        result = orch.white_label_bot("source_bot", "acme")
        assert result["price_usd"] == 50.0

    def test_white_label_negative_markup_treated_as_zero(self, orch):
        orch.register_bot("source_bot", price_usd=50.0)
        result = orch.white_label_bot("source_bot", "acme", markup_pct=-10)
        assert result["price_usd"] == 50.0

    def test_white_label_custom_display_name(self, orch):
        orch.register_bot("source_bot")
        result = orch.white_label_bot("source_bot", "acme", custom_display_name="Acme AI Bot")
        assert result["display_name"] == "Acme AI Bot"

    def test_white_label_default_display_name(self, orch):
        orch.register_bot("source_bot", display_name="Source Bot")
        result = orch.white_label_bot("source_bot", "acme")
        assert result["display_name"] == "acme - Source Bot"

    def test_white_label_registers_in_catalog(self, orch):
        orch.register_bot("source_bot")
        orch.white_label_bot("source_bot", "acme")
        assert "acme/source_bot" in orch._catalog

    def test_white_label_unknown_bot_raises(self, orch):
        with pytest.raises(OrchestratorError):
            orch.white_label_bot("nonexistent_bot", "acme")

    def test_white_label_inherits_features(self, orch):
        orch.register_bot("source_bot", features=["chat", "analytics"])
        orch.white_label_bot("source_bot", "acme")
        wl_spec = orch._catalog["acme/source_bot"]
        assert "chat" in wl_spec.features
        assert "analytics" in wl_spec.features

    def test_white_label_inherits_tier(self, orch):
        orch.register_bot("source_bot", tier="ENTERPRISE")
        orch.white_label_bot("source_bot", "acme")
        wl_spec = orch._catalog["acme/source_bot"]
        assert wl_spec.tier == "ENTERPRISE"

    def test_white_label_can_be_activated(self, orch):
        orch.register_bot("source_bot")
        orch.white_label_bot("source_bot", "acme")
        orch.go_live("acme/source_bot")
        assert orch._catalog["acme/source_bot"].is_live is True
