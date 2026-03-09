"""Tests for bots/control_center/control_center.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.control_center.control_center import ControlCenter
from bots.affiliate_bot.affiliate_bot import AffiliateBot
from bots.mining_bot.mining_bot import MiningBot
from bots.deal_finder_bot.deal_finder_bot import DealFinderBot
from bots.money_finder_bot.money_finder_bot import MoneyFinderBot


class TestControlCenterInstantiation:
    def test_instantiates(self):
        cc = ControlCenter()
        assert cc is not None

    def test_starts_with_no_bots(self):
        cc = ControlCenter()
        status = cc.get_status()
        assert status["total_bots"] == 0

    def test_starts_with_empty_income_log(self):
        cc = ControlCenter()
        summary = cc.get_income_summary()
        assert summary["total_income_usd"] == 0.0
        assert summary["entry_count"] == 0


class TestRegisterBot:
    def test_register_single_bot(self):
        cc = ControlCenter()
        bot = AffiliateBot(tier=Tier.FREE)
        cc.register_bot("affiliate", bot)
        status = cc.get_status()
        assert status["total_bots"] == 1
        assert "affiliate" in status["bots"]

    def test_register_multiple_bots(self):
        cc = ControlCenter()
        cc.register_bot("affiliate", AffiliateBot(tier=Tier.PRO))
        cc.register_bot("mining", MiningBot(tier=Tier.PRO))
        cc.register_bot("deal_finder", DealFinderBot(tier=Tier.FREE))
        status = cc.get_status()
        assert status["total_bots"] == 3

    def test_registered_bot_has_tier_info(self):
        cc = ControlCenter()
        cc.register_bot("affiliate", AffiliateBot(tier=Tier.PRO))
        status = cc.get_status()
        assert status["bots"]["affiliate"]["tier"] == "pro"


class TestGetStatus:
    def test_returns_dict(self):
        cc = ControlCenter()
        result = cc.get_status()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        cc = ControlCenter()
        result = cc.get_status()
        assert "total_bots" in result
        assert "bots" in result
        assert "timestamp" in result

    def test_bot_status_has_run_count(self):
        cc = ControlCenter()
        cc.register_bot("mining", MiningBot(tier=Tier.FREE))
        status = cc.get_status()
        assert "run_count" in status["bots"]["mining"]


class TestAddIncomeEntry:
    def test_adds_entry(self):
        cc = ControlCenter()
        cc.add_income_entry("affiliate", 125.50)
        summary = cc.get_income_summary()
        assert summary["entry_count"] == 1

    def test_total_accumulates(self):
        cc = ControlCenter()
        cc.add_income_entry("affiliate", 100.0)
        cc.add_income_entry("mining", 50.0)
        summary = cc.get_income_summary()
        assert abs(summary["total_income_usd"] - 150.0) < 0.01

    def test_by_source_tracking(self):
        cc = ControlCenter()
        cc.add_income_entry("affiliate", 100.0)
        cc.add_income_entry("affiliate", 50.0)
        cc.add_income_entry("mining", 75.0)
        summary = cc.get_income_summary()
        assert abs(summary["by_source"]["affiliate"] - 150.0) < 0.01
        assert abs(summary["by_source"]["mining"] - 75.0) < 0.01


class TestGetIncomeSummary:
    def test_returns_dict(self):
        cc = ControlCenter()
        result = cc.get_income_summary()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        cc = ControlCenter()
        result = cc.get_income_summary()
        for key in ("total_income_usd", "by_source", "entry_count", "income_log"):
            assert key in result

    def test_income_log_is_list(self):
        cc = ControlCenter()
        cc.add_income_entry("affiliate", 99.99)
        summary = cc.get_income_summary()
        assert isinstance(summary["income_log"], list)
        assert len(summary["income_log"]) == 1


class TestRunAll:
    def test_returns_dict(self):
        cc = ControlCenter()
        cc.register_bot("mining", MiningBot(tier=Tier.FREE))
        result = cc.run_all()
        assert isinstance(result, dict)

    def test_result_has_bot_key(self):
        cc = ControlCenter()
        cc.register_bot("mining", MiningBot(tier=Tier.FREE))
        result = cc.run_all()
        assert "mining" in result

    def test_run_increments_run_count(self):
        cc = ControlCenter()
        cc.register_bot("mining", MiningBot(tier=Tier.FREE))
        cc.run_all()
        cc.run_all()
        status = cc.get_status()
        assert status["bots"]["mining"]["run_count"] == 2

    def test_multiple_bots_all_run(self):
        cc = ControlCenter()
        cc.register_bot("affiliate", AffiliateBot(tier=Tier.FREE))
        cc.register_bot("mining", MiningBot(tier=Tier.FREE))
        cc.register_bot("money", MoneyFinderBot(tier=Tier.PRO))
        result = cc.run_all()
        assert len(result) == 3


class TestGetMonitoringDashboard:
    def test_returns_dict(self):
        cc = ControlCenter()
        result = cc.get_monitoring_dashboard()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        cc = ControlCenter()
        result = cc.get_monitoring_dashboard()
        for key in ("dashboard", "registered_bots", "bot_status", "income_summary", "health"):
            assert key in result

    def test_health_is_healthy_with_no_errors(self):
        cc = ControlCenter()
        cc.register_bot("affiliate", AffiliateBot(tier=Tier.FREE))
        dashboard = cc.get_monitoring_dashboard()
        assert dashboard["health"] == "healthy"

    def test_dashboard_reflects_income(self):
        cc = ControlCenter()
        cc.add_income_entry("affiliate", 200.0)
        dashboard = cc.get_monitoring_dashboard()
        assert dashboard["income_summary"]["total_income_usd"] == 200.0
