"""Tests for FiverrBot."""
import pytest

from core.revenue_engine import RevenueEngine
from core.monetization_hooks import MonetizationHooks
from Fiverr_bots.fiverr_bot import FiverrBot
from core.bot_base import BotStatus


class TestFiverrBot:
    def _make_bot(self):
        return FiverrBot(
            revenue_engine=RevenueEngine(),
            monetization_hooks=MonetizationHooks(),
        )

    def test_initial_state(self):
        bot = self._make_bot()
        assert bot.status == BotStatus.IDLE
        assert bot.get_completed_gigs() == []

    def test_add_gig_queues_gig(self):
        bot = self._make_bot()
        bot.add_gig("Python Tutorial", ["python", "tutorial"], word_count=300)
        assert len(bot._pending_gigs) == 1

    def test_run_processes_gig(self):
        bot = self._make_bot()
        bot.add_gig("SEO Guide", ["seo", "content marketing"])
        bot.run()
        completed = bot.get_completed_gigs()
        assert len(completed) == 1
        assert completed[0]["title"] == "SEO Guide"

    def test_gig_content_contains_keywords(self):
        bot = self._make_bot()
        bot.add_gig("Digital Marketing", ["digital marketing", "seo"])
        bot.run()
        content = bot.get_completed_gigs()[0]["content"]
        assert "digital marketing" in content.lower() or "Digital Marketing" in content

    def test_gig_records_revenue(self):
        revenue_engine = RevenueEngine()
        bot = FiverrBot(revenue_engine=revenue_engine)
        bot.add_gig("Blog Post", ["writing"])
        bot.run()
        assert revenue_engine.total() == FiverrBot.GIG_PRICE_USD

    def test_multiple_gigs_cumulative_revenue(self):
        revenue_engine = RevenueEngine()
        bot = FiverrBot(revenue_engine=revenue_engine)
        bot.add_gig("Gig 1", ["kw1"])
        bot.add_gig("Gig 2", ["kw2"])
        bot.run()
        assert revenue_engine.total() == FiverrBot.GIG_PRICE_USD * 2

    def test_export_text_returns_string(self):
        bot = self._make_bot()
        bot.add_gig("Test Gig", ["test"])
        bot.run()
        gig = bot.get_completed_gigs()[0]
        assert isinstance(gig["txt_output"], str)
        assert "Test Gig" in gig["txt_output"]

    def test_export_pdf_returns_bytes(self):
        bot = self._make_bot()
        bot.add_gig("PDF Gig", ["pdf"])
        bot.run()
        gig = bot.get_completed_gigs()[0]
        assert isinstance(gig["pdf_output"], bytes)
        assert b"%PDF" in gig["pdf_output"]

    def test_pending_gigs_cleared_after_execute(self):
        bot = self._make_bot()
        bot.add_gig("Cleared Gig", ["clear"])
        bot.run()
        assert len(bot._pending_gigs) == 0

    def test_lifecycle_status_after_run(self):
        bot = self._make_bot()
        bot.add_gig("Status Test", ["status"])
        bot.run()
        assert bot.status == BotStatus.STOPPED

    def test_monetization_hooks_track_gig_events(self):
        hooks = MonetizationHooks()
        bot = FiverrBot(monetization_hooks=hooks)
        bot.add_gig("Hooks Test", ["hook"])
        bot.run()
        stages = [e["stage"] for e in hooks.funnel_report()]
        assert "bot_started" in stages
        assert "gig_started" in stages
        assert "gig_completed" in stages
        assert "bot_stopped" in stages
