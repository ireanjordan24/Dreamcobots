"""Marketing Bot package."""

from .marketing_bot import MarketingBot, MarketingRequestLimitError, MarketingTierError
from .tiers import MARKETING_CHANNELS, MARKETING_EXTRA_FEATURES, get_marketing_tier_info

__all__ = [
    "MarketingBot",
    "MarketingTierError",
    "MarketingRequestLimitError",
    "get_marketing_tier_info",
    "MARKETING_EXTRA_FEATURES",
    "MARKETING_CHANNELS",
]
