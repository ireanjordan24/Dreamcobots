"""
Tier definitions for the Code Study Bots / Tool Library Builder ecosystem.

Tiers
-----
FREE       — Discover up to 5 languages, generate tools from documented APIs only.
PRO        — All languages, hidden-capability discovery, versioning, 1 000 tools/month.
ENTERPRISE — Unlimited, marketplace deployment, white-label exports, priority updates.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bots", "ai-models-integration"))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path  # noqa: F401

# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_LIBRARY_DISCOVERY = "library_discovery"
FEATURE_TOOL_GENERATION = "tool_generation"
FEATURE_HIDDEN_CAPABILITY_DISCOVERY = "hidden_capability_discovery"
FEATURE_VERSION_MANAGEMENT = "version_management"
FEATURE_MARKETPLACE_DEPLOYMENT = "marketplace_deployment"
FEATURE_PERIODIC_UPDATES = "periodic_updates"
FEATURE_COUNTRY_CATEGORIZATION = "country_categorization"
FEATURE_WHITE_LABEL_EXPORT = "white_label_export"
FEATURE_UNLIMITED_TOOLS = "unlimited_tools"

TOOL_LIBRARY_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        FEATURE_LIBRARY_DISCOVERY,
        FEATURE_TOOL_GENERATION,
    ],
    Tier.PRO.value: [
        FEATURE_LIBRARY_DISCOVERY,
        FEATURE_TOOL_GENERATION,
        FEATURE_HIDDEN_CAPABILITY_DISCOVERY,
        FEATURE_VERSION_MANAGEMENT,
        FEATURE_PERIODIC_UPDATES,
        FEATURE_COUNTRY_CATEGORIZATION,
    ],
    Tier.ENTERPRISE.value: [
        FEATURE_LIBRARY_DISCOVERY,
        FEATURE_TOOL_GENERATION,
        FEATURE_HIDDEN_CAPABILITY_DISCOVERY,
        FEATURE_VERSION_MANAGEMENT,
        FEATURE_PERIODIC_UPDATES,
        FEATURE_COUNTRY_CATEGORIZATION,
        FEATURE_MARKETPLACE_DEPLOYMENT,
        FEATURE_WHITE_LABEL_EXPORT,
        FEATURE_UNLIMITED_TOOLS,
    ],
}

# Monthly tool-generation limits per tier (None = unlimited)
TOOL_LIMITS: dict[str, int | None] = {
    Tier.FREE.value: 50,
    Tier.PRO.value: 1_000,
    Tier.ENTERPRISE.value: None,
}

# Languages accessible per tier
FREE_LANGUAGES = ["python", "javascript", "sql"]
PRO_LANGUAGES = FREE_LANGUAGES + [
    "typescript", "java", "go", "rust", "ruby", "php", "bash",
    "kotlin", "swift", "scala", "r", "dart",
]
ENTERPRISE_LANGUAGES = PRO_LANGUAGES + [
    "c", "cpp", "haskell", "elixir", "clojure", "lua", "perl",
    "matlab", "julia", "erlang", "fortran", "cobol",
]

LANGUAGE_LIMITS: dict[str, list[str]] = {
    Tier.FREE.value: FREE_LANGUAGES,
    Tier.PRO.value: PRO_LANGUAGES,
    Tier.ENTERPRISE.value: ENTERPRISE_LANGUAGES,
}


def get_tool_library_tier_info(tier: Tier) -> dict:
    """Return a complete tier info dict for the Tool Library Builder."""
    config = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": config.name,
        "price_usd_monthly": config.price_usd_monthly,
        "tool_limit_per_month": TOOL_LIMITS[tier.value],
        "languages": LANGUAGE_LIMITS[tier.value],
        "features": TOOL_LIBRARY_FEATURES[tier.value],
        "support_level": config.support_level,
    }
