"""
Tests for bots/real_estate_bot/tiers.py and bots/real_estate_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.real_estate_bot.tiers import REAL_ESTATE_FEATURES, get_real_estate_tier_info
from bots.real_estate_bot.bot import (
    RealEstateBot,
    RealEstateBotTierError,
    RealEstateBotRequestLimitError,
)


class TestRealEstateTierInfo:
    def test_free_tier_info_keys(self):
        info = get_real_estate_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_real_estate_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        info = get_real_estate_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in REAL_ESTATE_FEATURES
            assert len(REAL_ESTATE_FEATURES[tier.value]) > 0


class TestRealEstateBot:
    def test_default_tier_is_free(self):
        bot = RealEstateBot()
        assert bot.tier == Tier.FREE

    def test_find_deals_returns_expected_keys(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.find_deals({"location": "Austin, TX"})
        for key in ("deals", "count", "tier"):
            assert key in result

    def test_find_deals_tier_value(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.find_deals({"location": "Dallas"})
        assert result["tier"] == "free"

    def test_find_deals_returns_list(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.find_deals({"location": "Houston"})
        assert isinstance(result["deals"], list)

    def test_find_deals_count_matches_deals(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.find_deals({"location": "Denver"})
        assert result["count"] == len(result["deals"])

    def test_analyze_property_free_tier_raises(self):
        bot = RealEstateBot(tier=Tier.FREE)
        with pytest.raises(RealEstateBotTierError):
            bot.analyze_property("PROP-001")

    def test_analyze_property_pro_tier(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.analyze_property("PROP-001")
        assert "property_id" in result
        assert "tier" in result

    def test_calculate_roi_free_tier_raises(self):
        bot = RealEstateBot(tier=Tier.FREE)
        with pytest.raises(RealEstateBotTierError):
            bot.calculate_roi({"purchase_price": 200000, "monthly_rent": 1500})

    def test_calculate_roi_pro_tier(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.calculate_roi({"purchase_price": 200000, "monthly_rent": 1500})
        assert "roi" in result or "annual_return" in result or "tier" in result

    def test_request_counter_increments(self):
        bot = RealEstateBot(tier=Tier.FREE)
        bot.find_deals({"location": "Seattle"})
        bot.find_deals({"location": "Portland"})
        assert bot._request_count == 2

    def test_request_limit_exceeded(self):
        bot = RealEstateBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(RealEstateBotRequestLimitError):
            bot.find_deals({"location": "Miami"})

    def test_enterprise_no_request_limit(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        bot._request_count = 9999
        result = bot.find_deals({"location": "NYC"})
        assert "deals" in result

    def test_get_stats_buddy_integration(self):
        bot = RealEstateBot(tier=Tier.FREE)
        stats = bot.get_stats()
        assert stats["buddy_integration"] is True

    def test_get_stats_keys(self):
        bot = RealEstateBot(tier=Tier.PRO)
        stats = bot.get_stats()
        assert "tier" in stats
        assert "requests_used" in stats
