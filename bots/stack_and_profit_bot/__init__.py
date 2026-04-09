"""Stack & Profit Bot — AI-powered deal stacking and profit optimization."""

from .stack_and_profit_bot import (
    StackAndProfitBot,
    StackAndProfitBotTierError,
    DealBot,
    PennyBot,
    ReceiptBot,
    FlipBot,
    CouponBot,
    ProfitEngine,
    RankingAI,
    AlertEngine,
    Deal,
)
from .tiers import Tier, get_tier_config, get_upgrade_path

__all__ = [
    "StackAndProfitBot",
    "StackAndProfitBotTierError",
    "DealBot",
    "PennyBot",
    "ReceiptBot",
    "FlipBot",
    "CouponBot",
    "ProfitEngine",
    "RankingAI",
    "AlertEngine",
    "Deal",
    "Tier",
    "get_tier_config",
    "get_upgrade_path",
]
