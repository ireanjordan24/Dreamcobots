"""
tiers.py – Tiered feature definitions for the Dreamcobots AI Chatbot platform.

Tiers
-----
free         : Core chatbot features available to every user at no cost.
intermediate : Advanced customisation, integrations, and analytics access.
premium      : Extended AI capabilities (KimiK models, priority support,
               full partner-recruitment tools, and marketing-doc management).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class Tier(str, Enum):
    FREE = "free"
    INTERMEDIATE = "intermediate"
    PREMIUM = "premium"


@dataclass(frozen=True)
class TierConfig:
    name: str
    tier: Tier
    monthly_price_usd: float
    max_messages_per_day: int
    ai_models: List[str]
    features: List[str]
    description: str


# ---------------------------------------------------------------------------
# Tier registry
# ---------------------------------------------------------------------------
TIER_CONFIGS: Dict[Tier, TierConfig] = {
    Tier.FREE: TierConfig(
        name="Free",
        tier=Tier.FREE,
        monthly_price_usd=0.0,
        max_messages_per_day=50,
        ai_models=["basic-llm"],
        features=[
            "core_chat",
            "faq_answers",
            "basic_onboarding",
            "resource_lookup",
            "conversation_history",
        ],
        description=(
            "Core chatbot features – no credit card required. "
            "Perfect for individuals exploring Dreamcobots."
        ),
    ),
    Tier.INTERMEDIATE: TierConfig(
        name="Intermediate",
        tier=Tier.INTERMEDIATE,
        monthly_price_usd=29.99,
        max_messages_per_day=500,
        ai_models=["basic-llm", "advanced-llm"],
        features=[
            "core_chat",
            "faq_answers",
            "basic_onboarding",
            "resource_lookup",
            "conversation_history",
            "advanced_customisation",
            "third_party_integrations",
            "analytics_dashboard",
            "email_campaigns",
            "priority_response",
        ],
        description=(
            "Advanced customisation and integrations for growing teams. "
            "Ideal for small-to-medium businesses."
        ),
    ),
    Tier.PREMIUM: TierConfig(
        name="Premium",
        tier=Tier.PREMIUM,
        monthly_price_usd=99.99,
        max_messages_per_day=-1,  # unlimited
        ai_models=["basic-llm", "advanced-llm", "kimi-k"],
        features=[
            "core_chat",
            "faq_answers",
            "basic_onboarding",
            "resource_lookup",
            "conversation_history",
            "advanced_customisation",
            "third_party_integrations",
            "analytics_dashboard",
            "email_campaigns",
            "priority_response",
            "kimi_k_ai",
            "partner_recruitment",
            "ai_ecosystem_directory",
            "marketing_doc_manager",
            "white_label",
            "dedicated_support",
            "sla_guarantee",
        ],
        description=(
            "Full AI power with KimiK models, partner-recruitment tools, "
            "AI-ecosystem directory, and priority dedicated support. "
            "Built for enterprises and platform builders."
        ),
    ),
}


# ---------------------------------------------------------------------------
# Feature-gate helper
# ---------------------------------------------------------------------------

def has_feature(tier: Tier, feature: str) -> bool:
    """Return True if *feature* is available on *tier*."""
    return feature in TIER_CONFIGS[tier].features


def require_feature(tier: Tier, feature: str) -> None:
    """Raise PermissionError if *feature* is not available on *tier*."""
    if not has_feature(tier, feature):
        cfg = TIER_CONFIGS[tier]
        raise PermissionError(
            f"Feature '{feature}' is not available on the {cfg.name} tier. "
            f"Please upgrade to access this feature."
        )


def tier_summary() -> str:
    """Return a human-readable comparison of all tiers."""
    lines = ["Dreamcobots AI Chatbot – Tier Comparison", "=" * 45]
    for cfg in TIER_CONFIGS.values():
        price = "Free" if cfg.monthly_price_usd == 0 else f"${cfg.monthly_price_usd:.2f}/mo"
        msgs = "Unlimited" if cfg.max_messages_per_day == -1 else str(cfg.max_messages_per_day)
        lines += [
            f"\n[{cfg.name}]  {price}",
            f"  Messages/day : {msgs}",
            f"  AI models    : {', '.join(cfg.ai_models)}",
            f"  Description  : {cfg.description}",
            f"  Features     : {', '.join(cfg.features)}",
        ]
    return "\n".join(lines)
