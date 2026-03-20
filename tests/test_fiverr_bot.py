"""
Tests for bots/fiverr_bot/fiverr_bot.py

Covers:
  1. Tiers
  2. Gig management (create, update, deactivate, list)
  3. Order management (receive, start, deliver, complete, cancel)
  4. Inbox automation & bulk messaging
  5. Review collection
  6. Pricing optimizer (rules-based + AI tier)
  7. Analytics & revenue summary
  8. CRM export
  9. Chat & process interfaces
  10. run() helper
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.fiverr_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_GIG_LISTING,
    FEATURE_ORDER_TRACKING,
    FEATURE_INBOX_AUTOMATION,
    FEATURE_REVIEW_COLLECTION,
    FEATURE_ANALYTICS,
    FEATURE_PRICING_OPTIMIZER,
    FEATURE_CRM_EXPORT,
    FEATURE_AI_PRICING,
    FEATURE_WHITE_LABEL,
)
from bots.fiverr_bot.fiverr_bot import (
    FiverrBot,
    FiverrBotError,
    FiverrBotTierError,
    GigCategory,
    OrderStatus,
)


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestFiverrBotTiers:
    def test_three_tiers(self):
        assert len(list_tiers()) == 3

    def test_free_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_gig_limit(self):
        assert get_tier_config(Tier.FREE).max_gigs == 5

    def test_pro_gig_limit(self):
        assert get_tier_config(Tier.PRO).max_gigs == 50

    def test_enterprise_unlimited_gigs(self):
        assert get_tier_config(Tier.ENTERPRISE).max_gigs is None
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_gigs() is True

    def test_free_has_gig_listing(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_GIG_LISTING)

    def test_free_lacks_inbox_automation(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_INBOX_AUTOMATION)

    def test_pro_has_inbox_automation(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_INBOX_AUTOMATION)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feat in [
            FEATURE_GIG_LISTING, FEATURE_ORDER_TRACKING, FEATURE_INBOX_AUTOMATION,
            FEATURE_REVIEW_COLLECTION, FEATURE_ANALYTICS, FEATURE_PRICING_OPTIMIZER,
            FEATURE_CRM_EXPORT, FEATURE_AI_PRICING, FEATURE_WHITE_LABEL,
        ]:
            assert cfg.has_feature(feat), f"Missing feature: {feat}"

    def test_upgrade_from_free_to_pro(self):
        next_tier = get_upgrade_path(Tier.FREE)
        assert next_tier.tier == Tier.PRO

    def test_upgrade_from_pro_to_enterprise(self):
        next_tier = get_upgrade_path(Tier.PRO)
        assert next_tier.tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None


# ===========================================================================
# 2. Gig management
# ===========================================================================

class TestGigManagement:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)

    def test_create_gig_returns_dict(self):
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        assert isinstance(gig, dict)
        assert "gig_id" in gig

    def test_create_gig_uses_template(self):
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        assert "data" in gig["title"].lower() or "entry" in gig["title"].lower()

    def test_create_gig_custom_title(self):
        gig = self.bot.create_gig(GigCategory.RESEARCH, title="Custom Research Gig")
        assert gig["title"] == "Custom Research Gig"

    def test_create_gig_custom_price(self):
        gig = self.bot.create_gig(GigCategory.CONTENT_WRITING, price_usd=99.0)
        assert gig["price_usd"] == 99.0

    def test_create_gig_increments_id(self):
        g1 = self.bot.create_gig(GigCategory.DATA_ENTRY)
        g2 = self.bot.create_gig(GigCategory.RESEARCH)
        assert g1["gig_id"] != g2["gig_id"]

    def test_create_gig_active_by_default(self):
        gig = self.bot.create_gig(GigCategory.SEO)
        assert gig["active"] is True

    def test_free_tier_gig_limit(self):
        bot = FiverrBot(tier=Tier.FREE)
        for cat in [GigCategory.DATA_ENTRY, GigCategory.RESEARCH,
                    GigCategory.CONTENT_WRITING, GigCategory.ANALYTICS,
                    GigCategory.SEO]:
            bot.create_gig(cat)
        with pytest.raises(FiverrBotTierError):
            bot.create_gig(GigCategory.SOCIAL_MEDIA)

    def test_update_gig_price(self):
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        updated = self.bot.update_gig_price(gig["gig_id"], 99.99)
        assert updated["price_usd"] == 99.99

    def test_deactivate_gig(self):
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        result = self.bot.deactivate_gig(gig["gig_id"])
        assert result["active"] is False

    def test_get_gigs_returns_list(self):
        self.bot.create_gig(GigCategory.DATA_ENTRY)
        self.bot.create_gig(GigCategory.RESEARCH)
        gigs = self.bot.get_gigs()
        assert len(gigs) == 2

    def test_get_gigs_active_only(self):
        g1 = self.bot.create_gig(GigCategory.DATA_ENTRY)
        g2 = self.bot.create_gig(GigCategory.RESEARCH)
        self.bot.deactivate_gig(g1["gig_id"])
        active = self.bot.get_gigs(active_only=True)
        assert len(active) == 1
        assert active[0]["gig_id"] == g2["gig_id"]

    def test_get_unknown_gig_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.update_gig_price("gig_9999", 10.0)

    def test_free_tier_cannot_use_analytics(self):
        bot = FiverrBot(tier=Tier.FREE)
        bot.create_gig(GigCategory.DATA_ENTRY)
        with pytest.raises(FiverrBotTierError):
            bot.get_analytics()


# ===========================================================================
# 3. Order management
# ===========================================================================

class TestOrderManagement:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        self.gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        self.gig_id = self.gig["gig_id"]

    def test_receive_order_returns_dict(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        assert isinstance(order, dict)
        assert "order_id" in order

    def test_receive_order_status_pending(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        assert order["status"] == OrderStatus.PENDING.value

    def test_receive_order_price_matches_gig(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        assert order["amount_usd"] == self.gig["price_usd"]

    def test_start_order_changes_status(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        started = self.bot.start_order(order["order_id"])
        assert started["status"] == OrderStatus.IN_PROGRESS.value

    def test_deliver_order(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        self.bot.start_order(order["order_id"])
        delivered = self.bot.deliver_order(order["order_id"], "Here is your file.")
        assert delivered["status"] == OrderStatus.DELIVERED.value
        assert delivered["deliverable"] == "Here is your file."

    def test_complete_order(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        self.bot.deliver_order(order["order_id"], "Done!")
        completed = self.bot.complete_order(order["order_id"])
        assert completed["status"] == OrderStatus.COMPLETED.value

    def test_complete_order_logs_revenue(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        self.bot.deliver_order(order["order_id"], "Done!")
        self.bot.complete_order(order["order_id"])
        rev = self.bot.get_revenue_summary()
        assert rev["total_revenue_usd"] > 0

    def test_cancel_order(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        cancelled = self.bot.cancel_order(order["order_id"])
        assert cancelled["status"] == OrderStatus.CANCELLED.value

    def test_get_orders_all(self):
        self.bot.receive_order(self.gig_id, "buyer1")
        self.bot.receive_order(self.gig_id, "buyer2")
        orders = self.bot.get_orders()
        assert len(orders) == 2

    def test_get_orders_filtered(self):
        o1 = self.bot.receive_order(self.gig_id, "buyer1")
        o2 = self.bot.receive_order(self.gig_id, "buyer2")
        self.bot.complete_order(o1["order_id"])
        completed = self.bot.get_orders(status=OrderStatus.COMPLETED)
        assert len(completed) == 1

    def test_get_unknown_order_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.start_order("ord_9999")


# ===========================================================================
# 4. Inbox automation & bulk messaging
# ===========================================================================

class TestInboxAutomation:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)

    def test_send_message(self):
        result = self.bot.send_message("buyer123", "Hello!")
        assert result["status"] == "sent"
        assert result["to"] == "buyer123"

    def test_inbox_records_message(self):
        self.bot.send_message("buyer1", "Hi!")
        self.bot.send_message("buyer2", "Hey!")
        assert len(self.bot.get_inbox()) == 2

    def test_auto_respond_inquiry(self):
        result = self.bot.auto_respond_inquiry("buyer123", "Can you help me?")
        assert result["status"] == "sent"
        assert "buyer123" in result["message"]

    def test_bulk_message(self):
        result = self.bot.bulk_message(["a", "b", "c"], "Promo!")
        assert result["recipients"] == 3
        assert len(result["messages"]) == 3

    def test_free_tier_cannot_send_message(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.send_message("buyer", "Hello")

    def test_free_tier_cannot_bulk_message(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.bulk_message(["a", "b"], "Hi")


# ===========================================================================
# 5. Review collection
# ===========================================================================

class TestReviewCollection:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        self.gig_id = gig["gig_id"]
        order = self.bot.receive_order(self.gig_id, "buyer123")
        self.order_id = order["order_id"]
        self.bot.deliver_order(self.order_id, "Done!")
        self.bot.complete_order(self.order_id)

    def test_request_review(self):
        result = self.bot.request_review(self.order_id)
        assert result["status"] == "sent"

    def test_record_review(self):
        review = self.bot.record_review(self.order_id, rating=5.0, comment="Great!")
        assert review["rating"] == 5.0
        assert review["comment"] == "Great!"

    def test_invalid_rating_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.record_review(self.order_id, rating=6.0)

    def test_rating_below_1_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.record_review(self.order_id, rating=0.5)

    def test_gig_rating_updated(self):
        self.bot.record_review(self.order_id, rating=4.5)
        gigs = self.bot.get_gigs()
        gig = next(g for g in gigs if g["gig_id"] == self.gig_id)
        assert gig["rating"] == 4.5
        assert gig["review_count"] == 1

    def test_get_reviews_all(self):
        self.bot.record_review(self.order_id, rating=4.0)
        assert len(self.bot.get_reviews()) == 1

    def test_get_reviews_by_gig(self):
        self.bot.record_review(self.order_id, rating=4.0)
        reviews = self.bot.get_reviews(gig_id=self.gig_id)
        assert len(reviews) == 1

    def test_request_review_on_non_completed_order_raises(self):
        gig = self.bot.create_gig(GigCategory.RESEARCH)
        order = self.bot.receive_order(gig["gig_id"], "buyer456")
        with pytest.raises(FiverrBotError):
            self.bot.request_review(order["order_id"])

    def test_free_tier_cannot_collect_reviews(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.record_review("ord_0001", rating=5.0)


# ===========================================================================
# 6. Pricing optimizer
# ===========================================================================

class TestPricingOptimizer:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        self.gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        self.gig_id = self.gig["gig_id"]

    def test_optimize_returns_dict(self):
        result = self.bot.optimize_price(self.gig_id)
        assert "optimized_price_usd" in result

    def test_optimize_includes_current_price(self):
        result = self.bot.optimize_price(self.gig_id)
        assert result["current_price_usd"] == self.gig["price_usd"]

    def test_optimize_method_rules_based(self):
        result = self.bot.optimize_price(self.gig_id)
        assert result["optimization_method"] == "rules-based"

    def test_enterprise_uses_ai_pricing(self):
        bot = FiverrBot(tier=Tier.ENTERPRISE)
        gig = bot.create_gig(GigCategory.DATA_ENTRY)
        result = bot.optimize_price(gig["gig_id"])
        assert result["optimization_method"] == "AI demand modeling"

    def test_free_tier_cannot_optimize_price(self):
        bot = FiverrBot(tier=Tier.FREE)
        gig = bot.create_gig(GigCategory.DATA_ENTRY)
        with pytest.raises(FiverrBotTierError):
            bot.optimize_price(gig["gig_id"])


# ===========================================================================
# 7. Analytics & revenue summary
# ===========================================================================

class TestAnalytics:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        gig = self.bot.create_gig(GigCategory.ANALYTICS)
        self.gig_id = gig["gig_id"]
        order = self.bot.receive_order(self.gig_id, "buyer_a")
        self.bot.deliver_order(order["order_id"], "Dashboard ready!")
        self.bot.complete_order(order["order_id"])

    def test_analytics_returns_dict(self):
        result = self.bot.get_analytics()
        assert isinstance(result, dict)

    def test_analytics_has_required_keys(self):
        result = self.bot.get_analytics()
        for key in ("total_gigs", "total_orders", "completed_orders",
                    "total_revenue_usd", "avg_rating", "conversion_rate_pct"):
            assert key in result, f"Missing key: {key}"

    def test_analytics_counts_correct(self):
        result = self.bot.get_analytics()
        assert result["total_gigs"] == 1
        assert result["completed_orders"] == 1

    def test_analytics_revenue_positive(self):
        result = self.bot.get_analytics()
        assert result["total_revenue_usd"] > 0

    def test_revenue_summary_structure(self):
        rev = self.bot.get_revenue_summary()
        assert "total_revenue_usd" in rev
        assert "completed_orders" in rev
        assert "by_gig" in rev
        assert "revenue_log" in rev

    def test_revenue_by_gig(self):
        rev = self.bot.get_revenue_summary()
        assert self.gig_id in rev["by_gig"]


# ===========================================================================
# 8. CRM export
# ===========================================================================

class TestCRMExport:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.ENTERPRISE)
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        order = self.bot.receive_order(gig["gig_id"], "buyer_crm")
        self.bot.deliver_order(order["order_id"], "Data done!")
        self.bot.complete_order(order["order_id"])

    def test_export_returns_dict(self):
        result = self.bot.export_to_crm("HubSpot")
        assert isinstance(result, dict)

    def test_export_crm_name(self):
        result = self.bot.export_to_crm("Salesforce")
        assert result["crm"] == "Salesforce"

    def test_export_record_count(self):
        result = self.bot.export_to_crm()
        assert result["records_exported"] >= 1

    def test_export_status_success(self):
        result = self.bot.export_to_crm()
        assert result["status"] == "success"

    def test_pro_tier_cannot_export_crm(self):
        bot = FiverrBot(tier=Tier.PRO)
        with pytest.raises(FiverrBotTierError):
            bot.export_to_crm()


# ===========================================================================
# 9. Chat & process interfaces
# ===========================================================================

class TestChatAndProcess:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)

    def test_chat_summary(self):
        result = self.bot.chat("show me the summary")
        assert "data" in result

    def test_chat_gigs(self):
        self.bot.create_gig(GigCategory.DATA_ENTRY)
        result = self.bot.chat("list my gigs")
        assert "data" in result

    def test_chat_orders(self):
        result = self.bot.chat("show orders")
        assert "data" in result

    def test_chat_revenue(self):
        result = self.bot.chat("revenue please")
        assert "data" in result

    def test_chat_unknown(self):
        result = self.bot.chat("something random XYZ")
        assert "message" in result

    def test_process_create_gig(self):
        result = self.bot.process({
            "action": "create_gig",
            "category": "data_entry",
            "price_usd": 20.0,
        })
        assert "gig_id" in result

    def test_process_receive_order(self):
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        result = self.bot.process({
            "action": "receive_order",
            "gig_id": gig["gig_id"],
            "buyer_username": "testbuyer",
        })
        assert "order_id" in result

    def test_process_get_analytics(self):
        result = self.bot.process({"action": "get_analytics"})
        assert "total_gigs" in result

    def test_process_default_returns_summary(self):
        result = self.bot.process({})
        assert "tier" in result


# ===========================================================================
# 10. run() helper
# ===========================================================================

class TestRunHelper:
    def test_run_returns_string(self):
        bot = FiverrBot(tier=Tier.FREE)
        result = bot.run()
        assert isinstance(result, str)

    def test_run_contains_tier(self):
        bot = FiverrBot(tier=Tier.PRO)
        result = bot.run()
        assert "pro" in result

    def test_run_contains_gig_count(self):
        bot = FiverrBot(tier=Tier.PRO)
        bot.create_gig(GigCategory.DATA_ENTRY)
        result = bot.run()
        assert "1 gig" in result

    def test_describe_tier(self):
        bot = FiverrBot(tier=Tier.PRO)
        output = bot.describe_tier()
        assert "Pro" in output
        assert "$49.00" in output
