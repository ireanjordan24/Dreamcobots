import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "scan open issues (last 10)",
        "scan open pull requests (last 5)",
        "basic action item generation",
    ],
    Tier.PRO.value: [
        "scan open issues (last 50)",
        "scan open pull requests (last 25)",
        "advanced action item generation",
        "issue categorisation",
        "PR review prioritisation",
        "workflow integration suggestions",
    ],
    Tier.ENTERPRISE.value: [
        "all PRO features",
        "unlimited issue/PR scanning",
        "auto-create bot templates for issues",
        "autonomous workflow updates",
        "cross-repo activity monitoring",
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
