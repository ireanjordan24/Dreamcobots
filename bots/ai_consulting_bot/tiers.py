"""
Tier configuration for the DreamCo AI Consulting Bot.
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
AI_CONSULTING_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "1 consulting session",
        "AI readiness report",
        "community expert matching",
        "email support",
    ],
    Tier.PRO.value: [
        "10 consulting sessions/month",
        "dedicated expert matching",
        "custom AI roadmap",
        "session transcripts",
        "progress tracking",
        "priority support",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited consulting sessions",
        "dedicated AI transition team",
        "custom AI roadmap with milestones",
        "white-glove onboarding",
        "SLA-backed delivery",
        "executive AI briefings",
        "change management playbook",
        "24/7 dedicated support",
    ],
}


def get_ai_consulting_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": AI_CONSULTING_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
