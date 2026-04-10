import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config

BOT_FEATURES = {
    Tier.FREE.value: [
        "AutoClientHunter — up to 5 leads/day",
        "basic_closer — scripted negotiation templates",
        "stripe_payments — single Stripe integration",
        "basic revenue tracking",
        "daily activity summary",
    ],
    Tier.PRO.value: [
        "AutoClientHunter — unlimited leads/day",
        "ai_closer — full AI negotiation engine",
        "stripe + paypal + invoice automation",
        "ViralEngine — 3 social platforms",
        "SelfImprovingAI — revenue stream optimization",
        "advanced analytics & reports",
        "automated outreach proposals",
        "deal pipeline tracking",
        "email revenue alerts",
    ],
    Tier.ENTERPRISE.value: [
        "AutoClientHunter — unlimited leads + white-label outreach",
        "ai_closer — enterprise deal closing + bulk booking",
        "all payment providers (Stripe, PayPal, Crypto, Bank Transfer)",
        "ViralEngine — all social platforms (unlimited posts/day)",
        "SelfImprovingAI — custom AI training + auto-prioritization",
        "white_label — full white-label branding",
        "API access — programmatic control of all engines",
        "dedicated_support — dedicated account manager",
        "custom_ai_training — fine-tune on your business data",
        "full revenue orchestration + custom dashboards",
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
