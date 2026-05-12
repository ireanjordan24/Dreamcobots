"""
AI Enablement Hub — GitHub's eight-pillar AI enablement model for DreamCobots.

Orchestrates the five core pillars of AI adoption enablement:

  1. AI Advocates Program  — peer-to-peer influence networks
  2. Clear Policies & Guardrails — vetted AI tool guidelines
  3. Learning & Development — accelerated onboarding resources
  4. Data-driven Metrics  — MAU, segmentation, cycle-time analytics
  5. Communities of Practice — collaborative ideation channels

Plus two cross-cutting capabilities:

  • BotTierClassifier — dynamic scalability scoring for every bot
  • Retraining Optimizer — performance-degradation-triggered retraining

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)
from framework.retraining_optimizer import RetrainingOptimizer  # noqa: F401

from bots.ai_enablement_hub.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_ADVOCATES_PROGRAM,
    FEATURE_POLICIES_GUARDRAILS,
    FEATURE_LEARNING_DEVELOPMENT,
    FEATURE_DATA_METRICS,
    FEATURE_COMMUNITY_PRACTICE,
    FEATURE_BOT_TIER_CLASSIFIER,
    FEATURE_RETRAINING_OPTIMIZER,
    FEATURE_ADVANCED_SEGMENTATION,
    FEATURE_CUSTOM_POLICIES,
    BOT_FEATURES,
    get_bot_tier_info,
)
from bots.ai_enablement_hub.advocates import AdvocatesProgram
from bots.ai_enablement_hub.policies import PoliciesGuardrails
from bots.ai_enablement_hub.learning import LearningDevelopment
from bots.ai_enablement_hub.metrics import DataMetrics
from bots.ai_enablement_hub.community import CommunityOfPractice
from bots.ai_enablement_hub.bot_tier_classifier import BotTierClassifier


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AIEnablementHubError(Exception):
    """Base exception for AI Enablement Hub errors."""


class AIEnablementTierError(AIEnablementHubError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

class AIEnablementHub:
    """
    DreamCo AI Enablement Hub — state-of-the-art AI adoption scaling.

    Implements GitHub's framework for achieving AI fluency and maximising
    adoption across workforces through five structured pillars and advanced
    bot-level intelligence.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling which pillars and features are active.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._config: TierConfig = get_tier_config(tier)

        # Pillar 1 — AI Advocates Program (FREE+)
        self.advocates = AdvocatesProgram()

        # Pillar 2 — Policies & Guardrails (PRO+)
        self.policies = PoliciesGuardrails(
            allow_custom=self._config.has_feature(FEATURE_CUSTOM_POLICIES)
        )

        # Pillar 3 — Learning & Development (PRO+)
        self.learning = LearningDevelopment()

        # Pillar 4 — Data Metrics (FREE+, advanced segmentation PRO+)
        self.metrics = DataMetrics(
            advanced_segmentation=self._config.has_feature(FEATURE_ADVANCED_SEGMENTATION)
        )

        # Pillar 5 — Communities of Practice (PRO+)
        self.community = CommunityOfPractice()

        # Cross-cutting: Bot Tier Classifier (PRO+)
        self.bot_tier_classifier = BotTierClassifier()

        # Cross-cutting: Retraining Optimizer (ENTERPRISE+)
        self._retraining_optimizer: RetrainingOptimizer | None = None
        if self._config.has_feature(FEATURE_RETRAINING_OPTIMIZER):
            self._retraining_optimizer = RetrainingOptimizer()

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        """Raise AIEnablementTierError if feature is not on the current tier."""
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            hint = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade
                else ""
            )
            raise AIEnablementTierError(
                f"Feature '{feature}' is not available on the "
                f"{self._config.name} tier.{hint}"
            )

    # ------------------------------------------------------------------
    # Pillar 1 — AI Advocates (FREE+)
    # ------------------------------------------------------------------

    def enroll_advocate(self, name: str, email: str, expertise=None):
        """Enrol a new advocate in the peer network."""
        self._require(FEATURE_ADVOCATES_PROGRAM)
        return self.advocates.enroll_advocate(name, email, expertise)

    def record_influence(self, advocate_id: str, target_user: str, channel: str, outcome: str):
        """Record a peer-to-peer influence interaction."""
        self._require(FEATURE_ADVOCATES_PROGRAM)
        return self.advocates.record_influence(advocate_id, target_user, channel, outcome)

    # ------------------------------------------------------------------
    # Pillar 2 — Policies & Guardrails (PRO+)
    # ------------------------------------------------------------------

    def list_policies(self, category=None, enabled_only=False):
        """Return the current policy catalogue."""
        self._require(FEATURE_POLICIES_GUARDRAILS)
        return self.policies.list_policies(category=category, enabled_only=enabled_only)

    def record_violation(self, policy_id: str, actor: str, detail: str):
        """Record a policy violation."""
        self._require(FEATURE_POLICIES_GUARDRAILS)
        return self.policies.record_violation(policy_id, actor, detail)

    def guardrails_report(self) -> dict:
        """Return a compliance and guardrails report."""
        self._require(FEATURE_POLICIES_GUARDRAILS)
        return self.policies.guardrails_report()

    # ------------------------------------------------------------------
    # Pillar 3 — Learning & Development (PRO+)
    # ------------------------------------------------------------------

    def list_learning_resources(self, skill_level=None, bot_target=None):
        """Return available learning resources."""
        self._require(FEATURE_LEARNING_DEVELOPMENT)
        return self.learning.list_resources(skill_level=skill_level, bot_target=bot_target)

    def mark_resource_completed(self, learner_id: str, resource_id: str) -> None:
        """Mark a learning resource as completed for a learner."""
        self._require(FEATURE_LEARNING_DEVELOPMENT)
        self.learning.mark_completed(learner_id, resource_id)

    # ------------------------------------------------------------------
    # Pillar 4 — Data Metrics (FREE+)
    # ------------------------------------------------------------------

    def record_adoption_event(
        self,
        user_id: str,
        bot_id: str,
        event_type: str,
        segment: str,
        cycle_time_days: float = 0.0,
    ):
        """Record an adoption/usage event for metrics tracking."""
        self._require(FEATURE_DATA_METRICS)
        return self.metrics.record_event(user_id, bot_id, event_type, segment, cycle_time_days)

    def metrics_dashboard(self) -> dict:
        """Return the full adoption metrics dashboard."""
        self._require(FEATURE_DATA_METRICS)
        return self.metrics.dashboard()

    # ------------------------------------------------------------------
    # Pillar 5 — Communities of Practice (PRO+)
    # ------------------------------------------------------------------

    def create_community(self, name: str, description: str, channel_type: str, focus_area: str):
        """Create a new Community of Practice."""
        self._require(FEATURE_COMMUNITY_PRACTICE)
        return self.community.create_community(name, description, channel_type, focus_area)

    def post_idea(self, community_id: str, author_id: str, title: str, body: str, tags=None):
        """Submit an ideation post to a community."""
        self._require(FEATURE_COMMUNITY_PRACTICE)
        return self.community.post_idea(community_id, author_id, title, body, tags)

    # ------------------------------------------------------------------
    # Bot Tier Classifier (PRO+)
    # ------------------------------------------------------------------

    def classify_bot(
        self,
        bot_id: str,
        subscription_tier: str,
        feature_count: int,
        monthly_active_users: int,
        avg_cycle_time_days: float,
        revenue_usd: float,
        has_retraining: bool = False,
        has_governance: bool = False,
    ):
        """Classify a bot's scalability tier."""
        self._require(FEATURE_BOT_TIER_CLASSIFIER)
        return self.bot_tier_classifier.classify(
            bot_id=bot_id,
            subscription_tier=subscription_tier,
            feature_count=feature_count,
            monthly_active_users=monthly_active_users,
            avg_cycle_time_days=avg_cycle_time_days,
            revenue_usd=revenue_usd,
            has_retraining=has_retraining,
            has_governance=has_governance,
        )

    # ------------------------------------------------------------------
    # Retraining Optimizer (ENTERPRISE+)
    # ------------------------------------------------------------------

    def check_retraining(self, bot_id: str, current_accuracy: float) -> dict:
        """
        Check whether a bot requires retraining based on accuracy degradation.

        Returns a retraining decision dict with fields:
          - requires_retraining (bool)
          - reason (str)
          - recommended_method (str)
        """
        self._require(FEATURE_RETRAINING_OPTIMIZER)
        assert self._retraining_optimizer is not None
        return self._retraining_optimizer.evaluate(bot_id, current_accuracy)

    # ------------------------------------------------------------------
    # Hub summary
    # ------------------------------------------------------------------

    def hub_status(self) -> dict:
        """Return a comprehensive status snapshot of the AI Enablement Hub."""
        features = BOT_FEATURES[self.tier.value]
        status: dict = {
            "tier": self.tier.value,
            "active_features": features,
            "pillars": {},
        }

        # Always available
        status["pillars"]["advocates"] = self.advocates.network_summary()
        status["pillars"]["metrics"] = self.metrics.dashboard()

        if self._config.has_feature(FEATURE_POLICIES_GUARDRAILS):
            status["pillars"]["policies"] = self.policies.guardrails_report()

        if self._config.has_feature(FEATURE_LEARNING_DEVELOPMENT):
            status["pillars"]["learning"] = self.learning.programme_summary()

        if self._config.has_feature(FEATURE_COMMUNITY_PRACTICE):
            status["pillars"]["community"] = self.community.collaboration_report()

        if self._config.has_feature(FEATURE_BOT_TIER_CLASSIFIER):
            status["bot_classifications"] = len(self.bot_tier_classifier._profiles)

        if self._retraining_optimizer is not None:
            status["retraining_optimizer"] = self._retraining_optimizer.status()

        return status

    def __repr__(self) -> str:
        return f"AIEnablementHub(tier={self.tier.value!r})"
