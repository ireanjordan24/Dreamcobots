"""
Tier configuration for the AI Level-Up Bot.

Tiers:
  - FREE:       Open-source models, limited compute, basic course access.
  - STARTER:    Core AI tools, token marketplace, Levels 1-3, $29/mo.
  - PRO:        Full marketplace, Levels 1-7, agent builder, $99/mo.
  - ENTERPRISE: All features, unlimited agents, all 10 levels, $399/mo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    """Configuration for an AI Level-Up Bot subscription tier.

    Attributes
    ----------
    name : str
        Human-readable tier name.
    tier : Tier
        Enum value identifying the tier.
    price_usd_monthly : float
        Monthly subscription price in USD.
    max_course_level : int
        Highest AI University level accessible on this tier.
    max_agents : int | None
        Maximum custom AI agents a user can create.  ``None`` = unlimited.
    token_markup : float
        Decimal markup applied on top of base token costs (e.g. 0.25 = 25%).
    features : list[str]
        Feature flags enabled on this tier.
    support_level : str
        Description of the support offering.
    """

    name: str
    tier: Tier
    price_usd_monthly: float
    max_course_level: int
    max_agents: Optional[int]
    token_markup: float
    features: list
    support_level: str

    def is_unlimited_agents(self) -> bool:
        """Return True if this tier has no agent-creation cap."""
        return self.max_agents is None

    def has_feature(self, feature: str) -> bool:
        """Return True if *feature* is enabled on this tier."""
        return feature in self.features


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_OPEN_SOURCE_MODELS = "open_source_models"
FEATURE_AI_COMPANIES_DATABASE = "ai_companies_database"
FEATURE_TOKEN_MARKETPLACE = "token_marketplace"
FEATURE_COURSE_ENGINE = "course_engine"
FEATURE_SKILL_TREE = "skill_tree"
FEATURE_AGENTS_GENERATOR = "agents_generator"
FEATURE_PREMIUM_MODELS = "premium_models"
FEATURE_BULK_TOKEN_BUNDLES = "bulk_token_bundles"
FEATURE_SUBSCRIPTION_TOKENS = "subscription_tokens"
FEATURE_ADVANCED_AGENTS = "advanced_agents"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_ENTERPRISE_API = "enterprise_api"
FEATURE_ANALYTICS_DASHBOARD = "analytics_dashboard"

FREE_FEATURES = [
    FEATURE_OPEN_SOURCE_MODELS,
    FEATURE_COURSE_ENGINE,
    FEATURE_SKILL_TREE,
]

STARTER_FEATURES = FREE_FEATURES + [
    FEATURE_AI_COMPANIES_DATABASE,
    FEATURE_TOKEN_MARKETPLACE,
    FEATURE_AGENTS_GENERATOR,
]

PRO_FEATURES = STARTER_FEATURES + [
    FEATURE_PREMIUM_MODELS,
    FEATURE_BULK_TOKEN_BUNDLES,
    FEATURE_SUBSCRIPTION_TOKENS,
    FEATURE_ADVANCED_AGENTS,
    FEATURE_ANALYTICS_DASHBOARD,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_WHITE_LABEL,
    FEATURE_ENTERPRISE_API,
]

# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------

TIER_CATALOGUE: dict[str, TierConfig] = {
    "free": TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_course_level=1,
        max_agents=0,
        token_markup=0.25,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    "starter": TierConfig(
        name="Starter",
        tier=Tier.STARTER,
        price_usd_monthly=29.0,
        max_course_level=3,
        max_agents=5,
        token_markup=0.25,
        features=STARTER_FEATURES,
        support_level="Email",
    ),
    "pro": TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=99.0,
        max_course_level=7,
        max_agents=25,
        token_markup=0.25,
        features=PRO_FEATURES,
        support_level="Priority Email",
    ),
    "enterprise": TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=399.0,
        max_course_level=10,
        max_agents=None,
        token_markup=0.25,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated Account Manager",
    ),
}

_UPGRADE_PATH: dict[Tier, Tier] = {
    Tier.FREE: Tier.STARTER,
    Tier.STARTER: Tier.PRO,
    Tier.PRO: Tier.ENTERPRISE,
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for the given Tier enum value."""
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list[TierConfig]:
    """Return all tier configurations ordered from lowest to highest."""
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(tier: Tier) -> Optional[TierConfig]:
    """Return the next tier config, or None if already at ENTERPRISE."""
    next_tier = _UPGRADE_PATH.get(tier)
    if next_tier is None:
        return None
    return get_tier_config(next_tier)
