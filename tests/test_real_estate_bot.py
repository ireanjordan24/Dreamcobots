"""Tests for bots/real_estate_bot/tiers.py and bots/real_estate_bot/real_estate_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.real_estate_bot.real_estate_bot import RealEstateBot, RealEstateBotTierError


class TestRealEstateBotInstantiation:
    def test_default_tier_is_free(self):
        bot = RealEstateBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = RealEstateBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = RealEstateBot()
        assert bot.config is not None


class TestSearchDeals:
    def test_returns_list(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.search_deals("austin", 500000)
        assert isinstance(result, list)

    def test_results_under_budget(self):
        bot = RealEstateBot(tier=Tier.FREE)
        budget = 350000
        results = bot.search_deals("austin", budget)
        for prop in results:
            assert prop["price"] <= budget

    def test_free_location_limit_enforced(self):
        bot = RealEstateBot(tier=Tier.FREE)
        bot.search_deals("austin", 500000)
        with pytest.raises(RealEstateBotTierError):
            bot.search_deals("phoenix", 500000)

    def test_pro_allows_10_locations(self):
        bot = RealEstateBot(tier=Tier.PRO)
        locations = ["austin", "phoenix", "nashville", "denver", "tampa",
                     "charlotte", "atlanta", "dallas", "houston", "las_vegas"]
        for loc in locations:
            result = bot.search_deals(loc, 500000)
            assert isinstance(result, list)

    def test_enterprise_unlimited_locations(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        locations = ["austin", "phoenix", "nashville", "denver", "tampa",
                     "charlotte", "atlanta", "dallas", "houston", "las_vegas"]
        for loc in locations:
            result = bot.search_deals(loc, 500000)
            assert isinstance(result, list)


class TestEvaluateProperty:
    def test_returns_dict(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.evaluate_property("1204 Oak Blvd, Austin TX")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.evaluate_property("1204 Oak Blvd, Austin TX")
        for key in ("price", "cap_rate_pct", "monthly_cashflow_usd", "roi_estimate_pct"):
            assert key in result

    def test_enterprise_has_ai_valuation(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.evaluate_property("1204 Oak Blvd, Austin TX")
        assert "ai_valuation" in result


class TestEstimateROI:
    def test_returns_float(self):
        bot = RealEstateBot(tier=Tier.FREE)
        prop = {"price": 300000, "monthly_rent": 2200}
        result = bot.estimate_roi(prop)
        assert isinstance(result, float)

    def test_positive_roi_for_good_property(self):
        bot = RealEstateBot(tier=Tier.FREE)
        prop = {"price": 200000, "monthly_rent": 2000}
        result = bot.estimate_roi(prop)
        assert result > 0


class TestGetMarketTrends:
    def test_pro_returns_dict(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.get_market_trends("austin")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.get_market_trends("austin")
        for key in ("avg_price_change_pct_yoy", "inventory_months_supply", "avg_days_on_market"):
            assert key in result

    def test_free_tier_raises(self):
        bot = RealEstateBot(tier=Tier.FREE)
        with pytest.raises(RealEstateBotTierError):
            bot.get_market_trends("austin")

    def test_enterprise_has_predictive_analytics(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.get_market_trends("austin")
        assert "predictive_analytics" in result
