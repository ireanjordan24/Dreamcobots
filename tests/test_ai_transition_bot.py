"""
Tests for bots/ai_transition_bot/tiers.py and bots/ai_transition_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.ai_transition_bot.tiers import AI_TRANSITION_FEATURES, get_ai_transition_tier_info
from bots.ai_transition_bot.bot import (
    AITransitionBot,
    AITransitionBotTierError,
    AITransitionBotRequestLimitError,
    ASSESSMENT_DIMENSIONS,
    TRAINING_LEVELS,
    INTEGRATION_PLATFORMS,
    FREE_MODULE_LIMIT,
    FREE_INTEGRATION_LIMIT,
)


class TestAITransitionTierInfo:
    def test_free_tier_info_keys(self):
        info = get_ai_transition_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_ai_transition_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        info = get_ai_transition_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in AI_TRANSITION_FEATURES
            assert len(AI_TRANSITION_FEATURES[tier.value]) > 0

    def test_enterprise_has_more_features_than_free(self):
        free_count = len(AI_TRANSITION_FEATURES[Tier.FREE.value])
        ent_count = len(AI_TRANSITION_FEATURES[Tier.ENTERPRISE.value])
        assert ent_count > free_count


class TestAITransitionBotAssessment:
    def test_default_tier_is_free(self):
        bot = AITransitionBot()
        assert bot.tier == Tier.FREE

    def test_assessment_returns_dict(self):
        bot = AITransitionBot(tier=Tier.FREE)
        result = bot.run_assessment({"name": "TestCo"})
        assert isinstance(result, dict)

    def test_assessment_free_keys(self):
        bot = AITransitionBot(tier=Tier.FREE)
        result = bot.run_assessment({"name": "TestCo"})
        for key in ("assessment_id", "company_name", "overall_score", "readiness_level", "tier"):
            assert key in result

    def test_assessment_pro_includes_dimensions(self):
        bot = AITransitionBot(tier=Tier.PRO)
        result = bot.run_assessment({
            "name": "ProCo",
            "industry": "retail",
            "scores": {dim: 60 for dim in ASSESSMENT_DIMENSIONS},
        })
        assert "dimension_scores" in result
        assert "recommendations" in result

    def test_assessment_enterprise_includes_dimensions(self):
        bot = AITransitionBot(tier=Tier.ENTERPRISE)
        result = bot.run_assessment({"name": "EntCo"})
        assert "dimension_scores" in result

    def test_readiness_level_advanced(self):
        bot = AITransitionBot(tier=Tier.PRO)
        result = bot.run_assessment({
            "name": "HighCo",
            "scores": {dim: 90 for dim in ASSESSMENT_DIMENSIONS},
        })
        assert result["readiness_level"] == "advanced"

    def test_readiness_level_beginner(self):
        bot = AITransitionBot(tier=Tier.PRO)
        result = bot.run_assessment({
            "name": "LowCo",
            "scores": {dim: 20 for dim in ASSESSMENT_DIMENSIONS},
        })
        assert result["readiness_level"] == "beginner"

    def test_assessment_increments_request_count(self):
        bot = AITransitionBot(tier=Tier.FREE)
        bot.run_assessment({"name": "A"})
        bot.run_assessment({"name": "B"})
        assert bot._request_count == 2

    def test_request_limit_raises(self):
        bot = AITransitionBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(AITransitionBotRequestLimitError):
            bot.run_assessment({"name": "Over"})


class TestAITransitionBotTraining:
    def test_enroll_beginner_free(self):
        bot = AITransitionBot(tier=Tier.FREE)
        result = bot.enroll_training({
            "employee_name": "Alice",
            "level": "beginner",
            "topic": "AI Basics",
        })
        assert result["status"] == "enrolled"
        assert result["level"] == "beginner"

    def test_enroll_returns_expected_keys(self):
        bot = AITransitionBot(tier=Tier.PRO)
        result = bot.enroll_training({"employee_name": "Bob", "level": "intermediate"})
        for key in ("enrollment_id", "employee_name", "level", "estimated_duration", "status", "tier"):
            assert key in result

    def test_free_tier_rejects_intermediate(self):
        bot = AITransitionBot(tier=Tier.FREE)
        with pytest.raises(AITransitionBotTierError):
            bot.enroll_training({"employee_name": "Carol", "level": "intermediate"})

    def test_free_tier_rejects_advanced(self):
        bot = AITransitionBot(tier=Tier.FREE)
        with pytest.raises(AITransitionBotTierError):
            bot.enroll_training({"employee_name": "Dave", "level": "advanced"})

    def test_pro_tier_rejects_advanced(self):
        bot = AITransitionBot(tier=Tier.PRO)
        with pytest.raises(AITransitionBotTierError):
            bot.enroll_training({"employee_name": "Eve", "level": "advanced"})

    def test_enterprise_allows_advanced(self):
        bot = AITransitionBot(tier=Tier.ENTERPRISE)
        result = bot.enroll_training({"employee_name": "Frank", "level": "advanced"})
        assert result["level"] == "advanced"

    def test_free_module_limit_enforced(self):
        bot = AITransitionBot(tier=Tier.FREE)
        for i in range(FREE_MODULE_LIMIT):
            bot.enroll_training({"employee_name": f"Emp{i}", "level": "beginner"})
        with pytest.raises(AITransitionBotTierError):
            bot.enroll_training({"employee_name": "Extra", "level": "beginner"})

    def test_invalid_level_defaults_to_beginner(self):
        bot = AITransitionBot(tier=Tier.FREE)
        result = bot.enroll_training({"employee_name": "Grace", "level": "expert"})
        assert result["level"] == "beginner"


class TestAITransitionBotIntegration:
    def test_activate_integration_returns_dict(self):
        bot = AITransitionBot(tier=Tier.FREE)
        result = bot.activate_integration({"platform": "crm"})
        assert isinstance(result, dict)

    def test_activate_integration_keys(self):
        bot = AITransitionBot(tier=Tier.PRO)
        result = bot.activate_integration({"platform": "erp", "workflow_name": "test"})
        for key in ("integration_id", "platform", "endpoint_url", "api_key_stub", "status", "tier"):
            assert key in result

    def test_activate_integration_status_active(self):
        bot = AITransitionBot(tier=Tier.FREE)
        result = bot.activate_integration({"platform": "hr"})
        assert result["status"] == "active"

    def test_unsupported_platform_raises(self):
        bot = AITransitionBot(tier=Tier.PRO)
        with pytest.raises(AITransitionBotTierError):
            bot.activate_integration({"platform": "unknown_platform"})

    def test_free_integration_limit_enforced(self):
        bot = AITransitionBot(tier=Tier.FREE)
        bot.activate_integration({"platform": "crm"})
        with pytest.raises(AITransitionBotTierError):
            bot.activate_integration({"platform": "erp"})

    def test_pro_integration_limit_enforced(self):
        bot = AITransitionBot(tier=Tier.PRO)
        for platform in INTEGRATION_PLATFORMS:
            bot.activate_integration({"platform": platform})
        with pytest.raises(AITransitionBotTierError):
            bot.activate_integration({"platform": "crm"})

    def test_enterprise_no_integration_limit(self):
        bot = AITransitionBot(tier=Tier.ENTERPRISE)
        for platform in INTEGRATION_PLATFORMS:
            bot.activate_integration({"platform": platform})
        # Should not raise — enterprise has no cap
        result = bot.activate_integration({"platform": "crm"})
        assert result["status"] == "active"


class TestAITransitionBotStats:
    def test_get_stats_keys(self):
        bot = AITransitionBot(tier=Tier.FREE)
        stats = bot.get_stats()
        for key in ("tier", "requests_used", "requests_remaining",
                    "assessments_run", "enrollments_created",
                    "integrations_active", "buddy_integration"):
            assert key in stats

    def test_buddy_integration_true(self):
        bot = AITransitionBot(tier=Tier.FREE)
        assert bot.get_stats()["buddy_integration"] is True

    def test_stats_counters_accurate(self):
        bot = AITransitionBot(tier=Tier.PRO)
        bot.run_assessment({"name": "Co"})
        bot.enroll_training({"employee_name": "H", "level": "beginner"})
        bot.activate_integration({"platform": "crm"})
        stats = bot.get_stats()
        assert stats["assessments_run"] == 1
        assert stats["enrollments_created"] == 1
        assert stats["integrations_active"] == 1

    def test_enterprise_requests_remaining_unlimited(self):
        bot = AITransitionBot(tier=Tier.ENTERPRISE)
        assert bot.get_stats()["requests_remaining"] == "unlimited"


class TestAITransitionBotProcess:
    def test_process_assess(self):
        bot = AITransitionBot(tier=Tier.PRO)
        result = bot.process({"command": "assess", "company": {"name": "ProcessCo"}})
        assert "assessment_id" in result

    def test_process_train(self):
        bot = AITransitionBot(tier=Tier.PRO)
        result = bot.process({"command": "train",
                              "request": {"employee_name": "Tester", "level": "beginner"}})
        assert "enrollment_id" in result

    def test_process_integrate(self):
        bot = AITransitionBot(tier=Tier.PRO)
        result = bot.process({"command": "integrate", "request": {"platform": "crm"}})
        assert "integration_id" in result

    def test_process_stats(self):
        bot = AITransitionBot(tier=Tier.FREE)
        result = bot.process({"command": "stats"})
        assert "tier" in result

    def test_process_unknown_command(self):
        bot = AITransitionBot(tier=Tier.FREE)
        result = bot.process({"command": "unknown"})
        assert "error" in result
