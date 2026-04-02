"""
CreatorEmpire bot package.

Talent Agency + Event Planner + Distribution +
Sports Representation + Streaming Launchpad Bot.
"""

from bots.creator_empire.creator_empire import CreatorEmpire, CreatorEmpireError
from bots.creator_empire.tiers import (
    Tier,
    get_creator_tier_info,
    CREATOR_FEATURES,
    CREATOR_EXTRAS,
)

__all__ = [
    "CreatorEmpire",
    "CreatorEmpireError",
    "Tier",
    "get_creator_tier_info",
    "CREATOR_FEATURES",
    "CREATOR_EXTRAS",
]
