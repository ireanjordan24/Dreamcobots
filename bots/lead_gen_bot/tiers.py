"""
Lead Generation Bot — Tiers

Tiers:
  - FREE:       Up to 50 leads/month, basic collection, no Stripe integration.
  - PRO:        Up to 2 000 leads/month, Stripe payments for lead packages.
  - ENTERPRISE: Unlimited leads, full Stripe integration, webhook automation.
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
    """Configuration for a Lead Gen Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_leads_per_month: Optional[int]
    features: list
    support_level: str

    def is_unlimited(self) -> bool:
        return self.max_leads_per_month is None

    def has_feature(self, feature: str) -> bool:
        return feature in self.features


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_LEAD_COLLECTION = "lead_collection"
FEATURE_STRIPE_PAYMENTS = "stripe_payments"
FEATURE_LEAD_PACKAGES = "lead_packages"
FEATURE_WEBHOOK_NOTIFICATIONS = "webhook_notifications"
FEATURE_CRM_EXPORT = "crm_export"
FEATURE_LEAD_SCORING = "lead_scoring"
FEATURE_BULK_EXPORT = "bulk_export"
FEATURE_WHITE_LABEL = "white_label"

FREE_FEATURES = [FEATURE_LEAD_COLLECTION]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_STRIPE_PAYMENTS,
    FEATURE_LEAD_PACKAGES,
    FEATURE_CRM_EXPORT,
    FEATURE_LEAD_SCORING,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_WEBHOOK_NOTIFICATIONS,
    FEATURE_BULK_EXPORT,
    FEATURE_WHITE_LABEL,
]

# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------

TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_leads_per_month=50,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_leads_per_month=2_000,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_leads_per_month=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list[TierConfig]:
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
