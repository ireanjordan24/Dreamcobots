"""
Bot Tier Classifier — dynamic categorization of bots by scalability potential.

Analyses a bot's feature set, revenue metrics, tier, and adoption signals
to assign a scalability tier (EMERGING → ENTERPRISE_GRADE) and surface
actionable upgrade recommendations.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Scalability tiers (distinct from the subscription FREE/PRO/ENTERPRISE)
# ---------------------------------------------------------------------------

class ScalabilityTier:
    """Scalability classification labels for dynamic bot tier categorisation."""

    EMERGING = "emerging"           # Low feature count, early-stage
    GROWTH = "growth"               # Solid features, growing usage
    SCALED = "scaled"               # High adoption, revenue generating
    ENTERPRISE_GRADE = "enterprise_grade"  # Full feature set, transformative impact

    ALL = [EMERGING, GROWTH, SCALED, ENTERPRISE_GRADE]

    # Score thresholds
    THRESHOLDS = {
        EMERGING: 0,
        GROWTH: 25,
        SCALED: 55,
        ENTERPRISE_GRADE: 80,
    }

    @classmethod
    def from_score(cls, score: float) -> str:
        """Derive scalability tier from a composite score (0–100)."""
        result = cls.EMERGING
        for tier, threshold in sorted(cls.THRESHOLDS.items(), key=lambda x: x[1]):
            if score >= threshold:
                result = tier
        return result


@dataclass
class BotScalabilityProfile:
    """Scalability assessment for a single bot."""

    bot_id: str
    subscription_tier: str          # free | pro | enterprise
    feature_count: int
    monthly_active_users: int
    avg_cycle_time_days: float
    revenue_usd: float
    has_retraining: bool = False
    has_governance: bool = False
    assessed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Computed after assessment
    composite_score: float = 0.0
    scalability_tier: str = ScalabilityTier.EMERGING
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "bot_id": self.bot_id,
            "subscription_tier": self.subscription_tier,
            "feature_count": self.feature_count,
            "monthly_active_users": self.monthly_active_users,
            "avg_cycle_time_days": self.avg_cycle_time_days,
            "revenue_usd": self.revenue_usd,
            "has_retraining": self.has_retraining,
            "has_governance": self.has_governance,
            "composite_score": self.composite_score,
            "scalability_tier": self.scalability_tier,
            "recommendations": list(self.recommendations),
            "assessed_at": self.assessed_at,
        }


# ---------------------------------------------------------------------------
# Bot Tier Classifier
# ---------------------------------------------------------------------------

class BotTierClassifier:
    """
    Dynamically categorises bots by scalability potential.

    Scoring algorithm
    -----------------
    - Subscription tier:  FREE=0, PRO=15, ENTERPRISE=30 pts
    - Feature count:      1 pt per feature, capped at 20 pts
    - MAU:                log-scaled, up to 20 pts
    - Revenue:            log-scaled, up to 15 pts
    - Governance present: 10 pts
    - Retraining present: 10 pts
    - Cycle time bonus:   < 7 days → +5 pts, < 30 days → +2 pts

    Maximum possible score = 110 (scores > 100 are normalised to 100).
    """

    _TIER_BASE_SCORE = {"free": 0, "pro": 15, "enterprise": 30}

    def __init__(self) -> None:
        self._profiles: dict[str, BotScalabilityProfile] = {}

    def classify(
        self,
        bot_id: str,
        subscription_tier: str,
        feature_count: int,
        monthly_active_users: int,
        avg_cycle_time_days: float,
        revenue_usd: float,
        has_retraining: bool = False,
        has_governance: bool = False,
    ) -> BotScalabilityProfile:
        """
        Classify a bot and store/return its scalability profile.

        Parameters
        ----------
        bot_id : str
            Unique bot identifier.
        subscription_tier : str
            "free", "pro", or "enterprise".
        feature_count : int
            Number of active features.
        monthly_active_users : int
            Current MAU.
        avg_cycle_time_days : float
            Average adoption cycle time.
        revenue_usd : float
            Revenue generated in the current period.
        has_retraining : bool
            Whether the bot has retraining optimisation enabled.
        has_governance : bool
            Whether the bot implements governance controls.
        """
        import math

        tier_score = self._TIER_BASE_SCORE.get(subscription_tier.lower(), 0)
        feature_score = min(feature_count, 20)
        mau_score = min(math.log1p(monthly_active_users) * 2, 20)
        revenue_score = min(math.log1p(revenue_usd) / math.log1p(1_000_000) * 15, 15)
        governance_score = 10 if has_governance else 0
        retraining_score = 10 if has_retraining else 0
        cycle_bonus = 5 if avg_cycle_time_days < 7 else (2 if avg_cycle_time_days < 30 else 0)

        raw_score = (
            tier_score + feature_score + mau_score + revenue_score
            + governance_score + retraining_score + cycle_bonus
        )
        composite_score = min(round(raw_score, 2), 100.0)
        scalability_tier = ScalabilityTier.from_score(composite_score)

        recommendations = self._build_recommendations(
            subscription_tier, feature_count, monthly_active_users,
            has_retraining, has_governance, avg_cycle_time_days,
        )

        profile = BotScalabilityProfile(
            bot_id=bot_id,
            subscription_tier=subscription_tier,
            feature_count=feature_count,
            monthly_active_users=monthly_active_users,
            avg_cycle_time_days=avg_cycle_time_days,
            revenue_usd=revenue_usd,
            has_retraining=has_retraining,
            has_governance=has_governance,
            composite_score=composite_score,
            scalability_tier=scalability_tier,
            recommendations=recommendations,
        )
        self._profiles[bot_id] = profile
        return profile

    def get_profile(self, bot_id: str) -> BotScalabilityProfile:
        """Return the most recent scalability profile for a bot."""
        if bot_id not in self._profiles:
            raise KeyError(f"No profile found for bot '{bot_id}'.")
        return self._profiles[bot_id]

    def list_profiles(
        self, scalability_tier: Optional[str] = None
    ) -> list[dict]:
        """Return all profiles, optionally filtered by scalability tier."""
        profiles = self._profiles.values()
        if scalability_tier is not None:
            profiles = [p for p in profiles if p.scalability_tier == scalability_tier]
        return [
            p.to_dict()
            for p in sorted(profiles, key=lambda p: p.composite_score, reverse=True)
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_recommendations(
        subscription_tier: str,
        feature_count: int,
        mau: int,
        has_retraining: bool,
        has_governance: bool,
        avg_cycle_time_days: float,
    ) -> list[str]:
        recs: list[str] = []
        if subscription_tier.lower() == "free":
            recs.append("Upgrade to PRO to unlock full 5-pillar enablement features.")
        if not has_retraining:
            recs.append("Enable RetrainingOptimizer to auto-recover from performance drift.")
        if not has_governance:
            recs.append("Integrate GovernanceSecurityLayer to reach enterprise-grade compliance.")
        if mau < 50:
            recs.append("Boost adoption: engage AI Advocates for peer-to-peer outreach.")
        if avg_cycle_time_days > 30:
            recs.append("Reduce cycle time: add onboarding resources in Learning & Development.")
        if feature_count < 5:
            recs.append("Expand feature set to increase scalability score.")
        return recs
