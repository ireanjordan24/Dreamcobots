"""
Tier configuration for the Dreamcobots Mining Bot.

Tiers:
  - FREE:       Basic mining, single algorithm, limited analytics.
  - PRO:        Multi-strategy mining, advanced analytics, fraud detection.
  - ENTERPRISE: Unlimited features, AI-driven optimisation, hardware wallet
                support, multi-exchange execution.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class MiningTierConfig:
    """Configuration for a Mining Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    monitored_coins: int  # maximum simultaneously monitored coins
    max_strategies: int   # pool, solo, merged …
    analytics_depth: str  # "basic" | "advanced" | "full"
    ai_optimisation: bool
    fraud_detection: bool
    multi_exchange: bool
    hardware_wallet: bool
    backtesting: bool
    alerts: bool
    support_level: str
    features: List[str] = field(default_factory=list)

    def has_feature(self, feature: str) -> bool:
        return feature in self.features


# ---------------------------------------------------------------------------
# Feature flag constants
# ---------------------------------------------------------------------------
FEATURE_POOL_MINING = "pool_mining"
FEATURE_SOLO_MINING = "solo_mining"
FEATURE_MERGED_MINING = "merged_mining"
FEATURE_ADAPTIVE_STRATEGY = "adaptive_strategy"
FEATURE_PROFITABILITY_ANALYTICS = "profitability_analytics"
FEATURE_ENERGY_ANALYTICS = "energy_analytics"
FEATURE_ROI_TRACKING = "roi_tracking"
FEATURE_SMART_ALERTS = "smart_alerts"
FEATURE_AI_OPTIMISATION = "ai_optimisation"
FEATURE_FRAUD_DETECTION = "fraud_detection"
FEATURE_HONEYPOT_DETECTION = "honeypot_detection"
FEATURE_CONTRACT_VERIFICATION = "contract_verification"
FEATURE_MULTI_EXCHANGE = "multi_exchange"
FEATURE_DEX_ROUTING = "dex_routing"
FEATURE_HARDWARE_WALLET = "hardware_wallet"
FEATURE_BACKTESTING = "backtesting"
FEATURE_REINFORCEMENT_LEARNING = "reinforcement_learning"

# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------
TIER_CATALOGUE: dict[str, MiningTierConfig] = {
    Tier.FREE.value: MiningTierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        monitored_coins=2,
        max_strategies=1,
        analytics_depth="basic",
        ai_optimisation=False,
        fraud_detection=False,
        multi_exchange=False,
        hardware_wallet=False,
        backtesting=False,
        alerts=False,
        support_level="Community",
        features=[
            FEATURE_POOL_MINING,
            FEATURE_PROFITABILITY_ANALYTICS,
        ],
    ),
    Tier.PRO.value: MiningTierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        monitored_coins=10,
        max_strategies=3,
        analytics_depth="advanced",
        ai_optimisation=False,
        fraud_detection=True,
        multi_exchange=True,
        hardware_wallet=False,
        backtesting=True,
        alerts=True,
        support_level="Email (48 h SLA)",
        features=[
            FEATURE_POOL_MINING,
            FEATURE_SOLO_MINING,
            FEATURE_MERGED_MINING,
            FEATURE_ADAPTIVE_STRATEGY,
            FEATURE_PROFITABILITY_ANALYTICS,
            FEATURE_ENERGY_ANALYTICS,
            FEATURE_ROI_TRACKING,
            FEATURE_SMART_ALERTS,
            FEATURE_FRAUD_DETECTION,
            FEATURE_HONEYPOT_DETECTION,
            FEATURE_CONTRACT_VERIFICATION,
            FEATURE_MULTI_EXCHANGE,
            FEATURE_BACKTESTING,
        ],
    ),
    Tier.ENTERPRISE.value: MiningTierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=299.0,
        monitored_coins=0,  # unlimited (0 = no cap)
        max_strategies=0,   # unlimited
        analytics_depth="full",
        ai_optimisation=True,
        fraud_detection=True,
        multi_exchange=True,
        hardware_wallet=True,
        backtesting=True,
        alerts=True,
        support_level="Dedicated 24/7",
        features=[
            FEATURE_POOL_MINING,
            FEATURE_SOLO_MINING,
            FEATURE_MERGED_MINING,
            FEATURE_ADAPTIVE_STRATEGY,
            FEATURE_PROFITABILITY_ANALYTICS,
            FEATURE_ENERGY_ANALYTICS,
            FEATURE_ROI_TRACKING,
            FEATURE_SMART_ALERTS,
            FEATURE_AI_OPTIMISATION,
            FEATURE_FRAUD_DETECTION,
            FEATURE_HONEYPOT_DETECTION,
            FEATURE_CONTRACT_VERIFICATION,
            FEATURE_MULTI_EXCHANGE,
            FEATURE_DEX_ROUTING,
            FEATURE_HARDWARE_WALLET,
            FEATURE_BACKTESTING,
            FEATURE_REINFORCEMENT_LEARNING,
        ],
    ),
}


def get_tier_config(tier: Tier) -> MiningTierConfig:
    return TIER_CATALOGUE[tier.value]


def get_upgrade_path(tier: Tier) -> Optional[MiningTierConfig]:
    order = [Tier.FREE, Tier.PRO, Tier.ENTERPRISE]
    idx = order.index(tier)
    if idx + 1 >= len(order):
        return None
    return TIER_CATALOGUE[order[idx + 1].value]


def list_tiers() -> List[MiningTierConfig]:
    return [TIER_CATALOGUE[t.value] for t in Tier]
