"""
Tests for bots/dream_sales_pro/

Covers:
  1. Tiers
  2. Catalog loading
  3. BotRecord data model
  4. Division Explorer (list_categories, list_bots, get_bot, search_bots, get_division_summary)
  5. Bot activation / deactivation
  6. Task execution hooks (all 9 categories)
  7. Monetization (get_monetization_options, get_bundle_options)
  8. Analytics dashboard
  9. Outreach tools
  10. Pipeline tools
  11. Enterprise reporting
  12. Tier enforcement
  13. run() and describe_tier()
  14. Specific bots present in catalog
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.dream_sales_pro.tiers import (
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
    FEATURE_OUTREACH_TOOLS,
    FEATURE_PIPELINE_TOOLS,
    FEATURE_ENTERPRISE_REPORTING,
)
from bots.dream_sales_pro.dream_sales_pro import (
    DreamSalesPro,
    DreamSalesProTierError,
    DreamSalesProBotNotFoundError,
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
        div = DreamSalesPro(tier=Tier.PRO)
        assert len(div._catalog) > 0

    def test_catalog_count(self):
        div = DreamSalesPro(tier=Tier.PRO)
        assert len(div._catalog) == 25

    def test_catalog_all_dream_sales_pro(self):
        div = DreamSalesPro(tier=Tier.PRO)
        for bot in div._catalog:
            assert bot.division == "DreamSalesPro"

    def test_catalog_has_required_fields(self):
        div = DreamSalesPro(tier=Tier.PRO)
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
        div = DreamSalesPro(tier=Tier.PRO)
        for bot in div._catalog:
            assert len(bot.features) > 0


# ===========================================================================
# 3. BotRecord data model
# ===========================================================================

class TestBotRecord:
    def test_from_dict(self):
        data = {
            "division": "DreamSalesPro",
            "category": "Leads",
            "botName": "Test Bot",
            "botId": "test-bot",
            "tier": "Pro",
            "description": "A test bot.",
            "pricingType": "SaaS subscription",
            "audience": "SDR teams",
            "price": "$199/mo",
            "features": ["Feature A", "Feature B"],
        }
        bot = BotRecord.from_dict(data)
        assert bot.bot_id == "test-bot"
        assert bot.bot_name == "Test Bot"
        assert bot.category == "Leads"
        assert len(bot.features) == 2

    def test_to_dict_round_trip(self):
        data = {
            "division": "DreamSalesPro",
            "category": "Pipeline",
            "botName": "Round Trip Bot",
            "botId": "round-trip",
            "tier": "Enterprise",
            "description": "Round trip test.",
            "pricingType": "Enterprise license",
            "audience": "Sales leaders",
            "price": "$499/mo",
            "features": ["Feat 1"],
        }
        bot = BotRecord.from_dict(data)
        result = bot.to_dict()
        assert result["botId"] == "round-trip"
        assert result["features"] == ["Feat 1"]

    def test_from_dict_empty_features(self):
        data = {
            "division": "DreamSalesPro",
            "category": "Analytics",
            "botName": "No Features Bot",
            "botId": "no-features",
            "tier": "Pro",
            "description": "Bot with no features.",
            "pricingType": "SaaS subscription",
            "audience": "Teams",
            "price": "$99/mo",
        }
        bot = BotRecord.from_dict(data)
        assert bot.features == []


# ===========================================================================
# 4. Division Explorer
# ===========================================================================

class TestDivisionExplorer:
    def test_list_categories_returns_list(self):
        div = DreamSalesPro(tier=Tier.PRO)
        cats = div.list_categories()
        assert isinstance(cats, list)
        assert len(cats) > 0

    def test_list_categories_count(self):
        div = DreamSalesPro(tier=Tier.PRO)
        cats = div.list_categories()
        assert len(cats) == 9

    def test_list_categories_contains_analytics(self):
        div = DreamSalesPro(tier=Tier.PRO)
        assert "Analytics" in div.list_categories()

    def test_list_categories_contains_pipeline(self):
        div = DreamSalesPro(tier=Tier.PRO)
        assert "Pipeline" in div.list_categories()

    def test_list_bots_no_filter(self):
        div = DreamSalesPro(tier=Tier.PRO)
        bots = div.list_bots()
        assert len(bots) == 25

    def test_list_bots_by_category_analytics(self):
        div = DreamSalesPro(tier=Tier.PRO)
        bots = div.list_bots(category="Analytics")
        assert len(bots) == 3

    def test_list_bots_by_category_billing(self):
        div = DreamSalesPro(tier=Tier.PRO)
        bots = div.list_bots(category="Billing")
        assert len(bots) == 3

    def test_list_bots_by_tier_filter_pro(self):
        div = DreamSalesPro(tier=Tier.PRO)
        bots = div.list_bots(tier_filter="Pro")
        assert all(b.tier.lower() == "pro" for b in bots)

    def test_list_bots_by_tier_filter_enterprise(self):
        div = DreamSalesPro(tier=Tier.ENTERPRISE)
        bots = div.list_bots(tier_filter="Enterprise")
        assert all(b.tier.lower() == "enterprise" for b in bots)

    def test_list_bots_by_pricing_type(self):
        div = DreamSalesPro(tier=Tier.PRO)
        bots = div.list_bots(pricing_type_filter="SaaS")
        assert all("saas" in b.pricing_type.lower() for b in bots)

    def test_list_bots_case_insensitive_category(self):
        div = DreamSalesPro(tier=Tier.PRO)
        bots = div.list_bots(category="leads")
        assert len(bots) == 3

    def test_get_bot_existing(self):
        div = DreamSalesPro(tier=Tier.PRO)
        bot = div.get_bot("campaign-roi")
        assert bot.bot_id == "campaign-roi"
        assert bot.category == "Analytics"

    def test_get_bot_not_found(self):
        div = DreamSalesPro(tier=Tier.PRO)
        with pytest.raises(DreamSalesProBotNotFoundError):
            div.get_bot("nonexistent-bot-xyz")

    def test_search_bots_by_name(self):
        div = DreamSalesPro(tier=Tier.PRO)
        results = div.search_bots("pipeline")
        assert len(results) > 0

    def test_search_bots_by_feature(self):
        div = DreamSalesPro(tier=Tier.PRO)
        results = div.search_bots("email verification")
        assert len(results) > 0

    def test_search_bots_no_match(self):
        div = DreamSalesPro(tier=Tier.PRO)
        results = div.search_bots("zxqwerty12345nonexistent")
        assert results == []

    def test_get_division_summary(self):
        div = DreamSalesPro(tier=Tier.PRO)
        summary = div.get_division_summary()
        assert summary["division"] == "DreamSalesPro"
        assert summary["total_bots"] == 25
        assert summary["total_categories"] == 9
        assert "tier_counts" in summary
        assert "categories" in summary

    def test_division_summary_tier_counts(self):
        div = DreamSalesPro(tier=Tier.PRO)
        summary = div.get_division_summary()
        total = summary["tier_counts"]["Pro"] + summary["tier_counts"]["Enterprise"]
        assert total == 25


# ===========================================================================
# 5. Bot activation / deactivation
# ===========================================================================

class TestBotActivation:
    def test_activate_pro_bot_on_pro_tier(self):
        div = DreamSalesPro(tier=Tier.PRO)
        result = div.activate_bot("campaign-roi")
        assert result["status"] == "active"
        assert result["bot_id"] == "campaign-roi"

    def test_activate_enterprise_bot_on_enterprise_tier(self):
        div = DreamSalesPro(tier=Tier.ENTERPRISE)
        result = div.activate_bot("market-intel")
        assert result["status"] == "active"

    def test_activate_enterprise_bot_on_pro_tier_raises(self):
        div = DreamSalesPro(tier=Tier.PRO)
        with pytest.raises(DreamSalesProTierError):
            div.activate_bot("market-intel")

    def test_activate_same_bot_twice_is_idempotent(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.activate_bot("campaign-roi")
        div.activate_bot("campaign-roi")
        assert div._active_bots.count("campaign-roi") == 1

    def test_deactivate_bot(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.activate_bot("campaign-roi")
        result = div.deactivate_bot("campaign-roi")
        assert result["status"] == "inactive"
        assert "campaign-roi" not in div._active_bots

    def test_deactivate_non_active_bot_does_not_raise(self):
        div = DreamSalesPro(tier=Tier.PRO)
        result = div.deactivate_bot("campaign-roi")
        assert result["status"] == "inactive"

    def test_list_active_bots(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.activate_bot("campaign-roi")
        div.activate_bot("lead-scraper")
        active = div.list_active_bots()
        assert "campaign-roi" in active
        assert "lead-scraper" in active

    def test_pro_tier_bot_limit(self):
        div = DreamSalesPro(tier=Tier.PRO)
        pro_bots = [b.bot_id for b in div.list_bots(tier_filter="Pro")][:10]
        for bot_id in pro_bots:
            div.activate_bot(bot_id)
        extra_bot = [b.bot_id for b in div.list_bots(tier_filter="Pro")
                     if b.bot_id not in pro_bots][0]
        with pytest.raises(DreamSalesProTierError):
            div.activate_bot(extra_bot)

    def test_enterprise_tier_no_bot_limit(self):
        div = DreamSalesPro(tier=Tier.ENTERPRISE)
        all_bot_ids = [b.bot_id for b in div._catalog]
        for bot_id in all_bot_ids:
            div.activate_bot(bot_id)
        assert len(div._active_bots) == 25


# ===========================================================================
# 6. Task execution — all categories
# ===========================================================================

class TestTaskExecution:
    def _exec(self, bot_id: str, task: str, params: dict = None, tier: Tier = Tier.PRO) -> TaskResult:
        div = DreamSalesPro(tier=tier)
        return div.execute_task(bot_id, task, params or {})

    def test_analytics_task(self):
        result = self._exec("campaign-roi", "calculate_roi", {"roi": 3.5})
        assert result.status == "success"
        assert result.output["roi"] == 3.5

    def test_autonomy_task(self):
        result = self._exec("campaign-controller", "set_autonomy",
                            {"autonomy_level": "semi-auto", "budget_cap": 5000.0})
        assert result.status == "success"
        assert result.output["autonomy_level"] == "semi-auto"

    def test_billing_task(self):
        result = self._exec("stripe-billing", "create_invoice",
                            {"invoice_created": True, "mrr": 10000.0})
        assert result.status == "success"
        assert result.output["invoice_created"] is True
        assert result.output["mrr"] == 10000.0

    def test_conversion_task(self):
        result = self._exec("funnel-optimizer", "analyze_funnel",
                            {"conversion_rate": 4.2})
        assert result.status == "success"
        assert result.output["conversion_rate"] == 4.2

    def test_intelligence_task(self):
        result = self._exec("objection-handler-ai", "handle_objection",
                            {"objections_handled": 5, "win_probability": 0.72})
        assert result.status == "success"
        assert result.output["win_probability"] == 0.72

    def test_leads_task(self):
        result = self._exec("lead-scraper", "scrape_leads",
                            {"leads_scraped": 250, "icp_matches": 80})
        assert result.status == "success"
        assert result.output["leads_scraped"] == 250
        assert result.output["icp_matches"] == 80

    def test_outreach_task(self):
        result = self._exec("cold-email-engine", "send_sequence",
                            {"emails_sent": 500, "open_rate": 0.28})
        assert result.status == "success"
        assert result.output["emails_sent"] == 500
        assert result.output["open_rate"] == 0.28

    def test_pipeline_task(self):
        result = self._exec("appointment-setter", "book_appointment",
                            {"appointments_booked": 12})
        assert result.status == "success"
        assert result.output["appointments_booked"] == 12

    def test_white_label_task(self):
        result = self._exec("white-label-saas", "onboard_client",
                            {"clients_onboarded": 3},
                            tier=Tier.ENTERPRISE)
        assert result.status == "success"
        assert result.output["clients_onboarded"] == 3

    def test_risk_monitor_enterprise_task(self):
        result = self._exec("risk-monitor", "check_compliance", {},
                            tier=Tier.ENTERPRISE)
        assert result.status == "success"

    def test_cro_engine_enterprise_task(self):
        result = self._exec("cro-engine", "run_ab_test", {"ab_test_winner": "variant_b"},
                            tier=Tier.ENTERPRISE)
        assert result.status == "success"
        assert result.output["ab_test_winner"] == "variant_b"

    def test_task_logged(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.execute_task("campaign-roi", "calc_roi")
        div.execute_task("lead-scraper", "scrape")
        assert len(div.get_task_log()) == 2

    def test_task_result_has_executed_at(self):
        div = DreamSalesPro(tier=Tier.PRO)
        result = div.execute_task("campaign-roi", "calc_roi")
        assert result.executed_at

    def test_task_bot_not_found_raises(self):
        div = DreamSalesPro(tier=Tier.PRO)
        with pytest.raises(DreamSalesProBotNotFoundError):
            div.execute_task("nonexistent-xyz", "some_task")

    def test_task_enterprise_bot_on_pro_raises(self):
        div = DreamSalesPro(tier=Tier.PRO)
        with pytest.raises(DreamSalesProTierError):
            div.execute_task("market-intel", "predict_trends")

    def test_task_params_none_defaults_to_empty(self):
        div = DreamSalesPro(tier=Tier.PRO)
        result = div.execute_task("campaign-roi", "calc_roi", None)
        assert result.status == "success"


# ===========================================================================
# 7. Monetization
# ===========================================================================

class TestMonetization:
    def test_get_monetization_options_pro_bot(self):
        div = DreamSalesPro(tier=Tier.PRO)
        options = div.get_monetization_options("campaign-roi")
        assert len(options) >= 2
        actions = {o.action for o in options}
        assert "demo" in actions
        assert "subscribe" in actions

    def test_get_monetization_options_enterprise_bot(self):
        div = DreamSalesPro(tier=Tier.ENTERPRISE)
        options = div.get_monetization_options("market-intel")
        actions = {o.action for o in options}
        assert "enterprise_license" in actions

    def test_monetization_option_has_payment_url(self):
        div = DreamSalesPro(tier=Tier.PRO)
        options = div.get_monetization_options("campaign-roi")
        for opt in options:
            assert opt.payment_url.startswith("https://dreamco.io/pay/sales-pro/")

    def test_monetization_option_has_price(self):
        div = DreamSalesPro(tier=Tier.PRO)
        options = div.get_monetization_options("campaign-roi")
        for opt in options:
            assert opt.price

    def test_get_bundle_options(self):
        div = DreamSalesPro(tier=Tier.PRO)
        bundles = div.get_bundle_options()
        assert len(bundles) == 3

    def test_bundle_ids(self):
        div = DreamSalesPro(tier=Tier.PRO)
        bundles = div.get_bundle_options()
        ids = {b["bundle_id"] for b in bundles}
        assert "starter_plus" in ids
        assert "growth_plus" in ids
        assert "empire" in ids

    def test_bundle_has_required_fields(self):
        div = DreamSalesPro(tier=Tier.PRO)
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
        div = DreamSalesPro(tier=Tier.PRO)
        summary = div.get_analytics_summary()
        assert summary["division"] == "DreamSalesPro"
        assert summary["tier"] == "pro"
        assert summary["total_bots_in_catalog"] == 25

    def test_analytics_after_tasks(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.execute_task("campaign-roi", "calc_roi")
        div.execute_task("lead-scraper", "scrape_leads")
        summary = div.get_analytics_summary()
        assert summary["tasks_executed"] == 2
        assert summary["tasks_succeeded"] == 2
        assert summary["success_rate_pct"] == 100.0

    def test_analytics_active_bots(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.activate_bot("campaign-roi")
        summary = div.get_analytics_summary()
        assert summary["active_bots"] == 1

    def test_analytics_no_tasks_zero_rate(self):
        div = DreamSalesPro(tier=Tier.PRO)
        summary = div.get_analytics_summary()
        assert summary["success_rate_pct"] == 0.0


# ===========================================================================
# 9. Outreach tools
# ===========================================================================

class TestOutreachTools:
    def test_get_outreach_tools(self):
        div = DreamSalesPro(tier=Tier.PRO)
        tools = div.get_outreach_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_outreach_tools_count(self):
        div = DreamSalesPro(tier=Tier.PRO)
        tools = div.get_outreach_tools()
        assert len(tools) == 3


# ===========================================================================
# 10. Pipeline tools
# ===========================================================================

class TestPipelineTools:
    def test_get_pipeline_tools(self):
        div = DreamSalesPro(tier=Tier.PRO)
        tools = div.get_pipeline_tools()
        assert isinstance(tools, list)
        assert len(tools) == 3

    def test_pipeline_tools_contains_appointment(self):
        div = DreamSalesPro(tier=Tier.PRO)
        tools = div.get_pipeline_tools()
        assert any("Appointment" in t for t in tools)


# ===========================================================================
# 11. Enterprise reporting
# ===========================================================================

class TestEnterpriseReporting:
    def test_enterprise_report_enterprise_tier(self):
        div = DreamSalesPro(tier=Tier.ENTERPRISE)
        report = div.generate_enterprise_report()
        assert report["report_type"] == "enterprise_division_report"
        assert "division_summary" in report
        assert report["tier"] == "enterprise"

    def test_enterprise_report_pro_tier_raises(self):
        div = DreamSalesPro(tier=Tier.PRO)
        with pytest.raises(DreamSalesProTierError):
            div.generate_enterprise_report()

    def test_enterprise_report_has_timestamp(self):
        div = DreamSalesPro(tier=Tier.ENTERPRISE)
        report = div.generate_enterprise_report()
        assert "generated_at" in report


# ===========================================================================
# 12. Tier enforcement
# ===========================================================================

class TestTierEnforcement:
    def test_list_categories_requires_division_explorer(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamSalesProTierError):
            div.list_categories()

    def test_analytics_requires_analytics_dashboard(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamSalesProTierError):
            div.get_analytics_summary()

    def test_monetization_requires_feature(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamSalesProTierError):
            div.get_monetization_options("campaign-roi")

    def test_task_requires_task_automation(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamSalesProTierError):
            div.execute_task("campaign-roi", "task")

    def test_bundle_requires_monetization(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamSalesProTierError):
            div.get_bundle_options()

    def test_outreach_requires_feature(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamSalesProTierError):
            div.get_outreach_tools()

    def test_pipeline_requires_feature(self):
        div = DreamSalesPro(tier=Tier.PRO)
        div.config.features = []
        with pytest.raises(DreamSalesProTierError):
            div.get_pipeline_tools()


# ===========================================================================
# 13. run() and describe_tier()
# ===========================================================================

class TestRunAndDescribeTier:
    def test_run_returns_string(self):
        div = DreamSalesPro(tier=Tier.PRO)
        result = div.run()
        assert isinstance(result, str)
        assert "DreamSalesPro" in result

    def test_run_contains_tier(self):
        div = DreamSalesPro(tier=Tier.PRO)
        result = div.run()
        assert "pro" in result.lower()

    def test_run_contains_bot_count(self):
        div = DreamSalesPro(tier=Tier.PRO)
        result = div.run()
        assert "25" in result

    def test_describe_tier_pro(self):
        div = DreamSalesPro(tier=Tier.PRO)
        desc = div.describe_tier()
        assert "Pro" in desc
        assert "99.00" in desc
        assert "10" in desc

    def test_describe_tier_enterprise(self):
        div = DreamSalesPro(tier=Tier.ENTERPRISE)
        desc = div.describe_tier()
        assert "Enterprise" in desc
        assert "499.00" in desc
        assert "Unlimited" in desc

    def test_bot_alias(self):
        bot = Bot(tier=Tier.PRO)
        assert isinstance(bot, DreamSalesPro)


# ===========================================================================
# 14. Instantiation
# ===========================================================================

class TestInstantiation:
    def test_default_tier_is_pro(self):
        div = DreamSalesPro()
        assert div.tier == Tier.PRO

    def test_enterprise_tier(self):
        div = DreamSalesPro(tier=Tier.ENTERPRISE)
        assert div.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        div = DreamSalesPro()
        assert div.config is not None

    def test_custom_operator_name(self):
        div = DreamSalesPro(operator_name="Test Operator")
        assert div.operator_name == "Test Operator"


# ===========================================================================
# 15. Specific bots present in catalog
# ===========================================================================

class TestSpecificBots:
    EXPECTED_BOT_IDS = [
        "campaign-roi",
        "market-intel",
        "predictive-analytics",
        "campaign-controller",
        "risk-monitor",
        "stripe-billing",
        "revenue-engine",
        "subscription-lifecycle",
        "landing-page-ai",
        "funnel-optimizer",
        "cro-engine",
        "objection-handler-ai",
        "pitch-craft-ai",
        "deal-intelligence",
        "lead-scraper",
        "icp-builder",
        "lead-validator",
        "cold-email-engine",
        "multi-channel-outreach",
        "deliverability-mgr",
        "appointment-setter",
        "pipeline-manager",
        "sales-performance",
        "white-label-saas",
        "client-success",
    ]

    def test_all_expected_bots_present(self):
        div = DreamSalesPro(tier=Tier.PRO)
        catalog_ids = {b.bot_id for b in div._catalog}
        for bot_id in self.EXPECTED_BOT_IDS:
            assert bot_id in catalog_ids, f"Bot '{bot_id}' not found in catalog"

    def test_all_categories_present(self):
        div = DreamSalesPro(tier=Tier.PRO)
        cats = set(div.list_categories())
        expected = {
            "Analytics", "Autonomy", "Billing", "Conversion",
            "Intelligence", "Leads", "Outreach", "Pipeline", "White-Label",
        }
        assert cats == expected
