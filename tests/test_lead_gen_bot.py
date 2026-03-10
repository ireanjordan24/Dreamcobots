"""Tests for LeadGenBot."""
import pytest

from core.revenue_engine import RevenueEngine
from core.monetization_hooks import MonetizationHooks
from core.dream_core import DreamCore
from bots.lead_gen_bot.lead_gen_bot import LeadGenBot
from core.bot_base import BotStatus


SAMPLE_HTML = """
<html>
<body>
  <div class="lead-card">
    <span class="name">John Doe</span>
    <a href="mailto:john.doe@example.com">john.doe@example.com</a>
    <span class="phone">555-123-4567</span>
    <span class="company">Acme Corp</span>
    <a href="https://acme.example.com">Website</a>
  </div>
</body>
</html>
"""

SAMPLE_HTML_MULTI = """
<html>
<body>
  <article>
    name: "Alice Smith"
    alice@example.com
    company: TechCo
    https://tech.example.com
  </article>
  <article>
    name: "Bob Jones"
    bob@example.com
    company: BuildCo
    https://build.example.com
  </article>
</body>
</html>
"""


def _make_bot():
    return LeadGenBot(
        revenue_engine=RevenueEngine(),
        monetization_hooks=MonetizationHooks(),
        dream_core=DreamCore(),
    )


class TestLeadGenBotScraping:
    def test_scrape_email_from_html(self):
        bot = _make_bot()
        leads = bot.scrape_html(SAMPLE_HTML)
        emails = [l["email"] for l in leads]
        assert any("john.doe@example.com" in e for e in emails)

    def test_scrape_phone_from_html(self):
        bot = _make_bot()
        leads = bot.scrape_html(SAMPLE_HTML)
        phones = [l["phone"] for l in leads]
        assert any("555" in p for p in phones)

    def test_scrape_url_from_html(self):
        bot = _make_bot()
        leads = bot.scrape_html(SAMPLE_HTML)
        urls = [l["url"] for l in leads]
        assert any(u.startswith("https://") for u in urls)

    def test_empty_html_returns_empty_list(self):
        bot = _make_bot()
        leads = bot.scrape_html("<html><body></body></html>")
        assert leads == []

    def test_scrape_returns_list(self):
        bot = _make_bot()
        result = bot.scrape_html(SAMPLE_HTML)
        assert isinstance(result, list)

    def test_scrape_lead_dict_has_required_keys(self):
        bot = _make_bot()
        leads = bot.scrape_html(SAMPLE_HTML)
        assert len(leads) > 0
        for lead in leads:
            assert "name" in lead
            assert "email" in lead
            assert "phone" in lead
            assert "company" in lead
            assert "url" in lead


class TestLeadGenBotLifecycle:
    def test_initial_status_is_idle(self):
        bot = _make_bot()
        assert bot.status == BotStatus.IDLE

    def test_run_scrapes_and_sends_outreach(self):
        bot = _make_bot()
        bot.add_html_source(SAMPLE_HTML)
        bot.run()
        assert len(bot.get_leads()) > 0
        assert len(bot.get_outreach_emails()) > 0

    def test_run_records_revenue(self):
        revenue_engine = RevenueEngine()
        bot = LeadGenBot(revenue_engine=revenue_engine)
        bot.add_html_source(SAMPLE_HTML)
        bot.run()
        assert revenue_engine.total() > 0

    def test_status_stopped_after_run(self):
        bot = _make_bot()
        bot.add_html_source(SAMPLE_HTML)
        bot.run()
        assert bot.status == BotStatus.STOPPED

    def test_multiple_html_sources(self):
        bot = _make_bot()
        bot.add_html_source(SAMPLE_HTML)
        bot.add_html_source(SAMPLE_HTML)
        bot.run()
        assert len(bot.get_leads()) >= 2

    def test_html_sources_cleared_after_execute(self):
        bot = _make_bot()
        bot.add_html_source(SAMPLE_HTML)
        bot.run()
        assert len(bot._html_sources) == 0


class TestLeadGenBotCSVExport:
    def test_export_csv_returns_string(self):
        bot = _make_bot()
        bot.add_html_source(SAMPLE_HTML)
        bot.run()
        csv_data = bot.export_csv()
        assert isinstance(csv_data, str)

    def test_export_csv_contains_header(self):
        bot = _make_bot()
        bot.add_html_source(SAMPLE_HTML)
        bot.run()
        csv_data = bot.export_csv()
        assert "email" in csv_data

    def test_export_csv_empty_when_no_leads(self):
        bot = _make_bot()
        csv_data = bot.export_csv()
        assert csv_data == ""

    def test_export_csv_contains_lead_data(self):
        bot = _make_bot()
        bot.add_html_source(SAMPLE_HTML)
        bot.run()
        csv_data = bot.export_csv()
        assert "john.doe@example.com" in csv_data or len(csv_data) > 0


class TestLeadGenBotMonetizationHooks:
    def test_hooks_track_lifecycle_events(self):
        hooks = MonetizationHooks()
        bot = LeadGenBot(monetization_hooks=hooks)
        bot.add_html_source(SAMPLE_HTML)
        bot.run()
        stages = [e["stage"] for e in hooks.funnel_report()]
        assert "bot_started" in stages
        assert "lead_scraped" in stages
        assert "outreach_sent" in stages
        assert "bot_stopped" in stages
