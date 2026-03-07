"""
Tier configuration for the Dreamcobots Real Estate Bot.
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
REAL_ESTATE_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: ["10 property searches/month", "basic filters", "market overview"],
    Tier.PRO.value: ["500 searches/month", "deal scoring", "investment calculator", "comparable analysis"],
    Tier.ENTERPRISE.value: ["unlimited searches", "predictive pricing", "portfolio management", "MLS integration"],
}


def get_real_estate_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": REAL_ESTATE_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
