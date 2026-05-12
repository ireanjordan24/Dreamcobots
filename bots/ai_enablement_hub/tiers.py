"""
Tier definitions for the AI Enablement Hub.

Tiers:
  - FREE ($0):       Core pillars — Advocates Program + basic Metrics.
  - PRO ($49):       Full 5-pillar framework, segmented metrics, L&D resources,
                     Bot Tier Classifier.
  - ENTERPRISE ($299): All PRO features plus Retraining Optimizer, custom policies,
                       and API access.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Tier enum
# ---------------------------------------------------------------------------

class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_ADVOCATES_PROGRAM = "advocates_program"
FEATURE_POLICIES_GUARDRAILS = "policies_guardrails"
FEATURE_LEARNING_DEVELOPMENT = "learning_development"
FEATURE_DATA_METRICS = "data_metrics"
FEATURE_COMMUNITY_PRACTICE = "community_practice"
FEATURE_BOT_TIER_CLASSIFIER = "bot_tier_classifier"
FEATURE_RETRAINING_OPTIMIZER = "retraining_optimizer"
FEATURE_ADVANCED_SEGMENTATION = "advanced_segmentation"
FEATURE_CUSTOM_POLICIES = "custom_policies"
FEATURE_API_ACCESS = "api_access"

FREE_FEATURES: list[str] = [
    FEATURE_ADVOCATES_PROGRAM,
    FEATURE_DATA_METRICS,
]

PRO_FEATURES: list[str] = FREE_FEATURES + [
    FEATURE_POLICIES_GUARDRAILS,
    FEATURE_LEARNING_DEVELOPMENT,
    FEATURE_COMMUNITY_PRACTICE,
    FEATURE_BOT_TIER_CLASSIFIER,
    FEATURE_ADVANCED_SEGMENTATION,
]

ENTERPRISE_FEATURES: list[str] = PRO_FEATURES + [
    FEATURE_RETRAINING_OPTIMIZER,
    FEATURE_CUSTOM_POLICIES,
    FEATURE_API_ACCESS,
]

# ---------------------------------------------------------------------------
# Bot-level tier feature matrix (used by BotTierClassifier)
# ---------------------------------------------------------------------------

BOT_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}


# ---------------------------------------------------------------------------
# TierConfig
# ---------------------------------------------------------------------------

@dataclass
class TierConfig:
    name: str
    tier: Tier
    price_usd_monthly: float
    features: list[str] = field(default_factory=list)
    support_level: str = "Community"

    def has_feature(self, feature: str) -> bool:
        return feature in self.features


TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=299.0,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for the given Tier enum value."""
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list[TierConfig]:
    """Return all tier configs ordered from cheapest to most expensive."""
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    """Return the next higher tier, or None if already at the top."""
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None


def get_bot_tier_info(tier: Tier) -> dict:
    """Return enablement-hub-specific tier information."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
