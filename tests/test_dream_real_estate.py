"""
Tests for bots/dream_real_estate/

Covers:
  1. Tiers
  2. Catalog loading
  3. Division Explorer (list_categories, list_bots, get_bot, search_bots, get_division_summary)
  4. Bot activation / deactivation
  5. Task execution hooks (all 20 categories)
  6. Monetization (get_monetization_options, get_bundle_options)
  7. Analytics dashboard
  8. Portfolio tools
  9. Enterprise reporting
  10. Tier enforcement
  11. Error handling
  12. BotRecord data model
  13. run() method
  14. describe_tier()
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.dream_real_estate.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_PRO_BOTS,
    FEATURE_ENTERPRISE_BOTS,
    FEATURE_DIVISION_EXPLORER,
    FEATURE_BOT_EXECUTOR,
    FEATURE_ANALYTICS_DASHBOARD,
    FEATURE_MONETIZATION,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_TASK_AUTOMATION,
    FEATURE_PORTFOLIO_TOOLS,
    FEATURE_ENTERPRISE_REPORTING,
)
from bots.dream_real_estate.dream_real_estate import (
    DreamRealEstate,
    DreamRealEstateTierError,
    DreamRealEstateBotNotFoundError,
    BotRecord,
    TaskResult,
    MonetizationOption,
    Bot,
)


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_tier_enum_values(self):
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_get_tier_config_pro(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.tier == Tier.PRO
        assert cfg.price_usd_monthly == 99.0
        assert cfg.max_active_bots == 10
        assert cfg.support_level == "email"

    def test_get_tier_config_enterprise(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.tier == Tier.ENTERPRISE
        assert cfg.price_usd_monthly == 499.0
        assert cfg.max_active_bots is None
        assert cfg.support_level == "dedicated"

    def test_enterprise_is_unlimited_bots(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_bots() is True

    def test_pro_is_not_unlimited_bots(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.is_unlimited_bots() is False

    def test_tier_config_has_feature_pro(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_PRO_BOTS) is True
        assert cfg.has_feature(FEATURE_ENTERPRISE_BOTS) is False

    def test_tier_config_has_feature_enterprise(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_ENTERPRISE_BOTS) is True
        assert cfg.has_feature(FEATURE_WHITE_LABEL) is True

    def test_get_upgrade_path_pro(self):
        assert get_upgrade_path(Tier.PRO) == Tier.ENTERPRISE

    def test_get_upgrade_path_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_list_tiers_returns_all(self):
        tiers = list_tiers()
        assert len(tiers) == 2

    def test_tier_catalogue_keys(self):
        assert Tier.PRO in TIER_CATALOGUE
        assert Tier.ENTERPRISE in TIER_CATALOGUE


# ===========================================================================
# 2. Catalog loading
# ===========================================================================

class TestCatalogLoading:
    def test_catalog_is_loaded(self):
        div = DreamRealEstate(tier=Tier.PRO)
        assert len(div._catalog) > 0

    def test_catalog_count(self):
        div = DreamRealEstate(tier=Tier.PRO)
        assert len(div._catalog) == 25

    def test_catalog_all_dream_real_estate(self):
        div = DreamRealEstate(tier=Tier.PRO)
        for bot in div._catalog:
            assert bot.division == "DreamRealEstate"

    def test_catalog_has_required_fields(self):
        div = DreamRealEstate(tier=Tier.PRO)
        for bot in div._catalog:
            assert bot.bot_id
            assert bot.bot_name
            assert bot.category
            assert bot.tier
            assert bot.description
            assert bot.pricing_type
            assert bot.audience
            assert bot.price
            assert isinstance(bot.features, list)

    def test_catalog_features_non_empty(self):
        div = DreamRealEstate(tier=Tier.PRO)
        for bot in div._catalog:
            assert len(bot.features) > 0


# ===========================================================================
# 3. BotRecord data model
# ===========================================================================

class TestBotRecord:
    def test_from_dict(self):
        data = {
            "division": "DreamRealEstate",
            "category": "Acquisition",
            "botName": "Test Bot",
            "botId": "test-bot",
            "tier": "Pro",
            "description": "A test bot.",
            "pricingType": "SaaS subscription",
            "audience": "Investors",
            "price": "$99/mo",
            "features": ["Feature A", "Feature B"],
        }
        bot = BotRecord.from_dict(data)
        assert bot.bot_id == "test-bot"
        assert bot.bot_name == "Test Bot"
        assert bot.category == "Acquisition"
        assert len(bot.features) == 2

    def test_to_dict_round_trip(self):
        data = {
            "division": "DreamRealEstate",
            "category": "Analytics",
            "botName": "Round Trip Bot",
            "botId": "round-trip",
            "tier": "Enterprise",
            "description": "Round trip test.",
            "pricingType": "Enterprise license",
            "audience": "Enterprises",
            "price": "$499/mo",
            "features": ["Feat 1"],
        }
        bot = BotRecord.from_dict(data)
        result = bot.to_dict()
        assert result["botId"] == "round-trip"
        assert result["botName"] == "Round Trip Bot"
        assert result["features"] == ["Feat 1"]

    def test_from_dict_empty_features(self):
        data = {
            "division": "DreamRealEstate",
            "category": "Tax",
            "botName": "No Features Bot",
            "botId": "no-features",
            "tier": "Pro",
            "description": "Bot with no features.",
            "pricingType": "SaaS subscription",
            "audience": "Investors",
            "price": "$99/mo",
        }
        bot = BotRecord.from_dict(data)
        assert bot.features == []


# ===========================================================================
# 4. Division Explorer
# ===========================================================================

class TestDivisionExplorer:
    def test_list_categories_returns_list(self):
        div = DreamRealEstate(tier=Tier.PRO)
        cats = div.list_categories()
        assert isinstance(cats, list)
        assert len(cats) > 0

    def test_list_categories_count(self):
        div = DreamRealEstate(tier=Tier.PRO)
        cats = div.list_categories()
        assert len(cats) == 20

    def test_list_categories_contains_acquisition(self):
        div = DreamRealEstate(tier=Tier.PRO)
        assert "Acquisition" in div.list_categories()

    def test_list_categories_contains_tax(self):
        div = DreamRealEstate(tier=Tier.PRO)
        assert "Tax" in div.list_categories()

    def test_list_bots_no_filter(self):
        div = DreamRealEstate(tier=Tier.PRO)
        bots = div.list_bots()
        assert len(bots) == 25

    def test_list_bots_by_category(self):
        div = DreamRealEstate(tier=Tier.PRO)
        bots = div.list_bots(category="Tax")
        assert len(bots) == 3

    def test_list_bots_by_tier_filter_pro(self):
        div = DreamRealEstate(tier=Tier.PRO)
        bots = div.list_bots(tier_filter="Pro")
        assert all(b.tier.lower() == "pro" for b in bots)
        assert len(bots) > 0

    def test_list_bots_by_tier_filter_enterprise(self):
        div = DreamRealEstate(tier=Tier.ENTERPRISE)
        bots = div.list_bots(tier_filter="Enterprise")
        assert all(b.tier.lower() == "enterprise" for b in bots)
        assert len(bots) > 0

    def test_list_bots_by_pricing_type(self):
        div = DreamRealEstate(tier=Tier.PRO)
        bots = div.list_bots(pricing_type_filter="SaaS")
        assert all("saas" in b.pricing_type.lower() for b in bots)

    def test_list_bots_case_insensitive_category(self):
        div = DreamRealEstate(tier=Tier.PRO)
        bots = div.list_bots(category="acquisition")
        assert len(bots) == 2

    def test_get_bot_existing(self):
        div = DreamRealEstate(tier=Tier.PRO)
        bot = div.get_bot("commercial-scanner")
        assert bot.bot_id == "commercial-scanner"
        assert bot.category == "Acquisition"

    def test_get_bot_not_found(self):
        div = DreamRealEstate(tier=Tier.PRO)
        with pytest.raises(DreamRealEstateBotNotFoundError):
            div.get_bot("nonexistent-bot-xyz")

    def test_search_bots_by_name(self):
        div = DreamRealEstate(tier=Tier.PRO)
        results = div.search_bots("valuation")
        assert any("valuation" in b.bot_name.lower() or "valuation" in b.description.lower()
                   or any("valuation" in f.lower() for f in b.features)
                   for b in results)

    def test_search_bots_by_feature(self):
        div = DreamRealEstate(tier=Tier.PRO)
        results = div.search_bots("cap rate")
        assert len(results) > 0

    def test_search_bots_no_match(self):
        div = DreamRealEstate(tier=Tier.PRO)
        results = div.search_bots("zxqwerty12345nonexistent")
        assert results == []

    def test_get_division_summary(self):
        div = DreamRealEstate(tier=Tier.PRO)
        summary = div.get_division_summary()
        assert summary["division"] == "DreamRealEstate"
        assert summary["total_bots"] == 25
        assert summary["total_categories"] == 20
        assert "tier_counts" in summary
        assert "categories" in summary

    def test_division_summary_tier_counts(self):
        div = DreamRealEstate(tier=Tier.PRO)
        summary = div.get_division_summary()
        assert summary["tier_counts"]["Pro"] > 0
        assert summary["tier_counts"]["Enterprise"] > 0
        assert summary["tier_counts"]["Pro"] + summary["tier_counts"]["Enterprise"] == 25


# ===========================================================================
# 5. Bot activation / deactivation
# ===========================================================================

class TestBotActivation:
    def test_activate_pro_bot_on_pro_tier(self):
        div = DreamRealEstate(tier=Tier.PRO)
        result = div.activate_bot("urban-heatmap")
        assert result["status"] == "active"
        assert result["bot_id"] == "urban-heatmap"

    def test_activate_enterprise_bot_on_enterprise_tier(self):
        div = DreamRealEstate(tier=Tier.ENTERPRISE)
        result = div.activate_bot("commercial-scanner")
        assert result["status"] == "active"

    def test_activate_enterprise_bot_on_pro_tier_raises(self):
        div = DreamRealEstate(tier=Tier.PRO)
        with pytest.raises(DreamRealEstateTierError):
            div.activate_bot("commercial-scanner")

    def test_activate_same_bot_twice_is_idempotent(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.activate_bot("urban-heatmap")
        div.activate_bot("urban-heatmap")
        assert div._active_bots.count("urban-heatmap") == 1

    def test_deactivate_bot(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.activate_bot("urban-heatmap")
        result = div.deactivate_bot("urban-heatmap")
        assert result["status"] == "inactive"
        assert "urban-heatmap" not in div._active_bots

    def test_deactivate_non_active_bot_does_not_raise(self):
        div = DreamRealEstate(tier=Tier.PRO)
        result = div.deactivate_bot("urban-heatmap")
        assert result["status"] == "inactive"

    def test_list_active_bots(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.activate_bot("urban-heatmap")
        div.activate_bot("property-liquidity")
        active = div.list_active_bots()
        assert "urban-heatmap" in active
        assert "property-liquidity" in active

    def test_pro_tier_bot_limit(self):
        div = DreamRealEstate(tier=Tier.PRO)
        pro_bots = [b.bot_id for b in div.list_bots(tier_filter="Pro")][:10]
        for bot_id in pro_bots:
            div.activate_bot(bot_id)
        extra_bot = [b.bot_id for b in div.list_bots(tier_filter="Pro")
                     if b.bot_id not in pro_bots][0]
        with pytest.raises(DreamRealEstateTierError):
            div.activate_bot(extra_bot)

    def test_enterprise_tier_no_bot_limit(self):
        div = DreamRealEstate(tier=Tier.ENTERPRISE)
        all_bot_ids = [b.bot_id for b in div._catalog]
        for bot_id in all_bot_ids:
            div.activate_bot(bot_id)
        assert len(div._active_bots) == 25


# ===========================================================================
# 6. Task execution — all categories
# ===========================================================================

class TestTaskExecution:
    def _exec(self, bot_id: str, task: str, params: dict = None, tier: Tier = Tier.PRO) -> TaskResult:
        div = DreamRealEstate(tier=tier)
        return div.execute_task(bot_id, task, params or {})

    def test_acquisition_task(self):
        result = self._exec("multifamily-acquisition", "scan_properties",
                            {"deals_found": 3}, tier=Tier.ENTERPRISE)
        assert result.status == "success"
        assert result.output["deals_found"] == 3

    def test_analytics_task(self):
        result = self._exec("urban-heatmap", "generate_heatmap", {"heatmap_data": {"city": "Austin"}})
        assert result.status == "success"

    def test_construction_task(self):
        result = self._exec("construction-budget", "track_budget", {"budget_variance": -5000.0})
        assert result.status == "success"
        assert result.output["budget_variance"] == -5000.0

    def test_crowdfunding_task(self):
        result = self._exec("re-crowdfunding", "rank_deals", {"ranked_deals": ["deal_1", "deal_2"]})
        assert result.status == "success"
        assert len(result.output["ranked_deals"]) == 2

    def test_distressed_assets_task(self):
        result = self._exec("distressed-asset", "scan_foreclosures", {"foreclosures_found": 10})
        assert result.status == "success"
        assert result.output["foreclosures_found"] == 10

    def test_energy_optimization_task(self):
        result = self._exec("energy-optimizer", "optimize_energy", {"energy_savings_pct": 15.0})
        assert result.status == "success"
        assert result.output["energy_savings_pct"] == 15.0

    def test_investor_reporting_task(self):
        result = self._exec("investor-reporting", "generate_report", {"irr": 18.5, "equity_multiple": 2.1})
        assert result.status == "success"
        assert result.output["irr"] == 18.5

    def test_land_banking_task(self):
        result = self._exec("land-bank", "score_parcels", {"parcels_scored": 50})
        assert result.status == "success"
        assert result.output["parcels_scored"] == 50

    def test_lease_analysis_task(self):
        result = self._exec("lease-optimizer", "optimize_rent", {"optimized_rent": 2500.0})
        assert result.status == "success"
        assert result.output["optimized_rent"] == 2500.0

    def test_lease_analyzer_task(self):
        result = self._exec("lease-analyzer", "abstract_lease", {"lease_abstractions": ["CAM", "NNN"]})
        assert result.status == "success"

    def test_portfolio_task(self):
        result = self._exec("re-rebalancer", "rebalance", {"allocation_drift": 5.2})
        assert result.status == "success"
        assert result.output["allocation_drift"] == 5.2

    def test_predictive_maintenance_task(self):
        result = self._exec("predictive-maintenance", "predict_failures",
                            {"failures_predicted": ["HVAC Unit 3"]})
        assert result.status == "success"

    def test_property_management_task(self):
        result = self._exec("property-mgmt", "collect_rent", {"rent_collected": 12000.0})
        assert result.status == "success"
        assert result.output["rent_collected"] == 12000.0

    def test_reit_analysis_task(self):
        result = self._exec("reit-predictor", "forecast_ffo", {"ffo_forecast": 3.25})
        assert result.status == "success"
        assert result.output["ffo_forecast"] == 3.25

    def test_residential_investing_task(self):
        result = self._exec("re-investment", "find_deals", {"deals_found": 7, "flip_roi_pct": 22.0})
        assert result.status == "success"
        assert result.output["flip_roi_pct"] == 22.0

    def test_risk_simulation_task(self):
        result = self._exec("property-risk-sim", "run_monte_carlo",
                            {"monte_carlo_runs": 10000, "portfolio_var": 0.08},
                            tier=Tier.ENTERPRISE)
        assert result.status == "success"
        assert result.output["monte_carlo_runs"] == 10000

    def test_smart_buildings_task(self):
        result = self._exec("smart-building", "optimize_hvac",
                            {"hvac_optimized": True, "energy_saved_kwh": 500.0},
                            tier=Tier.ENTERPRISE)
        assert result.status == "success"
        assert result.output["hvac_optimized"] is True

    def test_syndication_task(self):
        result = self._exec("syndication-mgr", "track_capital", {"capital_raised": 5000000.0})
        assert result.status == "success"
        assert result.output["capital_raised"] == 5000000.0

    def test_tax_task(self):
        result = self._exec("exchange-1031", "plan_exchange", {"tax_savings": 75000.0})
        assert result.status == "success"
        assert result.output["tax_savings"] == 75000.0

    def test_valuation_task(self):
        result = self._exec("property-value", "estimate_value",
                            {"estimated_value": 850000.0},
                            tier=Tier.ENTERPRISE)
        assert result.status == "success"
        assert result.output["estimated_value"] == 850000.0

    def test_zoning_compliance_task(self):
        result = self._exec("zoning-compliance", "check_compliance",
                            {"zoning_code": "R-2", "compliant": True})
        assert result.status == "success"
        assert result.output["compliant"] is True

    def test_task_logged(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.execute_task("urban-heatmap", "generate_heatmap")
        div.execute_task("property-liquidity", "forecast_liquidity")
        log = div.get_task_log()
        assert len(log) == 2

    def test_task_result_has_executed_at(self):
        div = DreamRealEstate(tier=Tier.PRO)
        result = div.execute_task("urban-heatmap", "generate_heatmap")
        assert result.executed_at

    def test_task_bot_not_found_raises(self):
        div = DreamRealEstate(tier=Tier.PRO)
        with pytest.raises(DreamRealEstateBotNotFoundError):
            div.execute_task("nonexistent-xyz", "some_task")

    def test_task_enterprise_bot_on_pro_raises(self):
        div = DreamRealEstate(tier=Tier.PRO)
        with pytest.raises(DreamRealEstateTierError):
            div.execute_task("commercial-scanner", "scan")

    def test_task_params_none_defaults_to_empty(self):
        div = DreamRealEstate(tier=Tier.PRO)
        result = div.execute_task("urban-heatmap", "generate_heatmap", None)
        assert result.status == "success"


# ===========================================================================
# 7. Monetization
# ===========================================================================

class TestMonetization:
    def test_get_monetization_options_pro_bot(self):
        div = DreamRealEstate(tier=Tier.PRO)
        options = div.get_monetization_options("urban-heatmap")
        assert len(options) >= 2
        actions = {o.action for o in options}
        assert "demo" in actions
        assert "subscribe" in actions

    def test_get_monetization_options_enterprise_bot(self):
        div = DreamRealEstate(tier=Tier.ENTERPRISE)
        options = div.get_monetization_options("commercial-scanner")
        actions = {o.action for o in options}
        assert "enterprise_license" in actions

    def test_monetization_option_has_payment_url(self):
        div = DreamRealEstate(tier=Tier.PRO)
        options = div.get_monetization_options("urban-heatmap")
        for opt in options:
            assert opt.payment_url.startswith("https://dreamco.io/pay/real-estate/")

    def test_monetization_option_has_price(self):
        div = DreamRealEstate(tier=Tier.PRO)
        options = div.get_monetization_options("urban-heatmap")
        for opt in options:
            assert opt.price

    def test_get_bundle_options(self):
        div = DreamRealEstate(tier=Tier.PRO)
        bundles = div.get_bundle_options()
        assert len(bundles) == 3

    def test_bundle_ids(self):
        div = DreamRealEstate(tier=Tier.PRO)
        bundles = div.get_bundle_options()
        ids = {b["bundle_id"] for b in bundles}
        assert "starter_plus" in ids
        assert "growth_plus" in ids
        assert "empire" in ids

    def test_bundle_has_required_fields(self):
        div = DreamRealEstate(tier=Tier.PRO)
        bundles = div.get_bundle_options()
        for bundle in bundles:
            assert "bundle_id" in bundle
            assert "name" in bundle
            assert "price" in bundle
            assert "bot_count" in bundle


# ===========================================================================
# 8. Analytics dashboard
# ===========================================================================

class TestAnalyticsDashboard:
    def test_get_analytics_summary(self):
        div = DreamRealEstate(tier=Tier.PRO)
        summary = div.get_analytics_summary()
        assert summary["division"] == "DreamRealEstate"
        assert summary["tier"] == "pro"
        assert summary["total_bots_in_catalog"] == 25

    def test_analytics_after_tasks(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.execute_task("urban-heatmap", "gen_heatmap")
        div.execute_task("property-liquidity", "forecast")
        summary = div.get_analytics_summary()
        assert summary["tasks_executed"] == 2
        assert summary["tasks_succeeded"] == 2
        assert summary["success_rate_pct"] == 100.0

    def test_analytics_active_bots(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.activate_bot("urban-heatmap")
        summary = div.get_analytics_summary()
        assert summary["active_bots"] == 1

    def test_analytics_no_tasks_zero_rate(self):
        div = DreamRealEstate(tier=Tier.PRO)
        summary = div.get_analytics_summary()
        assert summary["success_rate_pct"] == 0.0


# ===========================================================================
# 9. Portfolio tools
# ===========================================================================

class TestPortfolioTools:
    def test_get_portfolio_tools(self):
        div = DreamRealEstate(tier=Tier.PRO)
        tools = div.get_portfolio_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_portfolio_tools_contains_rebalancer(self):
        div = DreamRealEstate(tier=Tier.PRO)
        tools = div.get_portfolio_tools()
        assert any("Portfolio Rebalancer" in t or "Rebalancer" in t for t in tools)


# ===========================================================================
# 10. Enterprise reporting
# ===========================================================================

class TestEnterpriseReporting:
    def test_enterprise_report_enterprise_tier(self):
        div = DreamRealEstate(tier=Tier.ENTERPRISE)
        report = div.generate_enterprise_report()
        assert report["report_type"] == "enterprise_division_report"
        assert "division_summary" in report
        assert "analytics" in report
        assert report["tier"] == "enterprise"

    def test_enterprise_report_pro_tier_raises(self):
        div = DreamRealEstate(tier=Tier.PRO)
        with pytest.raises(DreamRealEstateTierError):
            div.generate_enterprise_report()

    def test_enterprise_report_has_timestamp(self):
        div = DreamRealEstate(tier=Tier.ENTERPRISE)
        report = div.generate_enterprise_report()
        assert "generated_at" in report
        assert report["generated_at"]


# ===========================================================================
# 11. Tier enforcement
# ===========================================================================

class TestTierEnforcement:
    def test_list_categories_requires_division_explorer(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamRealEstateTierError):
            div.list_categories()

    def test_analytics_requires_analytics_dashboard(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamRealEstateTierError):
            div.get_analytics_summary()

    def test_monetization_requires_feature(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamRealEstateTierError):
            div.get_monetization_options("urban-heatmap")

    def test_task_requires_task_automation(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamRealEstateTierError):
            div.execute_task("urban-heatmap", "task")

    def test_bundle_requires_monetization(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamRealEstateTierError):
            div.get_bundle_options()

    def test_portfolio_tools_requires_feature(self):
        div = DreamRealEstate(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamRealEstateTierError):
            div.get_portfolio_tools()


# ===========================================================================
# 12. run() and describe_tier()
# ===========================================================================

class TestRunAndDescribeTier:
    def test_run_returns_string(self):
        div = DreamRealEstate(tier=Tier.PRO)
        result = div.run()
        assert isinstance(result, str)
        assert "DreamRealEstate" in result

    def test_run_contains_tier(self):
        div = DreamRealEstate(tier=Tier.PRO)
        result = div.run()
        assert "pro" in result.lower()

    def test_run_contains_bot_count(self):
        div = DreamRealEstate(tier=Tier.PRO)
        result = div.run()
        assert "25" in result

    def test_describe_tier_pro(self):
        div = DreamRealEstate(tier=Tier.PRO)
        desc = div.describe_tier()
        assert "Pro" in desc
        assert "99.00" in desc
        assert "10" in desc

    def test_describe_tier_enterprise(self):
        div = DreamRealEstate(tier=Tier.ENTERPRISE)
        desc = div.describe_tier()
        assert "Enterprise" in desc
        assert "499.00" in desc
        assert "Unlimited" in desc

    def test_bot_alias(self):
        bot = Bot(tier=Tier.PRO)
        assert isinstance(bot, DreamRealEstate)


# ===========================================================================
# 13. Instantiation
# ===========================================================================

class TestInstantiation:
    def test_default_tier_is_pro(self):
        div = DreamRealEstate()
        assert div.tier == Tier.PRO

    def test_enterprise_tier(self):
        div = DreamRealEstate(tier=Tier.ENTERPRISE)
        assert div.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        div = DreamRealEstate()
        assert div.config is not None

    def test_custom_operator_name(self):
        div = DreamRealEstate(operator_name="Test Operator")
        assert div.operator_name == "Test Operator"


# ===========================================================================
# 14. Specific bots present in catalog
# ===========================================================================

class TestSpecificBots:
    EXPECTED_BOT_IDS = [
        "commercial-scanner",
        "multifamily-acquisition",
        "urban-heatmap",
        "property-liquidity",
        "construction-budget",
        "re-crowdfunding",
        "distressed-asset",
        "energy-optimizer",
        "investor-reporting",
        "land-bank",
        "lease-optimizer",
        "lease-analyzer",
        "re-rebalancer",
        "predictive-maintenance",
        "property-mgmt",
        "reit-predictor",
        "re-investment",
        "property-risk-sim",
        "smart-building",
        "syndication-mgr",
        "exchange-1031",
        "tax-lien",
        "tax-incentive-finder",
        "property-value",
        "zoning-compliance",
    ]

    def test_all_expected_bots_present(self):
        div = DreamRealEstate(tier=Tier.PRO)
        catalog_ids = {b.bot_id for b in div._catalog}
        for bot_id in self.EXPECTED_BOT_IDS:
            assert bot_id in catalog_ids, f"Bot '{bot_id}' not found in catalog"

    def test_all_categories_present(self):
        div = DreamRealEstate(tier=Tier.PRO)
        cats = set(div.list_categories())
        expected = {
            "Acquisition", "Analytics", "Construction", "Crowdfunding",
            "Distressed-Assets", "Energy-Optimization", "Investor-Reporting",
            "Land-Banking", "Lease-Analysis", "Portfolio", "Predictive-Maintenance",
            "Property-Management", "Reit-Analysis", "Residential-Investing",
            "Risk-Simulation", "Smart-Buildings", "Syndication", "Tax",
            "Valuation", "Zoning-Compliance",
        }
        assert cats == expected
