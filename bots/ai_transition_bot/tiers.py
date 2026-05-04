"""
Tier configuration for the DreamCo AI Transition Bot.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
)

# Bot-specific features per tier
AI_TRANSITION_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "basic readiness assessment",
        "5 training modules",
        "1 integration API",
        "email support",
    ],
    Tier.PRO.value: [
        "advanced readiness assessment",
        "30 training modules",
        "10 integration APIs",
        "workflow mapping",
        "employee skill scoring",
        "priority support",
    ],
    Tier.ENTERPRISE.value: [
        "full readiness assessment",
        "unlimited training modules",
        "unlimited integration APIs",
        "custom workflow mapping",
        "AI adoption roadmap",
        "white-label kit",
        "dedicated onboarding specialist",
        "SLA support",
    ],
}


def get_ai_transition_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": AI_TRANSITION_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
