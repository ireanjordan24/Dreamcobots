import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["mock leads", "local business data", "JSON export"],
    Tier.PRO.value: ["mock leads", "local business data", "JSON export", "multi-city support", "lead deduplication"],
    Tier.ENTERPRISE.value: ["mock leads", "local business data", "JSON export", "multi-city support", "lead deduplication", "SerpAPI integration", "Google Places API", "bulk export"],
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
