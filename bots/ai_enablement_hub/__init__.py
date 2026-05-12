"""
AI Enablement Hub package.

Exposes the main orchestrator and key sub-components for external use.
"""

from bots.ai_enablement_hub.ai_enablement_hub import (
    AIEnablementHub,
    AIEnablementHubError,
    AIEnablementTierError,
)
from bots.ai_enablement_hub.tiers import Tier, get_bot_tier_info
from bots.ai_enablement_hub.bot_tier_classifier import BotTierClassifier, ScalabilityTier

__all__ = [
    "AIEnablementHub",
    "AIEnablementHubError",
    "AIEnablementTierError",
    "Tier",
    "get_bot_tier_info",
    "BotTierClassifier",
    "ScalabilityTier",
]
