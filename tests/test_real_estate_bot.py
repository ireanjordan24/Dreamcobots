"""Tests for bots/real_estate_bot/tiers.py and bots/real_estate_bot/real_estate_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.real_estate_bot.real_estate_bot import (
    RealEstateBot,
    RealEstateBotTierError,
    MultiPlatformAcquisitionEngine,
    HouseFlipPipeline,
    GovernmentContractMatcher,
    OutreachBot,
    RevenueMatchingEngine,
    SALE_PLATFORMS,
)


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


# ============================================================
# Fixture helpers
# ============================================================

SAMPLE_DISTRESSED = {
    "id": "TEST001",
    "address": "123 Test St, Detroit MI",
    "price": 15000,
    "beds": 3,
    "baths": 1,
    "sqft": 1200,
    "type": "single_family",
    "status": "foreclosure",
    "platform": "zillow",
    "arv_estimate": 65000,
}

SAMPLE_MULTIFAMILY = {
    "id": "TEST002",
    "address": "456 Oak Ave, Milwaukee WI",
    "price": 29000,
    "beds": 5,
    "baths": 2,
    "sqft": 1800,
    "type": "multifamily",
    "status": "tax_deed",
    "platform": "county_tax_sale",
    "arv_estimate": 88000,
}


# ============================================================
# MultiPlatformAcquisitionEngine
# ============================================================

class TestMultiPlatformAcquisitionEngine:
    def test_search_all_platforms_returns_list(self):
        eng = MultiPlatformAcquisitionEngine(Tier.FREE)
        results = eng.search_all_platforms(50000)
        assert isinstance(results, list)

    def test_results_under_budget(self):
        eng = MultiPlatformAcquisitionEngine(Tier.FREE)
        budget = 30000
        results = eng.search_all_platforms(budget)
        for r in results:
            assert r["price"] <= budget

    def test_equity_spread_in_results(self):
        eng = MultiPlatformAcquisitionEngine(Tier.FREE)
        results = eng.search_all_platforms(100000)
        assert len(results) > 0
        for r in results:
            assert "equity_spread" in r
            assert "equity_pct" in r
            assert r["equity_spread"] == r["arv_estimate"] - r["price"]

    def test_sorted_by_equity_pct_desc(self):
        eng = MultiPlatformAcquisitionEngine(Tier.FREE)
        results = eng.search_all_platforms(100000)
        if len(results) >= 2:
            for i in range(len(results) - 1):
                assert results[i]["equity_pct"] >= results[i + 1]["equity_pct"]

    def test_search_single_platform_zillow(self):
        eng = MultiPlatformAcquisitionEngine(Tier.FREE)
        results = eng.search_platform("zillow", 50000)
        for r in results:
            assert r["platform"] == "zillow"
            assert r["price"] <= 50000

    def test_search_single_platform_unknown_returns_empty(self):
        eng = MultiPlatformAcquisitionEngine(Tier.FREE)
        assert eng.search_platform("unknown_platform", 100000) == []

    def test_find_distressed_only(self):
        eng = MultiPlatformAcquisitionEngine(Tier.FREE)
        results = eng.find_distressed_only(100000)
        distressed_statuses = {
            "foreclosure", "tax_sale", "tax_deed", "abandoned",
            "foreclosure_auction", "reo_auction",
        }
        for r in results:
            assert r["status"] in distressed_statuses

    def test_find_multifamily(self):
        eng = MultiPlatformAcquisitionEngine(Tier.FREE)
        results = eng.find_multifamily(200000)
        for r in results:
            assert r["type"] == "multifamily"

    def test_all_platforms_covered(self):
        eng = MultiPlatformAcquisitionEngine(Tier.FREE)
        assert set(eng.available_platforms) == {
            "zillow", "facebook_marketplace", "county_tax_sale", "auction_com", "realtor_com"
        }

    def test_zero_budget_returns_empty(self):
        eng = MultiPlatformAcquisitionEngine(Tier.FREE)
        results = eng.search_all_platforms(0)
        assert results == []

    def test_filter_by_type_and_status(self):
        eng = MultiPlatformAcquisitionEngine(Tier.FREE)
        results = eng.search_all_platforms(
            200000, property_types=["single_family"], statuses=["foreclosure"]
        )
        for r in results:
            assert r["type"] == "single_family"
            assert r["status"] == "foreclosure"


# ============================================================
# HouseFlipPipeline
# ============================================================

class TestHouseFlipPipeline:
    def test_add_property_returns_pipeline_entry(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        entry = pipe.add_property(SAMPLE_DISTRESSED)
        assert entry["stage"] == "identified"
        assert "pipeline_id" in entry

    def test_advance_stage(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        entry = pipe.add_property(SAMPLE_DISTRESSED)
        pid = entry["pipeline_id"]
        advanced = pipe.advance_stage(pid)
        assert advanced["stage"] == "under_contract"

    def test_advance_through_all_stages(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        entry = pipe.add_property(SAMPLE_DISTRESSED)
        pid = entry["pipeline_id"]
        stages = HouseFlipPipeline.FLIP_STAGES
        for expected in stages[1:]:
            result = pipe.advance_stage(pid)
            assert result["stage"] == expected

    def test_advance_unknown_id_returns_empty(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        assert pipe.advance_stage("FAKE-9999") == {}

    def test_estimate_renovation_cost_returns_dict(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        result = pipe.estimate_renovation_cost(SAMPLE_DISTRESSED)
        assert isinstance(result, dict)
        assert "estimated_renovation_cost" in result
        assert result["estimated_renovation_cost"] > 0

    def test_calculate_flip_profit_structure(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        result = pipe.calculate_flip_profit(SAMPLE_DISTRESSED, "zillow")
        for key in ("net_profit", "total_cost", "roi_pct", "arv", "sale_platform"):
            assert key in result

    def test_flip_profit_net_positive_for_good_deal(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        result = pipe.calculate_flip_profit(SAMPLE_DISTRESSED, "zillow")
        # equity_spread is large so net profit should be positive
        assert result["net_profit"] > 0

    def test_compare_sale_platforms_returns_all_platforms(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        results = pipe.compare_sale_platforms(SAMPLE_DISTRESSED)
        returned_platforms = [r["sale_platform"] for r in results]
        for p in SALE_PLATFORMS:
            assert p in returned_platforms

    def test_compare_sorted_by_net_profit_desc(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        results = pipe.compare_sale_platforms(SAMPLE_DISTRESSED)
        for i in range(len(results) - 1):
            assert results[i]["net_profit"] >= results[i + 1]["net_profit"]

    def test_get_pipeline(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        pipe.add_property(SAMPLE_DISTRESSED)
        pipe.add_property(SAMPLE_MULTIFAMILY)
        assert len(pipe.get_pipeline()) == 2

    def test_get_pipeline_by_stage(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        e1 = pipe.add_property(SAMPLE_DISTRESSED)
        pipe.add_property(SAMPLE_MULTIFAMILY)
        pipe.advance_stage(e1["pipeline_id"])
        identified = pipe.get_pipeline_by_stage("identified")
        under_contract = pipe.get_pipeline_by_stage("under_contract")
        assert len(identified) == 1
        assert len(under_contract) == 1

    def test_platform_fee_lowers_net_profit_for_auction(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        zillow_result = pipe.calculate_flip_profit(SAMPLE_DISTRESSED, "zillow")
        auction_result = pipe.calculate_flip_profit(SAMPLE_DISTRESSED, "auction_com")
        # auction_com has higher fee (2.5%) vs zillow (1.5%)
        assert auction_result["net_profit"] < zillow_result["net_profit"]

    def test_facebook_marketplace_zero_platform_fee(self):
        pipe = HouseFlipPipeline(Tier.PRO)
        result = pipe.calculate_flip_profit(SAMPLE_DISTRESSED, "facebook_marketplace")
        assert result["platform_fee"] == 0


# ============================================================
# GovernmentContractMatcher
# ============================================================

class TestGovernmentContractMatcher:
    def test_find_matching_programs_returns_list(self):
        matcher = GovernmentContractMatcher(Tier.ENTERPRISE)
        results = matcher.find_matching_programs(SAMPLE_DISTRESSED)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_matched_programs_have_required_keys(self):
        matcher = GovernmentContractMatcher(Tier.ENTERPRISE)
        results = matcher.find_matching_programs(SAMPLE_DISTRESSED)
        for p in results:
            for key in ("id", "name", "portal", "payment_per_person_monthly"):
                assert key in p

    def test_bed_filter_respected(self):
        matcher = GovernmentContractMatcher(Tier.ENTERPRISE)
        tiny_prop = {"beds": 1, "type": "condo"}
        results = matcher.find_matching_programs(tiny_prop)
        for p in results:
            assert p["min_beds"] <= 1

    def test_calculate_monthly_income_returns_dict(self):
        matcher = GovernmentContractMatcher(Tier.ENTERPRISE)
        programs = matcher.find_matching_programs(SAMPLE_DISTRESSED)
        result = matcher.calculate_monthly_income(SAMPLE_DISTRESSED, programs[0]["id"])
        assert "monthly_income" in result
        assert "annual_income" in result
        assert result["monthly_income"] > 0

    def test_monthly_income_scales_with_beds(self):
        matcher = GovernmentContractMatcher(Tier.ENTERPRISE)
        prop3 = {"beds": 3, "type": "single_family"}
        prop5 = {"beds": 5, "type": "single_family"}
        programs3 = matcher.find_matching_programs(prop3)
        programs5 = matcher.find_matching_programs(prop5)
        if programs3 and programs5:
            prog_id = programs3[0]["id"]
            inc3 = matcher.calculate_monthly_income(prop3, prog_id)
            inc5 = matcher.calculate_monthly_income(prop5, prog_id)
            assert inc5["monthly_income"] > inc3["monthly_income"]

    def test_unknown_program_id_returns_error(self):
        matcher = GovernmentContractMatcher(Tier.ENTERPRISE)
        result = matcher.calculate_monthly_income(SAMPLE_DISTRESSED, "FAKE999")
        assert "error" in result

    def test_find_grants_returns_list(self):
        matcher = GovernmentContractMatcher(Tier.ENTERPRISE)
        grants = matcher.find_grants(SAMPLE_DISTRESSED)
        assert isinstance(grants, list)

    def test_grants_have_grant_amount(self):
        matcher = GovernmentContractMatcher(Tier.ENTERPRISE)
        grants = matcher.find_grants(SAMPLE_DISTRESSED)
        for g in grants:
            assert g.get("grant_amount", 0) > 0

    def test_multifamily_matches_some_programs(self):
        matcher = GovernmentContractMatcher(Tier.ENTERPRISE)
        multi = matcher.find_matching_programs({"beds": 5, "type": "multifamily"})
        # multifamily 5-bed should match at least one program
        assert len(multi) >= 1
        for p in multi:
            assert "multifamily" in p["property_types"]


# ============================================================
# OutreachBot
# ============================================================

class TestOutreachBot:
    def test_generate_owner_outreach_returns_string(self):
        bot = OutreachBot(Tier.PRO)
        result = bot.generate_owner_outreach("123 Test St, Detroit MI")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_owner_outreach_contains_address(self):
        bot = OutreachBot(Tier.PRO)
        address = "123 Test St, Detroit MI"
        result = bot.generate_owner_outreach(address)
        assert address in result

    def test_owner_outreach_custom_name(self):
        bot = OutreachBot(Tier.PRO)
        result = bot.generate_owner_outreach(
            "123 Test St", owner_name="John Smith", your_name="Jane Doe"
        )
        assert "John Smith" in result
        assert "Jane Doe" in result

    def test_housing_dept_outreach_returns_string(self):
        bot = OutreachBot(Tier.PRO)
        result = bot.generate_housing_dept_outreach(
            address="456 Oak Ave",
            city="Milwaukee",
            beds=5,
        )
        assert isinstance(result, str)
        assert "Milwaukee" in result

    def test_housing_dept_outreach_contains_beds(self):
        bot = OutreachBot(Tier.PRO)
        result = bot.generate_housing_dept_outreach(
            address="456 Oak Ave", city="Milwaukee", beds=5
        )
        assert "5" in result

    def test_partnership_proposal_returns_string(self):
        bot = OutreachBot(Tier.PRO)
        result = bot.generate_partnership_proposal(
            partner_name="Milwaukee Housing Authority",
            city="Milwaukee",
            unit_count=5,
            monthly_per_unit=850,
        )
        assert isinstance(result, str)
        assert "Milwaukee Housing Authority" in result

    def test_partnership_proposal_total_monthly(self):
        bot = OutreachBot(Tier.PRO)
        result = bot.generate_partnership_proposal(
            partner_name="Test Org", city="Detroit", unit_count=4, monthly_per_unit=900
        )
        assert "3600" in result  # 4 * 900 = 3600


# ============================================================
# RevenueMatchingEngine
# ============================================================

class TestRevenueMatchingEngine:
    def _get_programs(self):
        matcher = GovernmentContractMatcher(Tier.ENTERPRISE)
        return matcher.find_matching_programs(SAMPLE_MULTIFAMILY)

    def test_match_returns_list(self):
        eng = RevenueMatchingEngine(Tier.ENTERPRISE)
        programs = self._get_programs()
        result = eng.match(SAMPLE_MULTIFAMILY, programs)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_match_sorted_by_monthly_income_desc(self):
        eng = RevenueMatchingEngine(Tier.ENTERPRISE)
        programs = self._get_programs()
        result = eng.match(SAMPLE_MULTIFAMILY, programs)
        for i in range(len(result) - 1):
            assert result[i]["monthly_income"] >= result[i + 1]["monthly_income"]

    def test_match_has_required_keys(self):
        eng = RevenueMatchingEngine(Tier.ENTERPRISE)
        programs = self._get_programs()
        matches = eng.match(SAMPLE_MULTIFAMILY, programs)
        for m in matches:
            for key in ("program_name", "monthly_income", "annual_income", "total_contract_value"):
                assert key in m

    def test_best_match_returns_highest_income(self):
        eng = RevenueMatchingEngine(Tier.ENTERPRISE)
        programs = self._get_programs()
        matches = eng.match(SAMPLE_MULTIFAMILY, programs)
        best = eng.best_match(SAMPLE_MULTIFAMILY, programs)
        assert best["monthly_income"] == matches[0]["monthly_income"]

    def test_best_match_empty_programs_returns_empty(self):
        eng = RevenueMatchingEngine(Tier.ENTERPRISE)
        result = eng.best_match(SAMPLE_DISTRESSED, [])
        assert result == {}

    def test_master_lease_analysis(self):
        eng = RevenueMatchingEngine(Tier.ENTERPRISE)
        result = eng.master_lease_analysis(SAMPLE_MULTIFAMILY, 1500, 900)
        assert "net_monthly_profit" in result
        assert result["model"] == "master_lease"
        assert result["requires_ownership"] is False
        # 5 beds * 900 = 4500 income - 1500 lease = 3000 net
        assert result["net_monthly_profit"] == 4500 - 1500

    def test_flip_and_convert_analysis(self):
        eng = RevenueMatchingEngine(Tier.ENTERPRISE)
        result = eng.flip_and_convert_analysis(SAMPLE_DISTRESSED, 800)
        assert "roi_pct" in result
        assert "payback_months" in result
        assert result["model"] == "flip_and_convert"
        assert result["requires_ownership"] is True

    def test_flip_and_convert_custom_renovation_cost(self):
        eng = RevenueMatchingEngine(Tier.ENTERPRISE)
        result = eng.flip_and_convert_analysis(SAMPLE_DISTRESSED, 800, renovation_cost=20000)
        expected_invested = SAMPLE_DISTRESSED["price"] + 20000
        assert result["total_invested"] == expected_invested

    def test_full_deal_summary_structure(self):
        eng = RevenueMatchingEngine(Tier.ENTERPRISE)
        programs = self._get_programs()
        result = eng.full_deal_summary(SAMPLE_MULTIFAMILY, programs, lease_monthly=1500)
        assert "best_program" in result
        assert "flip_and_convert" in result
        assert "master_lease" in result
        assert "top_programs" in result

    def test_full_deal_summary_no_lease(self):
        eng = RevenueMatchingEngine(Tier.ENTERPRISE)
        programs = self._get_programs()
        result = eng.full_deal_summary(SAMPLE_MULTIFAMILY, programs)
        assert result["master_lease"] is None


# ============================================================
# RealEstateBot — new convenience methods
# ============================================================

class TestRealEstateBotNewMethods:
    def test_engines_attached_on_init(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        assert hasattr(bot, "acquisition")
        assert hasattr(bot, "flip_pipeline")
        assert hasattr(bot, "gov_matcher")
        assert hasattr(bot, "outreach")
        assert hasattr(bot, "revenue_engine")

    def test_find_flippable_properties_free_tier(self):
        bot = RealEstateBot(tier=Tier.FREE)
        results = bot.find_flippable_properties(50000)
        assert isinstance(results, list)

    def test_find_flippable_properties_distressed_only(self):
        bot = RealEstateBot(tier=Tier.FREE)
        results = bot.find_flippable_properties(100000, distressed_only=True)
        distressed_statuses = {
            "foreclosure", "tax_sale", "tax_deed", "abandoned",
            "foreclosure_auction", "reo_auction",
        }
        for r in results:
            assert r["status"] in distressed_statuses

    def test_find_flippable_pro_includes_renovation_estimate(self):
        bot = RealEstateBot(tier=Tier.PRO)
        results = bot.find_flippable_properties(50000)
        for r in results:
            assert "estimated_renovation_cost" in r
            assert "renovation_label" in r

    def test_flip_on_platforms_free_raises(self):
        bot = RealEstateBot(tier=Tier.FREE)
        with pytest.raises(RealEstateBotTierError):
            bot.flip_on_platforms(SAMPLE_DISTRESSED)

    def test_flip_on_platforms_pro_returns_list(self):
        bot = RealEstateBot(tier=Tier.PRO)
        results = bot.flip_on_platforms(SAMPLE_DISTRESSED)
        assert isinstance(results, list)
        assert len(results) == len(SALE_PLATFORMS)

    def test_flip_on_platforms_enterprise_returns_list(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        results = bot.flip_on_platforms(SAMPLE_DISTRESSED)
        assert isinstance(results, list)

    def test_match_government_programs_non_enterprise_raises(self):
        for tier in (Tier.FREE, Tier.PRO):
            bot = RealEstateBot(tier=tier)
            with pytest.raises(RealEstateBotTierError):
                bot.match_government_programs(SAMPLE_DISTRESSED)

    def test_match_government_programs_enterprise(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.match_government_programs(SAMPLE_DISTRESSED)
        assert "matching_programs" in result
        assert "grants_available" in result
        assert "best_income_projection" in result
        assert "all_revenue_matches" in result

    def test_full_deal_analysis_free_tier(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.full_deal_analysis(SAMPLE_DISTRESSED)
        assert "renovation_estimate" in result
        assert "flip_platform_comparison" not in result
        assert "government_income" not in result

    def test_full_deal_analysis_pro_tier(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.full_deal_analysis(SAMPLE_DISTRESSED)
        assert "flip_platform_comparison" in result
        assert "government_income" not in result

    def test_full_deal_analysis_enterprise_tier(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.full_deal_analysis(SAMPLE_MULTIFAMILY, lease_monthly=1500)
        assert "flip_platform_comparison" in result
        assert "government_income" in result
        assert "grants" in result
