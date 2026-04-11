"""
Tier configuration for the Quantum Decision Bot.

Tiers:
  - FREE:              Basic scenario generation (3 scenarios, 100 simulations),
                       single-dimension scoring, best-path output.
  - PRO ($49):         Unlimited scenarios, 10,000 simulations, multi-dimensional
                       modeling, entangled bot routing, money automation,
                       content viral engine, Stripe billing, referral system.
  - ENTERPRISE ($199): All PRO features + self-improving AI learning loop,
                       hyper-simulation (100,000 runs), global bot orchestration,
                       white-label, priority support.
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
    max_scenarios: Optional[int]
    max_simulations: int
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_QUANTUM_ENGINE = "quantum_engine"
FEATURE_SIMULATION_ENGINE = "simulation_engine"
FEATURE_PROBABILITY_MODEL = "probability_model"
FEATURE_DIMENSION_MAPPER = "dimension_mapper"
FEATURE_BOT_ROUTER = "bot_router"
FEATURE_MONEY_AUTOMATION = "money_automation"
FEATURE_CONTENT_VIRAL_ENGINE = "content_viral_engine"
FEATURE_SELF_IMPROVING_AI = "self_improving_ai"
FEATURE_HYPER_SIMULATION = "hyper_simulation"
FEATURE_GLOBAL_ORCHESTRATION = "global_orchestration"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_STRIPE_BILLING = "stripe_billing"
FEATURE_REFERRAL_SYSTEM = "referral_system"

FREE_FEATURES = [
    FEATURE_QUANTUM_ENGINE,
    FEATURE_SIMULATION_ENGINE,
    FEATURE_PROBABILITY_MODEL,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_DIMENSION_MAPPER,
    FEATURE_BOT_ROUTER,
    FEATURE_MONEY_AUTOMATION,
    FEATURE_CONTENT_VIRAL_ENGINE,
    FEATURE_STRIPE_BILLING,
    FEATURE_REFERRAL_SYSTEM,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_SELF_IMPROVING_AI,
    FEATURE_HYPER_SIMULATION,
    FEATURE_GLOBAL_ORCHESTRATION,
    FEATURE_WHITE_LABEL,
]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_scenarios=3,
        max_simulations=100,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_scenarios=None,
        max_simulations=10_000,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_scenarios=None,
        max_simulations=100_000,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}

BOT_FEATURES = {
    "quantum_engine": "Generate all possible outcome scenarios and collapse to best path",
    "simulation_engine": "Monte Carlo multi-outcome simulation runner",
    "probability_model": "Profit/risk scoring for each simulated outcome",
    "dimension_mapper": "Map decisions across time, capital, risk, and scale dimensions",
    "bot_router": "Entangled network: dispatch decisions to all connected DreamCo bots",
    "money_automation": "Autonomous opportunity scanner and action recommender",
    "content_viral_engine": "Auto-generate viral content scripts based on simulation results",
    "self_improving_ai": "Learning loop that updates probability weights from real outcomes",
    "hyper_simulation": "Up to 100,000 simulation runs per decision",
    "global_orchestration": "Full orchestration of all registered DreamCo bots",
    "white_label": "White-label branding for enterprise clients",
    "stripe_billing": "Integrated Stripe subscription management",
    "referral_system": "Referral tracking and commission payouts",
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list:
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_bot_tier_info() -> dict:
    return {tier.value: TIER_CATALOGUE[tier.value] for tier in Tier}


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
