"""
Tier configuration for the DreamOps AI Automation Suite.

Tiers:
  - FREE:       $0/mo - basic monitoring, up to 5 workflows, 3 bots
  - PRO:        $149/mo - 50 workflows, 10 bots, anomaly detection, bottleneck detection
  - ENTERPRISE: $499/mo - unlimited workflows/bots, all tools, auto-failover, cost reduction engine, throughput maximizer
"""

import sys
import os
import importlib.util

_AI_MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "ai-models-integration")
_AI_MODELS_DIR = os.path.abspath(_AI_MODELS_DIR)
_AI_TIERS_PATH = os.path.join(_AI_MODELS_DIR, "tiers.py")
sys.path.insert(0, _AI_MODELS_DIR)

_tiers_mod = sys.modules.get("tiers")
if not _tiers_mod or not getattr(_tiers_mod, "__file__", "").startswith(_AI_MODELS_DIR):
    _spec = importlib.util.spec_from_file_location("tiers", _AI_TIERS_PATH)
    _tiers_mod = importlib.util.module_from_spec(_spec)
    assert _spec and _spec.loader
    _spec.loader.exec_module(_tiers_mod)
    sys.modules["tiers"] = _tiers_mod

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401

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


class _TierKeyMap(dict):
    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        key_value = getattr(key, "value", None)
        if key_value is not None and key_value in self:
            return super().__getitem__(key_value)
        return super().__getitem__(key)

WORKFLOW_LIMITS = _TierKeyMap({
    Tier.FREE.value: 5,
    Tier.PRO.value: 50,
    Tier.ENTERPRISE.value: None,  # unlimited
})

BOT_LIMITS = _TierKeyMap({
    Tier.FREE.value: 3,
    Tier.PRO.value: 10,
    Tier.ENTERPRISE.value: None,  # unlimited
})


def get_bot_tier_info(tier: Tier) -> dict:
    tier_value = getattr(tier, "value", str(tier).lower())
    cfg = get_tier_config(Tier(tier_value))
    return {
        "tier": tier_value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "features": BOT_FEATURES[tier_value],
        "support_level": cfg.support_level,
        "workflow_limit": WORKFLOW_LIMITS[tier_value],
        "bot_limit": BOT_LIMITS[tier_value],
    }
