"""
Tests for bots/ai_level_up_bot/

Covers:
  - tiers.py
  - ai_companies_database.py
  - token_marketplace.py
  - ai_course_engine.py
  - ai_skill_tree.py
  - ai_agents_generator.py
  - ai_level_up_bot.py  (integration)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.ai_level_up_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_OPEN_SOURCE_MODELS,
    FEATURE_AI_COMPANIES_DATABASE,
    FEATURE_TOKEN_MARKETPLACE,
    FEATURE_COURSE_ENGINE,
    FEATURE_SKILL_TREE,
    FEATURE_AGENTS_GENERATOR,
    FEATURE_PREMIUM_MODELS,
    FEATURE_WHITE_LABEL,
)
from bots.ai_level_up_bot.ai_companies_database import (
    AICompanyDatabase,
    AITool,
    AICategory,
    PricingModel,
)
from bots.ai_level_up_bot.token_marketplace import (
    TokenMarketplace,
    ServiceType,
    ServicePricing,
    TokenTransaction,
    InsufficientTokensError,
    TokenMarketplaceError,
    get_service_pricing,
    list_all_pricing,
    DEFAULT_MARKUP,
    TOKEN_BUNDLES,
)
from bots.ai_level_up_bot.ai_course_engine import (
    AICourseEngine,
    CourseLevel,
    CourseModule,
    TeachingMode,
    AICourseEngineError,
)
from bots.ai_level_up_bot.ai_skill_tree import (
    AISkillTree,
    SkillNode,
    Badge,
    SkillRarity,
    SkillTreeError,
)
from bots.ai_level_up_bot.ai_agents_generator import (
    AIAgentsGenerator,
    CustomAgent,
    AgentPurpose,
    AgentStatus,
    AgentsGeneratorError,
    AgentLimitExceededError,
    AgentNotFoundError,
    PURPOSE_TOOL_TEMPLATES,
)
from bots.ai_level_up_bot.ai_level_up_bot import AILevelUpBot, AILevelUpBotError


# ===========================================================================
# Tiers
# ===========================================================================

class TestTierConfig:
    """Tests for tiers.py"""

    def test_four_tiers_present(self):
        assert set(TIER_CATALOGUE.keys()) == {"free", "starter", "pro", "enterprise"}

    def test_free_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_starter_price(self):
        assert get_tier_config(Tier.STARTER).price_usd_monthly == 29.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 99.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 399.0

    def test_free_max_course_level(self):
        assert get_tier_config(Tier.FREE).max_course_level == 1

    def test_enterprise_max_course_level(self):
        assert get_tier_config(Tier.ENTERPRISE).max_course_level == 10

    def test_enterprise_unlimited_agents(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_agents()
        assert cfg.max_agents is None

    def test_starter_agent_cap(self):
        assert get_tier_config(Tier.STARTER).max_agents == 5

    def test_markup_is_25_pct(self):
        for t in Tier:
            assert get_tier_config(t).token_markup == 0.25

    def test_list_tiers_returns_four(self):
        assert len(list_tiers()) == 4

    def test_upgrade_free_to_starter(self):
        nxt = get_upgrade_path(Tier.FREE)
        assert nxt is not None
        assert nxt.tier == Tier.STARTER

    def test_upgrade_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_has_course_engine(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_COURSE_ENGINE)

    def test_free_lacks_marketplace(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_TOKEN_MARKETPLACE)

    def test_starter_has_marketplace(self):
        assert get_tier_config(Tier.STARTER).has_feature(FEATURE_TOKEN_MARKETPLACE)

    def test_pro_has_premium_models(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_PREMIUM_MODELS)

    def test_enterprise_has_white_label(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_WHITE_LABEL)

    def test_has_feature_unknown_returns_false(self):
        assert not get_tier_config(Tier.FREE).has_feature("nonexistent_feature")


# ===========================================================================
# AI Companies Database
# ===========================================================================

class TestAICompanyDatabase:
    """Tests for ai_companies_database.py"""

    def setup_method(self):
        self.db = AICompanyDatabase()

    def test_seed_tools_loaded(self):
        assert self.db.count() > 0

    def test_get_tool_openai(self):
        tool = self.db.get_tool("OpenAI")
        assert tool.name == "OpenAI"
        assert tool.category == AICategory.CORE_AI

    def test_get_tool_case_insensitive(self):
        tool = self.db.get_tool("openai")
        assert tool.name == "OpenAI"

    def test_get_tool_not_found_raises(self):
        with pytest.raises(KeyError):
            self.db.get_tool("NonExistentToolXYZ")

    def test_search_returns_results(self):
        results = self.db.search("voice")
        assert len(results) > 0

    def test_search_empty_query(self):
        # Empty query should match everything (all tools have names)
        results = self.db.search("")
        assert len(results) >= self.db.count()

    def test_filter_by_category_core_ai(self):
        core = self.db.filter_by_category(AICategory.CORE_AI)
        assert all(t.category == AICategory.CORE_AI for t in core)
        assert len(core) >= 3

    def test_filter_by_pricing_free(self):
        free_tools = self.db.filter_by_pricing(PricingModel.FREE)
        assert all(t.pricing_model == PricingModel.FREE for t in free_tools)

    def test_filter_by_region_usa(self):
        usa_tools = self.db.filter_by_region("USA")
        assert all(t.region == "USA" for t in usa_tools)

    def test_filter_by_region_case_insensitive(self):
        tools_lower = self.db.filter_by_region("usa")
        tools_upper = self.db.filter_by_region("USA")
        assert len(tools_lower) == len(tools_upper)

    def test_add_tool_increases_count(self):
        before = self.db.count()
        new_tool = AITool(
            name="TestToolXYZ",
            category=AICategory.OTHER,
            pricing_model=PricingModel.FREE,
        )
        self.db.add_tool(new_tool)
        assert self.db.count() == before + 1

    def test_add_tool_retrievable(self):
        new_tool = AITool(
            name="UniqueTestTool999",
            category=AICategory.OTHER,
            pricing_model=PricingModel.PAY_PER_USE,
            token_cost_usd=0.05,
        )
        self.db.add_tool(new_tool)
        retrieved = self.db.get_tool("UniqueTestTool999")
        assert retrieved.token_cost_usd == 0.05

    def test_list_all_returns_copy(self):
        all_tools = self.db.list_all()
        assert len(all_tools) == self.db.count()

    def test_tool_is_free(self):
        tool = self.db.get_tool("Meta Llama")
        assert tool.is_free() is True

    def test_tool_not_free(self):
        tool = self.db.get_tool("OpenAI")
        assert tool.is_free() is False

    def test_tool_to_dict(self):
        tool = self.db.get_tool("OpenAI")
        d = tool.to_dict()
        assert d["name"] == "OpenAI"
        assert "capabilities" in d
        assert "pricing_model" in d

    def test_chinese_ai_present(self):
        chinese = self.db.filter_by_category(AICategory.CHINESE_AI)
        assert len(chinese) >= 3

    def test_image_ai_present(self):
        image = self.db.filter_by_category(AICategory.IMAGE_AI)
        assert len(image) >= 2

    def test_voice_ai_present(self):
        voice = self.db.filter_by_category(AICategory.VOICE_AI)
        assert len(voice) >= 2


# ===========================================================================
# Token Marketplace
# ===========================================================================

class TestTokenMarketplace:
    """Tests for token_marketplace.py"""

    def setup_method(self):
        self.mp = TokenMarketplace(user_id="test_user")

    def test_default_markup(self):
        assert self.mp.markup == DEFAULT_MARKUP

    def test_initial_balance_zero(self):
        assert self.mp.balance_usd == 0.0

    def test_purchase_tokens_credits_balance(self):
        self.mp.purchase_tokens(20.0)
        assert self.mp.balance_usd == 20.0

    def test_purchase_tokens_records_transaction(self):
        self.mp.purchase_tokens(10.0)
        txs = self.mp.get_transactions("purchase")
        assert len(txs) == 1

    def test_purchase_zero_raises(self):
        with pytest.raises(TokenMarketplaceError):
            self.mp.purchase_tokens(0.0)

    def test_purchase_negative_raises(self):
        with pytest.raises(TokenMarketplaceError):
            self.mp.purchase_tokens(-5.0)

    def test_gpt_pricing(self):
        pricing = get_service_pricing(ServiceType.GPT)
        assert pricing.base_cost_usd == 1.0
        assert pricing.dreamco_price_usd == pytest.approx(1.25)

    def test_image_pricing(self):
        pricing = get_service_pricing(ServiceType.IMAGE_GENERATION)
        assert pricing.base_cost_usd == pytest.approx(0.10)
        assert pricing.dreamco_price_usd == pytest.approx(0.125)

    def test_voice_pricing(self):
        pricing = get_service_pricing(ServiceType.VOICE_GENERATION)
        assert pricing.base_cost_usd == pytest.approx(0.20)
        assert pricing.dreamco_price_usd == pytest.approx(0.25)

    def test_profit_per_unit_gpt(self):
        pricing = get_service_pricing(ServiceType.GPT)
        assert pricing.profit_per_unit == pytest.approx(0.25)

    def test_list_all_pricing_returns_three(self):
        assert len(list_all_pricing()) == 3

    def test_use_service_deducts_balance(self):
        self.mp.purchase_tokens(10.0)
        self.mp.use_service("gpt", units=1)
        assert self.mp.balance_usd == pytest.approx(10.0 - 1.25)

    def test_use_service_string_input(self):
        self.mp.purchase_tokens(5.0)
        result = self.mp.use_service("image_generation", units=2)
        assert result["service"] == "image_generation"

    def test_use_service_enum_input(self):
        self.mp.purchase_tokens(5.0)
        result = self.mp.use_service(ServiceType.VOICE_GENERATION, units=1)
        assert result["service"] == "voice_generation"

    def test_use_service_insufficient_balance(self):
        with pytest.raises(InsufficientTokensError):
            self.mp.use_service("gpt", units=1)

    def test_use_service_unknown_raises(self):
        self.mp.purchase_tokens(100.0)
        with pytest.raises(TokenMarketplaceError):
            self.mp.use_service("unknown_service")

    def test_use_service_records_transaction(self):
        self.mp.purchase_tokens(5.0)
        self.mp.use_service("gpt", units=1)
        txs = self.mp.get_transactions("usage")
        assert len(txs) == 1

    def test_billing_summary_structure(self):
        self.mp.purchase_tokens(50.0)
        self.mp.use_service("gpt", units=2)
        summary = self.mp.billing_summary()
        assert "balance_usd" in summary
        assert "total_purchased_usd" in summary
        assert "total_spent_usd" in summary
        assert "total_profit_usd" in summary

    def test_is_low_balance_true(self):
        self.mp.purchase_tokens(3.0)
        assert self.mp.is_low_balance() is True

    def test_is_low_balance_false(self):
        self.mp.purchase_tokens(100.0)
        assert self.mp.is_low_balance() is False

    def test_bundle_bonus_applied(self):
        # $50 bundle should get 5% bonus
        result = self.mp.purchase_tokens(50.0)
        assert result["bonus_pct"] == 5.0
        assert result["tokens_credited_usd"] == pytest.approx(52.5)

    def test_no_bonus_small_purchase(self):
        result = self.mp.purchase_tokens(5.0)
        assert result["bonus_pct"] == 0.0

    def test_transaction_ids_unique(self):
        self.mp.purchase_tokens(100.0)
        self.mp.use_service("gpt", units=1)
        self.mp.use_service("image_generation", units=2)
        ids = {tx.transaction_id for tx in self.mp.transactions}
        assert len(ids) == 3

    def test_profit_tracked(self):
        self.mp.purchase_tokens(100.0)
        self.mp.use_service("gpt", units=4)
        # 4 * $0.25 profit = $1.00
        assert self.mp.total_profit_usd == pytest.approx(1.0)

    def test_get_transactions_all(self):
        self.mp.purchase_tokens(50.0)
        self.mp.use_service("gpt")
        all_txs = self.mp.get_transactions()
        assert len(all_txs) == 2

    def test_initial_balance_parameter(self):
        mp2 = TokenMarketplace(user_id="u2", initial_balance=25.0)
        assert mp2.balance_usd == 25.0


# ===========================================================================
# AI Course Engine
# ===========================================================================

class TestAICourseEngine:
    """Tests for ai_course_engine.py"""

    def setup_method(self):
        self.engine = AICourseEngine()

    def test_ten_levels(self):
        assert len(self.engine.list_levels()) == 10

    def test_level_one_title(self):
        level = self.engine.get_level(1)
        assert level.title == "AI Basics"

    def test_level_ten_title(self):
        level = self.engine.get_level(10)
        assert "Superintelligence" in level.title

    def test_invalid_level_raises(self):
        with pytest.raises(AICourseEngineError):
            self.engine.get_level(0)

    def test_invalid_level_11_raises(self):
        with pytest.raises(AICourseEngineError):
            self.engine.get_level(11)

    def test_level_has_modules(self):
        for lv in self.engine.list_levels():
            assert lv.module_count() >= 1

    def test_level_one_no_prerequisite(self):
        assert self.engine.get_level(1).prerequisite_level is None

    def test_level_two_prerequisite_is_one(self):
        assert self.engine.get_level(2).prerequisite_level == 1

    def test_level_total_xp_positive(self):
        for lv in self.engine.list_levels():
            assert lv.total_xp > 0

    def test_level_total_duration_positive(self):
        for lv in self.engine.list_levels():
            assert lv.total_duration_minutes > 0

    def test_certificate_name_nonempty(self):
        for lv in self.engine.list_levels():
            assert lv.certificate_name != ""

    def test_complete_module_awards_xp(self):
        result = self.engine.complete_module("u1", 1, "What is Artificial Intelligence?")
        assert result["xp_awarded"] > 0

    def test_complete_module_twice_no_double_xp(self):
        self.engine.complete_module("u1", 1, "What is Artificial Intelligence?")
        result2 = self.engine.complete_module("u1", 1, "What is Artificial Intelligence?")
        assert result2["xp_awarded"] == 0

    def test_complete_module_unknown_raises(self):
        with pytest.raises(AICourseEngineError):
            self.engine.complete_module("u1", 1, "Nonexistent Module Title")

    def test_complete_all_modules_marks_level_complete(self):
        level = self.engine.get_level(1)
        for module in level.modules:
            result = self.engine.complete_module("u_complete", 1, module.title)
        assert result["level_complete"] is True

    def test_complete_level_awards_certificate(self):
        level = self.engine.get_level(1)
        for module in level.modules:
            result = self.engine.complete_module("u_cert", 1, module.title)
        assert result["certificate"] == level.certificate_name

    def test_get_user_progress_structure(self):
        progress = self.engine.get_user_progress("new_user")
        assert "total_xp" in progress
        assert "levels" in progress
        assert len(progress["levels"]) == 10

    def test_is_level_unlocked_level_one(self):
        assert self.engine.is_level_unlocked("u1", 1, 10) is True

    def test_is_level_unlocked_exceeds_max(self):
        assert self.engine.is_level_unlocked("u1", 5, 3) is False

    def test_is_level_unlocked_prereq_not_met(self):
        assert self.engine.is_level_unlocked("new_user", 2, 10) is False

    def test_is_level_unlocked_after_completing_prereq(self):
        level = self.engine.get_level(1)
        for module in level.modules:
            self.engine.complete_module("u_unlock", 1, module.title)
        assert self.engine.is_level_unlocked("u_unlock", 2, 10) is True


# ===========================================================================
# AI Skill Tree
# ===========================================================================

class TestAISkillTree:
    """Tests for ai_skill_tree.py"""

    def setup_method(self):
        self.tree = AISkillTree(user_id="tree_user")

    def test_initial_xp_zero(self):
        assert self.tree.xp == 0

    def test_initial_level_one(self):
        assert self.tree.level == 1

    def test_award_xp_increases_total(self):
        self.tree.award_xp(100)
        assert self.tree.xp == 100

    def test_award_xp_zero_raises(self):
        with pytest.raises(SkillTreeError):
            self.tree.award_xp(0)

    def test_award_xp_negative_raises(self):
        with pytest.raises(SkillTreeError):
            self.tree.award_xp(-50)

    def test_level_up_occurs(self):
        result = self.tree.award_xp(250)
        assert result["leveled_up"] is True
        assert self.tree.level > 1

    def test_badge_awarded_on_first_100_xp(self):
        result = self.tree.award_xp(100)
        assert "First Step" in result["new_badges"]

    def test_list_skills_nonempty(self):
        assert len(self.tree.list_skills()) > 0

    def test_skills_start_locked(self):
        for skill in self.tree.list_skills():
            assert skill.unlocked is False

    def test_unlock_skill_with_sufficient_xp(self):
        self.tree.award_xp(200)
        result = self.tree.unlock_skill("ai_fundamentals")
        assert result["status"] == "unlocked"

    def test_unlock_skill_insufficient_xp_raises(self):
        with pytest.raises(SkillTreeError):
            self.tree.unlock_skill("ai_fundamentals")

    def test_unlock_skill_already_unlocked(self):
        self.tree.award_xp(200)
        self.tree.unlock_skill("ai_fundamentals")
        result = self.tree.unlock_skill("ai_fundamentals")
        assert result["status"] == "already_unlocked"

    def test_unlock_skill_prerequisites_not_met(self):
        self.tree.award_xp(5000)
        with pytest.raises(SkillTreeError):
            self.tree.unlock_skill("prompt_engineering_basics")

    def test_unlock_prerequisite_chain(self):
        self.tree.award_xp(5000)
        self.tree.unlock_skill("ai_fundamentals")
        self.tree.unlock_skill("ai_tool_explorer")
        result = self.tree.unlock_skill("prompt_engineering_basics")
        assert result["status"] == "unlocked"

    def test_get_total_token_discount_increases_on_unlock(self):
        self.tree.award_xp(5000)
        before = self.tree.get_total_token_discount()
        self.tree.unlock_skill("ai_fundamentals")
        after = self.tree.get_total_token_discount()
        assert after >= before  # ai_fundamentals has 0 discount; but should not decrease

    def test_token_discount_from_skill(self):
        self.tree.award_xp(5000)
        self.tree.unlock_skill("ai_fundamentals")
        self.tree.unlock_skill("ai_tool_explorer")
        discount = self.tree.get_total_token_discount()
        assert discount == pytest.approx(1.0)

    def test_skill_tree_summary_structure(self):
        summary = self.tree.skill_tree_summary()
        assert "xp" in summary
        assert "level" in summary
        assert "skills_unlocked" in summary
        assert "token_discount_pct" in summary
        assert "badges_earned" in summary

    def test_list_unlocked_skills_empty_initially(self):
        assert self.tree.list_skills(unlocked_only=True) == []

    def test_list_badges_nonempty(self):
        assert len(self.tree.list_badges()) > 0

    def test_no_badges_earned_initially(self):
        assert self.tree.list_badges(earned_only=True) == []

    def test_get_skill_unknown_raises(self):
        with pytest.raises(SkillTreeError):
            self.tree.get_skill("nonexistent_skill_xyz")

    def test_unlock_skill_unknown_raises(self):
        with pytest.raises(SkillTreeError):
            self.tree.unlock_skill("nonexistent_skill_xyz")

    def test_xp_to_next_level_decreases_as_xp_grows(self):
        result1 = self.tree.award_xp(50)
        xp_to_next_1 = result1["xp_to_next_level"]
        result2 = self.tree.award_xp(50)
        xp_to_next_2 = result2["xp_to_next_level"]
        # After levelling up xp_to_next resets; before level-up it should decrease
        assert xp_to_next_1 > xp_to_next_2 or result2["leveled_up"]


# ===========================================================================
# AI Agents Generator
# ===========================================================================

class TestAIAgentsGenerator:
    """Tests for ai_agents_generator.py"""

    def setup_method(self):
        self.gen = AIAgentsGenerator(user_id="agent_user", max_agents=5)

    def test_create_agent_returns_custom_agent(self):
        agent = self.gen.create_agent(
            name="Marketing Bot",
            purpose=AgentPurpose.MARKETING.value,
        )
        assert isinstance(agent, CustomAgent)

    def test_create_agent_default_tools_from_template(self):
        agent = self.gen.create_agent(
            name="Research Bot",
            purpose=AgentPurpose.RESEARCH.value,
        )
        assert "OpenAI" in agent.tools or len(agent.tools) > 0

    def test_create_agent_custom_tools(self):
        agent = self.gen.create_agent(
            name="Custom Bot",
            purpose=AgentPurpose.CUSTOM.value,
            tools=["OpenAI", "ElevenLabs"],
        )
        assert "OpenAI" in agent.tools
        assert "ElevenLabs" in agent.tools

    def test_create_agent_has_id(self):
        agent = self.gen.create_agent(name="Test", purpose="Marketing")
        assert agent.agent_id != ""

    def test_create_agent_draft_status(self):
        agent = self.gen.create_agent(name="Test", purpose="Coding")
        assert agent.status == AgentStatus.DRAFT

    def test_agent_limit_exceeded(self):
        gen_limited = AIAgentsGenerator(user_id="u_lim", max_agents=1)
        gen_limited.create_agent(name="Bot1", purpose="Marketing")
        with pytest.raises(AgentLimitExceededError):
            gen_limited.create_agent(name="Bot2", purpose="Coding")

    def test_unlimited_agents(self):
        gen_unlimited = AIAgentsGenerator(user_id="u_unlim", max_agents=None)
        for i in range(20):
            gen_unlimited.create_agent(name=f"Bot{i}", purpose="Marketing")
        assert gen_unlimited.agent_count() == 20

    def test_get_agent_retrieves_by_id(self):
        agent = self.gen.create_agent(name="Finder", purpose="Marketing")
        retrieved = self.gen.get_agent(agent.agent_id)
        assert retrieved.name == "Finder"

    def test_get_agent_not_found_raises(self):
        with pytest.raises(AgentNotFoundError):
            self.gen.get_agent("nonexistent-id-xyz")

    def test_list_agents_returns_all(self):
        self.gen.create_agent(name="A", purpose="Marketing")
        self.gen.create_agent(name="B", purpose="Coding")
        assert len(self.gen.list_agents()) == 2

    def test_list_agents_filtered_by_status(self):
        agent = self.gen.create_agent(name="Active", purpose="Marketing")
        self.gen.activate_agent(agent.agent_id)
        active = self.gen.list_agents(status=AgentStatus.ACTIVE)
        assert len(active) == 1

    def test_activate_agent(self):
        agent = self.gen.create_agent(name="Activate Me", purpose="Marketing")
        result = self.gen.activate_agent(agent.agent_id)
        assert result["status"] == AgentStatus.ACTIVE.value

    def test_pause_agent(self):
        agent = self.gen.create_agent(name="Pause Me", purpose="Marketing")
        self.gen.activate_agent(agent.agent_id)
        result = self.gen.pause_agent(agent.agent_id)
        assert result["status"] == AgentStatus.PAUSED.value

    def test_pause_non_active_raises(self):
        agent = self.gen.create_agent(name="Draft Agent", purpose="Marketing")
        with pytest.raises(AgentsGeneratorError):
            self.gen.pause_agent(agent.agent_id)

    def test_archive_agent(self):
        agent = self.gen.create_agent(name="Archive Me", purpose="Marketing")
        result = self.gen.archive_agent(agent.agent_id)
        assert result["status"] == AgentStatus.ARCHIVED.value

    def test_archived_agent_not_counted(self):
        agent = self.gen.create_agent(name="To Archive", purpose="Marketing")
        self.gen.archive_agent(agent.agent_id)
        assert self.gen.agent_count() == 0

    def test_run_task_on_active_agent(self):
        agent = self.gen.create_agent(name="Worker", purpose="Marketing")
        self.gen.activate_agent(agent.agent_id)
        result = self.gen.run_task(agent.agent_id, "Write a tweet")
        assert result["status"] == "completed"
        assert result["tasks_run_total"] == 1

    def test_run_task_on_inactive_raises(self):
        agent = self.gen.create_agent(name="Idle", purpose="Marketing")
        with pytest.raises(AgentsGeneratorError):
            self.gen.run_task(agent.agent_id, "Write a tweet")

    def test_update_agent_name(self):
        agent = self.gen.create_agent(name="OldName", purpose="Marketing")
        updated = self.gen.update_agent(agent.agent_id, name="NewName")
        assert updated.name == "NewName"

    def test_update_agent_invalid_field_raises(self):
        agent = self.gen.create_agent(name="Bot", purpose="Marketing")
        with pytest.raises(AgentsGeneratorError):
            self.gen.update_agent(agent.agent_id, status="active")

    def test_get_purpose_template_marketing(self):
        tools = self.gen.get_purpose_template("Marketing")
        assert len(tools) > 0

    def test_get_purpose_template_unknown(self):
        tools = self.gen.get_purpose_template("unknown_purpose_xyz")
        assert tools == []

    def test_list_purposes_nonempty(self):
        assert len(self.gen.list_purposes()) > 0

    def test_reactivate_archived_raises(self):
        agent = self.gen.create_agent(name="Dead", purpose="Marketing")
        self.gen.archive_agent(agent.agent_id)
        with pytest.raises(AgentsGeneratorError):
            self.gen.activate_agent(agent.agent_id)

    def test_system_prompt_generated(self):
        agent = self.gen.create_agent(name="Promo Bot", purpose="Marketing")
        assert len(agent.system_prompt) > 0

    def test_custom_system_prompt_preserved(self):
        agent = self.gen.create_agent(
            name="Custom", purpose="Marketing", system_prompt="Custom instructions."
        )
        assert agent.system_prompt == "Custom instructions."


# ===========================================================================
# AI Level-Up Bot (integration)
# ===========================================================================

class TestAILevelUpBot:
    """Integration tests for ai_level_up_bot.py"""

    def setup_method(self):
        self.bot = AILevelUpBot(user_id="int_user", tier=Tier.ENTERPRISE)

    def test_run_prints(self, capsys):
        self.bot.run()
        captured = capsys.readouterr()
        assert "AI Level Up Bot" in captured.out

    def test_teach_ai_tool(self):
        result = self.bot.teach_ai_tool("OpenAI")
        assert result["tool"] == "OpenAI"
        assert "capabilities" in result

    def test_search_tools(self):
        results = self.bot.search_tools("image")
        assert len(results) > 0

    def test_purchase_and_use_tokens(self):
        self.bot.purchase_tokens(50.0)
        result = self.bot.use_service("gpt", units=1)
        assert result["cost_usd"] == pytest.approx(1.25)

    def test_token_balance_after_purchase(self):
        self.bot.purchase_tokens(100.0)
        # $100 purchase qualifies for the $100 bundle → 10% bonus → $110 credited
        assert self.bot.token_balance() == pytest.approx(110.0)

    def test_billing_summary(self):
        self.bot.purchase_tokens(10.0)
        summary = self.bot.billing_summary()
        assert summary["total_purchased_usd"] == pytest.approx(10.0)

    def test_pricing_overview(self):
        prices = self.bot.pricing_overview()
        assert len(prices) == 3
        services = {p["service"] for p in prices}
        assert "gpt" in services

    def test_get_course_level(self):
        level = self.bot.get_course_level(1)
        assert level["title"] == "AI Basics"
        assert len(level["modules"]) > 0

    def test_complete_module_and_get_xp(self):
        result = self.bot.complete_module(1, "What is Artificial Intelligence?")
        assert result["xp_awarded"] > 0

    def test_complete_module_updates_skill_tree(self):
        self.bot.complete_module(1, "What is Artificial Intelligence?")
        summary = self.bot.skill_tree_summary()
        assert summary["xp"] > 0

    def test_course_progress_returns_all_levels(self):
        progress = self.bot.course_progress()
        assert len(progress["levels"]) == 10

    def test_award_xp(self):
        result = self.bot.award_xp(500)
        assert result["total_xp"] == 500

    def test_unlock_skill_flow(self):
        self.bot.award_xp(5000)
        result = self.bot.unlock_skill("ai_fundamentals")
        assert result["status"] == "unlocked"

    def test_skill_tree_summary(self):
        summary = self.bot.skill_tree_summary()
        assert "xp" in summary

    def test_create_agent(self):
        result = self.bot.create_agent(name="My Bot", purpose="Marketing")
        assert result["name"] == "My Bot"
        assert result["purpose"] == "Marketing"

    def test_list_agents(self):
        self.bot.create_agent(name="Bot A", purpose="Coding")
        agents = self.bot.list_agents()
        assert len(agents) >= 1

    def test_activate_and_run_agent(self):
        agent_dict = self.bot.create_agent(name="Worker", purpose="Research")
        agent_id = agent_dict["agent_id"]
        self.bot.activate_agent(agent_id)
        result = self.bot.run_agent_task(agent_id, "Summarise AI trends")
        assert result["status"] == "completed"

    def test_tier_info(self):
        info = self.bot.tier_info()
        assert info["tier"] == "enterprise"
        assert info["max_course_level"] == 10

    def test_upgrade_info_enterprise_none(self):
        assert self.bot.upgrade_info() is None

    def test_upgrade_info_starter(self):
        bot = AILevelUpBot(user_id="u2", tier=Tier.STARTER)
        info = bot.upgrade_info()
        assert info is not None
        assert info["tier"] == "pro"

    def test_free_tier_blocks_marketplace(self):
        bot = AILevelUpBot(user_id="free_user", tier=Tier.FREE)
        with pytest.raises(AILevelUpBotError):
            bot.purchase_tokens(10.0)

    def test_free_tier_allows_course_engine(self):
        bot = AILevelUpBot(user_id="free_user2", tier=Tier.FREE)
        level = bot.get_course_level(1)
        assert level["level_number"] == 1

    def test_free_tier_blocks_level_2(self):
        bot = AILevelUpBot(user_id="free_user3", tier=Tier.FREE)
        with pytest.raises(AILevelUpBotError):
            bot.complete_module(2, "Prompt Anatomy")

    def test_chat_tier_response(self):
        result = self.bot.chat("What is my tier?")
        assert "enterprise" in result["message"].lower() or "Enterprise" in result["message"]

    def test_chat_pricing_response(self):
        result = self.bot.chat("Show me the token pricing")
        assert "gpt" in result["message"].lower()

    def test_chat_course_response(self):
        result = self.bot.chat("Show me the course levels")
        assert "Level" in result["message"]

    def test_chat_skill_response(self):
        result = self.bot.chat("What is my XP and skill progress?")
        assert "Level" in result["message"] or "XP" in result["message"]

    def test_chat_balance_response(self):
        result = self.bot.chat("What is my token balance?")
        assert "balance" in result["message"].lower()

    def test_chat_upgrade_enterprise(self):
        result = self.bot.chat("Can I upgrade my plan?")
        assert "top-tier" in result["message"].lower() or "already" in result["message"].lower()

    def test_chat_upgrade_starter(self):
        bot = AILevelUpBot(user_id="u_start", tier=Tier.STARTER)
        result = bot.chat("upgrade plan")
        assert "Pro" in result["message"] or "pro" in result["message"]

    def test_chat_default_response(self):
        result = self.bot.chat("Hello there!")
        assert "bot" in result
        assert "message" in result

    def test_bot_name_and_version(self):
        assert AILevelUpBot.bot_name == "AI Level Up Bot"
        assert AILevelUpBot.version == "1.0"

    def test_tools_by_category(self):
        results = self.bot.tools_by_category(AICategory.VOICE_AI)
        assert all(t["category"] == AICategory.VOICE_AI.value for t in results)
