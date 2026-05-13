"""
Tests for the code_study_bots unified tool-building ecosystem.

Covers:
- LibraryScraper  — catalog discovery and filtering
- ToolGenerator   — tool generation (documented + hidden symbols)
- VersionManager  — semantic version tracking and bumping
- MarketplaceDeployer — listing lifecycle and search
- ToolLibraryBuilderBot — orchestrator, tier enforcement, chat interface
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(REPO_ROOT, "bots", "ai-models-integration"))
sys.path.insert(0, REPO_ROOT)

import pytest

from code_study_bots.tiers import (
    Tier,
    TOOL_LIBRARY_FEATURES,
    TOOL_LIMITS,
    LANGUAGE_LIMITS,
    get_tool_library_tier_info,
    FEATURE_HIDDEN_CAPABILITY_DISCOVERY,
    FEATURE_MARKETPLACE_DEPLOYMENT,
    FEATURE_VERSION_MANAGEMENT,
    FEATURE_PERIODIC_UPDATES,
)
from code_study_bots.library_scraper import LibraryScraper, LibraryRecord
from code_study_bots.tool_generator import ToolGenerator, GeneratedTool
from code_study_bots.version_manager import VersionManager
from code_study_bots.marketplace_deployer import MarketplaceDeployer
from code_study_bots.tool_library_builder import (
    ToolLibraryBuilderBot,
    ToolLibraryBuilderTierError,
    ToolLibraryBuilderLimitError,
    ToolLibraryBuilderError,
)


# ===========================================================================
# Tier definitions
# ===========================================================================

class TestTierDefinitions:
    def test_all_tiers_have_features(self):
        for tier in Tier:
            assert tier.value in TOOL_LIBRARY_FEATURES
            assert len(TOOL_LIBRARY_FEATURES[tier.value]) > 0

    def test_all_tiers_have_tool_limits(self):
        for tier in Tier:
            assert tier.value in TOOL_LIMITS

    def test_enterprise_has_unlimited_tools(self):
        assert TOOL_LIMITS[Tier.ENTERPRISE.value] is None

    def test_free_languages_subset_of_enterprise(self):
        free = set(LANGUAGE_LIMITS[Tier.FREE.value])
        ent = set(LANGUAGE_LIMITS[Tier.ENTERPRISE.value])
        assert free.issubset(ent)

    def test_enterprise_has_marketplace_feature(self):
        assert FEATURE_MARKETPLACE_DEPLOYMENT in TOOL_LIBRARY_FEATURES[Tier.ENTERPRISE.value]

    def test_free_lacks_hidden_capability_feature(self):
        assert FEATURE_HIDDEN_CAPABILITY_DISCOVERY not in TOOL_LIBRARY_FEATURES[Tier.FREE.value]

    def test_tier_info_returns_expected_keys(self):
        info = get_tool_library_tier_info(Tier.PRO)
        for key in ("tier", "name", "price_usd_monthly", "tool_limit_per_month",
                    "languages", "features", "support_level"):
            assert key in info

    def test_free_tier_price_is_zero(self):
        info = get_tool_library_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0


# ===========================================================================
# LibraryScraper
# ===========================================================================

class TestLibraryScraper:
    def setup_method(self):
        self.scraper = LibraryScraper()

    def test_seed_catalog_not_empty(self):
        libs = self.scraper.list_libraries()
        assert len(libs) > 0

    def test_list_by_language_python(self):
        libs = self.scraper.list_libraries(language="python")
        assert all(lib.language == "python" for lib in libs)
        assert len(libs) > 0

    def test_list_by_language_javascript(self):
        libs = self.scraper.list_libraries(language="javascript")
        assert len(libs) > 0

    def test_list_by_country(self):
        us_libs = self.scraper.list_libraries(country="US")
        assert all(lib.country_of_origin == "US" for lib in us_libs)

    def test_get_existing_library(self):
        rec = self.scraper.get_library("python", "pandas")
        assert rec is not None
        assert rec.name == "pandas"
        assert rec.language == "python"

    def test_get_nonexistent_library_returns_none(self):
        assert self.scraper.get_library("python", "nonexistent_lib") is None

    def test_register_new_library(self):
        rec = LibraryRecord(
            name="testlib", language="python", version="0.1.0",
            purpose_category="testing", country_of_origin="CA",
            description="A test library.", doc_url="https://example.com",
            exported_symbols=["helper", "runner"], hidden_symbols=[],
        )
        self.scraper.register_library(rec)
        found = self.scraper.get_library("python", "testlib")
        assert found is not None
        assert found.name == "testlib"

    def test_discover_symbols_returns_documented_and_hidden(self):
        result = self.scraper.discover_symbols("python", "pandas")
        assert "documented" in result
        assert "hidden" in result
        assert result["total"] == len(result["documented"]) + len(result["hidden"])

    def test_discover_symbols_unknown_library(self):
        result = self.scraper.discover_symbols("python", "unknown_lib")
        assert "error" in result

    def test_catalog_summary_keys(self):
        summary = self.scraper.catalog_summary()
        for key in ("total_libraries", "by_language", "by_country", "by_purpose"):
            assert key in summary

    def test_list_languages_includes_python_and_javascript(self):
        langs = self.scraper.list_languages()
        assert "python" in langs
        assert "javascript" in langs

    def test_scrape_by_language_returns_dicts(self):
        data = self.scraper.scrape_by_language("python")
        assert isinstance(data, list)
        assert all(isinstance(item, dict) for item in data)

    def test_scrape_by_country_returns_dicts(self):
        data = self.scraper.scrape_by_country("US")
        assert isinstance(data, list)


# ===========================================================================
# ToolGenerator
# ===========================================================================

class TestToolGenerator:
    def setup_method(self):
        self.scraper = LibraryScraper()
        self.generator = ToolGenerator()

    def _pandas_record(self):
        return self.scraper.get_library("python", "pandas")

    def test_generate_all_returns_list_of_generated_tools(self):
        rec = self._pandas_record()
        tools = self.generator.generate_all(rec)
        assert isinstance(tools, list)
        assert len(tools) == len(rec.exported_symbols)
        assert all(isinstance(t, GeneratedTool) for t in tools)

    def test_generate_all_with_hidden(self):
        rec = self._pandas_record()
        tools_no_hidden = self.generator.generate_all(rec, include_hidden=False)
        generator2 = ToolGenerator()
        tools_with_hidden = generator2.generate_all(rec, include_hidden=True)
        assert len(tools_with_hidden) == len(rec.exported_symbols) + len(rec.hidden_symbols)
        assert len(tools_with_hidden) > len(tools_no_hidden)

    def test_hidden_tools_flagged_correctly(self):
        rec = self._pandas_record()
        tools = self.generator.generate_all(rec, include_hidden=True)
        hidden = [t for t in tools if t.is_hidden_capability]
        assert len(hidden) == len(rec.hidden_symbols)

    def test_tool_id_format(self):
        rec = self._pandas_record()
        tools = self.generator.generate_all(rec)
        for tool in tools:
            assert tool.tool_id.startswith("python__pandas__")

    def test_generated_tool_to_dict_keys(self):
        rec = self._pandas_record()
        tools = self.generator.generate_all(rec)
        d = tools[0].to_dict()
        for key in ("tool_id", "library_name", "language", "symbol",
                    "purpose_category", "description", "is_hidden_capability",
                    "version", "created_at", "tags", "marketplace_ready"):
            assert key in d

    def test_source_code_is_string(self):
        rec = self._pandas_record()
        tool = self.generator.generate_for_symbol(rec, "DataFrame")
        assert isinstance(tool.source_code, str)
        assert "class" in tool.source_code
        assert "def run" in tool.source_code

    def test_get_tool_by_id(self):
        rec = self._pandas_record()
        tools = self.generator.generate_all(rec)
        tool = tools[0]
        found = self.generator.get_tool(tool.tool_id)
        assert found is not None
        assert found.tool_id == tool.tool_id

    def test_list_tools_by_language(self):
        rec = self._pandas_record()
        self.generator.generate_all(rec)
        python_tools = self.generator.list_tools(language="python")
        assert all(t.language == "python" for t in python_tools)

    def test_list_tools_hidden_only(self):
        rec = self._pandas_record()
        self.generator.generate_all(rec, include_hidden=True)
        hidden = self.generator.list_tools(hidden_only=True)
        assert all(t.is_hidden_capability for t in hidden)

    def test_tools_summary_keys(self):
        rec = self._pandas_record()
        self.generator.generate_all(rec)
        summary = self.generator.tools_summary()
        for key in ("total_tools", "by_language", "hidden_capability_tools", "marketplace_ready"):
            assert key in summary

    def test_marketplace_ready_for_documented_symbols(self):
        rec = self._pandas_record()
        tools = self.generator.generate_all(rec, include_hidden=False)
        assert all(t.marketplace_ready for t in tools)


# ===========================================================================
# VersionManager
# ===========================================================================

class TestVersionManager:
    def setup_method(self):
        self.vm = VersionManager()

    def test_register_new_tool(self):
        record = self.vm.register("python__pandas__DataFrame")
        assert record.version == "1.0.0"

    def test_register_idempotent(self):
        self.vm.register("tool_a")
        r2 = self.vm.register("tool_a")
        assert r2.version == "1.0.0"

    def test_bump_patch(self):
        self.vm.register("tool_b", "1.0.0")
        record = self.vm.bump_patch("tool_b")
        assert record.version == "1.0.1"

    def test_bump_minor(self):
        self.vm.register("tool_c", "1.2.3")
        record = self.vm.bump_minor("tool_c")
        assert record.version == "1.3.0"

    def test_bump_major(self):
        self.vm.register("tool_d", "1.2.3")
        record = self.vm.bump_major("tool_d")
        assert record.version == "2.0.0"

    def test_auto_register_on_bump(self):
        record = self.vm.bump_patch("new_tool_xyz")
        assert record.version == "1.0.1"

    def test_current_version_returns_latest(self):
        self.vm.register("tool_e", "1.0.0")
        self.vm.bump_patch("tool_e")
        assert self.vm.current_version("tool_e") == "1.0.1"

    def test_history_tracks_all_versions(self):
        self.vm.register("tool_f", "1.0.0")
        self.vm.bump_patch("tool_f")
        self.vm.bump_minor("tool_f")
        history = self.vm.history("tool_f")
        assert len(history) == 3

    def test_bump_all_patch(self):
        self.vm.register("python__a__sym1", "1.0.0")
        self.vm.register("python__a__sym2", "2.0.0")
        self.vm.register("js__b__sym1", "1.0.0")
        updated = self.vm.bump_all_patch(language="python")
        assert len(updated) == 2
        assert self.vm.current_version("python__a__sym1") == "1.0.1"
        assert self.vm.current_version("js__b__sym1") == "1.0.0"  # unchanged

    def test_all_versions_returns_mapping(self):
        self.vm.register("t1")
        self.vm.register("t2")
        versions = self.vm.all_versions()
        assert "t1" in versions
        assert "t2" in versions

    def test_summary_keys(self):
        self.vm.register("t3")
        summary = self.vm.summary()
        assert "total_tools_versioned" in summary
        assert "versions" in summary


# ===========================================================================
# MarketplaceDeployer
# ===========================================================================

class TestMarketplaceDeployer:
    def setup_method(self):
        scraper = LibraryScraper()
        generator = ToolGenerator()
        rec = scraper.get_library("python", "pandas")
        self.tools = generator.generate_all(rec, include_hidden=False)
        self.deployer = MarketplaceDeployer()

    def test_deploy_single_tool(self):
        listing = self.deployer.deploy(self.tools[0])
        assert listing.tool_id == self.tools[0].tool_id
        assert listing.status == "active"

    def test_deploy_idempotent(self):
        listing1 = self.deployer.deploy(self.tools[0])
        listing2 = self.deployer.deploy(self.tools[0])
        assert listing1.listing_id == listing2.listing_id

    def test_deploy_batch(self):
        listings = self.deployer.deploy_batch(self.tools[:3])
        assert len(listings) == 3

    def test_price_is_positive_for_standard_tool(self):
        listing = self.deployer.deploy(self.tools[0])
        assert listing.price_usd_monthly >= 0

    def test_hidden_tool_priced_higher(self):
        scraper = LibraryScraper()
        generator = ToolGenerator()
        rec = scraper.get_library("python", "pandas")
        hidden_tools = generator.generate_all(rec, include_hidden=True)
        hidden = [t for t in hidden_tools if t.is_hidden_capability]
        if hidden:
            listing = self.deployer.deploy(hidden[0])
            assert listing.price_usd_monthly >= 9.99

    def test_get_listing_by_id(self):
        listing = self.deployer.deploy(self.tools[0])
        found = self.deployer.get_listing(listing.listing_id)
        assert found is not None
        assert found.listing_id == listing.listing_id

    def test_listing_for_tool(self):
        tool = self.tools[0]
        self.deployer.deploy(tool)
        listing = self.deployer.listing_for_tool(tool.tool_id)
        assert listing is not None

    def test_search_by_language(self):
        self.deployer.deploy_batch(self.tools)
        results = self.deployer.search(language="python")
        assert all(lst.language == "python" for lst in results)

    def test_deprecate_listing(self):
        listing = self.deployer.deploy(self.tools[0])
        success = self.deployer.deprecate(listing.listing_id)
        assert success
        assert self.deployer.get_listing(listing.listing_id).status == "deprecated"

    def test_update_version(self):
        listing = self.deployer.deploy(self.tools[0])
        success = self.deployer.update_version(listing.listing_id, "2.0.0")
        assert success
        assert self.deployer.get_listing(listing.listing_id).version == "2.0.0"

    def test_record_download(self):
        listing = self.deployer.deploy(self.tools[0])
        self.deployer.record_download(listing.listing_id)
        assert self.deployer.get_listing(listing.listing_id).downloads == 1

    def test_marketplace_summary_keys(self):
        summary = self.deployer.marketplace_summary()
        for key in ("total_listings", "active_listings", "total_downloads",
                    "estimated_monthly_revenue_usd", "listings_by_language"):
            assert key in summary

    def test_to_dict_has_expected_keys(self):
        listing = self.deployer.deploy(self.tools[0])
        d = listing.to_dict()
        for key in ("listing_id", "tool_id", "library_name", "language",
                    "purpose_category", "title", "description",
                    "price_usd_monthly", "tags", "version", "status", "downloads"):
            assert key in d


# ===========================================================================
# ToolLibraryBuilderBot — orchestrator
# ===========================================================================

class TestToolLibraryBuilderBotTierEnforcement:
    def test_default_tier_is_free(self):
        bot = ToolLibraryBuilderBot()
        assert bot.tier == Tier.FREE

    def test_free_cannot_use_hidden_capability(self):
        bot = ToolLibraryBuilderBot(tier=Tier.FREE)
        with pytest.raises(ToolLibraryBuilderTierError):
            bot.build_tools_for_library("python", "pandas", include_hidden=True)

    def test_free_cannot_deploy_marketplace(self):
        bot = ToolLibraryBuilderBot(tier=Tier.FREE)
        with pytest.raises(ToolLibraryBuilderTierError):
            bot.deploy_to_marketplace()

    def test_free_cannot_run_periodic_update(self):
        bot = ToolLibraryBuilderBot(tier=Tier.FREE)
        with pytest.raises(ToolLibraryBuilderTierError):
            bot.run_periodic_update()

    def test_free_cannot_use_version_management(self):
        bot = ToolLibraryBuilderBot(tier=Tier.FREE)
        with pytest.raises(ToolLibraryBuilderTierError):
            bot.update_tool_versions()

    def test_free_cannot_export_white_label(self):
        bot = ToolLibraryBuilderBot(tier=Tier.FREE)
        with pytest.raises(ToolLibraryBuilderTierError):
            bot.export_tool_library()

    def test_free_cannot_filter_by_country(self):
        bot = ToolLibraryBuilderBot(tier=Tier.FREE)
        with pytest.raises(ToolLibraryBuilderTierError):
            bot.discover_libraries(country="US")

    def test_pro_can_use_hidden_capability(self):
        bot = ToolLibraryBuilderBot(tier=Tier.PRO)
        tools = bot.build_tools_for_library("python", "pandas", include_hidden=True)
        assert len(tools) > 0

    def test_pro_can_filter_by_country(self):
        bot = ToolLibraryBuilderBot(tier=Tier.PRO)
        libs = bot.discover_libraries(country="US")
        assert isinstance(libs, list)

    def test_enterprise_can_deploy_to_marketplace(self):
        bot = ToolLibraryBuilderBot(tier=Tier.ENTERPRISE)
        bot.build_tools_for_library("python", "pandas")
        result = bot.deploy_to_marketplace(language="python")
        assert "listings_created" in result

    def test_enterprise_can_export_white_label(self):
        bot = ToolLibraryBuilderBot(tier=Tier.ENTERPRISE)
        bot.build_tools_for_library("python", "pandas")
        export = bot.export_tool_library(language="python")
        assert "manifest" in export
        assert export["total_tools"] > 0


class TestToolLibraryBuilderBotFunctionality:
    def setup_method(self):
        self.bot = ToolLibraryBuilderBot(tier=Tier.PRO)

    def test_discover_libraries_returns_list(self):
        libs = self.bot.discover_libraries()
        assert isinstance(libs, list)
        assert len(libs) > 0

    def test_discover_libraries_filtered_by_language(self):
        libs = self.bot.discover_libraries(language="python")
        assert all(lib["language"] == "python" for lib in libs)

    def test_catalog_summary_keys(self):
        summary = self.bot.catalog_summary()
        assert "total_libraries" in summary

    def test_build_tools_for_library(self):
        tools = self.bot.build_tools_for_library("python", "pandas")
        assert len(tools) > 0
        assert all("tool_id" in t for t in tools)

    def test_build_tools_for_unknown_library_raises(self):
        with pytest.raises(ToolLibraryBuilderError):
            self.bot.build_tools_for_library("python", "totally_unknown_lib")

    def test_build_tools_for_language(self):
        result = self.bot.build_tools_for_language("python")
        assert "total_tools_generated" in result
        assert result["total_tools_generated"] > 0

    def test_build_tools_for_unsupported_language_raises(self):
        bot = ToolLibraryBuilderBot(tier=Tier.FREE)
        with pytest.raises(ToolLibraryBuilderTierError):
            bot.build_tools_for_library("haskell", "some_lib")

    def test_version_management_after_build(self):
        self.bot.build_tools_for_library("python", "numpy")
        result = self.bot.update_tool_versions(language="python", bump_type="patch")
        assert result["tools_updated"] > 0

    def test_invalid_bump_type_raises(self):
        self.bot.build_tools_for_library("python", "scipy")
        with pytest.raises(ToolLibraryBuilderError):
            self.bot.update_tool_versions(bump_type="invalid")

    def test_get_version_returns_string(self):
        tools = self.bot.build_tools_for_library("python", "pandas")
        tool_id = tools[0]["tool_id"]
        version = self.bot.get_version(tool_id)
        assert version is not None
        assert "." in version

    def test_get_status_keys(self):
        status = self.bot.get_status()
        for key in ("tier", "tools_generated_this_month", "catalog", "tools",
                    "versions", "marketplace"):
            assert key in status

    def test_get_tier_info_keys(self):
        info = self.bot.get_tier_info()
        for key in ("tier", "name", "features", "languages"):
            assert key in info

    def test_register_custom_library(self):
        rec = LibraryRecord(
            name="mylib", language="python", version="1.0.0",
            purpose_category="utilities", country_of_origin="US",
            description="My custom library.", doc_url="https://mylib.example.com",
            exported_symbols=["do_thing", "do_other"], hidden_symbols=["_internal"],
        )
        result = self.bot.register_library(rec)
        assert result["status"] == "registered"
        tools = self.bot.build_tools_for_library("python", "mylib")
        assert len(tools) == 2

    def test_tool_limit_enforcement(self):
        bot = ToolLibraryBuilderBot(tier=Tier.FREE)
        bot._tools_generated_this_month = TOOL_LIMITS[Tier.FREE.value]
        with pytest.raises(ToolLibraryBuilderLimitError):
            bot.build_tools_for_library("python", "requests")

    def test_search_marketplace(self):
        bot = ToolLibraryBuilderBot(tier=Tier.ENTERPRISE)
        bot.build_tools_for_library("python", "pandas")
        bot.deploy_to_marketplace(language="python")
        results = bot.search_marketplace(language="python")
        assert isinstance(results, list)


class TestToolLibraryBuilderBotChat:
    def setup_method(self):
        self.bot = ToolLibraryBuilderBot(tier=Tier.FREE)

    def test_chat_status(self):
        result = self.bot.chat("show me the status")
        assert "message" in result
        assert "data" in result

    def test_chat_tier(self):
        result = self.bot.chat("what tier am I on?")
        assert "data" in result

    def test_chat_catalog(self):
        result = self.bot.chat("discover libraries")
        assert "data" in result

    def test_chat_marketplace(self):
        result = self.bot.chat("what's in the marketplace?")
        assert "data" in result

    def test_chat_update_free_returns_upgrade_message(self):
        result = self.bot.chat("run periodic update")
        assert "upgrade_required" in result.get("data", {}) or "not available" in result.get("message", "").lower()

    def test_chat_default_response(self):
        result = self.bot.chat("hello there")
        assert "message" in result
        assert result["data"]["tier"] == "free"


class TestToolLibraryBuilderBotEnterprise:
    def setup_method(self):
        self.bot = ToolLibraryBuilderBot(tier=Tier.ENTERPRISE)

    def test_run_periodic_update_returns_summary(self):
        result = self.bot.run_periodic_update()
        for key in ("libraries_processed", "tools_generated", "versions_bumped"):
            assert key in result

    def test_periodic_update_includes_marketplace(self):
        result = self.bot.run_periodic_update()
        assert "marketplace" in result

    def test_export_tool_library_format(self):
        self.bot.build_tools_for_library("python", "pandas")
        export = self.bot.export_tool_library()
        assert export["export_format"] == "dreamcobots-tool-library-v1"
        assert "python" in export["manifest"]

    def test_deploy_specific_tool_ids(self):
        tools = self.bot.build_tools_for_library("python", "pandas")
        ids = [tools[0]["tool_id"]]
        result = self.bot.deploy_to_marketplace(tool_ids=ids)
        assert result["listings_created"] >= 1

    def test_deploy_no_matching_tools(self):
        result = self.bot.deploy_to_marketplace(language="haskell")
        assert result["listings_created"] == 0
