"""Tests for bots/stack_and_profit_bot/tiers.py and bots/stack_and_profit_bot/stack_and_profit_bot.py"""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, "models"))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.stack_and_profit_bot.stack_and_profit_bot import (
    StackAndProfitBot,
    StackAndProfitBotTierError,
    DealBot,
    PennyBot,
    ReceiptBot,
    FlipBot,
    CouponBot,
    ProfitEngine,
    RankingAI,
    AlertEngine,
    Deal,
)
from bots.stack_and_profit_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ---------------------------------------------------------------------------
# TestInstantiation
# ---------------------------------------------------------------------------

class TestInstantiation:
    def test_default_tier_is_free(self):
        bot = StackAndProfitBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = StackAndProfitBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = StackAndProfitBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = StackAndProfitBot()
        assert bot.config is not None

    def test_user_id_auto_generated(self):
        bot = StackAndProfitBot()
        assert bot.user_id is not None
        assert len(bot.user_id) > 0

    def test_user_id_respected_when_provided(self):
        bot = StackAndProfitBot(user_id="test-user-42")
        assert bot.user_id == "test-user-42"

    def test_sub_bots_instantiated(self):
        bot = StackAndProfitBot()
        assert isinstance(bot.deal_bot, DealBot)
        assert isinstance(bot.penny_bot, PennyBot)
        assert isinstance(bot.receipt_bot, ReceiptBot)
        assert isinstance(bot.flip_bot, FlipBot)
        assert isinstance(bot.coupon_bot, CouponBot)

    def test_ai_engines_instantiated(self):
        bot = StackAndProfitBot()
        assert isinstance(bot.profit_engine, ProfitEngine)
        assert isinstance(bot.ranking_ai, RankingAI)
        assert isinstance(bot.alert_engine, AlertEngine)


# ---------------------------------------------------------------------------
# TestTierDefinitions
# ---------------------------------------------------------------------------

class TestTierDefinitions:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_free_features_is_nonempty_list(self):
        assert isinstance(BOT_FEATURES[Tier.FREE.value], list)
        assert len(BOT_FEATURES[Tier.FREE.value]) >= 1

    def test_pro_features_more_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_enterprise_features_nonempty(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) >= 1

    def test_get_bot_tier_info_free(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert "price_usd_monthly" in info
        assert isinstance(info["features"], list)
        assert info["price_usd_monthly"] == 0.0

    def test_get_bot_tier_info_pro(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] > 0

    def test_get_bot_tier_info_enterprise(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["tier"] == "enterprise"
        assert info["price_usd_monthly"] > 0

    def test_support_level_present_all_tiers(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert "support_level" in info
            assert len(info["support_level"]) > 0

    def test_requests_per_month_present(self):
        info = get_bot_tier_info(Tier.FREE)
        assert "requests_per_month" in info


# ---------------------------------------------------------------------------
# TestDealBot
# ---------------------------------------------------------------------------

class TestDealBot:
    def test_returns_list(self):
        bot = DealBot(tier=Tier.FREE)
        result = bot.find_deals()
        assert isinstance(result, list)

    def test_all_items_are_deal_instances(self):
        bot = DealBot(tier=Tier.PRO)
        result = bot.find_deals()
        assert all(isinstance(d, Deal) for d in result)

    def test_free_daily_limit_respected(self):
        bot = DealBot(tier=Tier.FREE)
        result = bot.find_deals()
        assert len(result) <= 5

    def test_filter_by_store(self):
        bot = DealBot(tier=Tier.PRO)
        result = bot.find_deals(store="Amazon")
        assert all(d.store == "Amazon" for d in result)
        assert len(result) > 0

    def test_filter_by_category(self):
        bot = DealBot(tier=Tier.PRO)
        result = bot.find_deals(category="electronics")
        assert all(d.category == "electronics" for d in result)

    def test_unknown_store_returns_empty(self):
        bot = DealBot(tier=Tier.PRO)
        result = bot.find_deals(store="NonExistentStore")
        assert result == []

    def test_deal_fields_present(self):
        bot = DealBot(tier=Tier.PRO)
        result = bot.find_deals(store="Amazon")
        for deal in result:
            assert deal.deal_id
            assert deal.title
            assert deal.store == "Amazon"
            assert deal.original_price > 0
            assert deal.sale_price > 0
            assert deal.sale_price < deal.original_price

    def test_affiliate_commission_positive(self):
        bot = DealBot(tier=Tier.FREE)
        deal = Deal("T01", "Test Item", "Amazon", 100.0, 60.0, "electronics")
        commission = bot.get_affiliate_commission(deal)
        assert commission > 0

    def test_affiliate_commission_based_on_sale_price(self):
        bot = DealBot(tier=Tier.FREE)
        deal = Deal("T02", "Test Item", "Amazon", 100.0, 60.0, "electronics")
        commission = bot.get_affiliate_commission(deal)
        assert commission <= 60.0 * 0.15

    def test_deal_to_dict(self):
        deal = Deal("D01", "Widget", "Amazon", 50.0, 30.0, "home", "CODE10", 5.0)
        d = deal.to_dict()
        assert d["deal_id"] == "D01"
        assert d["title"] == "Widget"
        assert d["store"] == "Amazon"
        assert d["original_price"] == 50.0
        assert d["sale_price"] == 30.0
        assert d["coupon_code"] == "CODE10"
        assert d["cashback_pct"] == 5.0
        assert d["category"] == "home"

    def test_pro_gets_more_deals_than_free(self):
        free_bot = DealBot(tier=Tier.FREE)
        pro_bot = DealBot(tier=Tier.PRO)
        free_result = free_bot.find_deals()
        pro_result = pro_bot.find_deals()
        assert len(pro_result) >= len(free_result)


# ---------------------------------------------------------------------------
# TestPennyBot
# ---------------------------------------------------------------------------

class TestPennyBot:
    def test_free_tier_raises(self):
        bot = PennyBot(tier=Tier.FREE)
        with pytest.raises(StackAndProfitBotTierError):
            bot.find_penny_deals()

    def test_pro_tier_allowed(self):
        bot = PennyBot(tier=Tier.PRO)
        result = bot.find_penny_deals()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_enterprise_tier_allowed(self):
        bot = PennyBot(tier=Tier.ENTERPRISE)
        result = bot.find_penny_deals()
        assert isinstance(result, list)

    def test_penny_deals_have_profit_field(self):
        bot = PennyBot(tier=Tier.PRO)
        result = bot.find_penny_deals()
        for item in result:
            assert "profit" in item
            assert item["profit"] >= 0

    def test_penny_deals_price_range(self):
        bot = PennyBot(tier=Tier.PRO)
        result = bot.find_penny_deals()
        for item in result:
            assert item["price"] <= 1.00

    def test_filter_by_store(self):
        bot = PennyBot(tier=Tier.PRO)
        result = bot.find_penny_deals(store="Walmart")
        assert all(item["store"] == "Walmart" for item in result)

    def test_estimate_resale_profit_free_raises(self):
        bot = PennyBot(tier=Tier.FREE)
        with pytest.raises(StackAndProfitBotTierError):
            bot.estimate_resale_profit({"price": 0.01, "resale_value": 5.0})

    def test_estimate_resale_profit_pro(self):
        bot = PennyBot(tier=Tier.PRO)
        profit = bot.estimate_resale_profit({"price": 0.01, "resale_value": 5.0})
        assert round(profit, 2) == 4.99


# ---------------------------------------------------------------------------
# TestReceiptBot
# ---------------------------------------------------------------------------

class TestReceiptBot:
    def test_upload_returns_dict(self):
        bot = ReceiptBot(tier=Tier.FREE)
        result = bot.upload_receipt("Walmart", 50.0)
        assert isinstance(result, dict)

    def test_result_has_total_cashback(self):
        bot = ReceiptBot(tier=Tier.FREE)
        result = bot.upload_receipt("Target", 100.0)
        assert "total_cashback" in result
        assert result["total_cashback"] > 0

    def test_free_only_one_cashback_app(self):
        bot = ReceiptBot(tier=Tier.FREE)
        result = bot.upload_receipt("Amazon", 80.0)
        assert len(result["cashback_by_app"]) == 1

    def test_pro_stacks_multiple_apps(self):
        bot = ReceiptBot(tier=Tier.PRO)
        result = bot.upload_receipt("Amazon", 80.0)
        assert len(result["cashback_by_app"]) > 1

    def test_free_daily_limit_enforced(self):
        bot = ReceiptBot(tier=Tier.FREE)
        bot.upload_receipt("Walmart", 10.0)
        bot.upload_receipt("Target", 10.0)
        bot.upload_receipt("Amazon", 10.0)
        with pytest.raises(StackAndProfitBotTierError):
            bot.upload_receipt("Best Buy", 10.0)

    def test_pro_no_daily_limit(self):
        bot = ReceiptBot(tier=Tier.PRO)
        for _ in range(10):
            result = bot.upload_receipt("Walmart", 20.0)
        assert result["total_cashback"] > 0

    def test_calculate_total_cashback(self):
        bot = ReceiptBot(tier=Tier.PRO)
        receipts = [
            {"total_cashback": 5.0},
            {"total_cashback": 3.50},
            {"total_cashback": 2.25},
        ]
        total = bot.calculate_total_cashback(receipts)
        assert round(total, 2) == 10.75

    def test_store_field_in_result(self):
        bot = ReceiptBot(tier=Tier.FREE)
        result = bot.upload_receipt("Target", 40.0)
        assert result["store"] == "Target"


# ---------------------------------------------------------------------------
# TestFlipBot
# ---------------------------------------------------------------------------

class TestFlipBot:
    def test_free_tier_raises(self):
        bot = FlipBot(tier=Tier.FREE)
        with pytest.raises(StackAndProfitBotTierError):
            bot.find_flips()

    def test_pro_tier_allowed(self):
        bot = FlipBot(tier=Tier.PRO)
        result = bot.find_flips()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_enterprise_tier_allowed(self):
        bot = FlipBot(tier=Tier.ENTERPRISE)
        result = bot.find_flips()
        assert isinstance(result, list)

    def test_flips_have_profit_pct(self):
        bot = FlipBot(tier=Tier.PRO)
        result = bot.find_flips()
        for flip in result:
            assert "profit_pct" in flip
            assert flip["profit_pct"] > 0

    def test_budget_filter(self):
        bot = FlipBot(tier=Tier.PRO)
        result = bot.find_flips(budget=100.0)
        for flip in result:
            assert flip["buy_price"] <= 100.0

    def test_rank_flips_sorted_desc(self):
        bot = FlipBot(tier=Tier.PRO)
        flips = bot.find_flips()
        ranked = bot.rank_flips(flips)
        for i in range(len(ranked) - 1):
            assert ranked[i]["profit_pct"] >= ranked[i + 1]["profit_pct"]

    def test_rank_flips_free_raises(self):
        bot = FlipBot(tier=Tier.FREE)
        with pytest.raises(StackAndProfitBotTierError):
            bot.rank_flips([])

    def test_flip_profit_positive(self):
        bot = FlipBot(tier=Tier.PRO)
        result = bot.find_flips()
        for flip in result:
            assert flip["profit"] > 0


# ---------------------------------------------------------------------------
# TestCouponBot
# ---------------------------------------------------------------------------

class TestCouponBot:
    def test_find_coupons_returns_list(self):
        bot = CouponBot(tier=Tier.FREE)
        result = bot.find_coupons("Amazon")
        assert isinstance(result, list)

    def test_find_coupons_known_store(self):
        bot = CouponBot(tier=Tier.FREE)
        result = bot.find_coupons("Amazon")
        assert len(result) > 0

    def test_find_coupons_unknown_store(self):
        bot = CouponBot(tier=Tier.FREE)
        result = bot.find_coupons("NonExistentStore")
        assert result == []

    def test_coupon_has_required_fields(self):
        bot = CouponBot(tier=Tier.FREE)
        result = bot.find_coupons("Target")
        for coupon in result:
            assert "code" in coupon
            assert "discount_amount" in coupon
            assert "discount_type" in coupon
            assert "source" in coupon

    def test_free_stack_applies_one_coupon(self):
        bot = CouponBot(tier=Tier.FREE)
        coupons = bot.find_coupons("Amazon")
        result = bot.stack_coupons(coupons, 300.0)
        assert len(result["applied_coupons"]) <= 1

    def test_pro_stack_applies_up_to_five(self):
        bot = CouponBot(tier=Tier.PRO)
        coupons = [
            {"code": "C1", "discount_amount": 5.0, "discount_type": "fixed", "min_purchase": 0.0},
            {"code": "C2", "discount_amount": 5.0, "discount_type": "fixed", "min_purchase": 0.0},
            {"code": "C3", "discount_amount": 5.0, "discount_type": "fixed", "min_purchase": 0.0},
            {"code": "C4", "discount_amount": 5.0, "discount_type": "fixed", "min_purchase": 0.0},
            {"code": "C5", "discount_amount": 5.0, "discount_type": "fixed", "min_purchase": 0.0},
            {"code": "C6", "discount_amount": 5.0, "discount_type": "fixed", "min_purchase": 0.0},
        ]
        result = bot.stack_coupons(coupons, 200.0)
        assert len(result["applied_coupons"]) <= 5

    def test_stack_reduces_price(self):
        bot = CouponBot(tier=Tier.PRO)
        coupons = [{"code": "SAVE10", "discount_amount": 10.0, "discount_type": "fixed", "min_purchase": 0.0}]
        result = bot.stack_coupons(coupons, 100.0)
        assert result["final_price"] < 100.0

    def test_stack_result_has_required_keys(self):
        bot = CouponBot(tier=Tier.FREE)
        coupons = bot.find_coupons("Walmart")
        result = bot.stack_coupons(coupons, 50.0)
        assert "original_price" in result
        assert "final_price" in result
        assert "total_saved" in result
        assert "applied_coupons" in result

    def test_total_saved_equals_price_difference(self):
        bot = CouponBot(tier=Tier.PRO)
        coupons = [{"code": "TEST5", "discount_amount": 5.0, "discount_type": "fixed", "min_purchase": 0.0}]
        result = bot.stack_coupons(coupons, 80.0)
        assert round(result["total_saved"], 2) == round(result["original_price"] - result["final_price"], 2)


# ---------------------------------------------------------------------------
# TestProfitEngine
# ---------------------------------------------------------------------------

class TestProfitEngine:
    def _make_deal(self, original=100.0, sale=60.0, cashback_pct=5.0):
        return Deal("PE-01", "Test Deal", "Amazon", original, sale, "electronics", None, cashback_pct)

    def test_returns_dict(self):
        engine = ProfitEngine(tier=Tier.FREE)
        result = engine.calculate_profit(self._make_deal())
        assert isinstance(result, dict)

    def test_savings_correct(self):
        engine = ProfitEngine()
        result = engine.calculate_profit(self._make_deal(100.0, 60.0))
        assert result["savings"] == 40.0

    def test_savings_pct_correct(self):
        engine = ProfitEngine()
        result = engine.calculate_profit(self._make_deal(100.0, 60.0))
        assert result["savings_pct"] == 40.0

    def test_cashback_correct(self):
        engine = ProfitEngine()
        result = engine.calculate_profit(self._make_deal(100.0, 60.0, 5.0))
        assert result["cashback"] == 3.0

    def test_final_cost_correct(self):
        engine = ProfitEngine()
        result = engine.calculate_profit(self._make_deal(100.0, 60.0, 5.0))
        assert result["finalCost"] == 57.0

    def test_net_profit_positive(self):
        engine = ProfitEngine()
        result = engine.calculate_profit(self._make_deal())
        assert result["net_profit"] > 0

    def test_roi_pct_positive(self):
        engine = ProfitEngine()
        result = engine.calculate_profit(self._make_deal())
        assert result["roi_pct"] > 0

    def test_batch_calculate_returns_list(self):
        engine = ProfitEngine()
        deals = [self._make_deal(), self._make_deal(200.0, 120.0)]
        results = engine.batch_calculate(deals)
        assert isinstance(results, list)
        assert len(results) == 2

    def test_deal_id_in_result(self):
        engine = ProfitEngine()
        result = engine.calculate_profit(self._make_deal())
        assert "deal_id" in result


# ---------------------------------------------------------------------------
# TestRankingAI
# ---------------------------------------------------------------------------

class TestRankingAI:
    def _deals(self):
        return [
            Deal("R01", "Big Savings", "Amazon", 200.0, 80.0, "electronics", None, 10.0),
            Deal("R02", "Small Savings", "eBay", 50.0, 48.0, "clothing", None, 0.0),
            Deal("R03", "Medium Savings", "Target", 100.0, 60.0, "home", None, 5.0),
        ]

    def test_score_deal_returns_float(self):
        ai = RankingAI()
        deal = Deal("S01", "Test", "Amazon", 100.0, 50.0, "electronics", None, 5.0)
        score = ai.score_deal(deal)
        assert isinstance(score, float)

    def test_score_in_range(self):
        ai = RankingAI()
        deal = Deal("S02", "Test", "Amazon", 100.0, 50.0, "electronics", None, 5.0)
        score = ai.score_deal(deal)
        assert 0.0 <= score <= 100.0

    def test_better_deal_higher_score(self):
        ai = RankingAI()
        good = Deal("G01", "Good", "Amazon", 200.0, 60.0, "electronics", None, 10.0)
        bad = Deal("B01", "Bad", "eBay", 50.0, 49.0, "clothing", None, 0.0)
        assert ai.score_deal(good) > ai.score_deal(bad)

    def test_rank_deals_sorted_desc(self):
        ai = RankingAI()
        deals = self._deals()
        ranked = ai.rank_deals(deals)
        scores = [ai.score_deal(d) for d in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_get_top_deals_returns_n(self):
        ai = RankingAI()
        deals = self._deals()
        top = ai.get_top_deals(deals, n=2)
        assert len(top) == 2

    def test_get_top_deals_are_best(self):
        ai = RankingAI()
        deals = self._deals()
        all_ranked = ai.rank_deals(deals)
        top = ai.get_top_deals(deals, n=1)
        assert top[0].deal_id == all_ranked[0].deal_id

    def test_zero_original_price_gives_zero_score(self):
        ai = RankingAI()
        deal = Deal("Z01", "Zero", "Amazon", 0.0, 0.0, "electronics")
        assert ai.score_deal(deal) == 0.0


# ---------------------------------------------------------------------------
# TestAlertEngine
# ---------------------------------------------------------------------------

class TestAlertEngine:
    def _high_profit_deal(self):
        return Deal("AE-01", "Big Deal", "Amazon", 500.0, 200.0, "electronics", None, 10.0)

    def _low_profit_deal(self):
        return Deal("AE-02", "Small Deal", "Target", 20.0, 19.0, "clothing", None, 1.0)

    def test_should_alert_high_profit(self):
        engine = AlertEngine()
        assert engine.should_alert(self._high_profit_deal(), min_profit=15.0) is True

    def test_should_not_alert_low_profit(self):
        engine = AlertEngine()
        assert engine.should_alert(self._low_profit_deal(), min_profit=15.0) is False

    def test_get_alerts_returns_list(self):
        engine = AlertEngine()
        deals = [self._high_profit_deal(), self._low_profit_deal()]
        alerts = engine.get_alerts(deals, min_profit=15.0)
        assert isinstance(alerts, list)

    def test_get_alerts_filters_correctly(self):
        engine = AlertEngine()
        deals = [self._high_profit_deal(), self._low_profit_deal()]
        alerts = engine.get_alerts(deals, min_profit=15.0)
        assert all(a["net_profit"] >= 15.0 for a in alerts)

    def test_alert_has_urgency(self):
        engine = AlertEngine()
        alerts = engine.get_alerts([self._high_profit_deal()], min_profit=10.0)
        assert len(alerts) > 0
        assert "urgency" in alerts[0]
        assert alerts[0]["urgency"] in ("HIGH", "MEDIUM", "LOW")

    def test_high_profit_gets_high_urgency(self):
        engine = AlertEngine()
        # Deal with >$100 net profit
        big_deal = Deal("BIG", "Big Savings", "Amazon", 800.0, 200.0, "electronics", None, 10.0)
        alerts = engine.get_alerts([big_deal], min_profit=10.0)
        assert alerts[0]["urgency"] == "HIGH"

    def test_alert_has_deal_dict(self):
        engine = AlertEngine()
        alerts = engine.get_alerts([self._high_profit_deal()], min_profit=10.0)
        assert "deal" in alerts[0]
        assert isinstance(alerts[0]["deal"], dict)

    def test_no_alerts_when_min_profit_too_high(self):
        engine = AlertEngine()
        alerts = engine.get_alerts([self._low_profit_deal()], min_profit=9999.0)
        assert alerts == []


# ---------------------------------------------------------------------------
# TestStackAndProfitBot
# ---------------------------------------------------------------------------

class TestStackAndProfitBot:
    def test_get_tier_info_returns_dict(self):
        bot = StackAndProfitBot(tier=Tier.FREE)
        info = bot.get_tier_info()
        assert isinstance(info, dict)
        assert info["tier"] == "free"

    def test_rank_deals_proxy(self):
        bot = StackAndProfitBot(tier=Tier.PRO)
        deals = bot.deal_bot.find_deals()
        ranked = bot.rank_deals(deals)
        assert isinstance(ranked, list)
        assert len(ranked) == len(deals)

    def test_get_alerts_proxy(self):
        bot = StackAndProfitBot(tier=Tier.PRO)
        deals = bot.deal_bot.find_deals()
        alerts = bot.get_alerts(deals, min_profit=5.0)
        assert isinstance(alerts, list)

    def test_calculate_profit_proxy(self):
        bot = StackAndProfitBot(tier=Tier.FREE)
        deal = Deal("CP01", "Test", "Amazon", 100.0, 60.0, "electronics", None, 5.0)
        result = bot.calculate_profit(deal)
        assert "net_profit" in result

    def test_run_all_bots_free(self):
        bot = StackAndProfitBot(tier=Tier.FREE)
        result = bot.run_all_bots()
        assert "deals" in result
        assert "penny_deals" in result
        assert "flips" in result
        assert "alerts" in result
        assert "total_opportunities" in result
        assert "estimated_daily_profit" in result

    def test_run_all_bots_free_no_penny_no_flip(self):
        bot = StackAndProfitBot(tier=Tier.FREE)
        result = bot.run_all_bots()
        assert result["penny_deals"] == []
        assert result["flips"] == []

    def test_run_all_bots_pro_has_penny_and_flip(self):
        bot = StackAndProfitBot(tier=Tier.PRO)
        result = bot.run_all_bots()
        assert len(result["penny_deals"]) > 0
        assert len(result["flips"]) > 0

    def test_run_all_bots_returns_deals_list(self):
        bot = StackAndProfitBot(tier=Tier.PRO)
        result = bot.run_all_bots()
        assert isinstance(result["deals"], list)
        assert len(result["deals"]) > 0

    def test_estimated_daily_profit_nonnegative(self):
        bot = StackAndProfitBot(tier=Tier.PRO)
        result = bot.run_all_bots()
        assert result["estimated_daily_profit"] >= 0

    def test_load_preloaded_deals_returns_list(self):
        bot = StackAndProfitBot()
        deals = bot.load_preloaded_deals()
        assert isinstance(deals, list)

    def test_load_preloaded_deals_50_items(self):
        bot = StackAndProfitBot()
        deals = bot.load_preloaded_deals()
        assert len(deals) == 50

    def test_load_preloaded_deals_are_deal_instances(self):
        bot = StackAndProfitBot()
        deals = bot.load_preloaded_deals()
        assert all(isinstance(d, Deal) for d in deals)


# ---------------------------------------------------------------------------
# TestTierGating
# ---------------------------------------------------------------------------

class TestTierGating:
    def test_require_tier_raises_for_free_when_pro_needed(self):
        bot = StackAndProfitBot(tier=Tier.FREE)
        with pytest.raises(StackAndProfitBotTierError):
            bot._require_tier("test_feature", Tier.PRO)

    def test_require_tier_ok_for_pro_when_pro_needed(self):
        bot = StackAndProfitBot(tier=Tier.PRO)
        bot._require_tier("test_feature", Tier.PRO)  # should not raise

    def test_require_tier_ok_for_enterprise_when_pro_needed(self):
        bot = StackAndProfitBot(tier=Tier.ENTERPRISE)
        bot._require_tier("test_feature", Tier.PRO)  # should not raise

    def test_require_tier_raises_for_pro_when_enterprise_needed(self):
        bot = StackAndProfitBot(tier=Tier.PRO)
        with pytest.raises(StackAndProfitBotTierError):
            bot._require_tier("test_feature", Tier.ENTERPRISE)

    def test_error_message_contains_feature_name(self):
        bot = StackAndProfitBot(tier=Tier.FREE)
        with pytest.raises(StackAndProfitBotTierError, match="my_feature"):
            bot._require_tier("my_feature", Tier.PRO)

    def test_penny_bot_free_gated(self):
        bot = PennyBot(tier=Tier.FREE)
        with pytest.raises(StackAndProfitBotTierError):
            bot.find_penny_deals()

    def test_flip_bot_free_gated(self):
        bot = FlipBot(tier=Tier.FREE)
        with pytest.raises(StackAndProfitBotTierError):
            bot.find_flips()

    def test_receipt_bot_free_limit_gated(self):
        bot = ReceiptBot(tier=Tier.FREE)
        for _ in range(3):
            bot.upload_receipt("Walmart", 10.0)
        with pytest.raises(StackAndProfitBotTierError):
            bot.upload_receipt("Target", 10.0)
