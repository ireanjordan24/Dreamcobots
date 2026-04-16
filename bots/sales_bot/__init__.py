"""DreamCo Sales Bot package — SMS outreach, follow-ups, and deal closing."""

from bots.sales_bot.conversion_tracker import ConversionTracker, LeadStatus
from bots.sales_bot.followup_bot import FollowUpBot
from bots.sales_bot.sales_bot import SalesBot, SalesBotError, SalesBotTierError
from bots.sales_bot.sms_bot import (
    DEFAULT_SMS_TEMPLATE,
    IRRESISTIBLE_OFFER_TEMPLATE,
    SMSBot,
)
from bots.sales_bot.tiers import Tier, TierConfig, get_tier_config

__all__ = [
    "SalesBot",
    "SalesBotError",
    "SalesBotTierError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "SMSBot",
    "DEFAULT_SMS_TEMPLATE",
    "IRRESISTIBLE_OFFER_TEMPLATE",
    "FollowUpBot",
    "ConversionTracker",
    "LeadStatus",
]
