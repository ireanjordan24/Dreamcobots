"""
Tests for new BaseBot methods: monetize() and report().
"""

from __future__ import annotations

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.base_bot import BaseBot, BaseBotError


# ---------------------------------------------------------------------------
# Minimal concrete bot for testing
# ---------------------------------------------------------------------------

class _DummyBot(BaseBot):
    bot_id = "dummy_bot"
    name = "Dummy Bot"
    category = "test"

    def run(self, task: dict) -> dict:
        return self._success(data={"task": task})


# ===========================================================================
# monetize()
# ===========================================================================

class TestBaseBotMonetize:
    def setup_method(self):
        self.bot = _DummyBot()

    def test_monetize_returns_dict(self):
        result = self.bot.monetize(amount=10.0, source="subscription")
        assert isinstance(result, dict)

    def test_monetize_contains_required_keys(self):
        result = self.bot.monetize(amount=5.0, source="api_call")
        for key in ("bot_id", "amount", "source", "total_revenue"):
            assert key in result

    def test_monetize_bot_id_matches(self):
        result = self.bot.monetize(amount=1.0)
        assert result["bot_id"] == "dummy_bot"

    def test_monetize_amount_is_recorded(self):
        result = self.bot.monetize(amount=25.0)
        assert result["amount"] == 25.0

    def test_monetize_source_is_recorded(self):
        result = self.bot.monetize(amount=1.0, source="marketplace")
        assert result["source"] == "marketplace"

    def test_monetize_default_source(self):
        result = self.bot.monetize(amount=1.0)
        assert result["source"] == "default"

    def test_monetize_accumulates_revenue(self):
        self.bot.monetize(amount=10.0)
        result = self.bot.monetize(amount=15.0)
        assert result["total_revenue"] == 25.0

    def test_monetize_zero_amount(self):
        result = self.bot.monetize(amount=0.0)
        assert result["total_revenue"] == 0.0

    def test_monetize_negative_amount_raises(self):
        with pytest.raises(ValueError):
            self.bot.monetize(amount=-1.0)

    def test_monetize_total_revenue_initial_zero(self):
        result = self.bot.monetize(amount=0.0)
        assert result["total_revenue"] == 0.0

    def test_monetize_multiple_calls(self):
        self.bot.monetize(amount=5.0)
        self.bot.monetize(amount=10.0)
        result = self.bot.monetize(amount=20.0)
        assert result["total_revenue"] == 35.0


# ===========================================================================
# report()
# ===========================================================================

class TestBaseBotReport:
    def setup_method(self):
        self.bot = _DummyBot()

    def test_report_returns_dict(self):
        assert isinstance(self.bot.report(), dict)

    def test_report_contains_required_keys(self):
        r = self.bot.report()
        for key in ("bot_id", "name", "category", "version", "total_revenue", "log_entries", "running"):
            assert key in r

    def test_report_bot_id(self):
        assert self.bot.report()["bot_id"] == "dummy_bot"

    def test_report_name(self):
        assert self.bot.report()["name"] == "Dummy Bot"

    def test_report_category(self):
        assert self.bot.report()["category"] == "test"

    def test_report_default_version(self):
        assert self.bot.report()["version"] == "1.0.0"

    def test_report_initial_revenue_zero(self):
        assert self.bot.report()["total_revenue"] == 0.0

    def test_report_revenue_after_monetize(self):
        self.bot.monetize(amount=50.0)
        assert self.bot.report()["total_revenue"] == 50.0

    def test_report_log_entries_empty(self):
        assert self.bot.report()["log_entries"] == 0

    def test_report_log_entries_after_log(self):
        self.bot.log("test message")
        assert self.bot.report()["log_entries"] == 1

    def test_report_running_default_false(self):
        assert self.bot.report()["running"] is False

    def test_report_running_after_start(self):
        self.bot.start()
        assert self.bot.report()["running"] is True

    def test_report_running_after_stop(self):
        self.bot.start()
        self.bot.stop()
        assert self.bot.report()["running"] is False
