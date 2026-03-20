"""Sales Bot package — auto outreach and deal closing bot."""
from bots.sales_bot.closer_bot import CloserBot, CloserBotTierError, Bot
from bots.sales_bot.tiers import Tier

__all__ = ["CloserBot", "CloserBotTierError", "Bot", "Tier"]
