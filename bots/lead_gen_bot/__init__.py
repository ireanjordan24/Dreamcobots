"""
Lead Generation Bot package.

Usage::

    from bots.lead_gen_bot import LeadGenBot, Tier

    bot = LeadGenBot(tier=Tier.PRO)
    lead = bot.collect_lead(name="Jane Doe", email="jane@example.com")
"""

from bots.lead_gen_bot.lead_gen_bot import (
    LeadGenBot,
    LeadGenBotError,
    LeadGenBotTierError,
    LeadGenBotLimitError,
    Lead,
    LEAD_PACKAGES,
)
from bots.lead_gen_bot.tiers import Tier, get_tier_config, list_tiers

__all__ = [
    "LeadGenBot",
    "LeadGenBotError",
    "LeadGenBotTierError",
    "LeadGenBotLimitError",
    "Lead",
    "LEAD_PACKAGES",
    "Tier",
    "get_tier_config",
    "list_tiers",
]
