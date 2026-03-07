"""Tier configuration for the Finance Bot."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers

__all__ = ["Tier", "TierConfig", "get_tier_config", "get_upgrade_path", "list_tiers",
           "FINANCE_FEATURES", "get_finance_tier_info"]

FINANCE_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Basic budget tracking",
        "Expense categorization",
        "Monthly spending reports",
    ],
    Tier.PRO.value: [
        "Investment portfolio tracking",
        "Tax estimation",
        "Multi-account sync",
        "Cash flow forecasting",
        "Bill reminders",
    ],
    Tier.ENTERPRISE.value: [
        "AI financial advisor",
        "Tax filing automation",
        "Custom financial models",
        "Multi-currency support",
        "Audit-ready reports",
        "Bank-level security",
    ],
}


def get_finance_tier_info(tier: Tier) -> dict:
    """Return finance-bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "support_level": cfg.support_level,
        "finance_features": FINANCE_FEATURES[tier.value],
    }
