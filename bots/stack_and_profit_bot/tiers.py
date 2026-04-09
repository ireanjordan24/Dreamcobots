"""
Tier configuration for the StackAndProfitBot.

Tiers:
  - FREE:            Basic deal finding (Walmart, Amazon, Target), 5 deals/day,
                     basic profit calc, receipt upload (3/day), basic coupon stacking.
  - PRO ($49/mo):    All free + penny deal finder, flip finder (local), full cashback
                     stacking (CoinOut/Ibotta/Fetch), AI ranking, 50 deals/day,
                     coupon stacking AI.
  - ENTERPRISE ($199/mo): All pro + unlimited deals, full AI profit engine, ranking AI,
                     alert engine, white-label, API access.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers  # noqa: F401

# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_DEAL_FINDER = "deal_finder"
FEATURE_PENNY_DEALS = "penny_deals"
FEATURE_RECEIPT_CASHBACK = "receipt_cashback"
FEATURE_FLIP_FINDER = "flip_finder"
FEATURE_COUPON_STACKING = "coupon_stacking"
FEATURE_AI_RANKING = "ai_ranking"
FEATURE_ALERT_ENGINE = "alert_engine"
FEATURE_PROFIT_ENGINE = "profit_engine"
FEATURE_API_ACCESS = "api_access"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_ANALYTICS = "analytics"

BOT_FEATURES = {
    Tier.FREE.value: [
        "deal finding (Walmart, Amazon, Target)",
        "5 deals/day",
        "basic profit calculation",
        "receipt upload (3/day)",
        "basic coupon stacking (1 coupon at a time)",
    ],
    Tier.PRO.value: [
        "penny deal finder",
        "flip finder (local markets)",
        "full cashback stacking (CoinOut / Ibotta / Fetch Rewards)",
        "AI deal ranking",
        "50 deals/day",
        "coupon stacking AI (up to 5 coupons)",
        "affiliate commission tracking",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited deals/day",
        "full AI profit engine",
        "advanced ranking AI",
        "alert engine (real-time deal alerts)",
        "white-label deployment",
        "full API access",
        "advanced analytics dashboard",
        "priority 24/7 support",
    ],
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a dict describing the tier features and pricing."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
