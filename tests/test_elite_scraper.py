"""
Tests for bots/elite_scraper/

Covers:
  1. KnowledgeFilter — scoring, filtering, deduplication
  2. EliteScraperBase — scrape(), run(), get_knowledge(), purge_stale()
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.elite_scraper.knowledge_filter import KnowledgeFilter
from bots.elite_scraper.base import EliteScraperBase
from bots.bot_library_manager import BotLibraryManager


# ===========================================================================
# KnowledgeFilter
# ===========================================================================

class TestKnowledgeFilterScore:
    def test_empty_item_scores_zero(self):
        filt = KnowledgeFilter(keywords=["python"])
        assert filt.score({}) == 0.0

    def test_no_keywords_neutral_score(self):
        filt = KnowledgeFilter(keywords=[])
        assert filt.score({"content": "anything here"}) == pytest.approx(50.0)

    def test_keyword_hit_increases_score(self):
        filt = KnowledgeFilter(keywords=["scraping"])
        score_with = filt.score({"content": "advanced scraping tutorial"})
        score_without = filt.score({"content": "cooking recipe"})
        assert score_with > score_without

    def test_multiple_keyword_hits(self):
        filt = KnowledgeFilter(keywords=["github", "workflow", "actions"])
        score = filt.score({"content": "github actions workflow automation"})
        assert score >= 30.0

    def test_short_content_penalty(self):
        filt = KnowledgeFilter(keywords=["python"])
        score_short = filt.score({"content": "py"})
        score_long = filt.score({"content": "python is a great scripting language for automation"})
        assert score_long > score_short

    def test_score_capped_at_100(self):
        filt = KnowledgeFilter(keywords=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"])
        score = filt.score({"content": "a b c d e f g h i j k"})
        assert score <= 100.0

    def test_title_field_used(self):
        filt = KnowledgeFilter(keywords=["github"])
        score = filt.score({"title": "github actions tutorial"})
        assert score > 0.0


class TestKnowledgeFilterFilter:
    def test_returns_two_lists(self):
        filt = KnowledgeFilter(keywords=["github"], min_score=10.0)
        kept, dropped = filt.filter([{"content": "github workflow"}])
        assert isinstance(kept, list)
        assert isinstance(dropped, list)

    def test_relevant_item_kept(self):
        filt = KnowledgeFilter(keywords=["scraping"], min_score=5.0)
        kept, dropped = filt.filter([{"content": "advanced scraping techniques"}])
        assert len(kept) == 1
        assert len(dropped) == 0

    def test_irrelevant_item_dropped(self):
        filt = KnowledgeFilter(keywords=["github"], min_score=50.0)
        kept, dropped = filt.filter([{"content": "baking bread recipe"}])
        assert len(kept) == 0
        assert len(dropped) == 1

    def test_relevance_score_injected(self):
        filt = KnowledgeFilter(keywords=["python"], min_score=5.0)
        kept, _ = filt.filter([{"content": "python tutorial"}])
        assert "relevance_score" in kept[0]

    def test_deduplication_drops_duplicates(self):
        filt = KnowledgeFilter(keywords=["x"], min_score=0.0, deduplicate=True)
        items = [{"content": "same text"}, {"content": "same text"}]
        kept, dropped = filt.filter(items)
        assert len(kept) + len(dropped) == 2
        assert len(dropped) >= 1

    def test_dedup_disabled_keeps_both(self):
        filt = KnowledgeFilter(keywords=["x"], min_score=0.0, deduplicate=False)
        items = [{"content": "repeat"}, {"content": "repeat"}]
        kept, dropped = filt.filter(items)
        assert len(kept) == 2
        assert len(dropped) == 0

    def test_reset_dedup_cache(self):
        filt = KnowledgeFilter(keywords=[], min_score=0.0, deduplicate=True)
        filt.filter([{"content": "x"}])
        filt.reset_dedup_cache()
        kept, _ = filt.filter([{"content": "x"}])
        assert len(kept) == 1


# ===========================================================================
# EliteScraperBase
# ===========================================================================

class _DummyScraper(EliteScraperBase):
    """Test subclass that returns hard-coded items."""

    bot_name = "test_bot"
    scraper_type = "dummy"
    keywords = ["relevant", "keyword"]
    min_relevance = 10.0

    def __init__(self, items=None, **kwargs):
        super().__init__(**kwargs)
        self._items = items or []

    def _fetch_raw(self, query: str):
        return list(self._items)


class TestEliteScraperBaseScrape:
    def test_scrape_returns_dict(self):
        s = _DummyScraper()
        result = s.scrape("test query")
        assert isinstance(result, dict)

    def test_scrape_has_expected_keys(self):
        s = _DummyScraper()
        result = s.scrape("q")
        for key in ("query", "items_found", "items_retained", "items_discarded", "kept", "dropped"):
            assert key in result

    def test_scrape_counts_correct(self):
        items = [
            {"content": "relevant keyword in here"},
            {"content": "noise noise noise"},
        ]
        s = _DummyScraper(items=items)
        result = s.scrape("relevant")
        assert result["items_found"] == 2

    def test_scrape_no_db_needed(self):
        s = _DummyScraper()
        result = s.scrape("q")
        assert result["items_retained"] == 0


class TestEliteScraperBaseRun:
    def setup_method(self):
        self.mgr = BotLibraryManager(retention_threshold=10.0)

    def teardown_method(self):
        self.mgr.close()

    def test_run_returns_dict(self):
        s = _DummyScraper()
        result = s.run("query")
        assert isinstance(result, dict)

    def test_run_has_bot_name(self):
        s = _DummyScraper()
        result = s.run("query")
        assert result["bot_name"] == "test_bot"

    def test_run_stores_retained_in_db(self):
        items = [{"content": "relevant keyword data for github workflow automation"}]
        s = _DummyScraper(items=items, db_manager=self.mgr)
        s.run("relevant")
        retained = self.mgr.get_retained_learning("test_bot")
        assert len(retained) >= 1

    def test_run_logs_scraper_run(self):
        s = _DummyScraper(db_manager=self.mgr)
        s.run("q")
        history = self.mgr.get_scraper_history("test_bot")
        assert len(history) == 1

    def test_run_without_db_does_not_raise(self):
        s = _DummyScraper()
        result = s.run("q")
        assert "items_found" in result

    def test_run_duration_ms_in_result(self):
        s = _DummyScraper()
        result = s.run("q")
        assert "duration_ms" in result
        assert isinstance(result["duration_ms"], int)


class TestEliteScraperHelpers:
    def setup_method(self):
        self.mgr = BotLibraryManager(retention_threshold=0.0)

    def teardown_method(self):
        self.mgr.close()

    def test_get_knowledge_without_db(self):
        s = _DummyScraper()
        assert s.get_knowledge() == []

    def test_get_knowledge_with_db(self):
        self.mgr.store_learning("test_bot", "tip", "x", relevance_score=80.0)
        s = _DummyScraper(db_manager=self.mgr)
        knowledge = s.get_knowledge()
        assert len(knowledge) >= 1

    def test_purge_stale_without_db(self):
        s = _DummyScraper()
        assert s.purge_stale() == 0

    def test_purge_stale_with_db(self):
        # Store one low-relevance entry (threshold=0 so it's retained)
        self.mgr.store_learning("test_bot", "t", "noise", relevance_score=5.0)
        s = _DummyScraper(db_manager=self.mgr)
        purged = s.purge_stale(threshold=50.0)
        assert purged == 1
