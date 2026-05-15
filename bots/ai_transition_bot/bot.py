"""
Dreamcobots AITransitionBot — tier-aware AI onboarding kit for businesses.

Provides three core capabilities:
  1. Readiness Assessment  — evaluate a company's AI readiness across six
     dimensions and produce a scored report with recommendations.
  2. Training Modules      — structured learning paths for employees at
     different skill levels (beginner, intermediate, advanced).
  3. Integration API Kit   — plug-and-play connectors for common business
     workflow platforms (CRM, ERP, HR, Analytics, Communication).

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config
from bots.ai_transition_bot.tiers import AI_TRANSITION_FEATURES, get_ai_transition_tier_info


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AITransitionBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class AITransitionBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ASSESSMENT_DIMENSIONS = [
    "data_infrastructure",
    "talent_skills",
    "process_automation",
    "leadership_strategy",
    "technology_stack",
    "change_management",
]

TRAINING_LEVELS = ("beginner", "intermediate", "advanced")

INTEGRATION_PLATFORMS = [
    "crm",
    "erp",
    "hr",
    "analytics",
    "communication",
    "document_management",
    "e_commerce",
    "supply_chain",
    "finance",
    "customer_support",
]

# Free tier caps
FREE_MODULE_LIMIT = 5
FREE_INTEGRATION_LIMIT = 1


# ---------------------------------------------------------------------------
# Main Bot Class
# ---------------------------------------------------------------------------

class AITransitionBot:
    """Tier-aware AI onboarding kit for companies transitioning to AI.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE, PRO, ENTERPRISE).
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._assessments: list[dict] = []
        self._enrollments: list[dict] = []
        self._integrations: list[dict] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise AITransitionBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_feature(self, feature: str) -> None:
        features = AI_TRANSITION_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise AITransitionBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                "Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def _score_dimension(self, value: int) -> str:
        """Return a readiness label for a 0-100 score."""
        if value >= 80:
            return "advanced"
        if value >= 50:
            return "intermediate"
        return "beginner"

    # ------------------------------------------------------------------
    # 1. Readiness Assessment
    # ------------------------------------------------------------------

    def run_assessment(self, company: dict) -> dict:
        """Evaluate a company's AI readiness.

        Parameters
        ----------
        company : dict
            Keys: ``name`` (str), ``industry`` (str), ``size`` (str),
            ``scores`` (dict mapping dimension names to 0-100 ints — optional).

        Returns
        -------
        dict
            Assessment report with dimension scores, overall score,
            readiness level, and recommendations.
        """
        self._check_request_limit()
        self._request_count += 1

        name = company.get("name", "Unknown Company")
        industry = company.get("industry", "general")
        size = company.get("size", "small")
        raw_scores: dict = company.get("scores", {})

        # Default scores when not provided (simulate assessment)
        dimension_scores = {
            dim: int(raw_scores.get(dim, 50))
            for dim in ASSESSMENT_DIMENSIONS
        }

        overall = sum(dimension_scores.values()) // len(dimension_scores)
        readiness_level = self._score_dimension(overall)

        # Build recommendations
        recommendations = []
        for dim, score in dimension_scores.items():
            if score < 50:
                recommendations.append(
                    f"Improve {dim.replace('_', ' ')} — current score {score}/100."
                )

        # PRO/ENTERPRISE get full breakdown; FREE gets summarised
        if self.tier == Tier.FREE:
            report = {
                "assessment_id": str(uuid.uuid4()),
                "company_name": name,
                "overall_score": overall,
                "readiness_level": readiness_level,
                "recommendation_count": len(recommendations),
                "tier": self.tier.value,
                "upgrade_hint": "Upgrade to PRO for full dimension breakdown.",
            }
        else:
            report = {
                "assessment_id": str(uuid.uuid4()),
                "company_name": name,
                "industry": industry,
                "company_size": size,
                "dimension_scores": dimension_scores,
                "overall_score": overall,
                "readiness_level": readiness_level,
                "recommendations": recommendations,
                "tier": self.tier.value,
            }

        self._assessments.append(report)
        return report

    # ------------------------------------------------------------------
    # 2. Training Modules
    # ------------------------------------------------------------------

    def enroll_training(self, request: dict) -> dict:
        """Enroll an employee in an AI training module.

        Parameters
        ----------
        request : dict
            Keys: ``employee_name`` (str), ``level`` (str — beginner /
            intermediate / advanced), ``topic`` (str — optional).

        Returns
        -------
        dict
            Enrollment confirmation with module ID and estimated duration.

        Raises
        ------
        AITransitionBotTierError
            If the tier's module quota has been reached or the level requires
            a higher tier.
        """
        self._check_request_limit()

        employee = request.get("employee_name", "Employee")
        level = request.get("level", "beginner").lower()
        topic = request.get("topic", "AI Fundamentals")

        if level not in TRAINING_LEVELS:
            level = "beginner"

        # FREE tier: max 5 enrollments and beginner level only
        if self.tier == Tier.FREE:
            if len(self._enrollments) >= FREE_MODULE_LIMIT:
                raise AITransitionBotTierError(
                    f"Training module limit of {FREE_MODULE_LIMIT} reached on the "
                    "Free tier. Please upgrade to PRO for unlimited modules."
                )
            if level != "beginner":
                raise AITransitionBotTierError(
                    f"'{level}' training is not available on the Free tier. "
                    "Upgrade to PRO to access intermediate and advanced modules."
                )

        # PRO tier: intermediate and below
        if self.tier == Tier.PRO and level == "advanced":
            raise AITransitionBotTierError(
                "Advanced training modules require an ENTERPRISE subscription."
            )

        self._request_count += 1

        duration_map = {"beginner": "2 hours", "intermediate": "4 hours", "advanced": "8 hours"}
        enrollment = {
            "enrollment_id": str(uuid.uuid4()),
            "employee_name": employee,
            "topic": topic,
            "level": level,
            "estimated_duration": duration_map[level],
            "status": "enrolled",
            "tier": self.tier.value,
        }
        self._enrollments.append(enrollment)
        return enrollment

    # ------------------------------------------------------------------
    # 3. Integration API Kit
    # ------------------------------------------------------------------

    def activate_integration(self, request: dict) -> dict:
        """Activate a plug-and-play integration for a business platform.

        Parameters
        ----------
        request : dict
            Keys: ``platform`` (str — see INTEGRATION_PLATFORMS),
            ``workflow_name`` (str — optional),
            ``config`` (dict — optional platform-specific settings).

        Returns
        -------
        dict
            Integration record with endpoint URL, API key stub, and status.

        Raises
        ------
        AITransitionBotTierError
            If the platform is unsupported or the tier's integration quota
            has been reached.
        """
        self._check_request_limit()

        platform = request.get("platform", "").lower()
        workflow = request.get("workflow_name", f"{platform}_workflow")
        cfg = request.get("config", {})

        if platform not in INTEGRATION_PLATFORMS:
            raise AITransitionBotTierError(
                f"Platform '{platform}' is not supported. "
                f"Supported platforms: {INTEGRATION_PLATFORMS}."
            )

        # FREE tier: max 1 integration
        if self.tier == Tier.FREE and len(self._integrations) >= FREE_INTEGRATION_LIMIT:
            raise AITransitionBotTierError(
                f"Integration limit of {FREE_INTEGRATION_LIMIT} reached on the "
                "Free tier. Please upgrade to PRO for up to 10 integrations."
            )

        # PRO tier: max 10 integrations
        if self.tier == Tier.PRO and len(self._integrations) >= 10:
            raise AITransitionBotTierError(
                "Integration limit of 10 reached on the PRO tier. "
                "Upgrade to ENTERPRISE for unlimited integrations."
            )

        self._request_count += 1

        integration = {
            "integration_id": str(uuid.uuid4()),
            "platform": platform,
            "workflow_name": workflow,
            "endpoint_url": f"https://api.dreamcobots.ai/integrations/{platform}",
            "api_key_stub": f"dc_{platform}_{str(uuid.uuid4())[:8]}",
            "config": cfg,
            "status": "active",
            "tier": self.tier.value,
            "activated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._integrations.append(integration)
        return integration

    # ------------------------------------------------------------------
    # Stats / introspection
    # ------------------------------------------------------------------

    def get_stats(self) -> dict:
        """Return a summary of activity for this session."""
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "assessments_run": len(self._assessments),
            "enrollments_created": len(self._enrollments),
            "integrations_active": len(self._integrations),
            "buddy_integration": True,
        }

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        command = payload.get("command", "")
        if command == "assess":
            return self.run_assessment(payload.get("company", {}))
        if command == "train":
            return self.enroll_training(payload.get("request", {}))
        if command == "integrate":
            return self.activate_integration(payload.get("request", {}))
        if command == "stats":
            return self.get_stats()
        return {"error": f"Unknown command '{command}'."}
