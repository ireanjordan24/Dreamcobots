"""Tests for bots/god_mode_bot/tiers.py and bots/god_mode_bot/god_mode_bot.py"""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.god_mode_bot.god_mode_bot import (
    GodModeBot,
    GodModeBotTierError,
    ClientLead,
    OutreachProposal,
    DealRecord,
    PaymentRecord,
    PostRecord,
    OptimizationInsight,
    AutoClientHunter,
    AutoCloser,
    PaymentAutoCollector,
    ViralEngine,
    SelfImprovingAI,
    run,
)
from bots.god_mode_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------

class TestGodModeBotTierDefinitions:
    def test_all_tiers_have_features(self):
        for tier in Tier:
            assert len(BOT_FEATURES[tier.value]) > 0

    def test_enterprise_has_more_features_than_pro(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.PRO.value])

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_enterprise_has_api_access(self):
        assert any("API" in f or "api" in f for f in BOT_FEATURES[Tier.ENTERPRISE.value])

    def test_enterprise_has_white_label(self):
        assert any("white_label" in f or "white-label" in f for f in BOT_FEATURES[Tier.ENTERPRISE.value])

    def test_pro_has_viral_engine(self):
        assert any("ViralEngine" in f or "viral" in f.lower() for f in BOT_FEATURES[Tier.PRO.value])

    def test_pro_has_self_improving_ai(self):
        assert any("SelfImproving" in f or "self_improvement" in f for f in BOT_FEATURES[Tier.PRO.value])

    def test_free_has_stripe_payments(self):
        assert any("stripe" in f.lower() for f in BOT_FEATURES[Tier.FREE.value])

    def test_get_bot_tier_info_free(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0
        assert "features" in info

    def test_get_bot_tier_info_pro(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] > 0

    def test_get_bot_tier_info_enterprise(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["tier"] == "enterprise"
        assert info["price_usd_monthly"] > get_bot_tier_info(Tier.PRO)["price_usd_monthly"]

    def test_tier_info_has_support_level(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert "support_level" in info
            assert info["support_level"]

    def test_tier_info_has_requests_per_month(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert "requests_per_month" in info


# ---------------------------------------------------------------------------
# GodModeBot instantiation
# ---------------------------------------------------------------------------

class TestGodModeBotInstantiation:
    def test_default_tier_is_free(self):
        bot = GodModeBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = GodModeBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = GodModeBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = GodModeBot()
        assert bot.config is not None

    def test_engines_are_initialized(self):
        bot = GodModeBot(tier=Tier.PRO)
        assert isinstance(bot.client_hunter, AutoClientHunter)
        assert isinstance(bot.closer, AutoCloser)
        assert isinstance(bot.payment_collector, PaymentAutoCollector)
        assert isinstance(bot.viral_engine, ViralEngine)
        assert isinstance(bot.self_improving_ai, SelfImprovingAI)

    def test_all_tiers_instantiate(self):
        for tier in Tier:
            bot = GodModeBot(tier=tier)
            assert bot.tier == tier


# ---------------------------------------------------------------------------
# AutoClientHunter
# ---------------------------------------------------------------------------

class TestAutoClientHunter:
    def test_hunt_returns_leads(self):
        hunter = AutoClientHunter(Tier.PRO)
        leads = hunter.hunt_leads("digital marketing", count=3)
        assert len(leads) == 3
        assert all(isinstance(l, ClientLead) for l in leads)

    def test_lead_has_required_fields(self):
        hunter = AutoClientHunter(Tier.PRO)
        leads = hunter.hunt_leads("digital marketing", count=1)
        lead = leads[0]
        assert lead.name
        assert lead.company
        assert lead.email
        assert lead.niche
        assert 0 <= lead.score <= 100

    def test_free_tier_lead_limit(self):
        hunter = AutoClientHunter(Tier.FREE)
        with pytest.raises(GodModeBotTierError):
            hunter.hunt_leads("digital marketing", count=10)

    def test_free_tier_allows_up_to_5(self):
        hunter = AutoClientHunter(Tier.FREE)
        leads = hunter.hunt_leads("digital marketing", count=5)
        assert len(leads) == 5

    def test_pro_tier_unlimited_leads(self):
        hunter = AutoClientHunter(Tier.PRO)
        leads = hunter.hunt_leads("digital marketing", count=7)
        assert len(leads) == 7

    def test_generate_proposal_free_tier(self):
        hunter = AutoClientHunter(Tier.FREE)
        leads = hunter.hunt_leads("digital marketing", count=1)
        proposal = hunter.generate_proposal(leads[0])
        assert isinstance(proposal, OutreachProposal)
        assert proposal.lead_name == leads[0].name
        assert proposal.estimated_value_usd > 0

    def test_generate_proposal_pro_tier(self):
        hunter = AutoClientHunter(Tier.PRO)
        leads = hunter.hunt_leads("digital marketing", count=1)
        proposal = hunter.generate_proposal(leads[0])
        assert "🚀" in proposal.subject or "AI" in proposal.subject

    def test_send_outreach_marks_lead(self):
        hunter = AutoClientHunter(Tier.PRO)
        leads = hunter.hunt_leads("digital marketing", count=1)
        lead = leads[0]
        proposal = hunter.generate_proposal(lead)
        result = hunter.send_outreach(lead, proposal)
        assert result["status"] == "sent"
        assert lead.outreach_sent is True
        assert "message_id" in result

    def test_leads_summary(self):
        hunter = AutoClientHunter(Tier.PRO)
        hunter.hunt_leads("digital marketing", count=3)
        summary = hunter.leads_summary()
        assert summary["total_leads"] == 3
        assert "avg_score" in summary

    def test_lead_to_dict(self):
        hunter = AutoClientHunter(Tier.PRO)
        leads = hunter.hunt_leads("digital marketing", count=1)
        d = leads[0].to_dict()
        assert "name" in d
        assert "company" in d
        assert "email" in d
        assert "score" in d
        assert "timestamp" in d

    def test_proposal_to_dict(self):
        hunter = AutoClientHunter(Tier.PRO)
        leads = hunter.hunt_leads("digital marketing", count=1)
        proposal = hunter.generate_proposal(leads[0])
        d = proposal.to_dict()
        assert "lead_name" in d
        assert "subject" in d
        assert "body" in d
        assert "estimated_value_usd" in d

    def test_different_niches_return_different_leads(self):
        hunter = AutoClientHunter(Tier.PRO)
        dm_leads = hunter.hunt_leads("digital marketing", count=2)
        ec_leads = hunter.hunt_leads("e-commerce", count=2)
        dm_names = {l.name for l in dm_leads}
        ec_names = {l.name for l in ec_leads}
        assert dm_names != ec_names


# ---------------------------------------------------------------------------
# AutoCloser
# ---------------------------------------------------------------------------

class TestAutoCloser:
    def _make_lead(self) -> ClientLead:
        return ClientLead(
            name="Test User",
            company="Test Corp",
            email="test@testcorp.com",
            niche="saas",
            score=80,
        )

    def test_start_negotiation_returns_deal(self):
        closer = AutoCloser(Tier.PRO)
        lead = self._make_lead()
        deal = closer.start_negotiation(lead)
        assert isinstance(deal, DealRecord)
        assert deal.status == "negotiating"
        assert deal.asking_price > 0

    def test_deal_has_initial_message(self):
        closer = AutoCloser(Tier.PRO)
        deal = closer.start_negotiation(self._make_lead())
        assert len(deal.messages) == 1
        assert deal.messages[0]["role"] == "bot"

    def test_negotiate_discount_request(self):
        closer = AutoCloser(Tier.PRO)
        deal = closer.start_negotiation(self._make_lead())
        deal = closer.negotiate(deal, "Can I get a discount?")
        assert deal.agreed_price > 0
        assert deal.agreed_price < deal.asking_price

    def test_negotiate_acceptance(self):
        closer = AutoCloser(Tier.PRO)
        deal = closer.start_negotiation(self._make_lead())
        closer.negotiate(deal, "Can I get a discount?")
        deal = closer.negotiate(deal, "Yes, I accept the deal")
        assert deal.status == "closing"

    def test_close_deal(self):
        closer = AutoCloser(Tier.PRO)
        deal = closer.start_negotiation(self._make_lead())
        deal = closer.close_deal(deal)
        assert deal.status == "closed"
        assert deal.agreed_price > 0

    def test_book_client_requires_pro(self):
        closer = AutoCloser(Tier.FREE)
        deal = closer.start_negotiation(self._make_lead())
        deal = closer.close_deal(deal)
        with pytest.raises(GodModeBotTierError):
            closer.book_client(deal)

    def test_book_client_pro(self):
        closer = AutoCloser(Tier.PRO)
        deal = closer.start_negotiation(self._make_lead())
        deal = closer.close_deal(deal)
        booking = closer.book_client(deal)
        assert booking["status"] == "booked"
        assert "booking_id" in booking
        assert deal.status == "booked"

    def test_book_client_requires_closed_deal(self):
        closer = AutoCloser(Tier.PRO)
        deal = closer.start_negotiation(self._make_lead())
        with pytest.raises(GodModeBotTierError):
            closer.book_client(deal)

    def test_negotiate_cancelled_deal_raises(self):
        closer = AutoCloser(Tier.PRO)
        deal = closer.start_negotiation(self._make_lead())
        deal.status = "cancelled"
        with pytest.raises(GodModeBotTierError):
            closer.negotiate(deal, "I want a discount")

    def test_close_cancelled_deal_raises(self):
        closer = AutoCloser(Tier.PRO)
        deal = closer.start_negotiation(self._make_lead())
        deal.status = "cancelled"
        with pytest.raises(GodModeBotTierError):
            closer.close_deal(deal)

    def test_deals_summary(self):
        closer = AutoCloser(Tier.PRO)
        for _ in range(3):
            deal = closer.start_negotiation(self._make_lead())
            closer.close_deal(deal)
        summary = closer.deals_summary()
        assert summary["total_deals"] == 3
        assert summary["closed_deals"] == 3
        assert summary["total_value_usd"] > 0

    def test_deal_to_dict(self):
        closer = AutoCloser(Tier.PRO)
        deal = closer.start_negotiation(self._make_lead())
        d = deal.to_dict()
        assert "deal_id" in d
        assert "client_name" in d
        assert "asking_price" in d
        assert "status" in d
        assert "messages" in d

    def test_enterprise_higher_max_discount(self):
        closer_pro = AutoCloser(Tier.PRO)
        closer_ent = AutoCloser(Tier.ENTERPRISE)
        lead = self._make_lead()
        deal_pro = closer_pro.start_negotiation(lead)
        deal_ent = closer_ent.start_negotiation(lead)
        closer_pro.negotiate(deal_pro, "give me a discount")
        closer_ent.negotiate(deal_ent, "give me a discount")
        assert deal_ent.agreed_price <= deal_pro.agreed_price


# ---------------------------------------------------------------------------
# PaymentAutoCollector
# ---------------------------------------------------------------------------

class TestPaymentAutoCollector:
    def test_create_subscription_returns_record(self):
        collector = PaymentAutoCollector(Tier.FREE)
        sub = collector.create_subscription("Alice", "Pro Plan", 99.0)
        assert isinstance(sub, PaymentRecord)
        assert sub.status == "active"
        assert sub.record_type == "subscription"

    def test_subscription_has_correct_amount(self):
        collector = PaymentAutoCollector(Tier.PRO)
        sub = collector.create_subscription("Bob", "Enterprise Plan", 499.0)
        assert sub.amount == 499.0
        assert sub.customer_name == "Bob"

    def test_generate_invoice_requires_pro(self):
        collector = PaymentAutoCollector(Tier.FREE)
        with pytest.raises(GodModeBotTierError):
            collector.generate_invoice("Alice", 500.0, "Consulting")

    def test_generate_invoice_pro(self):
        collector = PaymentAutoCollector(Tier.PRO)
        invoice = collector.generate_invoice("Carol", 750.0, "AI Services")
        assert isinstance(invoice, PaymentRecord)
        assert invoice.status == "pending"
        assert invoice.record_type == "invoice"

    def test_collect_payment(self):
        collector = PaymentAutoCollector(Tier.PRO)
        invoice = collector.generate_invoice("David", 1000.0, "Automation Setup")
        result = collector.collect_payment(invoice.record_id)
        assert result["status"] == "paid"
        assert result["amount_usd"] == 1000.0

    def test_collect_already_paid(self):
        collector = PaymentAutoCollector(Tier.PRO)
        invoice = collector.generate_invoice("Eva", 200.0, "Monthly retainer")
        collector.collect_payment(invoice.record_id)
        result = collector.collect_payment(invoice.record_id)
        assert result["status"] == "already_paid"

    def test_collect_nonexistent_invoice_raises(self):
        collector = PaymentAutoCollector(Tier.PRO)
        with pytest.raises(GodModeBotTierError):
            collector.collect_payment("inv_nonexistent")

    def test_list_subscriptions(self):
        collector = PaymentAutoCollector(Tier.PRO)
        collector.create_subscription("Alice", "Pro", 99.0)
        collector.create_subscription("Bob", "Enterprise", 499.0)
        subs = collector.list_subscriptions()
        assert len(subs) == 2
        assert all("record_id" in s for s in subs)

    def test_list_invoices(self):
        collector = PaymentAutoCollector(Tier.PRO)
        collector.generate_invoice("Alice", 100.0, "Invoice 1")
        collector.generate_invoice("Bob", 200.0, "Invoice 2")
        invoices = collector.list_invoices()
        assert len(invoices) == 2

    def test_revenue_total(self):
        collector = PaymentAutoCollector(Tier.PRO)
        collector.create_subscription("Alice", "Pro", 300.0)
        invoice = collector.generate_invoice("Bob", 500.0, "Setup fee")
        collector.collect_payment(invoice.record_id)
        total = collector.revenue_total()
        assert total["subscription_mrr_usd"] == 300.0
        assert total["invoices_collected_usd"] == 500.0
        assert total["total_usd"] == 800.0

    def test_payment_record_to_dict(self):
        collector = PaymentAutoCollector(Tier.PRO)
        sub = collector.create_subscription("Alice", "Pro", 99.0)
        d = sub.to_dict()
        assert "record_id" in d
        assert "customer_name" in d
        assert "amount" in d
        assert "record_type" in d
        assert "status" in d

    def test_revenue_total_empty(self):
        collector = PaymentAutoCollector(Tier.PRO)
        total = collector.revenue_total()
        assert total["total_usd"] == 0.0
        assert total["active_subscriptions"] == 0


# ---------------------------------------------------------------------------
# ViralEngine
# ---------------------------------------------------------------------------

class TestViralEngine:
    def test_detect_trends_returns_list(self):
        engine = ViralEngine(Tier.PRO)
        trends = engine.detect_trends("digital marketing")
        assert isinstance(trends, list)
        assert len(trends) > 0

    def test_free_tier_fewer_trends(self):
        free_engine = ViralEngine(Tier.FREE)
        pro_engine = ViralEngine(Tier.PRO)
        free_trends = free_engine.detect_trends("digital marketing")
        pro_trends = pro_engine.detect_trends("digital marketing")
        assert len(free_trends) <= len(pro_trends)

    def test_enterprise_gets_all_trends(self):
        ent_engine = ViralEngine(Tier.ENTERPRISE)
        pro_engine = ViralEngine(Tier.PRO)
        ent_trends = ent_engine.detect_trends("digital marketing")
        pro_trends = pro_engine.detect_trends("digital marketing")
        assert len(ent_trends) >= len(pro_trends)

    def test_generate_post_returns_record(self):
        engine = ViralEngine(Tier.PRO)
        post = engine.generate_post("AI automation", "twitter")
        assert isinstance(post, PostRecord)
        assert post.platform == "twitter"
        assert len(post.content) > 0

    def test_generate_post_invalid_platform(self):
        engine = ViralEngine(Tier.PRO)
        with pytest.raises(GodModeBotTierError):
            engine.generate_post("AI automation", "snapchat")

    def test_free_tier_platform_limit(self):
        engine = ViralEngine(Tier.FREE)
        engine.generate_post("AI automation", "twitter")
        with pytest.raises(GodModeBotTierError):
            engine.generate_post("AI automation", "instagram")

    def test_pro_tier_allows_3_platforms(self):
        engine = ViralEngine(Tier.PRO)
        engine.generate_post("AI automation", "twitter")
        engine.generate_post("AI automation", "instagram")
        engine.generate_post("AI automation", "linkedin")
        assert len({p.platform for p in engine._posts}) == 3

    def test_schedule_post(self):
        engine = ViralEngine(Tier.PRO)
        post = engine.generate_post("AI automation", "twitter")
        result = engine.schedule_post(post)
        assert result["status"] == "scheduled"
        assert post.scheduled is True

    def test_run_daily_posting(self):
        engine = ViralEngine(Tier.PRO)
        results = engine.run_daily_posting("digital marketing")
        assert isinstance(results, list)
        assert len(results) > 0
        assert all("post_id" in r for r in results)

    def test_posts_summary(self):
        engine = ViralEngine(Tier.PRO)
        engine.generate_post("AI automation", "twitter")
        engine.generate_post("SEO 2024", "twitter")
        summary = engine.posts_summary()
        assert summary["total_posts"] == 2
        assert "platforms" in summary

    def test_post_record_to_dict(self):
        engine = ViralEngine(Tier.PRO)
        post = engine.generate_post("AI automation", "twitter")
        d = post.to_dict()
        assert "post_id" in d
        assert "platform" in d
        assert "content" in d
        assert "trend" in d
        assert "scheduled" in d

    def test_enterprise_can_use_all_platforms(self):
        engine = ViralEngine(Tier.ENTERPRISE)
        platforms = ["twitter", "instagram", "linkedin", "tiktok", "facebook"]
        for p in platforms:
            engine.generate_post("AI automation", p)
        used = {post.platform for post in engine._posts}
        assert len(used) == len(platforms)

    def test_post_content_contains_trend(self):
        engine = ViralEngine(Tier.PRO)
        post = engine.generate_post("AI automation", "twitter")
        assert "AI automation" in post.content or "AI" in post.content


# ---------------------------------------------------------------------------
# SelfImprovingAI
# ---------------------------------------------------------------------------

class TestSelfImprovingAI:
    def test_analyze_performance_returns_report(self):
        ai = SelfImprovingAI(Tier.PRO)
        metrics = {"leads_generated": 20, "revenue_usd": 5000.0, "conversion_rate": 0.25}
        report = ai.analyze_performance(metrics)
        assert "performance_score" in report
        assert 0 <= report["performance_score"] <= 100

    def test_analyze_performance_assessment(self):
        ai = SelfImprovingAI(Tier.PRO)
        report = ai.analyze_performance({"leads_generated": 50, "revenue_usd": 10000.0, "conversion_rate": 0.4})
        assert "assessment" in report
        assert isinstance(report["assessment"], str)

    def test_analyze_performance_free_tier(self):
        ai = SelfImprovingAI(Tier.FREE)
        report = ai.analyze_performance({"leads_generated": 3, "revenue_usd": 200.0, "conversion_rate": 0.1})
        assert "performance_score" in report
        assert "bottleneck" not in report  # bottleneck only on PRO+

    def test_optimize_priorities_requires_pro(self):
        ai = SelfImprovingAI(Tier.FREE)
        with pytest.raises(GodModeBotTierError):
            ai.optimize_priorities()

    def test_optimize_priorities_pro(self):
        ai = SelfImprovingAI(Tier.PRO)
        insights = ai.optimize_priorities()
        assert len(insights) > 0
        assert all(isinstance(i, OptimizationInsight) for i in insights)

    def test_optimize_priorities_sorted_by_priority(self):
        ai = SelfImprovingAI(Tier.PRO)
        insights = ai.optimize_priorities()
        priorities = [i.priority for i in insights]
        assert priorities == sorted(priorities)

    def test_enterprise_gets_more_insights(self):
        ai_pro = SelfImprovingAI(Tier.PRO)
        ai_ent = SelfImprovingAI(Tier.ENTERPRISE)
        pro_insights = ai_pro.optimize_priorities()
        ent_insights = ai_ent.optimize_priorities()
        assert len(ent_insights) >= len(pro_insights)

    def test_get_recommendations_empty_without_optimize(self):
        ai = SelfImprovingAI(Tier.PRO)
        recs = ai.get_recommendations()
        assert recs == []

    def test_get_recommendations_after_optimize(self):
        ai = SelfImprovingAI(Tier.PRO)
        ai.optimize_priorities()
        recs = ai.get_recommendations()
        assert len(recs) > 0
        assert all("insight_id" in r for r in recs)

    def test_apply_optimization_requires_enterprise(self):
        ai = SelfImprovingAI(Tier.PRO)
        ai.optimize_priorities()
        insight_id = ai._insights[0].insight_id
        with pytest.raises(GodModeBotTierError):
            ai.apply_optimization(insight_id)

    def test_apply_optimization_enterprise(self):
        ai = SelfImprovingAI(Tier.ENTERPRISE)
        ai.optimize_priorities()
        insight_id = ai._insights[0].insight_id
        result = ai.apply_optimization(insight_id)
        assert result["status"] == "applied"
        assert ai._insights[0].applied is True

    def test_apply_optimization_nonexistent_raises(self):
        ai = SelfImprovingAI(Tier.ENTERPRISE)
        with pytest.raises(GodModeBotTierError):
            ai.apply_optimization("ins_nonexistent")

    def test_apply_already_applied_returns_status(self):
        ai = SelfImprovingAI(Tier.ENTERPRISE)
        ai.optimize_priorities()
        insight_id = ai._insights[0].insight_id
        ai.apply_optimization(insight_id)
        result = ai.apply_optimization(insight_id)
        assert result["status"] == "already_applied"

    def test_optimization_summary(self):
        ai = SelfImprovingAI(Tier.ENTERPRISE)
        ai.optimize_priorities()
        insight_id = ai._insights[0].insight_id
        ai.apply_optimization(insight_id)
        summary = ai.optimization_summary()
        assert summary["applied_insights"] == 1
        assert summary["total_estimated_lift_usd"] > 0

    def test_insight_to_dict(self):
        ai = SelfImprovingAI(Tier.PRO)
        ai.optimize_priorities()
        d = ai._insights[0].to_dict()
        assert "insight_id" in d
        assert "category" in d
        assert "title" in d
        assert "priority" in d
        assert "applied" in d


# ---------------------------------------------------------------------------
# GodModeBot run_all_engines
# ---------------------------------------------------------------------------

class TestGodModeBotRunAllEngines:
    def test_free_tier_run_all_engines(self):
        bot = GodModeBot(tier=Tier.FREE)
        report = bot.run_all_engines()
        assert report["tier"] == "free"
        assert "engines_run" in report
        assert "auto_client_hunter" in report["engines_run"]
        assert "payment_auto_collector" in report["engines_run"]

    def test_pro_tier_run_all_engines(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert report["tier"] == "pro"
        assert "auto_closer" in report["engines_run"]
        assert "self_improving_ai" in report["engines_run"]

    def test_enterprise_tier_run_all_engines(self):
        bot = GodModeBot(tier=Tier.ENTERPRISE)
        report = bot.run_all_engines()
        assert "auto_optimization" in report["engines_run"]

    def test_report_has_revenue_summary(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert "revenue_summary" in report

    def test_report_results_structure(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert "results" in report
        assert "client_hunter" in report["results"]
        assert "viral_engine" in report["results"]
        assert "payment_collector" in report["results"]

    def test_describe_tier(self):
        bot = GodModeBot(tier=Tier.PRO)
        description = bot.describe_tier()
        assert isinstance(description, str)
        assert "PRO" in description or "Pro" in description

    def test_describe_tier_contains_price(self):
        bot = GodModeBot(tier=Tier.FREE)
        description = bot.describe_tier()
        assert "$" in description

    def test_revenue_summary_returns_dict(self):
        bot = GodModeBot(tier=Tier.PRO)
        bot.create_subscription("Alice", "Pro", 99.0)
        summary = bot.revenue_summary()
        assert "subscription_mrr_usd" in summary
        assert "total_usd" in summary


# ---------------------------------------------------------------------------
# Module-level run()
# ---------------------------------------------------------------------------

class TestGodModeBotModuleLevelRun:
    def test_run_returns_dict(self):
        result = run()
        assert isinstance(result, dict)

    def test_run_status_success(self):
        result = run()
        assert result["status"] == "success"

    def test_run_returns_leads(self):
        result = run()
        assert result["leads"] == 25
        assert result["leads_generated"] == 25

    def test_run_returns_revenue(self):
        result = run()
        assert result["revenue"] == 5000

    def test_run_all_keys_present(self):
        result = run()
        assert "status" in result
        assert "leads" in result
        assert "leads_generated" in result
        assert "revenue" in result

    def test_run_idempotent(self):
        result1 = run()
        result2 = run()
        assert result1["status"] == result2["status"]
        assert result1["leads"] == result2["leads"]
        assert result1["revenue"] == result2["revenue"]


# ---------------------------------------------------------------------------
# GodModeBot integration (via delegation methods)
# ---------------------------------------------------------------------------

class TestGodModeBotDelegation:
    def test_hunt_leads_via_bot(self):
        bot = GodModeBot(tier=Tier.PRO)
        leads = bot.hunt_leads("digital marketing", count=3)
        assert len(leads) == 3

    def test_generate_proposal_via_bot(self):
        bot = GodModeBot(tier=Tier.PRO)
        leads = bot.hunt_leads("digital marketing", count=1)
        proposal = bot.generate_proposal(leads[0])
        assert isinstance(proposal, OutreachProposal)

    def test_send_outreach_via_bot(self):
        bot = GodModeBot(tier=Tier.PRO)
        leads = bot.hunt_leads("digital marketing", count=1)
        proposal = bot.generate_proposal(leads[0])
        result = bot.send_outreach(leads[0], proposal)
        assert result["status"] == "sent"

    def test_full_negotiation_flow(self):
        bot = GodModeBot(tier=Tier.PRO)
        leads = bot.hunt_leads("saas", count=1)
        deal = bot.start_negotiation(leads[0])
        deal = bot.negotiate(deal, "Can I get a discount?")
        deal = bot.close_deal(deal)
        booking = bot.book_client(deal)
        assert booking["status"] == "booked"

    def test_subscription_and_invoice_flow(self):
        bot = GodModeBot(tier=Tier.PRO)
        sub = bot.create_subscription("TechCorp", "Pro Monthly", 299.0)
        assert sub.status == "active"
        invoice = bot.generate_invoice("TechCorp", 1500.0, "Onboarding fee")
        payment = bot.collect_payment(invoice.record_id)
        assert payment["status"] == "paid"

    def test_detect_trends_via_bot(self):
        bot = GodModeBot(tier=Tier.PRO)
        trends = bot.detect_trends("saas")
        assert len(trends) > 0

    def test_generate_post_via_bot(self):
        bot = GodModeBot(tier=Tier.PRO)
        post = bot.generate_post("AI automation", "linkedin")
        assert isinstance(post, PostRecord)

    def test_run_daily_posting_via_bot(self):
        bot = GodModeBot(tier=Tier.PRO)
        posts = bot.run_daily_posting("digital marketing")
        assert len(posts) > 0

    def test_optimize_priorities_via_bot(self):
        bot = GodModeBot(tier=Tier.PRO)
        insights = bot.optimize_priorities()
        assert len(insights) > 0

    def test_get_recommendations_via_bot(self):
        bot = GodModeBot(tier=Tier.PRO)
        bot.optimize_priorities()
        recs = bot.get_recommendations()
        assert len(recs) > 0

    def test_apply_optimization_via_bot(self):
        bot = GodModeBot(tier=Tier.ENTERPRISE)
        insights = bot.optimize_priorities()
        result = bot.apply_optimization(insights[0].insight_id)
        assert result["status"] == "applied"

    def test_analyze_performance_via_bot(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.analyze_performance({"leads_generated": 10, "revenue_usd": 2000.0, "conversion_rate": 0.2})
        assert "performance_score" in report
