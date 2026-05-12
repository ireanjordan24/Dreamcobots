"""
Tier configuration for the AI Enablement Hub bot.

Tiers:
  - FREE ($0/mo):        Core policies, basic learning resources, community access.
  - PRO ($49/mo):        Full advocate network, metrics dashboards, advanced learning paths.
  - ENTERPRISE ($199/mo): All PRO + BotTierClassifier, RetrainingOptimizer, governance APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    """Configuration for an AI Enablement Hub subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_advocates: Optional[int]
    max_policies: Optional[int]
    max_learning_resources: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_advocates(self) -> bool:
        return self.max_advocates is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_POLICIES = "policies"
FEATURE_LEARNING = "learning"
FEATURE_COMMUNITY = "community"
FEATURE_ADVOCATES = "advocates"
FEATURE_METRICS = "metrics"
FEATURE_ADVANCED_LEARNING = "advanced_learning"
FEATURE_MATURITY_ASSESSMENT = "maturity_assessment"
FEATURE_SEGMENTATION = "segmentation"
FEATURE_BOT_TIER_CLASSIFIER = "bot_tier_classifier"
FEATURE_RETRAINING_OPTIMIZER = "retraining_optimizer"
FEATURE_GOVERNANCE_API = "governance_api"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_POLICIES,
    FEATURE_LEARNING,
    FEATURE_COMMUNITY,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_ADVOCATES,
    FEATURE_METRICS,
    FEATURE_ADVANCED_LEARNING,
    FEATURE_MATURITY_ASSESSMENT,
    FEATURE_SEGMENTATION,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_BOT_TIER_CLASSIFIER,
    FEATURE_RETRAINING_OPTIMIZER,
    FEATURE_GOVERNANCE_API,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_advocates=3,
        max_policies=5,
        max_learning_resources=8,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_advocates=25,
        max_policies=None,
        max_learning_resources=None,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_advocates=None,
        max_policies=None,
        max_learning_resources=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list:
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
