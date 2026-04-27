"""
Business Onboarding Bot — Buddy's guided onboarding wizard for new businesses.

Takes a new business or individual through a structured, adaptive onboarding
flow that:
  1. Gathers core business info (name, industry, stage, team size, goals).
  2. Recommends the best DreamCobots bots and features for their use-case.
  3. Generates a personalised quick-start checklist and action plan.
  4. Creates an initial configuration package ready for deployment.
  5. Schedules follow-up check-ins to ensure adoption success.

The wizard is step-based and fully stateful — users can pause and resume at
any point.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class OnboardingStage(str, Enum):
    WELCOME = "welcome"
    BUSINESS_INFO = "business_info"
    GOALS = "goals"
    BOT_SELECTION = "bot_selection"
    CONFIGURATION = "configuration"
    ACTION_PLAN = "action_plan"
    COMPLETE = "complete"


class BusinessIndustry(str, Enum):
    TECHNOLOGY = "technology"
    REAL_ESTATE = "real_estate"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    RETAIL = "retail"
    MARKETING = "marketing"
    LEGAL = "legal"
    FOOD_BEVERAGE = "food_beverage"
    LOGISTICS = "logistics"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


class BusinessStage(str, Enum):
    IDEA = "idea"
    STARTUP = "startup"
    GROWTH = "growth"
    SCALE = "scale"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Bot recommendation rules
# ---------------------------------------------------------------------------

_INDUSTRY_BOT_MAP: Dict[str, List[str]] = {
    BusinessIndustry.TECHNOLOGY.value: [
        "coding_assistant_bot", "devops_bot", "saas_bot", "cybersecurity_bot",
        "vibe_coding_bot", "builder_bot",
    ],
    BusinessIndustry.REAL_ESTATE.value: [
        "real_estate_bot", "dream_real_estate", "home_buyer_bot",
        "rental_cashflow_bot", "foreclosure_finder_bot",
    ],
    BusinessIndustry.FINANCE.value: [
        "finance_bot", "stock_trading_bot", "crypto_bot",
        "financial_literacy_bot", "fraud_detection_bot",
    ],
    BusinessIndustry.HEALTHCARE.value: [
        "health_wellness_bot", "biomedical_bot", "medical_bot",
        "compliance_bot",
    ],
    BusinessIndustry.EDUCATION.value: [
        "education_bot", "simulation_game_bot", "buddy_teach_bot",
        "ai_learning_system",
    ],
    BusinessIndustry.RETAIL.value: [
        "ecommerce_bot", "shopify_automation_bot", "deal_finder_bot",
        "crm_automation_bot", "discount_dominator",
    ],
    BusinessIndustry.MARKETING.value: [
        "marketing_bot", "social_media_bot", "influencer_bot",
        "email_campaign_manager_bot", "ad_copy_generator_bot",
    ],
    BusinessIndustry.LEGAL.value: [
        "legal_bot", "compliance_bot", "government_contract_bot",
    ],
    BusinessIndustry.FOOD_BEVERAGE.value: [
        "ecommerce_bot", "crm_automation_bot", "marketing_bot",
    ],
    BusinessIndustry.LOGISTICS.value: [
        "automation_bot", "devops_bot", "smart_city_bot",
    ],
    BusinessIndustry.ENTERTAINMENT.value: [
        "simulation_game_bot", "creative_studio_bot", "vibe_coding_bot",
        "cinecore_bot",
    ],
    BusinessIndustry.OTHER.value: [
        "buddy_bot", "automation_bot", "marketing_bot", "finance_bot",
    ],
}

_STAGE_EXTRAS: Dict[str, List[str]] = {
    BusinessStage.IDEA.value: ["business_launch_pad", "ai_brain", "lead_gen_bot"],
    BusinessStage.STARTUP.value: ["business_launch_pad", "saas_bot", "lead_gen_bot", "crm_automation_bot"],
    BusinessStage.GROWTH.value: ["revenue_engine_bot", "analytics_dashboard_bot", "saas_upsell"],
    BusinessStage.SCALE.value: ["global_bot_network", "auto_scaler", "enterprise_integrations_bot"],
    BusinessStage.ENTERPRISE.value: ["dreamco_empire_os", "quantum_ai_bot", "god_mode_bot"],
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class OnboardingStep:
    """A single step in the onboarding wizard."""

    stage: OnboardingStage
    prompt: str
    field_key: str
    required: bool = True
    options: Optional[List[str]] = None  # if set, user must pick one


@dataclass
class OnboardingProfile:
    """The growing profile collected during onboarding."""

    business_name: str = ""
    industry: str = ""
    stage: str = ""
    team_size: int = 1
    goals: List[str] = field(default_factory=list)
    monthly_budget_usd: float = 0.0
    primary_contact_email: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OnboardingSession:
    """State for an active onboarding wizard session."""

    session_id: str
    user_id: str
    current_stage: OnboardingStage = OnboardingStage.WELCOME
    profile: OnboardingProfile = field(default_factory=OnboardingProfile)
    recommended_bots: List[str] = field(default_factory=list)
    action_plan: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    completed: bool = False
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    followup_schedule: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "current_stage": self.current_stage.value,
            "profile": {
                "business_name": self.profile.business_name,
                "industry": self.profile.industry,
                "stage": self.profile.stage,
                "team_size": self.profile.team_size,
                "goals": self.profile.goals,
            },
            "recommended_bots": self.recommended_bots,
            "action_plan": self.action_plan,
            "completed": self.completed,
        }


# ---------------------------------------------------------------------------
# Wizard step definitions
# ---------------------------------------------------------------------------

_WIZARD_STEPS: List[OnboardingStep] = [
    OnboardingStep(
        stage=OnboardingStage.WELCOME,
        prompt="Welcome to DreamCobots! What is the name of your business?",
        field_key="business_name",
    ),
    OnboardingStep(
        stage=OnboardingStage.BUSINESS_INFO,
        prompt="Which industry best describes your business?",
        field_key="industry",
        options=[i.value for i in BusinessIndustry],
    ),
    OnboardingStep(
        stage=OnboardingStage.BUSINESS_INFO,
        prompt="What stage is your business at?",
        field_key="stage",
        options=[s.value for s in BusinessStage],
    ),
    OnboardingStep(
        stage=OnboardingStage.BUSINESS_INFO,
        prompt="How many people are on your team? (enter a number)",
        field_key="team_size",
    ),
    OnboardingStep(
        stage=OnboardingStage.GOALS,
        prompt="What are your top 3 business goals? (comma-separated, e.g. 'increase revenue, automate hiring, launch product')",
        field_key="goals",
    ),
    OnboardingStep(
        stage=OnboardingStage.GOALS,
        prompt="What is your estimated monthly tech budget in USD? (enter a number, 0 if unsure)",
        field_key="monthly_budget_usd",
    ),
    OnboardingStep(
        stage=OnboardingStage.GOALS,
        prompt="What is your primary contact email? (we'll send your action plan here)",
        field_key="primary_contact_email",
        required=False,
    ),
]


# ---------------------------------------------------------------------------
# OnboardingBot
# ---------------------------------------------------------------------------


class OnboardingBot:
    """
    Buddy's business onboarding wizard.

    Guides a new user through profile collection, bot recommendation,
    configuration generation, and action-plan creation.

    Parameters
    ----------
    buddy_name : str   Name of the Buddy instance greeting the user.
    """

    bot_id = "onboarding_bot"
    name = "Business Onboarding Bot"
    category = "onboarding"

    def __init__(self, buddy_name: str = "Buddy") -> None:
        self.buddy_name = buddy_name
        self._sessions: Dict[str, OnboardingSession] = {}

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def start_session(self, user_id: str) -> OnboardingSession:
        """Create and return a new onboarding session."""
        session = OnboardingSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[OnboardingSession]:
        return self._sessions.get(session_id)

    def get_current_prompt(self, session_id: str) -> Dict[str, Any]:
        """Return the next question Buddy should ask the user."""
        session = self._require_session(session_id)
        if session.completed:
            return {"completed": True, "message": "Onboarding is already complete."}

        step = self._current_step(session)
        if step is None:
            return self._finalise(session)

        return {
            "session_id": session_id,
            "stage": session.current_stage.value,
            "prompt": step.prompt,
            "field_key": step.field_key,
            "options": step.options,
            "required": step.required,
            "buddy_message": f"{self.buddy_name}: {step.prompt}",
        }

    def submit_answer(self, session_id: str, answer: Any) -> Dict[str, Any]:
        """
        Provide an answer to the current wizard step.

        Returns the next prompt or the completed onboarding summary.
        """
        session = self._require_session(session_id)
        if session.completed:
            return {"completed": True, "session": session.to_dict()}

        step = self._current_step(session)
        if step is None:
            return self._finalise(session)

        # Validate option choices
        if step.options and str(answer).lower() not in [o.lower() for o in step.options]:
            return {
                "error": f"Invalid answer. Please choose from: {step.options}",
                "field_key": step.field_key,
                "options": step.options,
            }

        self._apply_answer(session, step, answer)
        session.updated_at = time.time()

        # Advance to next step
        self._advance_step(session)

        # Check if all steps consumed
        if self._current_step(session) is None:
            return self._finalise(session)

        return self.get_current_prompt(session_id)

    # ------------------------------------------------------------------
    # Bot recommendation
    # ------------------------------------------------------------------

    def recommend_bots(self, session_id: str) -> List[str]:
        """Return the personalised bot stack for this user."""
        session = self._require_session(session_id)
        industry_bots = _INDUSTRY_BOT_MAP.get(session.profile.industry, _INDUSTRY_BOT_MAP[BusinessIndustry.OTHER.value])
        stage_extras = _STAGE_EXTRAS.get(session.profile.stage, [])
        # Always include Buddy core bots
        core_bots = ["buddy_bot", "device_monitor_bot", "builder_bot"]
        combined = list(dict.fromkeys(core_bots + industry_bots + stage_extras))
        session.recommended_bots = combined
        return combined

    # ------------------------------------------------------------------
    # Action plan generation
    # ------------------------------------------------------------------

    def generate_action_plan(self, session_id: str) -> List[str]:
        """Generate a personalised 30-day quick-start action plan."""
        session = self._require_session(session_id)
        p = session.profile
        plan = [
            f"✅ Day 1-3: Complete your DreamCobots account setup for {p.business_name or 'your business'}.",
            f"✅ Day 4-7: Activate and configure your top bots: {', '.join(session.recommended_bots[:3])}.",
            "✅ Week 2: Run Buddy's sandbox stress tests to validate your bot stack.",
            "✅ Week 2: Import your customer data and CRM connections.",
            f"✅ Week 3: Launch your first automated campaign targeting your goals: {'; '.join(p.goals[:2])}.",
            "✅ Week 3: Enable the Builder Bot for automated CI/CD pipelines.",
            "✅ Week 4: Review Buddy's weekly analytics report and optimise.",
            "✅ Day 30: Schedule a 1:1 onboarding review with the DreamCo team.",
        ]
        if p.monthly_budget_usd > 1000:
            plan.append("💡 Your budget unlocks PRO/Enterprise features — ask Buddy about custom AI model training.")
        session.action_plan = plan
        return plan

    # ------------------------------------------------------------------
    # Configuration package
    # ------------------------------------------------------------------

    def generate_config(self, session_id: str) -> Dict[str, Any]:
        """Generate a deployment-ready configuration package."""
        session = self._require_session(session_id)
        p = session.profile
        config = {
            "dreamcobots_config": {
                "version": "2.0",
                "business_name": p.business_name,
                "industry": p.industry,
                "stage": p.stage,
                "team_size": p.team_size,
                "enabled_bots": session.recommended_bots,
                "primary_contact": p.primary_contact_email,
                "budget_tier": (
                    "enterprise" if p.monthly_budget_usd >= 5000
                    else "pro" if p.monthly_budget_usd >= 500
                    else "free"
                ),
                "buddy_name": self.buddy_name,
                "goals": p.goals,
            }
        }
        session.configuration = config
        return config

    # ------------------------------------------------------------------
    # Follow-up scheduling
    # ------------------------------------------------------------------

    def schedule_followups(self, session_id: str) -> List[Dict[str, Any]]:
        """Schedule automated check-in events post-onboarding."""
        session = self._require_session(session_id)
        now = time.time()
        day = 86_400
        followups = [
            {"days_after": 3,  "type": "setup_check",  "message": "How's the initial setup going? Any help needed?"},
            {"days_after": 7,  "type": "first_week",   "message": "First week review: are your bots running smoothly?"},
            {"days_after": 14, "type": "mid_month",    "message": "Mid-month check-in: let's review your metrics together."},
            {"days_after": 30, "type": "monthly",      "message": "30-day onboarding complete! Time for your success review."},
        ]
        for f in followups:
            f["scheduled_at"] = now + f["days_after"] * day
        session.followup_schedule = followups
        return followups

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self) -> Dict[str, Any]:
        total = len(self._sessions)
        completed = sum(1 for s in self._sessions.values() if s.completed)
        return {
            "total_sessions": total,
            "completed": completed,
            "in_progress": total - completed,
            "buddy_name": self.buddy_name,
        }

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "name": self.name,
            "category": self.category,
            "wizard_steps": len(_WIZARD_STEPS),
            "supported_industries": [i.value for i in BusinessIndustry],
            "supported_stages": [s.value for s in BusinessStage],
            "features": [
                "Step-by-step guided onboarding wizard",
                "Industry and stage-aware bot recommendation engine",
                "Personalised 30-day action plan generation",
                "Deployment-ready configuration package export",
                "Automated follow-up scheduling",
                "Pause and resume at any step",
                "Multi-session support for agencies",
            ],
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _require_session(self, session_id: str) -> OnboardingSession:
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Onboarding session '{session_id}' not found.")
        return session

    def _current_step(self, session: OnboardingSession) -> Optional[OnboardingStep]:
        """Return the next unanswered wizard step, or None if all done."""
        answered: set = set(session.profile.metadata.get("_answered_steps", []))
        for i, step in enumerate(_WIZARD_STEPS):
            if i not in answered:
                return step
        return None

    def _advance_step(self, session: OnboardingSession) -> None:
        answered: List[int] = session.profile.metadata.setdefault("_answered_steps", [])
        next_idx = len(answered)
        answered.append(next_idx)
        # Update current_stage to match
        if next_idx < len(_WIZARD_STEPS):
            session.current_stage = _WIZARD_STEPS[min(next_idx, len(_WIZARD_STEPS) - 1)].stage

    def _apply_answer(self, session: OnboardingSession, step: OnboardingStep, answer: Any) -> None:
        p = session.profile
        key = step.field_key
        if key == "business_name":
            p.business_name = str(answer)
        elif key == "industry":
            p.industry = str(answer).lower()
        elif key == "stage":
            p.stage = str(answer).lower()
        elif key == "team_size":
            try:
                p.team_size = int(answer)
            except (ValueError, TypeError):
                pass
        elif key == "goals":
            p.goals = [g.strip() for g in str(answer).split(",") if g.strip()]
        elif key == "monthly_budget_usd":
            try:
                p.monthly_budget_usd = float(answer)
            except (ValueError, TypeError):
                pass
        elif key == "primary_contact_email":
            p.primary_contact_email = str(answer)

    def _finalise(self, session: OnboardingSession) -> Dict[str, Any]:
        """Generate all outputs and mark the session complete."""
        self.recommend_bots(session.session_id)
        self.generate_action_plan(session.session_id)
        self.generate_config(session.session_id)
        self.schedule_followups(session.session_id)
        session.current_stage = OnboardingStage.COMPLETE
        session.completed = True
        return {
            "completed": True,
            "session": session.to_dict(),
            "recommended_bots": session.recommended_bots,
            "action_plan": session.action_plan,
            "config": session.configuration,
            "followup_schedule": session.followup_schedule,
            "buddy_message": (
                f"🎉 {self.buddy_name}: Onboarding complete for {session.profile.business_name or 'your business'}! "
                "Your personalised bot stack is ready. Let's build something amazing together!"
            ),
        }
