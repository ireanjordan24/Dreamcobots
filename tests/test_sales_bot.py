"""
Tests for bots/sales_bot/outreach_bot.py

Covers:
  1. Instantiation
  2. run() — returns appropriate string for no leads / success / file-missing
  3. send_email() — calls SMTP correctly
  4. Bot alias
"""

from __future__ import annotations

import ast
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch, call

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

from bots.sales_bot.outreach_bot import OutreachBot, Bot


# ---------------------------------------------------------------------------
# 1. Instantiation
# ---------------------------------------------------------------------------

class TestOutreachBotInit:
    def test_default_name(self):
        bot = OutreachBot()
        assert bot.name == "Outreach Sales Bot"

    def test_default_smtp_port(self):
        bot = OutreachBot()
        assert bot.smtp_port == 587

    def test_custom_credentials(self):
        bot = OutreachBot(sender_email="me@test.com", password="secret")
        assert bot.sender_email == "me@test.com"
        assert bot.password == "secret"

    def test_custom_smtp(self):
        bot = OutreachBot(smtp_host="mail.test.com", smtp_port=465)
        assert bot.smtp_host == "mail.test.com"
        assert bot.smtp_port == 465


# ---------------------------------------------------------------------------
# 2. run()
# ---------------------------------------------------------------------------

class TestOutreachBotRun:
    def _write_leads(self, tmpdir: str, leads: list[dict]) -> None:
        with open(os.path.join(tmpdir, "leads.txt"), "w", encoding="utf-8") as fh:
            for lead in leads:
                fh.write(str(lead) + "\n")

    def test_run_returns_no_leads_when_file_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bot = OutreachBot(data_dir=tmpdir)
            result = bot.run()
        assert "No leads" in result

    def test_run_returns_no_leads_when_file_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "leads.txt"), "w").close()
            bot = OutreachBot(data_dir=tmpdir)
            result = bot.run()
        assert "No leads" in result

    def test_run_reports_count_on_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            leads = [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
            ]
            self._write_leads(tmpdir, leads)
            bot = OutreachBot(data_dir=tmpdir)
            with patch.object(bot, "send_email"):
                result = bot.run()
        assert "2" in result

    def test_run_calls_send_email_for_each_lead(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            leads = [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
            ]
            self._write_leads(tmpdir, leads)
            bot = OutreachBot(data_dir=tmpdir)
            with patch.object(bot, "send_email") as mock_send:
                bot.run()
            assert mock_send.call_count == 2

    def test_run_returns_failure_string_on_exception(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            leads = [{"name": "Alice", "phone": "x"}]
            self._write_leads(tmpdir, leads)
            bot = OutreachBot(data_dir=tmpdir)
            with patch.object(bot, "send_email", side_effect=RuntimeError("boom")):
                result = bot.run()
        assert "❌" in result


# ---------------------------------------------------------------------------
# 3. send_email()
# ---------------------------------------------------------------------------

class TestOutreachBotSendEmail:
    def test_send_email_uses_smtp(self):
        bot = OutreachBot(
            sender_email="sender@example.com",
            password="pass",
            smtp_host="smtp.example.com",
            smtp_port=587,
        )
        lead = {"name": "Alice", "email": "alice@example.com"}

        mock_server = MagicMock()
        mock_smtp_cls = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        with patch("bots.sales_bot.outreach_bot.smtplib.SMTP", mock_smtp_cls):
            bot.send_email(lead)

        mock_smtp_cls.assert_called_once_with("smtp.example.com", 587)

    def test_send_email_uses_lead_email_field(self):
        bot = OutreachBot()
        lead = {"name": "Bob", "email": "bob@example.com"}

        mock_server = MagicMock()
        mock_smtp_cls = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        with patch("bots.sales_bot.outreach_bot.smtplib.SMTP", mock_smtp_cls):
            bot.send_email(lead)

        mock_server.sendmail.assert_called_once()
        args = mock_server.sendmail.call_args[0]
        assert "bob@example.com" in args

    def test_send_email_falls_back_to_phone_field(self):
        # Lead has no 'email' key — the 'phone' field is used as the fallback
        # address, matching the raw lead structure produced by LeadScraperBot.
        bot = OutreachBot()
        lead = {"name": "Carol", "phone": "carol@example.com"}

        mock_server = MagicMock()
        mock_smtp_cls = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        with patch("bots.sales_bot.outreach_bot.smtplib.SMTP", mock_smtp_cls):
            bot.send_email(lead)

        mock_server.sendmail.assert_called_once()

    def test_send_email_handles_smtp_error_gracefully(self):
        # Using the 'phone' fallback to match raw scraper lead structure.
        bot = OutreachBot()
        lead = {"name": "Dave", "phone": "dave@example.com"}

        with patch("bots.sales_bot.outreach_bot.smtplib.SMTP", side_effect=ConnectionRefusedError):
            # Should not raise
            bot.send_email(lead)


# ---------------------------------------------------------------------------
# 4. Bot alias
# ---------------------------------------------------------------------------

class TestBotAlias:
    def test_bot_alias_is_subclass(self):
        assert issubclass(Bot, OutreachBot)

    def test_bot_alias_instantiates(self):
        bot = Bot()
        assert bot.name == "Outreach Sales Bot"
