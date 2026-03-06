"""
Dreamcobots AI Chatbot package.

Exports the public API for the tiered AI chatbot system.
"""

from .chatbot import AIChatbot, ChatSession, Message
from .tiers import Tier, TierConfig, TIER_CONFIGS, has_feature, require_feature, tier_summary
from .analytics import AnalyticsEngine, CompanyProfile, PartnerRecruitmentResult
from .marketplace import Marketplace, Subscription, CheckoutSession, MarketingDocument

__all__ = [
    # Chatbot
    "AIChatbot",
    "ChatSession",
    "Message",
    # Tiers
    "Tier",
    "TierConfig",
    "TIER_CONFIGS",
    "has_feature",
    "require_feature",
    "tier_summary",
    # Analytics
    "AnalyticsEngine",
    "CompanyProfile",
    "PartnerRecruitmentResult",
    # Marketplace
    "Marketplace",
    "Subscription",
    "CheckoutSession",
    "MarketingDocument",
]
