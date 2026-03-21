"""
Tier configuration for the DreamRealEstate Division.

Tiers:
  - PRO ($99/mo):        Access to Pro-tier bots, up to 10 bots active, SaaS features.
  - ENTERPRISE ($499/mo): All bots, enterprise features, white-label, API access.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Tier(Enum):
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    """Configuration for a DreamRealEstate subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_active_bots: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_bots(self) -> bool:
        return self.max_active_bots is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_PRO_BOTS = "pro_bots"
FEATURE_ENTERPRISE_BOTS = "enterprise_bots"
FEATURE_DIVISION_EXPLORER = "division_explorer"
FEATURE_BOT_EXECUTOR = "bot_executor"
FEATURE_ANALYTICS_DASHBOARD = "analytics_dashboard"
FEATURE_MONETIZATION = "monetization"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_TASK_AUTOMATION = "task_automation"
FEATURE_PORTFOLIO_TOOLS = "portfolio_tools"
FEATURE_ENTERPRISE_REPORTING = "enterprise_reporting"

PRO_FEATURES = [
    FEATURE_PRO_BOTS,
    FEATURE_DIVISION_EXPLORER,
    FEATURE_BOT_EXECUTOR,
    FEATURE_ANALYTICS_DASHBOARD,
    FEATURE_MONETIZATION,
    FEATURE_TASK_AUTOMATION,
    FEATURE_PORTFOLIO_TOOLS,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_ENTERPRISE_BOTS,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_ENTERPRISE_REPORTING,
]

TIER_CATALOGUE: dict[Tier, TierConfig] = {
    Tier.PRO: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=99.0,
        max_active_bots=10,
        features=PRO_FEATURES,
        support_level="email",
    ),
    Tier.ENTERPRISE: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=499.0,
        max_active_bots=None,
        features=ENTERPRISE_FEATURES,
        support_level="dedicated",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier]


def get_upgrade_path(current: Tier) -> Optional[Tier]:
    order = [Tier.PRO, Tier.ENTERPRISE]
    idx = order.index(current)
    return order[idx + 1] if idx + 1 < len(order) else None


def list_tiers() -> list[TierConfig]:
    return list(TIER_CATALOGUE.values())
