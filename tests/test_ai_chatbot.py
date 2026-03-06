"""
tests/test_ai_chatbot.py – Unit tests for the Dreamcobots AI Chatbot system.

Run with:
    cd /path/to/Dreamcobots
    python -m pytest tests/test_ai_chatbot.py -v
"""

import pytest
import sys
import os

# Ensure the repo root is on the path so relative imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bots.ai_chatbot.tiers import (
    Tier, TIER_CONFIGS, has_feature, require_feature, tier_summary
)
from bots.ai_chatbot.chatbot import AIChatbot, BasicLLMAdapter, AdvancedLLMAdapter, KimiKAdapter
from bots.ai_chatbot.analytics import AnalyticsEngine, CompanyProfile
from bots.ai_chatbot.marketplace import Marketplace, LAYOUT_TEMPLATES


# ---------------------------------------------------------------------------
# Tier / feature-gate tests
# ---------------------------------------------------------------------------

class TestTiers:
    def test_all_tiers_defined(self):
        assert set(TIER_CONFIGS.keys()) == {Tier.FREE, Tier.INTERMEDIATE, Tier.PREMIUM}

    def test_free_tier_price(self):
        assert TIER_CONFIGS[Tier.FREE].monthly_price_usd == 0.0

    def test_intermediate_tier_price(self):
        assert TIER_CONFIGS[Tier.INTERMEDIATE].monthly_price_usd == 29.99

    def test_premium_tier_price(self):
        assert TIER_CONFIGS[Tier.PREMIUM].monthly_price_usd == 99.99

    def test_free_has_core_chat(self):
        assert has_feature(Tier.FREE, "core_chat") is True

    def test_free_missing_kimi_k(self):
        assert has_feature(Tier.FREE, "kimi_k_ai") is False

    def test_intermediate_has_analytics(self):
        assert has_feature(Tier.INTERMEDIATE, "analytics_dashboard") is True

    def test_premium_has_all_features(self):
        premium_features = [
            "kimi_k_ai", "partner_recruitment", "ai_ecosystem_directory",
            "marketing_doc_manager", "white_label", "dedicated_support",
        ]
        for f in premium_features:
            assert has_feature(Tier.PREMIUM, f), f"Premium should have '{f}'"

    def test_require_feature_raises_for_free(self):
        with pytest.raises(PermissionError, match="kimi_k_ai"):
            require_feature(Tier.FREE, "kimi_k_ai")

    def test_require_feature_passes_for_premium(self):
        require_feature(Tier.PREMIUM, "kimi_k_ai")  # should not raise

    def test_tier_summary_contains_all_names(self):
        summary = tier_summary()
        for cfg in TIER_CONFIGS.values():
            assert cfg.name in summary

    def test_premium_unlimited_messages(self):
        assert TIER_CONFIGS[Tier.PREMIUM].max_messages_per_day == -1

    def test_premium_includes_kimi_k_model(self):
        assert "kimi-k" in TIER_CONFIGS[Tier.PREMIUM].ai_models

    def test_free_does_not_include_kimi_k_model(self):
        assert "kimi-k" not in TIER_CONFIGS[Tier.FREE].ai_models


# ---------------------------------------------------------------------------
# AI Chatbot engine tests
# ---------------------------------------------------------------------------

class TestAIChatbot:
    def test_free_bot_responds(self):
        bot = AIChatbot(user_id="u_free", tier=Tier.FREE)
        reply = bot.chat("Hello")
        assert isinstance(reply, str)
        assert len(reply) > 0

    def test_intermediate_bot_responds(self):
        bot = AIChatbot(user_id="u_inter", tier=Tier.INTERMEDIATE)
        reply = bot.chat("Show me the analytics dashboard")
        assert isinstance(reply, str)

    def test_premium_bot_uses_kimi_k(self):
        bot = AIChatbot(user_id="u_prem", tier=Tier.PREMIUM, model="kimi-k")
        assert bot.model == "kimi-k"
        reply = bot.chat("Tell me about partner recruitment")
        assert "KimiK" in reply

    def test_invalid_model_raises(self):
        with pytest.raises(ValueError, match="kimi-k"):
            AIChatbot(user_id="u_x", tier=Tier.FREE, model="kimi-k")

    def test_conversation_history_recorded(self):
        bot = AIChatbot(user_id="u_h", tier=Tier.FREE)
        bot.chat("Hello")
        bot.chat("How are you?")
        history = bot.get_history()
        assert len(history) == 4  # 2 user + 2 assistant messages

    def test_history_blocked_on_feature_missing_tier(self):
        # conversation_history is available on FREE, this just confirms it works
        bot = AIChatbot(user_id="u_h2", tier=Tier.FREE)
        bot.chat("hi")
        history = bot.get_history()
        assert any(m["role"] == "user" for m in history)

    def test_customize_requires_intermediate(self):
        bot = AIChatbot(user_id="u_c", tier=Tier.FREE)
        with pytest.raises(PermissionError, match="advanced_customisation"):
            bot.customize(persona="DreamBot")

    def test_customize_works_on_intermediate(self):
        bot = AIChatbot(user_id="u_c2", tier=Tier.INTERMEDIATE)
        bot.customize(persona="DreamBot", system_prompt="You are helpful.")
        msgs = bot.session.messages
        assert any(m.role == "system" for m in msgs)

    def test_rate_limit_enforced(self):
        bot = AIChatbot(user_id="u_limit", tier=Tier.FREE)
        # Manually set messages_today to the limit
        bot.session.messages_today = TIER_CONFIGS[Tier.FREE].max_messages_per_day
        with pytest.raises(RuntimeError, match="Daily message limit"):
            bot.chat("One more message")

    def test_premium_no_rate_limit(self):
        bot = AIChatbot(user_id="u_prem2", tier=Tier.PREMIUM)
        bot.session.messages_today = 10_000
        # Should not raise
        reply = bot.chat("Still going?")
        assert reply

    def test_export_session(self):
        bot = AIChatbot(user_id="u_exp", tier=Tier.INTERMEDIATE)
        bot.chat("Hello")
        export = bot.export_session()
        assert export["user_id"] == "u_exp"
        assert export["tier"] == "intermediate"
        assert "history" in export

    def test_basic_llm_adapter(self):
        adapter = BasicLLMAdapter()
        reply = adapter.generate([], "hello")
        assert "assistant" in reply.lower() or "Dreamcobots" in reply

    def test_advanced_llm_adapter(self):
        adapter = AdvancedLLMAdapter()
        reply = adapter.generate([], "Show me the analytics dashboard")
        assert "analytics" in reply.lower()

    def test_kimi_k_adapter_partner_query(self):
        adapter = KimiKAdapter()
        reply = adapter.generate([], "partner recruitment")
        assert "KimiK" in reply

    def test_kimi_k_adapter_marketing_query(self):
        adapter = KimiKAdapter()
        reply = adapter.generate([], "marketing documentation layout")
        assert "Marketing" in reply


# ---------------------------------------------------------------------------
# Analytics engine tests
# ---------------------------------------------------------------------------

class TestAnalyticsEngine:
    def setup_method(self):
        self.engine = AnalyticsEngine(tier=Tier.PREMIUM)

    def test_search_all_companies(self):
        results = self.engine.search_companies()
        assert len(results) >= 7

    def test_search_by_query(self):
        results = self.engine.search_companies(query="kimi")
        assert any("Moonshot" in c.name for c in results)

    def test_search_by_tag(self):
        results = self.engine.search_companies(tags=["enterprise"])
        assert len(results) >= 3

    def test_search_by_min_score(self):
        results = self.engine.search_companies(min_score=0.90)
        for c in results:
            assert c.partnership_potential_score >= 0.90

    def test_get_company_profile(self):
        profile = self.engine.get_company_profile("org_003")
        assert profile is not None
        assert "Moonshot" in profile.name

    def test_get_nonexistent_company(self):
        profile = self.engine.get_company_profile("org_999")
        assert profile is None

    def test_add_custom_company(self):
        new_co = CompanyProfile(
            company_id="org_custom",
            name="TestCo AI",
            industry="AI Testing",
            focus_areas=["testing"],
            headquarters="Test City",
            website="https://test.ai",
            description="A test company",
        )
        self.engine.add_company(new_co)
        assert self.engine.get_company_profile("org_custom") is not None

    def test_partner_recruitment(self):
        result = self.engine.run_partner_recruitment(
            requester_name="Dreamcobots",
            focus_areas=["large language models", "enterprise chatbots"],
            top_n=5,
        )
        assert len(result.candidates) == 5
        assert result.requester_company == "Dreamcobots"
        assert len(result.recommended_outreach) >= 3
        assert result.estimated_reach > 0

    def test_partner_recruitment_scores_in_range(self):
        result = self.engine.run_partner_recruitment(
            requester_name="Dreamcobots",
            focus_areas=["llm"],
            top_n=3,
        )
        for candidate in result.candidates:
            assert 0.0 <= candidate["score"] <= 1.0

    def test_ecosystem_directory_blocked_on_free(self):
        engine = AnalyticsEngine(tier=Tier.FREE)
        with pytest.raises(PermissionError, match="ai_ecosystem_directory"):
            engine.search_companies()

    def test_onsite_signup_developer_flow(self):
        flow = self.engine.generate_onsite_signup_flow("developer")
        assert "steps" in flow
        assert len(flow["steps"]) > 0

    def test_onsite_signup_enterprise_flow(self):
        flow = self.engine.generate_onsite_signup_flow("enterprise")
        assert "cta" in flow
        assert "enterprise" in flow["cta"].lower() or "demo" in flow["cta"].lower()

    def test_onsite_signup_partner_flow(self):
        flow = self.engine.generate_onsite_signup_flow("partner")
        assert any("partner" in step.lower() for step in flow["steps"])

    def test_usage_recording(self):
        engine = AnalyticsEngine(tier=Tier.INTERMEDIATE)
        engine.record_usage(total_messages=200, active_users=50,
                            tier_breakdown={"free": 30, "intermediate": 15, "premium": 5})
        summary = engine.usage_summary()
        assert summary["total_messages"] == 200
        assert summary["average_daily_active_users"] == 50.0

    def test_usage_blocked_on_free(self):
        engine = AnalyticsEngine(tier=Tier.FREE)
        with pytest.raises(PermissionError, match="analytics_dashboard"):
            engine.record_usage(total_messages=10, active_users=2)


# ---------------------------------------------------------------------------
# Marketplace tests
# ---------------------------------------------------------------------------

class TestMarketplace:
    def setup_method(self):
        self.mkt = Marketplace()

    def test_pricing_catalogue_contains_tiers(self):
        catalogue = self.mkt.get_pricing_catalogue()
        assert "Free" in catalogue
        assert "Intermediate" in catalogue
        assert "Premium" in catalogue

    def test_get_tier_details_free(self):
        details = self.mkt.get_tier_details(Tier.FREE)
        assert details["monthly_price_usd"] == 0.0
        assert "core_chat" in details["features"]

    def test_get_tier_details_premium(self):
        details = self.mkt.get_tier_details(Tier.PREMIUM)
        assert details["monthly_price_usd"] == 99.99
        assert "kimi_k_ai" in details["features"]

    def test_create_subscription(self):
        sub = self.mkt.create_subscription("user_1", Tier.PREMIUM)
        assert sub.user_id == "user_1"
        assert sub.tier == Tier.PREMIUM
        assert sub.status in ("active", "trialing")

    def test_cancel_subscription(self):
        self.mkt.create_subscription("user_2", Tier.INTERMEDIATE)
        sub = self.mkt.cancel_subscription("user_2")
        assert sub.status == "cancelled"

    def test_cancel_nonexistent_raises(self):
        with pytest.raises(KeyError):
            self.mkt.cancel_subscription("ghost_user")

    def test_get_subscription(self):
        self.mkt.create_subscription("user_3", Tier.FREE)
        sub = self.mkt.get_subscription("user_3")
        assert sub is not None
        assert sub.tier == Tier.FREE

    def test_checkout_session_free(self):
        session = self.mkt.create_checkout_session("user_4", Tier.FREE)
        assert session.amount_usd == 0.0
        assert session.tier == Tier.FREE

    def test_checkout_session_premium(self):
        session = self.mkt.create_checkout_session("user_5", Tier.PREMIUM)
        assert session.amount_usd == 99.99
        assert "kimi_k_ai" in session.metadata["features"]

    def test_list_templates_premium(self):
        templates = self.mkt.list_templates(Tier.PREMIUM)
        assert "b2b_landing" in templates
        assert "developer_portal" in templates
        assert "partner_brief" in templates

    def test_list_templates_blocked_on_free(self):
        with pytest.raises(PermissionError, match="marketing_doc_manager"):
            self.mkt.list_templates(Tier.FREE)

    def test_create_marketing_document(self):
        doc = self.mkt.create_marketing_document(
            tier=Tier.PREMIUM,
            template_key="b2b_landing",
            title="Q1 Campaign",
            brand_name="Dreamcobots",
        )
        assert doc.title == "Q1 Campaign"
        assert "Hero" in doc.content["sections"]

    def test_create_marketing_document_all_templates(self):
        for key in LAYOUT_TEMPLATES:
            doc = self.mkt.create_marketing_document(
                tier=Tier.PREMIUM,
                template_key=key,
                title=f"Test {key}",
            )
            assert doc.template_key == key

    def test_create_marketing_document_invalid_template(self):
        with pytest.raises(ValueError, match="Unknown template"):
            self.mkt.create_marketing_document(
                tier=Tier.PREMIUM,
                template_key="nonexistent_template",
                title="Bad Doc",
            )

    def test_get_marketing_document(self):
        doc = self.mkt.create_marketing_document(
            tier=Tier.PREMIUM, template_key="partner_brief", title="Partner Brief v1"
        )
        retrieved = self.mkt.get_document(doc.doc_id)
        assert retrieved is not None
        assert retrieved.title == "Partner Brief v1"

    def test_list_documents(self):
        self.mkt.create_marketing_document(
            tier=Tier.PREMIUM, template_key="enterprise_pitch", title="Enterprise Deck"
        )
        docs = self.mkt.list_documents()
        assert any(d["title"] == "Enterprise Deck" for d in docs)

    def test_white_label_configuration(self):
        config = self.mkt.configure_white_label(
            tier=Tier.PREMIUM,
            brand_name="AcmeCorp",
            primary_color="#FF5733",
        )
        assert config["brand_name"] == "AcmeCorp"
        assert "acmecorp" in config["custom_domain"]

    def test_white_label_blocked_on_intermediate(self):
        with pytest.raises(PermissionError, match="white_label"):
            self.mkt.configure_white_label(tier=Tier.INTERMEDIATE, brand_name="TestBrand")
