"""
Elite Scraper Bot — Package

Provides a reusable, per-bot Elite Scraper Bot system for all DreamCo bots.

Each bot gets a dedicated scraper team configured with custom search queries,
monetization targets, and a persistent knowledge store.  The system runs on a
schedule (or on-demand via GitHub Actions workflow_dispatch) to continuously
feed each parent bot with:

  * Relevant GitHub workflows and repositories
  * Online articles, tutorials, and documentation
  * Client-acquisition leads and partnership opportunities
  * Monetization strategies and revenue ideas
  * Self-improvement techniques and competing bot analysis

Usage
-----
    from bots.elite_scraper import EliteScraper, BOT_PROFILES, KnowledgeStore

    scraper = EliteScraper.for_bot("lead_gen_bot")
    result  = scraper.run()
    print(result.summary())
"""

from __future__ import annotations

from .elite_scraper import EliteScraper, ScraperResult
from .bot_profiles import BOT_PROFILES, BotProfile, get_profile
from .knowledge_store import KnowledgeStore

__all__ = [
    "EliteScraper",
    "ScraperResult",
    "BOT_PROFILES",
    "BotProfile",
    "get_profile",
    "KnowledgeStore",
]
