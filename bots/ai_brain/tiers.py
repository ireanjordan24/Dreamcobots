import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "basic revenue analysis",
        "5 decision options",
        "single-run decision",
        "simple logging",
    ],
    Tier.PRO.value: [
        "advanced revenue analysis",
        "CRM trend analysis",
        "workflow bottleneck detection",
        "weighted decision engine",
        "enhanced logging",
        "decision history (30 days)",
    ],
    Tier.ENTERPRISE.value: [
        "all PRO features",
        "full CRM integration",
        "multi-source data analysis",
        "autonomous decision cycles",
        "priority action routing",
        "unlimited decision history",
        "API access",
    ],
}


def get_bot_tier_info(tier: Tier) -> dict:
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
