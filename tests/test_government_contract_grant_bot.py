"""
Tests for the enhanced Government Contract & Grant Bot.
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier

# Use importlib to handle the hyphenated package name
import importlib.util
_bot_path = os.path.join(
    REPO_ROOT, 'bots', 'government-contract-grant-bot',
    'government_contract_grant_bot.py',
)
_spec = importlib.util.spec_from_file_location(
    "government_contract_grant_bot", _bot_path
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

GovernmentContractGrantBot = _mod.GovernmentContractGrantBot
GCGTierError = _mod.GCGTierError
GCGRequestLimitError = _mod.GCGRequestLimitError
GCG_TOOLS = _mod.GCG_TOOLS
GCG_EXTRA_FEATURES = _mod.GCG_EXTRA_FEATURES
get_gcg_tier_info = _mod.get_gcg_tier_info


class TestGCGTierInfo:
    def test_tier_info_keys(self):
        info = get_gcg_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "platform_features", "gcg_features", "tools", "support_level"):
            assert key in info

    def test_free_price_is_zero(self):
        assert get_gcg_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        assert get_gcg_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_pro_has_more_tools_than_free(self):
        free = get_gcg_tier_info(Tier.FREE)
        pro = get_gcg_tier_info(Tier.PRO)
        assert len(pro["tools"]) > len(free["tools"])

    def test_features_populated(self):
        for tier in Tier:
            assert len(GCG_EXTRA_FEATURES[tier.value]) > 0

    def test_free_has_opportunity_search(self):
        assert "opportunity_search" in GCG_TOOLS[Tier.FREE.value]

    def test_pro_has_sbir_grant_finder(self):
        assert "sbir_grant_finder" in GCG_TOOLS[Tier.PRO.value]

    def test_enterprise_has_pipeline_manager(self):
        assert "contract_pipeline_manager" in GCG_TOOLS[Tier.ENTERPRISE.value]


class TestGovernmentContractGrantBot:
    def test_default_tier_is_free(self):
        bot = GovernmentContractGrantBot()
        assert bot.tier == Tier.FREE

    def test_legacy_run_works(self, capsys):
        bot = GovernmentContractGrantBot()
        bot.run()
        captured = capsys.readouterr()
        assert "starting" in captured.out.lower()

    def test_chat_returns_dict(self):
        bot = GovernmentContractGrantBot(tier=Tier.FREE)
        result = bot.chat("Search for opportunities")
        assert isinstance(result, dict)

    def test_chat_result_keys(self):
        bot = GovernmentContractGrantBot(tier=Tier.FREE)
        result = bot.chat("Find grants")
        for key in ("message", "tool", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_free_cannot_use_sbir_finder(self):
        bot = GovernmentContractGrantBot(tier=Tier.FREE)
        with pytest.raises(GCGTierError):
            bot.chat("Find SBIR grants", tool="sbir_grant_finder")

    def test_pro_can_use_sbir_finder(self):
        bot = GovernmentContractGrantBot(tier=Tier.PRO)
        result = bot.chat("Find SBIR grants", tool="sbir_grant_finder")
        assert result["tool"] == "sbir_grant_finder"

    def test_enterprise_can_use_pipeline(self):
        bot = GovernmentContractGrantBot(tier=Tier.ENTERPRISE)
        result = bot.chat("Manage pipeline", tool="contract_pipeline_manager")
        assert result["tool"] == "contract_pipeline_manager"

    def test_search_opportunities_returns_dict(self):
        bot = GovernmentContractGrantBot(tier=Tier.FREE)
        result = bot.search_opportunities("AI research", agency="NSF")
        assert result["status"] == "success"

    def test_list_tools_returns_list(self):
        bot = GovernmentContractGrantBot(tier=Tier.FREE)
        tools = bot.list_tools()
        assert isinstance(tools, list) and len(tools) > 0

    def test_request_limit_raises(self):
        bot = GovernmentContractGrantBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(GCGRequestLimitError):
            bot.chat("another search")

    def test_enterprise_no_request_limit(self):
        bot = GovernmentContractGrantBot(tier=Tier.ENTERPRISE)
        bot._request_count = 10_000_000
        result = bot.chat("search")
        assert result["requests_remaining"] is None

    def test_history_grows(self):
        bot = GovernmentContractGrantBot()
        bot.chat("search 1")
        bot.chat("search 2")
        assert len(bot.get_history()) == 4

    def test_clear_history(self):
        bot = GovernmentContractGrantBot()
        bot.chat("search")
        bot.clear_history()
        assert bot.get_history() == []

    def test_describe_tier_contains_government(self):
        bot = GovernmentContractGrantBot(tier=Tier.FREE)
        desc = bot.describe_tier()
        assert "Government" in desc

    def test_show_upgrade_path_free(self):
        bot = GovernmentContractGrantBot(tier=Tier.FREE)
        msg = bot.show_upgrade_path()
        assert "Pro" in msg or "Upgrade" in msg

    def test_default_tool_sbir_keyword(self):
        bot = GovernmentContractGrantBot(tier=Tier.PRO)
        result = bot.chat("Find SBIR grants for my startup")
        assert result["tool"] == "sbir_grant_finder"

    def test_default_tool_grant_keyword(self):
        bot = GovernmentContractGrantBot(tier=Tier.FREE)
        result = bot.chat("What grants are available?")
        assert result["tool"] == "grant_browse"
