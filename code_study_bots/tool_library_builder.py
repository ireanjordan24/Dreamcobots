"""
Tool Library Builder Bot — unified orchestrator that ties together every
code-studying capability in the DreamCobots ecosystem.

This bot is the single entry-point for:

1. **Library Discovery**  — catalog coding libraries worldwide (LibraryScraper)
2. **Tool Generation**    — build usable tools from documented *and* hidden
                            library symbols (ToolGenerator)
3. **Version Management** — track and bump semantic versions (VersionManager)
4. **Marketplace Deployment** — publish tools for developers/orgs to buy
                                (MarketplaceDeployer)

Tiers
-----
FREE       — 3 languages, 50 tools/month, documented symbols only, no deployment.
PRO        — All open-source languages, 1,000 tools/month, hidden-symbol discovery,
             versioning, periodic-update scheduling.
ENTERPRISE — All languages, unlimited tools, marketplace deployment, white-label
             exports, SLA-backed support.

GLOBAL AI SOURCES FLOW compliance
----------------------------------
Import ``framework.GlobalAISourcesFlow`` is included as required by the
Dreamcobots framework mandate.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bots", "ai-models-integration"))

from framework import GlobalAISourcesFlow  # noqa: F401  — GLOBAL AI SOURCES FLOW

from .tiers import (
    Tier,
    get_tier_config,
    get_upgrade_path,
    TOOL_LIBRARY_FEATURES,
    TOOL_LIMITS,
    LANGUAGE_LIMITS,
    FEATURE_HIDDEN_CAPABILITY_DISCOVERY,
    FEATURE_MARKETPLACE_DEPLOYMENT,
    FEATURE_VERSION_MANAGEMENT,
    FEATURE_PERIODIC_UPDATES,
    FEATURE_COUNTRY_CATEGORIZATION,
    FEATURE_WHITE_LABEL_EXPORT,
    get_tool_library_tier_info,
)
from .library_scraper import LibraryScraper, LibraryRecord
from .tool_generator import ToolGenerator, GeneratedTool
from .version_manager import VersionManager
from .marketplace_deployer import MarketplaceDeployer, ToolListing


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class ToolLibraryBuilderTierError(Exception):
    """Raised when a requested feature is not available on the current tier."""


class ToolLibraryBuilderLimitError(Exception):
    """Raised when the monthly tool-generation limit has been reached."""


class ToolLibraryBuilderError(Exception):
    """Raised for general bot errors."""


# ---------------------------------------------------------------------------
# ToolLibraryBuilderBot
# ---------------------------------------------------------------------------

class ToolLibraryBuilderBot:
    """
    Unified tool-building ecosystem bot.

    Organises all code-studying bots, generates usable tools from every
    coding library on the planet (including hidden capabilities), stores
    them in categorised libraries by language and purpose, and deploys
    them to the DreamCo marketplace.
    """

    def __init__(self, tier: Tier = Tier.FREE, user_id: str = "user") -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self.user_id = user_id

        # Core sub-systems
        self.scraper = LibraryScraper()
        self.generator = ToolGenerator()
        self.versions = VersionManager()
        self.deployer = MarketplaceDeployer()

        self._tools_generated_this_month: int = 0

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if feature not in TOOL_LIBRARY_FEATURES[self.tier.value]:
            upgrade = get_upgrade_path(self.tier)
            tier_name = upgrade.name if upgrade else "a higher tier"
            raise ToolLibraryBuilderTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier. "
                f"Upgrade to {tier_name} for access."
            )

    def _check_tool_limit(self, count: int = 1) -> None:
        limit = TOOL_LIMITS[self.tier.value]
        if limit is not None and (self._tools_generated_this_month + count) > limit:
            raise ToolLibraryBuilderLimitError(
                f"Monthly tool-generation limit of {limit} reached on the "
                f"{self.config.name} tier. Upgrade to generate more tools."
            )

    def _check_language(self, language: str) -> None:
        allowed = LANGUAGE_LIMITS[self.tier.value]
        if language.lower() not in allowed:
            raise ToolLibraryBuilderTierError(
                f"Language '{language}' is not available on the {self.config.name} tier. "
                f"Allowed: {allowed}. Upgrade for more language support."
            )

    # ------------------------------------------------------------------
    # Library discovery
    # ------------------------------------------------------------------

    def discover_libraries(self, language: str | None = None,
                           country: str | None = None) -> list[dict]:
        """
        Return all known libraries, optionally filtered by language or country.

        Country filtering requires PRO tier or higher.
        """
        if country:
            self._require_feature(FEATURE_COUNTRY_CATEGORIZATION)

        libs = self.scraper.list_libraries(language=language, country=country)
        return [lib.to_dict() for lib in libs]

    def catalog_summary(self) -> dict:
        """Return a high-level summary of all catalogued libraries."""
        return self.scraper.catalog_summary()

    def register_library(self, record: LibraryRecord) -> dict:
        """Register a new library in the catalog (all tiers)."""
        self.scraper.register_library(record)
        return {"status": "registered", "library": record.name, "language": record.language}

    # ------------------------------------------------------------------
    # Tool generation
    # ------------------------------------------------------------------

    def build_tools_for_library(self, language: str, library_name: str,
                                include_hidden: bool = False) -> list[dict]:
        """
        Generate usable tools for every symbol in the given library.

        Parameters
        ----------
        language : str
            Programming language of the library.
        library_name : str
            Library name (must exist in the catalog).
        include_hidden : bool
            Generate tools for hidden/private symbols too.
            Requires PRO tier or higher.

        Returns
        -------
        list[dict]  — tool metadata dicts for each generated tool.
        """
        self._check_language(language)

        if include_hidden:
            self._require_feature(FEATURE_HIDDEN_CAPABILITY_DISCOVERY)

        record = self.scraper.get_library(language, library_name)
        if record is None:
            raise ToolLibraryBuilderError(
                f"Library '{library_name}' not found for language '{language}'. "
                "Use register_library() to add it first."
            )

        symbol_count = len(record.exported_symbols)
        if include_hidden:
            symbol_count += len(record.hidden_symbols)

        self._check_tool_limit(symbol_count)

        tools = self.generator.generate_all(record, include_hidden=include_hidden)
        self._tools_generated_this_month += len(tools)

        # Register versions
        for tool in tools:
            self.versions.register(tool.tool_id)

        return [t.to_dict() for t in tools]

    def build_tools_for_language(self, language: str,
                                 include_hidden: bool = False) -> dict:
        """
        Generate tools for all catalogued libraries in a language.

        Returns a summary dict with tool counts per library.
        """
        self._check_language(language)
        if include_hidden:
            self._require_feature(FEATURE_HIDDEN_CAPABILITY_DISCOVERY)

        libs = self.scraper.list_libraries(language=language)
        if not libs:
            raise ToolLibraryBuilderError(
                f"No libraries catalogued for language '{language}'."
            )

        summary: dict[str, int] = {}
        for lib in libs:
            tools = self.generator.generate_all(lib, include_hidden=include_hidden)
            self._tools_generated_this_month += len(tools)
            for tool in tools:
                self.versions.register(tool.tool_id)
            summary[lib.name] = len(tools)

        return {
            "language": language,
            "libraries_processed": len(libs),
            "tools_generated_by_library": summary,
            "total_tools_generated": sum(summary.values()),
        }

    # ------------------------------------------------------------------
    # Version management
    # ------------------------------------------------------------------

    def update_tool_versions(self, language: str | None = None,
                             bump_type: str = "patch") -> dict:
        """
        Bump versions for all tools, optionally filtered by language.

        Requires PRO tier or higher.  *bump_type* is one of:
        ``"patch"`` (default), ``"minor"``, or ``"major"``.
        """
        self._require_feature(FEATURE_VERSION_MANAGEMENT)

        if bump_type == "patch":
            records = self.versions.bump_all_patch(language=language)
        elif bump_type == "minor":
            records = [
                self.versions.bump_minor(tid)
                for tid, _ in self.versions.all_versions().items()
                if language is None or tid.startswith(language.lower() + "__")
            ]
        elif bump_type == "major":
            records = [
                self.versions.bump_major(tid)
                for tid, _ in self.versions.all_versions().items()
                if language is None or tid.startswith(language.lower() + "__")
            ]
        else:
            raise ToolLibraryBuilderError(
                f"Unknown bump_type '{bump_type}'. Use 'patch', 'minor', or 'major'."
            )

        return {
            "bump_type": bump_type,
            "tools_updated": len(records),
            "language_filter": language,
        }

    def get_version(self, tool_id: str) -> str | None:
        """Return the current version of a tool."""
        return self.versions.current_version(tool_id)

    # ------------------------------------------------------------------
    # Marketplace deployment
    # ------------------------------------------------------------------

    def deploy_to_marketplace(self, tool_ids: list[str] | None = None,
                              language: str | None = None) -> dict:
        """
        Deploy generated tools to the DreamCo marketplace.

        Requires ENTERPRISE tier.  If *tool_ids* is None, deploys all tools
        matching the optional *language* filter.
        """
        self._require_feature(FEATURE_MARKETPLACE_DEPLOYMENT)

        if tool_ids is not None:
            tools = [t for t in self.generator.list_tools() if t.tool_id in tool_ids]
        else:
            tools = self.generator.list_tools(language=language)

        if not tools:
            return {"listings_created": 0, "message": "No matching tools to deploy."}

        listings = self.deployer.deploy_batch(tools)

        # Sync versions into listings
        for listing in listings:
            current = self.versions.current_version(listing.tool_id)
            if current:
                self.deployer.update_version(listing.listing_id, current)

        return {
            "listings_created": len(listings),
            "listing_ids": [lst.listing_id for lst in listings],
            "marketplace_summary": self.deployer.marketplace_summary(),
        }

    def search_marketplace(self, query: str = "", language: str | None = None) -> list[dict]:
        """Search the marketplace for tool listings."""
        listings = self.deployer.search(query=query, language=language)
        return [lst.to_dict() for lst in listings]

    # ------------------------------------------------------------------
    # Periodic updates
    # ------------------------------------------------------------------

    def run_periodic_update(self) -> dict:
        """
        Execute a full update cycle:
        1. Rebuild tools for all catalogued libraries.
        2. Bump all tool patch versions.
        3. (ENTERPRISE) Redeploy updated tools to the marketplace.

        Requires PRO tier or higher.
        """
        self._require_feature(FEATURE_PERIODIC_UPDATES)

        languages = LANGUAGE_LIMITS[self.tier.value]
        total_tools = 0
        processed: dict[str, int] = {}

        for lang in languages:
            libs = self.scraper.list_libraries(language=lang)
            for lib in libs:
                include_hidden = FEATURE_HIDDEN_CAPABILITY_DISCOVERY in TOOL_LIBRARY_FEATURES[self.tier.value]
                tools = self.generator.generate_all(lib, include_hidden=include_hidden)
                for tool in tools:
                    self.versions.register(tool.tool_id)
                total_tools += len(tools)
                processed[lib.name] = len(tools)

        version_update = self.versions.bump_all_patch(note="Periodic update")

        result: dict = {
            "libraries_processed": len(processed),
            "tools_generated": total_tools,
            "versions_bumped": len(version_update),
        }

        if FEATURE_MARKETPLACE_DEPLOYMENT in TOOL_LIBRARY_FEATURES[self.tier.value]:
            deploy_result = self.deploy_to_marketplace()
            result["marketplace"] = deploy_result

        return result

    # ------------------------------------------------------------------
    # White-label export (ENTERPRISE)
    # ------------------------------------------------------------------

    def export_tool_library(self, language: str | None = None) -> dict:
        """
        Export the tool library as a structured manifest for white-label use.
        Requires ENTERPRISE tier.
        """
        self._require_feature(FEATURE_WHITE_LABEL_EXPORT)

        tools = self.generator.list_tools(language=language)
        manifest: dict[str, list[dict]] = {}
        for tool in tools:
            lang_key = tool.language
            if lang_key not in manifest:
                manifest[lang_key] = []
            entry = tool.to_dict()
            entry["current_version"] = self.versions.current_version(tool.tool_id) or tool.version
            manifest[lang_key].append(entry)

        return {
            "export_format": "dreamcobots-tool-library-v1",
            "language_filter": language,
            "total_tools": len(tools),
            "manifest": manifest,
        }

    # ------------------------------------------------------------------
    # Status & stats
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return a comprehensive status snapshot of the bot."""
        return {
            "tier": self.tier.value,
            "user_id": self.user_id,
            "tools_generated_this_month": self._tools_generated_this_month,
            "tool_limit": TOOL_LIMITS[self.tier.value],
            "catalog": self.scraper.catalog_summary(),
            "tools": self.generator.tools_summary(),
            "versions": self.versions.summary(),
            "marketplace": self.deployer.marketplace_summary(),
        }

    def get_tier_info(self) -> dict:
        """Return tier information and feature list."""
        return get_tool_library_tier_info(self.tier)

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Unified natural-language chat interface.

        Interprets common intents and dispatches to the appropriate method.
        """
        msg = message.lower()

        if any(kw in msg for kw in ("status", "health", "stats")):
            return {"message": "Tool Library Builder status retrieved.", "data": self.get_status()}

        if any(kw in msg for kw in ("tier", "features", "upgrade")):
            info = self.get_tier_info()
            return {"message": f"Current tier: {info['tier']}.", "data": info}

        if any(kw in msg for kw in ("catalog", "catalogue", "libraries", "discover")):
            summary = self.catalog_summary()
            return {"message": "Library catalog summary retrieved.", "data": summary}

        if any(kw in msg for kw in ("marketplace", "deploy", "sell", "buy")):
            summary = self.deployer.marketplace_summary()
            return {"message": "Marketplace summary retrieved.", "data": summary}

        if any(kw in msg for kw in ("update", "periodic", "refresh")):
            try:
                result = self.run_periodic_update()
                return {"message": "Periodic update completed.", "data": result}
            except ToolLibraryBuilderTierError as exc:
                return {"message": str(exc), "data": {"upgrade_required": True}}

        return {
            "message": (
                "DreamCobots Tool Library Builder ready. "
                "I can discover libraries, generate tools, manage versions, "
                "and deploy to the marketplace. What would you like to build?"
            ),
            "data": {"tier": self.tier.value},
        }
