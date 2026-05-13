"""
Tests for bots/onboarding_bot/onboarding_bot.py

Covers:
  1. Session creation and retrieval
  2. Wizard step prompting
  3. Answer submission — all fields
  4. Option validation
  5. Bot recommendation
  6. Action plan generation
  7. Configuration generation
  8. Follow-up scheduling
  9. Complete onboarding flow (end-to-end)
  10. Dashboard and capabilities
  11. Error paths
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.onboarding_bot.onboarding_bot import (
    OnboardingBot,
    OnboardingSession,
    OnboardingStage,
    BusinessIndustry,
    BusinessStage,
    _WIZARD_STEPS,
    _INDUSTRY_BOT_MAP,
    _STAGE_EXTRAS,
)


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------


class TestSessionManagement:
    def setup_method(self):
        self.bot = OnboardingBot(buddy_name="TestBuddy")

    def test_start_session_returns_session(self):
        session = self.bot.start_session("user1")
        assert isinstance(session, OnboardingSession)
        assert session.user_id == "user1"
        assert not session.completed

    def test_start_session_stored(self):
        session = self.bot.start_session("user2")
        assert self.bot.get_session(session.session_id) is session

    def test_get_session_nonexistent_returns_none(self):
        assert self.bot.get_session("ghost") is None

    def test_initial_stage_is_welcome(self):
        session = self.bot.start_session("u")
        assert session.current_stage == OnboardingStage.WELCOME


# ---------------------------------------------------------------------------
# Wizard prompting
# ---------------------------------------------------------------------------


class TestWizardPrompting:
    def setup_method(self):
        self.bot = OnboardingBot()
        self.session = self.bot.start_session("dev")

    def test_get_current_prompt_returns_dict(self):
        prompt = self.bot.get_current_prompt(self.session.session_id)
        assert "prompt" in prompt
        assert "field_key" in prompt

    def test_first_prompt_is_business_name(self):
        prompt = self.bot.get_current_prompt(self.session.session_id)
        assert prompt["field_key"] == "business_name"

    def test_buddy_message_includes_buddy_name(self):
        bot = OnboardingBot(buddy_name="Sparky")
        session = bot.start_session("u")
        prompt = bot.get_current_prompt(session.session_id)
        assert "Sparky" in prompt["buddy_message"]

    def test_get_prompt_on_completed_session(self):
        session = self.bot.start_session("done_user")
        session.completed = True
        result = self.bot.get_current_prompt(session.session_id)
        assert result.get("completed") is True

    def test_missing_session_raises(self):
        with pytest.raises(KeyError):
            self.bot.get_current_prompt("nonexistent")


# ---------------------------------------------------------------------------
# Answer submission
# ---------------------------------------------------------------------------


class TestAnswerSubmission:
    def setup_method(self):
        self.bot = OnboardingBot()
        self.session = self.bot.start_session("tester")

    def test_submit_business_name(self):
        result = self.bot.submit_answer(self.session.session_id, "DreamTech Inc")
        assert "prompt" in result or "completed" in result
        assert self.session.profile.business_name == "DreamTech Inc"

    def test_submit_industry_valid(self):
        # Advance past business_name step first
        self.bot.submit_answer(self.session.session_id, "MyBiz")
        result = self.bot.submit_answer(self.session.session_id, "technology")
        assert self.session.profile.industry == "technology"

    def test_submit_industry_invalid_option(self):
        self.bot.submit_answer(self.session.session_id, "MyBiz")
        result = self.bot.submit_answer(self.session.session_id, "underwater_basket_weaving")
        assert "error" in result

    def test_submit_team_size_as_int(self):
        self.bot.submit_answer(self.session.session_id, "ACME")
        self.bot.submit_answer(self.session.session_id, "retail")
        self.bot.submit_answer(self.session.session_id, "startup")
        self.bot.submit_answer(self.session.session_id, "5")
        assert self.session.profile.team_size == 5

    def test_submit_goals_parsed_as_list(self):
        # Fast-forward to goals step
        self.bot.submit_answer(self.session.session_id, "Biz")
        self.bot.submit_answer(self.session.session_id, "finance")
        self.bot.submit_answer(self.session.session_id, "startup")
        self.bot.submit_answer(self.session.session_id, "3")
        result = self.bot.submit_answer(self.session.session_id, "grow revenue, hire team, launch app")
        assert len(self.session.profile.goals) == 3

    def test_submit_on_completed_session(self):
        session = self.bot.start_session("done")
        session.completed = True
        result = self.bot.submit_answer(session.session_id, "anything")
        assert result.get("completed") is True


# ---------------------------------------------------------------------------
# Bot recommendation
# ---------------------------------------------------------------------------


class TestBotRecommendation:
    def setup_method(self):
        self.bot = OnboardingBot()

    def test_recommend_bots_returns_list(self):
        session = self.bot.start_session("u")
        session.profile.industry = "technology"
        session.profile.stage = "startup"
        recs = self.bot.recommend_bots(session.session_id)
        assert isinstance(recs, list)
        assert len(recs) > 0

    def test_recommend_bots_includes_buddy_core(self):
        session = self.bot.start_session("u")
        session.profile.industry = "education"
        session.profile.stage = "growth"
        recs = self.bot.recommend_bots(session.session_id)
        assert "buddy_bot" in recs

    def test_recommend_bots_stored_on_session(self):
        session = self.bot.start_session("u")
        session.profile.industry = "finance"
        session.profile.stage = "scale"
        self.bot.recommend_bots(session.session_id)
        assert len(session.recommended_bots) > 0

    def test_all_industries_have_recommendations(self):
        for industry in BusinessIndustry:
            session = self.bot.start_session(f"u_{industry.value}")
            session.profile.industry = industry.value
            session.profile.stage = BusinessStage.STARTUP.value
            recs = self.bot.recommend_bots(session.session_id)
            assert len(recs) > 0


# ---------------------------------------------------------------------------
# Action plan, config, and follow-ups
# ---------------------------------------------------------------------------


class TestPlanAndConfig:
    def setup_method(self):
        self.bot = OnboardingBot()
        self.session = self.bot.start_session("biz")
        self.session.profile.business_name = "TestCo"
        self.session.profile.industry = "technology"
        self.session.profile.stage = "startup"
        self.session.profile.goals = ["grow", "automate"]
        self.session.profile.monthly_budget_usd = 2000.0
        self.bot.recommend_bots(self.session.session_id)

    def test_generate_action_plan_returns_list(self):
        plan = self.bot.generate_action_plan(self.session.session_id)
        assert isinstance(plan, list)
        assert len(plan) >= 5

    def test_action_plan_stored(self):
        self.bot.generate_action_plan(self.session.session_id)
        assert len(self.session.action_plan) > 0

    def test_generate_config_returns_dict(self):
        config = self.bot.generate_config(self.session.session_id)
        assert "dreamcobots_config" in config

    def test_config_contains_business_name(self):
        config = self.bot.generate_config(self.session.session_id)
        assert config["dreamcobots_config"]["business_name"] == "TestCo"

    def test_config_tier_pro_for_2000_budget(self):
        config = self.bot.generate_config(self.session.session_id)
        assert config["dreamcobots_config"]["budget_tier"] == "pro"

    def test_config_tier_enterprise_for_5000_budget(self):
        self.session.profile.monthly_budget_usd = 5000
        config = self.bot.generate_config(self.session.session_id)
        assert config["dreamcobots_config"]["budget_tier"] == "enterprise"

    def test_schedule_followups_returns_4_events(self):
        followups = self.bot.schedule_followups(self.session.session_id)
        assert len(followups) == 4

    def test_followup_days_ordered(self):
        followups = self.bot.schedule_followups(self.session.session_id)
        days = [f["days_after"] for f in followups]
        assert days == sorted(days)


# ---------------------------------------------------------------------------
# End-to-end complete flow
# ---------------------------------------------------------------------------


class TestEndToEndFlow:
    def test_complete_onboarding(self):
        bot = OnboardingBot(buddy_name="Buddy")
        session = bot.start_session("enterprise_user")

        answers = [
            "AcmeCorp",           # business_name
            "technology",         # industry
            "scale",              # stage
            "50",                 # team_size
            "automate ops, scale revenue, launch SaaS",  # goals
            "10000",              # monthly_budget_usd
            "ceo@acme.com",       # primary_contact_email
        ]

        result = None
        for answer in answers:
            result = bot.submit_answer(session.session_id, answer)

        assert result is not None
        assert result.get("completed") is True
        assert len(result["recommended_bots"]) > 0
        assert len(result["action_plan"]) >= 5
        assert "dreamcobots_config" in result["config"]
        assert len(result["followup_schedule"]) == 4
        assert "Buddy" in result["buddy_message"]
        assert session.completed is True


# ---------------------------------------------------------------------------
# Dashboard and capabilities
# ---------------------------------------------------------------------------


class TestDashboard:
    def setup_method(self):
        self.bot = OnboardingBot()

    def test_dashboard_keys(self):
        dash = self.bot.dashboard()
        for key in ("total_sessions", "completed", "in_progress", "buddy_name"):
            assert key in dash

    def test_get_capabilities_keys(self):
        caps = self.bot.get_capabilities()
        assert caps["bot_id"] == "onboarding_bot"
        assert "wizard_steps" in caps
        assert len(caps["features"]) > 0

    def test_capabilities_wizard_steps(self):
        caps = self.bot.get_capabilities()
        assert caps["wizard_steps"] == len(_WIZARD_STEPS)
