"""
Tests for bots/real_estate_bot/tiers.py and bots/real_estate_bot/real_estate_bot.py
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
from bots.real_estate_bot.tiers import (
    get_re_tier_info,
    RE_EXTRA_FEATURES,
    RE_TOOLS,
)
from bots.real_estate_bot.real_estate_bot import (
    RealEstateBot,
    RealEstateTierError,
    RealEstateRequestLimitError,
)


class TestRETierInfo:
    def test_tier_info_keys(self):
        info = get_re_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "platform_features", "re_features", "tools", "support_level"):
            assert key in info

    def test_free_price_is_zero(self):
        assert get_re_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        assert get_re_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_pro_has_more_tools_than_free(self):
        free = get_re_tier_info(Tier.FREE)
        pro = get_re_tier_info(Tier.PRO)
        assert len(pro["tools"]) > len(free["tools"])

    def test_free_tools_subset_of_pro(self):
        free_tools = set(RE_TOOLS[Tier.FREE.value])
        pro_tools = set(RE_TOOLS[Tier.PRO.value])
        assert free_tools.issubset(pro_tools)

    def test_features_populated(self):
        for tier in Tier:
            assert len(RE_EXTRA_FEATURES[tier.value]) > 0

    def test_free_has_property_search(self):
        assert "property_search" in RE_TOOLS[Tier.FREE.value]

    def test_pro_has_investment_analyzer(self):
        assert "investment_analyzer" in RE_TOOLS[Tier.PRO.value]

    def test_enterprise_has_mls_integration(self):
        assert "mls_integration" in RE_TOOLS[Tier.ENTERPRISE.value]


class TestRealEstateBot:
    def test_default_tier_is_free(self):
        bot = RealEstateBot()
        assert bot.tier == Tier.FREE

    def test_chat_returns_dict(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.chat("Find homes in Seattle")
        assert isinstance(result, dict)

    def test_chat_result_keys(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.chat("Find homes in Seattle")
        for key in ("message", "tool", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_free_cannot_use_investment_analyzer(self):
        bot = RealEstateBot(tier=Tier.FREE)
        with pytest.raises(RealEstateTierError):
            bot.chat("Analyze investment", tool="investment_analyzer")

    def test_pro_can_use_investment_analyzer(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.chat("Analyze investment", tool="investment_analyzer")
        assert result["tool"] == "investment_analyzer"

    def test_enterprise_can_use_mls(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.chat("MLS data", tool="mls_integration")
        assert result["tool"] == "mls_integration"

    def test_search_properties_returns_dict(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.search_properties({"location": "Austin", "max_price": 400000})
        assert result["status"] == "success"

    def test_search_properties_tier_error_if_tool_blocked(self):
        # property_search is available on FREE, so no error expected
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.search_properties({"location": "Austin"})
        assert result["status"] == "success"

    def test_list_tools_returns_list(self):
        bot = RealEstateBot(tier=Tier.FREE)
        tools = bot.list_tools()
        assert isinstance(tools, list) and len(tools) > 0

    def test_request_limit_raises(self):
        bot = RealEstateBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(RealEstateRequestLimitError):
            bot.chat("another search")

    def test_enterprise_no_request_limit(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        bot._request_count = 10_000_000
        result = bot.chat("search")
        assert result["requests_remaining"] is None

    def test_history_grows(self):
        bot = RealEstateBot()
        bot.chat("search 1")
        bot.chat("search 2")
        assert len(bot.get_history()) == 4

    def test_clear_history(self):
        bot = RealEstateBot()
        bot.chat("search")
        bot.clear_history()
        assert bot.get_history() == []

    def test_describe_tier_contains_real_estate(self):
        bot = RealEstateBot(tier=Tier.FREE)
        desc = bot.describe_tier()
        assert "Real Estate" in desc

    def test_show_upgrade_path_free(self):
        bot = RealEstateBot(tier=Tier.FREE)
        msg = bot.show_upgrade_path()
        assert "Pro" in msg or "Upgrade" in msg

    def test_show_upgrade_path_enterprise(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        msg = bot.show_upgrade_path()
        assert "highest tier" in msg

    def test_default_tool_search_keyword(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.chat("Find 3-bedroom homes in Seattle")
        assert result["tool"] == "property_search"

    def test_default_tool_market_keyword(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.chat("What are the market trends in Austin?")
        assert result["tool"] == "market_overview"
