"""
Tier configuration specific to the Real Estate Bot.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config

RE_EXTRA_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Property search (public listings)",
        "Neighborhood overview",
        "Basic market price trends",
        "Mortgage payment estimator",
    ],
    Tier.PRO.value: [
        "Investment property analysis (ROI/cap rate)",
        "Rental yield calculator",
        "Comparable sales (comps) report",
        "School district & walkability scores",
        "Deal alert notifications",
        "PDF listing exports",
    ],
    Tier.ENTERPRISE.value: [
        "MLS data integration",
        "Multi-property portfolio management",
        "Deal pipeline CRM",
        "1031 exchange advisor",
        "Commercial property underwriting",
        "Dedicated real estate AI analyst",
    ],
}

RE_TOOLS: dict[str, list[str]] = {
    Tier.FREE.value: [
        "property_search",
        "market_overview",
        "mortgage_estimator",
    ],
    Tier.PRO.value: [
        "property_search",
        "market_overview",
        "mortgage_estimator",
        "investment_analyzer",
        "rental_yield_calculator",
        "comps_report",
        "deal_alerts",
    ],
    Tier.ENTERPRISE.value: [
        "property_search",
        "market_overview",
        "mortgage_estimator",
        "investment_analyzer",
        "rental_yield_calculator",
        "comps_report",
        "deal_alerts",
        "mls_integration",
        "portfolio_manager",
        "deal_pipeline_crm",
        "commercial_underwriter",
    ],
}


def get_re_tier_info(tier: Tier) -> dict:
    """Return Real Estate Bot tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "re_features": RE_EXTRA_FEATURES[tier.value],
        "tools": RE_TOOLS[tier.value],
        "support_level": cfg.support_level,
    }
