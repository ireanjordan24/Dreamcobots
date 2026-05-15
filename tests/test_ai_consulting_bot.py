"""
Tests for bots/ai_consulting_bot/tiers.py and bots/ai_consulting_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.ai_consulting_bot.tiers import AI_CONSULTING_FEATURES, get_ai_consulting_tier_info
from bots.ai_consulting_bot.bot import (
    AIConsultingBot,
    AIConsultingBotTierError,
    AIConsultingBotRequestLimitError,
    EXPERT_DOMAINS,
    ROADMAP_PHASES,
    SESSION_CAPS,
)


class TestAIConsultingTierInfo:
    def test_free_tier_info_keys(self):
        info = get_ai_consulting_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_ai_consulting_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        info = get_ai_consulting_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in AI_CONSULTING_FEATURES
            assert len(AI_CONSULTING_FEATURES[tier.value]) > 0

    def test_enterprise_has_more_features_than_free(self):
        free_count = len(AI_CONSULTING_FEATURES[Tier.FREE.value])
        ent_count = len(AI_CONSULTING_FEATURES[Tier.ENTERPRISE.value])
        assert ent_count > free_count


class TestAIConsultingBotExpertMatching:
    def test_default_tier_is_free(self):
        bot = AIConsultingBot()
        assert bot.tier == Tier.FREE

    def test_match_expert_returns_dict(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        result = bot.match_expert({"company_name": "TestCo", "industry": "retail"})
        assert isinstance(result, dict)

    def test_match_expert_free_keys(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        result = bot.match_expert({"company_name": "FreeCo"})
        for key in ("expert_id", "name", "domain", "experience_years", "tier"):
            assert key in result

    def test_match_expert_free_upgrade_hint(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        result = bot.match_expert({"company_name": "FreeCo"})
        assert "upgrade_hint" in result

    def test_match_expert_pro_no_upgrade_hint(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.match_expert({"company_name": "ProCo", "industry": "healthcare"})
        assert "upgrade_hint" not in result
        assert result["experience_years"] == 7

    def test_match_expert_enterprise_senior(self):
        bot = AIConsultingBot(tier=Tier.ENTERPRISE)
        result = bot.match_expert({"company_name": "EntCo", "industry": "finance"})
        assert result["experience_years"] == 12
        assert "goals_addressed" in result

    def test_unknown_industry_uses_general_domain(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.match_expert({"company_name": "Co", "industry": "underwater_basket_weaving"})
        assert result["domain"] == "general_ai_strategy"

    def test_request_count_increments(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        bot.match_expert({"company_name": "A"})
        assert bot._request_count == 1

    def test_request_limit_raises(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(AIConsultingBotRequestLimitError):
            bot.match_expert({"company_name": "Over"})


class TestAIConsultingBotSession:
    def test_book_session_returns_dict(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.book_session({
            "company_name": "Co",
            "expert_id": "expert-123",
            "topic": "AI Strategy",
        })
        assert isinstance(result, dict)

    def test_book_session_keys(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.book_session({"company_name": "Co", "topic": "Test"})
        for key in ("session_id", "company_name", "topic", "status", "agenda", "tier"):
            assert key in result

    def test_book_session_status_confirmed(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        result = bot.book_session({"company_name": "Co", "topic": "Test"})
        assert result["status"] == "confirmed"

    def test_free_session_cap_enforced(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        bot.book_session({"company_name": "Co", "topic": "First"})
        with pytest.raises(AIConsultingBotTierError):
            bot.book_session({"company_name": "Co", "topic": "Second"})

    def test_pro_session_cap_enforced(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        for i in range(SESSION_CAPS[Tier.PRO.value]):
            bot.book_session({"company_name": "Co", "topic": f"Session {i}"})
        with pytest.raises(AIConsultingBotTierError):
            bot.book_session({"company_name": "Co", "topic": "Over"})

    def test_enterprise_no_session_cap(self):
        bot = AIConsultingBot(tier=Tier.ENTERPRISE)
        for i in range(15):
            bot.book_session({"company_name": "Co", "topic": f"Session {i}"})
        assert len(bot._sessions) == 15

    def test_pro_session_has_transcript_url(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.book_session({"company_name": "Co", "topic": "Test"})
        assert "transcript_url" in result

    def test_free_session_no_transcript_url(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        result = bot.book_session({"company_name": "Co", "topic": "Test"})
        assert "transcript_url" not in result


class TestAIConsultingBotRoadmap:
    def test_free_tier_roadmap_raises(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        with pytest.raises(AIConsultingBotTierError):
            bot.generate_roadmap({"company_name": "FreeCo"})

    def test_pro_roadmap_returns_dict(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.generate_roadmap({
            "company_name": "ProCo",
            "industry": "manufacturing",
            "readiness_score": 60,
        })
        assert isinstance(result, dict)

    def test_roadmap_keys(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.generate_roadmap({"company_name": "Co", "readiness_score": 50})
        for key in ("roadmap_id", "company_name", "total_phases", "phases",
                    "estimated_total_weeks", "tier"):
            assert key in result

    def test_roadmap_phase_count(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.generate_roadmap({"company_name": "Co"})
        assert result["total_phases"] == len(ROADMAP_PHASES)
        assert len(result["phases"]) == len(ROADMAP_PHASES)

    def test_roadmap_total_weeks_positive(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.generate_roadmap({"company_name": "Co", "readiness_score": 80})
        assert result["estimated_total_weeks"] > 0

    def test_enterprise_roadmap_has_extra_fields(self):
        bot = AIConsultingBot(tier=Tier.ENTERPRISE)
        result = bot.generate_roadmap({"company_name": "EntCo", "readiness_score": 45})
        assert result.get("executive_briefing") is True
        assert result.get("change_management_playbook") is True

    def test_roadmap_increments_request_count(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        bot.generate_roadmap({"company_name": "Co"})
        assert bot._request_count == 1


class TestAIConsultingBotStats:
    def test_get_stats_keys(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        stats = bot.get_stats()
        for key in ("tier", "requests_used", "requests_remaining",
                    "sessions_booked", "sessions_remaining",
                    "roadmaps_generated", "buddy_integration"):
            assert key in stats

    def test_buddy_integration_true(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        assert bot.get_stats()["buddy_integration"] is True

    def test_sessions_remaining_decrements(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        stats_before = bot.get_stats()
        bot.book_session({"company_name": "Co", "topic": "Test"})
        stats_after = bot.get_stats()
        assert int(stats_after["sessions_remaining"]) < int(stats_before["sessions_remaining"])

    def test_enterprise_sessions_remaining_unlimited(self):
        bot = AIConsultingBot(tier=Tier.ENTERPRISE)
        assert bot.get_stats()["sessions_remaining"] == "unlimited"


class TestAIConsultingBotProcess:
    def test_process_match_expert(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.process({"command": "match_expert", "client": {"company_name": "Co"}})
        assert "expert_id" in result

    def test_process_book_session(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.process({"command": "book_session",
                              "session_request": {"company_name": "Co", "topic": "AI"}})
        assert "session_id" in result

    def test_process_generate_roadmap(self):
        bot = AIConsultingBot(tier=Tier.PRO)
        result = bot.process({"command": "generate_roadmap",
                              "company": {"company_name": "Co"}})
        assert "roadmap_id" in result

    def test_process_stats(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        result = bot.process({"command": "stats"})
        assert "tier" in result

    def test_process_unknown_command(self):
        bot = AIConsultingBot(tier=Tier.FREE)
        result = bot.process({"command": "unknown"})
        assert "error" in result
