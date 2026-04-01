"""
Tier configuration for the DreamCo Global Wealth System Bot.

Tiers:
  - FREE:        Join existing Wealth Hubs, view treasury dashboard,
                 basic governance voting (no active bots).
  - PRO ($29):   Create up to 3 Wealth Hubs, activate Income & Asset Bots,
                 dividend tracking, basic asset allocation.
  - ENTERPRISE ($99): Unlimited Wealth Hubs, all bot types (Commerce + Finance),
                 full governance, DreamCoin staking, advanced analytics,
                 white-label, Stripe billing.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    name: str
    tier: Tier
    price_usd_monthly: float
    max_hubs: Optional[int]      # None = unlimited
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_hubs(self) -> bool:
        return self.max_hubs is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_JOIN_HUB = "join_hub"
FEATURE_VIEW_TREASURY = "view_treasury"
FEATURE_BASIC_VOTING = "basic_voting"
FEATURE_CREATE_HUB = "create_hub"
FEATURE_INCOME_BOTS = "income_bots"
FEATURE_ASSET_BOTS = "asset_bots"
FEATURE_DIVIDEND_TRACKING = "dividend_tracking"
FEATURE_ASSET_ALLOCATION = "asset_allocation"
FEATURE_COMMERCE_BOTS = "commerce_bots"
FEATURE_FINANCE_BOTS = "finance_bots"
FEATURE_FULL_GOVERNANCE = "full_governance"
FEATURE_DREAMCOIN_STAKING = "dreamcoin_staking"
FEATURE_ADVANCED_ANALYTICS = "advanced_analytics"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_STRIPE_BILLING = "stripe_billing"

FREE_FEATURES = [
    FEATURE_JOIN_HUB,
    FEATURE_VIEW_TREASURY,
    FEATURE_BASIC_VOTING,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_CREATE_HUB,
    FEATURE_INCOME_BOTS,
    FEATURE_ASSET_BOTS,
    FEATURE_DIVIDEND_TRACKING,
    FEATURE_ASSET_ALLOCATION,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_COMMERCE_BOTS,
    FEATURE_FINANCE_BOTS,
    FEATURE_FULL_GOVERNANCE,
    FEATURE_DREAMCOIN_STAKING,
    FEATURE_ADVANCED_ANALYTICS,
    FEATURE_WHITE_LABEL,
    FEATURE_STRIPE_BILLING,
]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_hubs=0,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=29.0,
        max_hubs=3,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=99.0,
        max_hubs=None,
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
