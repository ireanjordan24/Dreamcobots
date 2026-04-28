"""
code_study_bots — Unified Tool-Building Ecosystem for Code-Studying Bots.

This package organises all code-studying bots into one coherent ecosystem that:

* Discovers coding libraries for every language globally (LibraryScraper)
* Generates usable tools from documented *and* hidden library capabilities (ToolGenerator)
* Tracks and manages semantic versions for every generated tool (VersionManager)
* Deploys tools to the DreamCo marketplace (MarketplaceDeployer)
* Orchestrates the entire pipeline through a single bot (ToolLibraryBuilderBot)

Quick start
-----------
>>> from code_study_bots import ToolLibraryBuilderBot
>>> from code_study_bots.tiers import Tier
>>> bot = ToolLibraryBuilderBot(tier=Tier.PRO)
>>> bot.build_tools_for_library("python", "pandas")
"""

from .tool_library_builder import (
    ToolLibraryBuilderBot,
    ToolLibraryBuilderTierError,
    ToolLibraryBuilderLimitError,
    ToolLibraryBuilderError,
)
from .library_scraper import LibraryScraper, LibraryRecord
from .tool_generator import ToolGenerator, GeneratedTool
from .version_manager import VersionManager
from .marketplace_deployer import MarketplaceDeployer, ToolListing
from .tiers import Tier, get_tool_library_tier_info

__all__ = [
    "ToolLibraryBuilderBot",
    "ToolLibraryBuilderTierError",
    "ToolLibraryBuilderLimitError",
    "ToolLibraryBuilderError",
    "LibraryScraper",
    "LibraryRecord",
    "ToolGenerator",
    "GeneratedTool",
    "VersionManager",
    "MarketplaceDeployer",
    "ToolListing",
    "Tier",
    "get_tool_library_tier_info",
]
