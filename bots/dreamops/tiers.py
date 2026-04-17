"""
Tier configuration for the DreamOps AI Automation Suite.

Tiers:
  - FREE:       $0/mo - basic monitoring, up to 5 workflows, 3 bots
  - PRO:        $149/mo - 50 workflows, 10 bots, anomaly detection, bottleneck detection
  - ENTERPRISE: $499/mo - unlimited workflows/bots, all tools, auto-failover, cost reduction engine, throughput maximizer
"""

import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration")
)
from tiers import (
    TIER_CATALOGUE,
    Tier,
    TierConfig,  # noqa: F401
    get_tier_config,
    get_upgrade_path,
    list_tiers,
)

BOT_FEATURES = {
    Tier.FREE.value: [
        "basic operations monitoring",
        "up to 5 workflows",
        "up to 3 bots",
        "simple status dashboard",
        "email alerts",
    ],
    Tier.PRO.value: [
        "50 workflows",
        "10 bots",
        "anomaly detection",
        "bottleneck detection",
        "auto-scaling",
        "ops commander",
        "task delegation AI",
        "advanced dashboard",
        "priority support",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited workflows",
        "unlimited bots",
        "all PRO features",
        "auto-failover",
        "cost reduction engine",
        "throughput maximizer",
        "resilience scorer",
        "full API access",
        "dedicated support",
        "white-label dashboard",
    ],
}

WORKFLOW_LIMITS = {
    Tier.FREE: 5,
    Tier.PRO: 50,
    Tier.ENTERPRISE: None,  # unlimited
}

BOT_LIMITS = {
    Tier.FREE: 3,
    Tier.PRO: 10,
    Tier.ENTERPRISE: None,  # unlimited
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
        "workflow_limit": WORKFLOW_LIMITS[tier],
        "bot_limit": BOT_LIMITS[tier],
    }
