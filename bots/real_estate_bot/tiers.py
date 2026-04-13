import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "1 location",
        "basic property search",
        "price estimate",
        "cap rate calculator",
        "multi-platform property search (Zillow + Facebook Marketplace only)",
    ],
    Tier.PRO.value: [
        "10 locations",
        "advanced search filters",
        "ROI calculator",
        "market trends",
        "cash flow analysis",
        "rental comps",
        "multi-platform property search across all 5 platforms (+ county tax, auctions, Realtor.com)",
        "house flip pipeline (acquire → renovate → list on 5 platforms)",
        "outreach script generator (owners + city housing departments)",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited locations",
        "AI valuation",
        "predictive analytics",
        "investment portfolio tracker",
        "deal scoring",
        "API access",
        "government contract matcher (SAM.gov, HUD, Grants.gov)",
        "revenue matching engine (property → program → monthly income)",
        "master lease strategy calculator",
        "LLC + nonprofit hybrid structure analysis",
        "automated deal dashboard",
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
