"""
Tests for bots/lead_gen_bot/

Covers tiers, lead collection, scoring, Stripe payment flows, and CRM export.
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.lead_gen_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_LEAD_COLLECTION,
    FEATURE_STRIPE_PAYMENTS,
    FEATURE_LEAD_PACKAGES,
    FEATURE_CRM_EXPORT,
    FEATURE_LEAD_SCORING,
    FEATURE_WEBHOOK_NOTIFICATIONS,
)
from bots.lead_gen_bot.lead_gen_bot import (
    LeadGenBot,
    LeadGenBotTierError,
    LeadGenBotLimitError,
    Lead,
    LEAD_PACKAGES,
)
from bots.stripe_integration.stripe_client import StripeClient


# ===========================================================================
# Tier configuration
# ===========================================================================

class TestLeadGenBotTiers:
    def test_three_tiers(self):
        assert len(list_tiers()) == 3

    def test_free_price_zero(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_lead_limit(self):
        assert get_tier_config(Tier.FREE).max_leads_per_month == 50

    def test_pro_lead_limit(self):
        assert get_tier_config(Tier.PRO).max_leads_per_month == 2_000

    def test_enterprise_unlimited(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited() is True

    def test_free_has_lead_collection(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_LEAD_COLLECTION)

    def test_free_lacks_stripe_payments(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_STRIPE_PAYMENTS)

    def test_pro_has_stripe_payments(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_STRIPE_PAYMENTS)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feature in (
            FEATURE_LEAD_COLLECTION,
            FEATURE_STRIPE_PAYMENTS,
            FEATURE_LEAD_PACKAGES,
            FEATURE_CRM_EXPORT,
            FEATURE_LEAD_SCORING,
            FEATURE_WEBHOOK_NOTIFICATIONS,
        ):
            assert cfg.has_feature(feature)

    def test_upgrade_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade.tier == Tier.PRO

    def test_upgrade_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade.tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None


# ===========================================================================
# Instantiation
# ===========================================================================

class TestLeadGenBotInstantiation:
    def test_default_tier_free(self):
        bot = LeadGenBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = LeadGenBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = LeadGenBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = LeadGenBot()
        assert bot.config is not None

    def test_custom_stripe_client(self):
        client = StripeClient()
        bot = LeadGenBot(tier=Tier.PRO, stripe_client=client)
        assert bot._stripe is client


# ===========================================================================
# Lead collection
# ===========================================================================

class TestLeadCollection:
    def test_collect_lead_returns_lead(self):
        bot = LeadGenBot(tier=Tier.FREE)
        lead = bot.collect_lead(name="Alice", email="alice@example.com")
        assert isinstance(lead, Lead)

    def test_lead_has_id(self):
        bot = LeadGenBot(tier=Tier.FREE)
        lead = bot.collect_lead(name="Alice", email="alice@example.com")
        assert lead.lead_id.startswith("lead_")

    def test_lead_name_email_stored(self):
        bot = LeadGenBot(tier=Tier.FREE)
        lead = bot.collect_lead(name="Bob", email="bob@test.com")
        assert lead.name == "Bob"
        assert lead.email == "bob@test.com"

    def test_lead_optional_fields(self):
        bot = LeadGenBot(tier=Tier.FREE)
        lead = bot.collect_lead(
            name="Carol",
            email="carol@test.com",
            phone="555-1234",
            company="ACME",
            industry="real_estate",
            location="Austin, TX",
            interest="buy a house",
        )
        assert lead.phone == "555-1234"
        assert lead.company == "ACME"
        assert lead.industry == "real_estate"
        assert lead.location == "Austin, TX"
        assert lead.interest == "buy a house"

    def test_monthly_count_increments(self):
        bot = LeadGenBot(tier=Tier.FREE)
        bot.collect_lead(name="D", email="d@test.com")
        bot.collect_lead(name="E", email="e@test.com")
        assert bot.get_lead_count() == 2

    def test_reset_monthly_count(self):
        bot = LeadGenBot(tier=Tier.FREE)
        bot.collect_lead(name="F", email="f@test.com")
        bot.reset_monthly_count()
        assert bot.get_lead_count() == 0

    def test_free_tier_limit_enforced(self):
        bot = LeadGenBot(tier=Tier.FREE)
        bot._monthly_count = 50
        with pytest.raises(LeadGenBotLimitError):
            bot.collect_lead(name="Over", email="over@test.com")

    def test_enterprise_no_limit(self):
        bot = LeadGenBot(tier=Tier.ENTERPRISE)
        bot._monthly_count = 999_999
        lead = bot.collect_lead(name="Unlimited", email="u@test.com")
        assert isinstance(lead, Lead)


# ===========================================================================
# Lead scoring
# ===========================================================================

class TestLeadScoring:
    def test_pro_tier_scores_lead(self):
        bot = LeadGenBot(tier=Tier.PRO)
        lead = bot.collect_lead(
            name="Scored",
            email="s@test.com",
            phone="555-0000",
            company="Corp",
            location="NYC",
            interest="SaaS",
        )
        assert lead.score > 0

    def test_free_tier_score_is_zero(self):
        bot = LeadGenBot(tier=Tier.FREE)
        lead = bot.collect_lead(name="No Score", email="ns@test.com")
        assert lead.score == 0.0

    def test_max_score_100(self):
        bot = LeadGenBot(tier=Tier.PRO)
        lead = bot.collect_lead(
            name="Full",
            email="full@test.com",
            phone="555-9999",
            company="Maxco",
            location="LA",
            interest="Everything",
        )
        assert lead.score <= 100.0


# ===========================================================================
# Get leads / filtering
# ===========================================================================

class TestGetLeads:
    def test_returns_all_leads(self):
        bot = LeadGenBot(tier=Tier.FREE)
        bot.collect_lead(name="A", email="a@test.com")
        bot.collect_lead(name="B", email="b@test.com")
        assert len(bot.get_leads()) == 2

    def test_filter_by_industry(self):
        bot = LeadGenBot(tier=Tier.FREE)
        bot.collect_lead(name="RE", email="re@test.com", industry="real_estate")
        bot.collect_lead(name="Tech", email="tech@test.com", industry="technology")
        results = bot.get_leads(industry="real_estate")
        assert all(l.industry == "real_estate" for l in results)
        assert len(results) == 1

    def test_filter_paid_only(self):
        bot = LeadGenBot(tier=Tier.FREE)
        lead = bot.collect_lead(name="Paid", email="paid@test.com")
        bot.collect_lead(name="Free", email="free@test.com")
        lead.paid = True
        paid = bot.get_leads(paid_only=True)
        assert len(paid) == 1
        assert paid[0].paid is True


# ===========================================================================
# Stripe — lead packages
# ===========================================================================

class TestLeadPackages:
    def test_lead_packages_defined(self):
        assert len(LEAD_PACKAGES) >= 3

    def test_package_has_required_keys(self):
        for pkg in LEAD_PACKAGES.values():
            assert "name" in pkg
            assert "amount_cents" in pkg
            assert "currency" in pkg
            assert "lead_count" in pkg

    def test_create_package_checkout_requires_pro(self):
        bot = LeadGenBot(tier=Tier.FREE)
        with pytest.raises(LeadGenBotTierError):
            bot.create_lead_package_checkout(
                "starter_pack", "buyer@test.com",
                "https://s.co", "https://c.co"
            )

    def test_create_package_checkout_pro(self):
        bot = LeadGenBot(tier=Tier.PRO)
        result = bot.create_lead_package_checkout(
            "starter_pack", "buyer@test.com",
            "https://s.co", "https://c.co"
        )
        assert "session_id" in result
        assert "checkout_url" in result
        assert result["lead_count"] == LEAD_PACKAGES["starter_pack"]["lead_count"]

    def test_create_package_checkout_invalid_package(self):
        bot = LeadGenBot(tier=Tier.PRO)
        with pytest.raises(Exception):
            bot.create_lead_package_checkout(
                "nonexistent_pack", "buyer@test.com",
                "https://s.co", "https://c.co"
            )

    def test_create_payment_link_pro(self):
        bot = LeadGenBot(tier=Tier.PRO)
        result = bot.create_payment_link("growth_pack")
        assert "url" in result
        assert "link_id" in result

    def test_create_payment_link_requires_pro(self):
        bot = LeadGenBot(tier=Tier.FREE)
        with pytest.raises(LeadGenBotTierError):
            bot.create_payment_link("starter_pack")

    def test_mark_lead_paid(self):
        bot = LeadGenBot(tier=Tier.FREE)
        lead = bot.collect_lead(name="Alice", email="a@test.com")
        result = bot.mark_lead_paid(lead.lead_id, "pi_abc123")
        assert result is True
        assert lead.paid is True
        assert lead.payment_id == "pi_abc123"

    def test_mark_lead_paid_unknown_id(self):
        bot = LeadGenBot(tier=Tier.FREE)
        result = bot.mark_lead_paid("lead_nonexistent", "pi_xyz")
        assert result is False


# ===========================================================================
# CRM export
# ===========================================================================

class TestCRMExport:
    def test_export_requires_pro(self):
        bot = LeadGenBot(tier=Tier.FREE)
        with pytest.raises(LeadGenBotTierError):
            bot.export_leads()

    def test_export_json_pro(self):
        bot = LeadGenBot(tier=Tier.PRO)
        bot.collect_lead(name="A", email="a@test.com")
        result = bot.export_leads("json")
        assert result["format"] == "json"
        assert result["count"] == 1
        assert isinstance(result["leads"], list)

    def test_export_csv_pro(self):
        bot = LeadGenBot(tier=Tier.PRO)
        bot.collect_lead(name="B", email="b@test.com")
        result = bot.export_leads("csv")
        assert result["format"] == "csv"
        assert "content" in result

    def test_export_empty_csv(self):
        bot = LeadGenBot(tier=Tier.PRO)
        result = bot.export_leads("csv")
        assert result["count"] == 0


# ===========================================================================
# Tier description
# ===========================================================================

class TestDescribeTier:
    def test_returns_string(self):
        bot = LeadGenBot(tier=Tier.FREE)
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_contains_tier_name(self):
        bot = LeadGenBot(tier=Tier.PRO)
        assert "Pro" in bot.describe_tier()

    def test_contains_price(self):
        bot = LeadGenBot(tier=Tier.PRO)
        assert "49" in bot.describe_tier()

    def test_upgrade_shown_for_non_enterprise(self):
        bot = LeadGenBot(tier=Tier.FREE)
        assert "Upgrade" in bot.describe_tier()

    def test_no_upgrade_for_enterprise(self):
        bot = LeadGenBot(tier=Tier.ENTERPRISE)
        assert "Upgrade" not in bot.describe_tier()


# ===========================================================================
# Chat interface
# ===========================================================================

class TestLeadGenBotChat:
    def test_chat_returns_dict(self):
        bot = LeadGenBot()
        result = bot.chat("hello")
        assert isinstance(result, dict)

    def test_chat_has_response(self):
        bot = LeadGenBot()
        result = bot.chat("hello")
        assert "response" in result

    def test_chat_has_bot_name(self):
        bot = LeadGenBot()
        result = bot.chat("hello")
        assert result["bot_name"] == "lead_gen_bot"

    def test_chat_tier_query(self):
        bot = LeadGenBot(tier=Tier.PRO)
        result = bot.chat("what tier am I on?")
        assert "Pro" in result["response"]

    def test_chat_package_query(self):
        bot = LeadGenBot(tier=Tier.FREE)
        result = bot.chat("show me packages")
        assert "lead" in result["response"].lower() or "pack" in result["response"].lower()

    def test_chat_stripe_query_free(self):
        bot = LeadGenBot(tier=Tier.FREE)
        result = bot.chat("can I use Stripe?")
        assert "Pro" in result["response"] or "upgrade" in result["response"].lower()

    def test_chat_stripe_query_pro(self):
        bot = LeadGenBot(tier=Tier.PRO)
        result = bot.chat("stripe payments")
        assert "active" in result["response"].lower() or "stripe" in result["response"].lower()
