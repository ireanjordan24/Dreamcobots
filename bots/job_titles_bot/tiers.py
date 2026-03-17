"""Tier definitions for the DreamCo Job Titles Bot."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "search job titles by keyword",
        "browse top 10 job titles per industry",
        "view basic job description",
        "view required skills",
        "hire a human employee",
    ],
    Tier.PRO.value: [
        "search all job titles (1000+)",
        "full industry browsing",
        "detailed job description & responsibilities",
        "required skills & education",
        "salary range data",
        "generate AI worker bot for any job",
        "hire human or AI worker",
        "business type lookup",
        "robot contract matching",
    ],
    Tier.ENTERPRISE.value: [
        "complete job title database (all industries)",
        "autonomous AI worker training",
        "bulk bot generation",
        "face & object recognition training",
        "antique / item valuation module",
        "scalable upgrade propagation (all buddy bots)",
        "white-label workforce solutions",
        "manufacturer & robot contract pipeline",
        "API access",
        "priority support",
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
