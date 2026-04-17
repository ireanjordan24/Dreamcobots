"""DreamCo Bot Wars Bot — Competition system, challenge manager, and drag-drop builder."""

from bots.bot_wars_bot.bot_wars_bot import BotWarsBot, BotWarsBotError, BotWarsTierError
from bots.bot_wars_bot.challenge_manager import (
    CHALLENGE_TYPES,
    ChallengeManager,
    ChallengeManagerError,
)
from bots.bot_wars_bot.competition_engine import (
    CompetitionEngine,
    CompetitionEngineError,
)
from bots.bot_wars_bot.drag_drop_builder import (
    BOT_COMPONENT_TYPES,
    DragDropBuilder,
    DragDropBuilderError,
)
from bots.bot_wars_bot.tiers import Tier

__all__ = [
    "BotWarsBot",
    "BotWarsBotError",
    "BotWarsTierError",
    "Tier",
    "CompetitionEngine",
    "CompetitionEngineError",
    "ChallengeManager",
    "ChallengeManagerError",
    "CHALLENGE_TYPES",
    "DragDropBuilder",
    "DragDropBuilderError",
    "BOT_COMPONENT_TYPES",
]
