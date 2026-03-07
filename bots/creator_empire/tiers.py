"""
Tier configuration for CreatorEmpire — Talent Agency + Event Planner +
Distribution + Sports Representation + Streaming Launchpad Bot.

Mirrors the DreamCo platform FREE / PRO / ENTERPRISE structure.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import (  # re-export for convenience
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
)

# ---------------------------------------------------------------------------
# CreatorEmpire-specific feature flags
# ---------------------------------------------------------------------------

FEATURE_TALENT_ONBOARDING = "talent_onboarding"
FEATURE_STREAMER_MODULE = "streamer_module"
FEATURE_ARTIST_MODULE = "artist_module"
FEATURE_ATHLETE_MODULE = "athlete_module"
FEATURE_EVENT_PLANNER = "event_planner"
FEATURE_LEGAL_PROTECTION = "legal_protection"
FEATURE_MONETIZATION_DASHBOARD = "monetization_dashboard"
FEATURE_AI_BRANDING = "ai_branding"
FEATURE_CLIP_DETECTION = "clip_detection"
FEATURE_OUTREACH_AUTOMATION = "outreach_automation"
FEATURE_ROYALTY_CALCULATOR = "royalty_calculator"
FEATURE_CONTRACT_ANALYZER = "contract_analyzer"
FEATURE_NIL_MONETIZATION = "nil_monetization"
FEATURE_STRIPE_PAYMENTS = "stripe_payments"
FEATURE_ADVANCED_ANALYTICS = "advanced_analytics"
FEATURE_WHITE_LABEL = "white_label"

# ---------------------------------------------------------------------------
# Per-tier feature sets
# ---------------------------------------------------------------------------

FREE_CREATOR_FEATURES = [
    FEATURE_TALENT_ONBOARDING,
    FEATURE_STREAMER_MODULE,
    FEATURE_ARTIST_MODULE,
    FEATURE_ATHLETE_MODULE,
    FEATURE_EVENT_PLANNER,
]

PRO_CREATOR_FEATURES = FREE_CREATOR_FEATURES + [
    FEATURE_LEGAL_PROTECTION,
    FEATURE_MONETIZATION_DASHBOARD,
    FEATURE_AI_BRANDING,
    FEATURE_CLIP_DETECTION,
    FEATURE_ROYALTY_CALCULATOR,
    FEATURE_CONTRACT_ANALYZER,
    FEATURE_STRIPE_PAYMENTS,
]

ENTERPRISE_CREATOR_FEATURES = PRO_CREATOR_FEATURES + [
    FEATURE_OUTREACH_AUTOMATION,
    FEATURE_NIL_MONETIZATION,
    FEATURE_ADVANCED_ANALYTICS,
    FEATURE_WHITE_LABEL,
]

CREATOR_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: FREE_CREATOR_FEATURES,
    Tier.PRO.value: PRO_CREATOR_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_CREATOR_FEATURES,
}

# ---------------------------------------------------------------------------
# Human-readable extras per tier shown in describe_tier()
# ---------------------------------------------------------------------------

CREATOR_EXTRAS: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Talent onboarding (up to 3 talent profiles)",
        "Streamer launcher (Twitch/YouTube basic setup)",
        "Artist module (basic distribution info)",
        "Athlete module (basic highlight tips)",
        "Event planner (up to 2 events/month)",
        "5-turn history limit",
    ],
    Tier.PRO.value: [
        "Talent onboarding (unlimited profiles)",
        "Streamer launcher with AI overlay templates",
        "Artist module with beat matching + royalty splits",
        "Athlete module with NIL guides",
        "Event planner (unlimited events)",
        "Legal & Protection layer (contract analysis)",
        "Monetization dashboard (service fees & subscriptions)",
        "Stripe/PayPal payment integration",
        "AI branding kit generation",
        "Clip detection & highlight reel creation",
        "Royalty calculator",
    ],
    Tier.ENTERPRISE.value: [
        "Everything in Pro",
        "Full outreach automation (email/DM campaigns)",
        "NIL deal monetization workflows",
        "Advanced analytics & reporting",
        "White-label branding",
        "Dedicated account manager",
        "Custom SLA",
    ],
}


def get_creator_tier_info(tier: Tier) -> dict:
    """Return a combined tier info dict for CreatorEmpire."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "creator_features": CREATOR_FEATURES[tier.value],
        "creator_extras": CREATOR_EXTRAS[tier.value],
        "support_level": cfg.support_level,
    }
