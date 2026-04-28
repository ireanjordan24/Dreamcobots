"""
tests/test_elite_scraper.py — Tests for the Elite Scraper Bot system.

Covers:
  1. BotProfile / profile registry
  2. KnowledgeStore — save, load, merge, prune
  3. EliteScraper — factory, run pipeline, result summary
  4. CLI runner (run_elite_scrapers.py) — smoke test
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

import pytest

# Ensure repo root is on the path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from bots.elite_scraper.bot_profiles import (
    BOT_PROFILES,
    BotProfile,
    get_profile,
)
from bots.elite_scraper.knowledge_store import KnowledgeStore
from bots.elite_scraper.elite_scraper import EliteScraper, ScraperResult


# ===========================================================================
# 1. BotProfile / Registry
# ===========================================================================

class TestBotProfiles:
    def test_default_profile_exists(self):
        assert "_default" in BOT_PROFILES

    def test_lead_gen_profile_exists(self):
        assert "lead_gen_bot" in BOT_PROFILES

    def test_get_profile_known_bot(self):
        profile = get_profile("lead_gen_bot")
        assert isinstance(profile, BotProfile)
        assert profile.bot_name == "lead_gen_bot"

    def test_get_profile_unknown_bot_returns_default(self):
        profile = get_profile("nonexistent_bot_xyz")
        assert profile.bot_name == "_default"

    def test_all_profiles_have_required_fields(self):
        required_list_fields = [
            "github_queries",
            "knowledge_topics",
            "monetization_keywords",
            "client_acquisition_keywords",
            "competing_bots_queries",
            "self_improvement_topics",
        ]
        for name, profile in BOT_PROFILES.items():
            assert profile.bot_name == name, f"{name}: bot_name mismatch"
            assert profile.display_name, f"{name}: missing display_name"
            assert profile.category, f"{name}: missing category"
            for attr in required_list_fields:
                value = getattr(profile, attr)
                assert isinstance(value, list), f"{name}.{attr} must be a list"
                assert len(value) > 0, f"{name}.{attr} must not be empty"

    def test_registered_bot_count(self):
        # At least 15 distinct bots registered (excluding _default)
        bots = [k for k in BOT_PROFILES if k != "_default"]
        assert len(bots) >= 15, f"Expected ≥15 bot profiles, got {len(bots)}"


# ===========================================================================
# 2. KnowledgeStore
# ===========================================================================

class TestKnowledgeStore:
    def _make_store(self, tmp_path: str) -> KnowledgeStore:
        return KnowledgeStore("test_bot", data_root=tmp_path)

    def test_load_empty_store(self, tmp_path):
        store = self._make_store(str(tmp_path))
        assert store.load("knowledge") == []

    def test_save_and_load(self, tmp_path):
        store = self._make_store(str(tmp_path))
        items = [{"url": "https://example.com/1", "title": "Item 1"}]
        store.save("knowledge", items)
        loaded = store.load("knowledge")
        assert len(loaded) == 1
        assert loaded[0]["url"] == "https://example.com/1"

    def test_deduplication_on_url(self, tmp_path):
        store = self._make_store(str(tmp_path))
        items = [{"url": "https://example.com/1", "title": "Item 1"}]
        store.save("knowledge", items)
        store.save("knowledge", items)  # second save should not duplicate
        loaded = store.load("knowledge")
        assert len(loaded) == 1

    def test_deduplication_on_id(self, tmp_path):
        store = self._make_store(str(tmp_path))
        items = [{"id": "unique-id-42", "title": "Item"}]
        store.save("knowledge", items)
        store.save("knowledge", items)
        loaded = store.load("knowledge")
        assert len(loaded) == 1

    def test_append_new_items(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save("knowledge", [{"url": "https://example.com/1", "title": "A"}])
        store.save("knowledge", [{"url": "https://example.com/2", "title": "B"}])
        loaded = store.load("knowledge")
        assert len(loaded) == 2

    def test_scraped_at_timestamp_added(self, tmp_path):
        store = self._make_store(str(tmp_path))
        items = [{"url": "https://example.com/ts", "title": "TS"}]
        store.save("knowledge", items)
        loaded = store.load("knowledge")
        assert "scraped_at" in loaded[0]

    def test_stats_returns_all_stores(self, tmp_path):
        store = self._make_store(str(tmp_path))
        stats = store.stats()
        for s in KnowledgeStore.STORES:
            assert s in stats

    def test_prune_removes_old_records(self, tmp_path):
        store = self._make_store(str(tmp_path))
        items = [{"url": f"https://example.com/{i}", "title": str(i)} for i in range(20)]
        store.save("knowledge", items)
        removed = store.prune("knowledge", keep=10)
        assert removed == 10
        loaded = store.load("knowledge")
        assert len(loaded) == 10

    def test_prune_noop_when_below_keep(self, tmp_path):
        store = self._make_store(str(tmp_path))
        items = [{"url": f"https://example.com/{i}"} for i in range(5)]
        store.save("knowledge", items)
        removed = store.prune("knowledge", keep=100)
        assert removed == 0

    def test_save_empty_list_is_noop(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save("knowledge", [])
        assert store.load("knowledge") == []

    def test_all_store_types(self, tmp_path):
        store = self._make_store(str(tmp_path))
        for s in KnowledgeStore.STORES:
            store.save(s, [{"url": f"https://example.com/{s}"}])
            assert len(store.load(s)) == 1


# ===========================================================================
# 3. EliteScraper
# ===========================================================================

class TestEliteScraperFactory:
    def test_for_bot_known(self):
        scraper = EliteScraper.for_bot("lead_gen_bot")
        assert scraper.profile.bot_name == "lead_gen_bot"

    def test_for_bot_unknown_uses_default(self):
        scraper = EliteScraper.for_bot("totally_unknown_bot_xyz")
        assert scraper.profile.bot_name == "_default"

    def test_for_bot_sets_github_token_from_env(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "test-token-123")
        scraper = EliteScraper.for_bot("lead_gen_bot")
        assert scraper.github_token == "test-token-123"

    def test_for_bot_no_token_when_env_unset(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        scraper = EliteScraper.for_bot("lead_gen_bot", github_token=None)
        assert scraper.github_token is None


class TestEliteScraperRun:
    """Tests that exercise the full scraping pipeline (offline / synthetic)."""

    def test_run_returns_scraper_result(self, tmp_path):
        scraper = EliteScraper.for_bot("lead_gen_bot", github_token=None, max_results_per_query=2)
        scraper.store = KnowledgeStore("lead_gen_bot", data_root=str(tmp_path))
        result = scraper.run()
        assert isinstance(result, ScraperResult)

    def test_result_has_bot_name(self, tmp_path):
        scraper = EliteScraper.for_bot("buddy_bot", github_token=None, max_results_per_query=2)
        scraper.store = KnowledgeStore("buddy_bot", data_root=str(tmp_path))
        result = scraper.run()
        assert result.bot_name == "buddy_bot"

    def test_result_has_timestamp(self, tmp_path):
        scraper = EliteScraper.for_bot("crypto_bot", github_token=None, max_results_per_query=2)
        scraper.store = KnowledgeStore("crypto_bot", data_root=str(tmp_path))
        result = scraper.run()
        assert result.timestamp

    def test_result_populates_all_categories(self, tmp_path):
        scraper = EliteScraper.for_bot("marketing_bot", github_token=None, max_results_per_query=2)
        scraper.store = KnowledgeStore("marketing_bot", data_root=str(tmp_path))
        result = scraper.run()
        assert len(result.github_repos) > 0
        assert len(result.knowledge_items) > 0
        assert len(result.monetization_ideas) > 0
        assert len(result.client_leads) > 0
        assert len(result.self_improvement) > 0

    def test_total_findings_positive(self, tmp_path):
        scraper = EliteScraper.for_bot("finance_bot", github_token=None, max_results_per_query=2)
        scraper.store = KnowledgeStore("finance_bot", data_root=str(tmp_path))
        result = scraper.run()
        assert result.total_findings() > 0

    def test_summary_contains_bot_name(self, tmp_path):
        scraper = EliteScraper.for_bot("lead_gen_bot", github_token=None, max_results_per_query=2)
        scraper.store = KnowledgeStore("lead_gen_bot", data_root=str(tmp_path))
        result = scraper.run()
        assert "lead_gen_bot" in result.summary()

    def test_knowledge_persisted_to_store(self, tmp_path):
        scraper = EliteScraper.for_bot("affiliate_bot", github_token=None, max_results_per_query=2)
        scraper.store = KnowledgeStore("affiliate_bot", data_root=str(tmp_path))
        scraper.run()
        # After run, stores should contain data
        stats = scraper.store.stats()
        total = sum(stats.values())
        assert total > 0

    def test_run_multiple_bots_no_cross_contamination(self, tmp_path):
        store_lead = KnowledgeStore("lead_gen_bot", data_root=str(tmp_path))
        store_crypto = KnowledgeStore("crypto_bot", data_root=str(tmp_path))

        s1 = EliteScraper.for_bot("lead_gen_bot", github_token=None, max_results_per_query=2)
        s1.store = store_lead
        s1.run()

        s2 = EliteScraper.for_bot("crypto_bot", github_token=None, max_results_per_query=2)
        s2.store = store_crypto
        s2.run()

        lead_items = store_lead.load("knowledge")
        crypto_items = store_crypto.load("knowledge")

        # Each bot's store should be populated
        assert len(lead_items) > 0
        assert len(crypto_items) > 0

        # The two stores should contain different data
        lead_ids = {i.get("id") for i in lead_items}
        crypto_ids = {i.get("id") for i in crypto_items}
        assert lead_ids != crypto_ids


# ===========================================================================
# 4. ScraperResult helpers
# ===========================================================================

class TestScraperResult:
    def test_total_findings_zero_on_empty(self):
        r = ScraperResult(bot_name="test", timestamp="2025-01-01T00:00:00+00:00")
        assert r.total_findings() == 0

    def test_total_findings_counts_all_categories(self):
        r = ScraperResult(
            bot_name="test",
            timestamp="2025-01-01T00:00:00+00:00",
            github_repos=[{}],
            knowledge_items=[{}, {}],
            monetization_ideas=[{}],
            client_leads=[{}, {}, {}],
            competing_bots=[{}],
            self_improvement=[{}],
        )
        assert r.total_findings() == 9

    def test_summary_is_string(self):
        r = ScraperResult(bot_name="test_bot", timestamp="2025-01-01T00:00:00+00:00")
        s = r.summary()
        assert isinstance(s, str)
        assert "test_bot" in s

    def test_summary_includes_error_when_present(self):
        r = ScraperResult(
            bot_name="test_bot",
            timestamp="2025-01-01T00:00:00+00:00",
            errors=["store: write failed"],
        )
        assert "Errors" in r.summary() or "error" in r.summary().lower()
