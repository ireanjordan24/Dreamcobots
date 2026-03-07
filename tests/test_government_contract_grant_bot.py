"""
Tests for bots/government-contract-grant-bot/tiers.py
and bots/government-contract-grant-bot/government_contract_grant_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
GOV_BOT_DIR = os.path.join(REPO_ROOT, 'bots', 'government-contract-grant-bot')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, GOV_BOT_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from government_contract_grant_bot import (
    GovernmentContractGrantBot,
    GovBotTierError,
    GovBotRequestLimitError,
)


# -----------------------------------------------------------------------
# Tier info tests
# -----------------------------------------------------------------------

class TestGovBotTierInfo:
    def test_import_get_govbot_tier_info(self):
        import importlib
        spec = importlib.util.spec_from_file_location(
            "_gov_tiers", os.path.join(GOV_BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        info = mod.get_govbot_tier_info(Tier.FREE)
        assert "tier" in info
        assert "price_usd_monthly" in info
        assert "govbot_features" in info

    def test_free_price_zero(self):
        import importlib
        spec = importlib.util.spec_from_file_location(
            "_gov_tiers2", os.path.join(GOV_BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        info = mod.get_govbot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        import importlib
        spec = importlib.util.spec_from_file_location(
            "_gov_tiers3", os.path.join(GOV_BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        info = mod.get_govbot_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_all_tiers_have_features(self):
        import importlib
        spec = importlib.util.spec_from_file_location(
            "_gov_tiers4", os.path.join(GOV_BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for tier in Tier:
            info = mod.get_govbot_tier_info(tier)
            assert len(info["govbot_features"]) > 0


# -----------------------------------------------------------------------
# GovernmentContractGrantBot tests
# -----------------------------------------------------------------------

class TestGovernmentContractGrantBot:
    def test_default_tier_free(self):
        bot = GovernmentContractGrantBot()
        assert bot.tier == Tier.FREE

    def test_search_contracts_returns_dict(self):
        bot = GovernmentContractGrantBot()
        result = bot.search_contracts("IT services")
        assert isinstance(result, dict)

    def test_search_contracts_keys(self):
        bot = GovernmentContractGrantBot()
        result = bot.search_contracts("software")
        for key in ("query", "results", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_search_contracts_increments_count(self):
        bot = GovernmentContractGrantBot()
        bot.search_contracts("test")
        bot.search_contracts("test2")
        assert bot._request_count == 2

    def test_search_contracts_with_filters_pro(self):
        bot = GovernmentContractGrantBot(tier=Tier.PRO)
        result = bot.search_contracts("construction", filters={"agency": "DoD"})
        assert isinstance(result, dict)

    def test_search_contracts_with_filters_free_raises(self):
        bot = GovernmentContractGrantBot(tier=Tier.FREE)
        with pytest.raises(GovBotTierError):
            bot.search_contracts("construction", filters={"agency": "DoD"})

    def test_check_grant_eligibility_returns_dict(self):
        bot = GovernmentContractGrantBot()
        result = bot.check_grant_eligibility({"name": "ACME Corp", "size": "small"})
        assert isinstance(result, dict)

    def test_check_grant_eligibility_keys(self):
        bot = GovernmentContractGrantBot()
        result = bot.check_grant_eligibility({"name": "Test Org"})
        for key in ("eligible_grants", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_free_tier_request_limit(self):
        bot = GovernmentContractGrantBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(GovBotRequestLimitError):
            bot.search_contracts("test")

    def test_enterprise_no_request_limit(self):
        bot = GovernmentContractGrantBot(tier=Tier.ENTERPRISE)
        bot._request_count = 999_999
        result = bot.search_contracts("test")
        assert result["requests_remaining"] == "unlimited"

    def test_describe_tier_returns_string(self):
        bot = GovernmentContractGrantBot()
        output = bot.describe_tier()
        assert isinstance(output, str)
        assert "Free" in output

    def test_show_upgrade_path_from_free(self):
        bot = GovernmentContractGrantBot()
        output = bot.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise_no_upgrade(self):
        bot = GovernmentContractGrantBot(tier=Tier.ENTERPRISE)
        output = bot.show_upgrade_path()
        assert "top-tier" in output

    def test_tier_attribute(self):
        for tier in Tier:
            bot = GovernmentContractGrantBot(tier=tier)
            assert bot.tier == tier

    def test_draft_application_pro_only(self):
        bot_free = GovernmentContractGrantBot(tier=Tier.FREE)
        with pytest.raises(GovBotTierError):
            bot_free.draft_grant_application("GRANT-001", {"org": "Test"})

    def test_draft_application_pro_ok(self):
        bot = GovernmentContractGrantBot(tier=Tier.PRO)
        result = bot.draft_grant_application("GRANT-001", {"org": "Test Corp"})
        assert isinstance(result, dict)
        assert "draft" in result
