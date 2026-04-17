"""
Creative Studio Bot — Package Initializer

Exports all public classes and helpers for the Creative Studio Bot.
"""

from bots.creative_studio_bot.content_creator import (
    GENRES,
    STYLES,
    ArtCreator,
    FilmCreator,
    MusicCreator,
)
from bots.creative_studio_bot.creative_studio_bot import (
    CreativeStudioBot,
    CreativeStudioBotError,
)
from bots.creative_studio_bot.influencer_engine import (
    PLATFORMS,
    ContentStrategyEngine,
    MemeGenerator,
)
from bots.creative_studio_bot.tiers import (
    BOT_FEATURES,
    Tier,
    TierConfig,
    get_bot_tier_info,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
)

__all__ = [
    "CreativeStudioBot",
    "CreativeStudioBotError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "get_upgrade_path",
    "list_tiers",
    "BOT_FEATURES",
    "get_bot_tier_info",
    "MusicCreator",
    "FilmCreator",
    "ArtCreator",
    "GENRES",
    "STYLES",
    "ContentStrategyEngine",
    "MemeGenerator",
    "PLATFORMS",
]
