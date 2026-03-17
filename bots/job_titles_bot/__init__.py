"""DreamCo Job Titles Bot — comprehensive AI workforce platform."""

from bots.job_titles_bot.job_titles_bot import JobTitlesBot, JobTitlesBotError, JobTitlesBotTierError
from bots.job_titles_bot.tiers import BOT_FEATURES, get_bot_tier_info
from bots.job_titles_bot.job_titles_database import JobTitleDatabase, JobTitle
from bots.job_titles_bot.job_bot_generator import JobBotGenerator, AIWorkerBot
from bots.job_titles_bot.autonomous_trainer import AutonomousTrainer, TrainingSession, ItemValuation

__all__ = [
    "JobTitlesBot",
    "JobTitlesBotError",
    "JobTitlesBotTierError",
    "BOT_FEATURES",
    "get_bot_tier_info",
    "JobTitleDatabase",
    "JobTitle",
    "JobBotGenerator",
    "AIWorkerBot",
    "AutonomousTrainer",
    "TrainingSession",
    "ItemValuation",
]
