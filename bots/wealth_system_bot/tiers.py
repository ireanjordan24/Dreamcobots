"""
Tier configuration for the DreamCo Global Wealth System Bot.

Tiers:
  - FREE:        1 Wealth Hub, basic investment tracking, money finder bot.
  - PRO ($49):   Up to 5 Wealth Hubs, all income bots, governance voting,
                 real-time asset tracking, automated dividends.
  - ENTERPRISE ($149): Unlimited Wealth Hubs, full bot ecosystem, DreamCoin
                 staking, cross-hub deals, white-label, API access,
                 advanced analytics, priority support.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401

# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_WEALTH_HUB = "wealth_hub"
FEATURE_MONEY_FINDER_BOT = "money_finder_bot"
FEATURE_REFERRAL_BOT = "referral_bot"
FEATURE_REAL_ESTATE_BOT = "real_estate_bot"
FEATURE_TRADING_BOT = "trading_bot"
FEATURE_ARBITRAGE_BOT = "arbitrage_bot"
FEATURE_GOVERNANCE_VOTING = "governance_voting"
FEATURE_AUTOMATED_DIVIDENDS = "automated_dividends"
FEATURE_DREAMCOIN = "dreamcoin"
FEATURE_CROSS_HUB_DEALS = "cross_hub_deals"
FEATURE_ANALYTICS = "analytics"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_ASSET_REBALANCING = "asset_rebalancing"
FEATURE_KYC_VERIFICATION = "kyc_verification"

FREE_FEATURES = [
    FEATURE_WEALTH_HUB,
    FEATURE_MONEY_FINDER_BOT,
    FEATURE_KYC_VERIFICATION,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_REFERRAL_BOT,
    FEATURE_REAL_ESTATE_BOT,
    FEATURE_TRADING_BOT,
    FEATURE_GOVERNANCE_VOTING,
    FEATURE_AUTOMATED_DIVIDENDS,
    FEATURE_ANALYTICS,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_ARBITRAGE_BOT,
    FEATURE_DREAMCOIN,
    FEATURE_CROSS_HUB_DEALS,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_ASSET_REBALANCING,
]

BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}

# Maximum number of Wealth Hubs per tier (None = unlimited).
HUB_LIMITS = {
    Tier.FREE: 1,
    Tier.PRO: 5,
    Tier.ENTERPRISE: None,
}

# Maximum members per Wealth Hub.
MEMBER_LIMITS = {
    Tier.FREE: 10,
    Tier.PRO: 100,
    Tier.ENTERPRISE: None,
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a summary dict for a given tier."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "max_hubs": HUB_LIMITS[tier],
        "max_members_per_hub": MEMBER_LIMITS[tier],
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
