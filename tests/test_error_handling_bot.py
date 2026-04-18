"""
Tests for the DreamCo Error Handling Bot.

Covers:
- Error categorization (all five categories + unknown)
- Exception capture
- Log text capture
- Learning mode on/off
- Fix suggestions presence
- Sandbox simulation
- Report generation
- Summary counts
- Beginner-friendly message content
"""

from __future__ import annotations

import pytest

from bots.error_handling_bot.error_handling_bot import (
    ErrorCategory,
    ErrorHandlingBot,
    ErrorRecord,
    FixSuggestion,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def bot():
    """Fresh ErrorHandlingBot with learning mode enabled."""
    b = ErrorHandlingBot(learning_mode=True, log_dir="/tmp/test-error-bot")
    b.start()
    return b


@pytest.fixture
def bot_no_learning():
    """Fresh ErrorHandlingBot with learning mode disabled."""
    b = ErrorHandlingBot(learning_mode=False, log_dir="/tmp/test-error-bot")
    b.start()
    return b


# ---------------------------------------------------------------------------
# Categorization tests
# ---------------------------------------------------------------------------

class TestCategorization:
    def test_syntax_error(self, bot):
        assert bot.categorize("SyntaxError: invalid syntax") == ErrorCategory.SYNTAX

    def test_indentation_error(self, bot):
        assert bot.categorize("IndentationError: unexpected indent") == ErrorCategory.SYNTAX

    def test_dependency_error_module_not_found(self, bot):
        assert (
            bot.categorize("ModuleNotFoundError: No module named 'openai'")
            == ErrorCategory.DEPENDENCY
        )

    def test_dependency_error_import(self, bot):
        assert (
            bot.categorize("ImportError: cannot import name 'foo' from 'bar'")
            == ErrorCategory.DEPENDENCY
        )

    def test_environment_key_error(self, bot):
        assert (
            bot.categorize("KeyError: 'STRIPE_API_KEY'") == ErrorCategory.ENVIRONMENT
        )

    def test_io_file_not_found(self, bot):
        assert (
            bot.categorize("FileNotFoundError: No such file or directory: 'config.json'")
            == ErrorCategory.IO
        )

    def test_io_permission_error(self, bot):
        assert (
            bot.categorize("PermissionError: [Errno 13] Permission denied")
            == ErrorCategory.IO
        )

    def test_http_connection_error(self, bot):
        assert (
            bot.categorize("requests.exceptions.HTTPError: 429 Too Many Requests")
            == ErrorCategory.HTTP
        )

    def test_http_status_500(self, bot):
        assert bot.categorize("status_code 500 Internal Server Error") == ErrorCategory.HTTP

    def test_unknown_error(self, bot):
        assert bot.categorize("something completely random") == ErrorCategory.UNKNOWN


# ---------------------------------------------------------------------------
# Exception capture tests
# ---------------------------------------------------------------------------

class TestCaptureException:
    def test_capture_returns_error_record(self, bot):
        exc = ModuleNotFoundError("No module named 'openai'")
        record = bot.capture_exception(exc, context="test_func")
        assert isinstance(record, ErrorRecord)

    def test_capture_correct_category(self, bot):
        exc = ModuleNotFoundError("No module named 'requests'")
        record = bot.capture_exception(exc)
        assert record.category == ErrorCategory.DEPENDENCY

    def test_capture_syntax_error(self, bot):
        exc = SyntaxError("invalid syntax")
        record = bot.capture_exception(exc, context="parse_file()")
        assert record.category == ErrorCategory.SYNTAX
        assert record.context == "parse_file()"

    def test_capture_io_error(self, bot):
        exc = FileNotFoundError("No such file or directory: 'missing.txt'")
        record = bot.capture_exception(exc)
        assert record.category == ErrorCategory.IO

    def test_capture_http_error(self, bot):
        exc = ConnectionError("requests.exceptions.HTTPError: 404 Not Found")
        record = bot.capture_exception(exc)
        assert record.category == ErrorCategory.HTTP

    def test_capture_stores_record(self, bot):
        exc = SyntaxError("bad syntax")
        bot.capture_exception(exc)
        assert len(bot.get_records()) == 1

    def test_capture_error_id_increments(self, bot):
        bot.capture_exception(SyntaxError("a"))
        bot.capture_exception(SyntaxError("b"))
        ids = [r.error_id for r in bot.get_records()]
        assert ids[0] != ids[1]

    def test_user_message_not_empty(self, bot):
        exc = SyntaxError("invalid syntax")
        record = bot.capture_exception(exc)
        assert len(record.user_message) > 10

    def test_suggestions_present(self, bot):
        exc = ModuleNotFoundError("No module named 'stripe'")
        record = bot.capture_exception(exc)
        assert len(record.suggestions) >= 1
        for s in record.suggestions:
            assert isinstance(s, FixSuggestion)
            assert len(s.instruction) > 0


# ---------------------------------------------------------------------------
# Log text capture tests
# ---------------------------------------------------------------------------

class TestCaptureLog:
    def test_capture_log_dependency(self, bot):
        log = "ModuleNotFoundError: No module named 'flask'\n    at main.py line 5"
        record = bot.capture_log(log, context="ci-run-42")
        assert record.category == ErrorCategory.DEPENDENCY

    def test_capture_log_http(self, bot):
        log = "requests.exceptions.HTTPError: 401 Unauthorized"
        record = bot.capture_log(log)
        assert record.category == ErrorCategory.HTTP

    def test_capture_log_unknown(self, bot):
        log = "some unusual random log line with no known pattern"
        record = bot.capture_log(log)
        assert record.category == ErrorCategory.UNKNOWN


# ---------------------------------------------------------------------------
# Learning mode tests
# ---------------------------------------------------------------------------

class TestLearningMode:
    def test_learning_mode_on_includes_tutorial(self, bot):
        exc = SyntaxError("invalid syntax")
        record = bot.capture_exception(exc)
        assert record.tutorial != ""
        assert "📖" in record.tutorial

    def test_learning_mode_off_no_tutorial(self, bot_no_learning):
        exc = SyntaxError("invalid syntax")
        record = bot_no_learning.capture_exception(exc)
        assert record.tutorial == ""

    def test_learning_mode_dependency_tutorial(self, bot):
        exc = ModuleNotFoundError("No module named 'openai'")
        record = bot.capture_exception(exc)
        assert "pip" in record.tutorial.lower()

    def test_learning_mode_io_tutorial(self, bot):
        exc = FileNotFoundError("config.json not found")
        record = bot.capture_exception(exc)
        assert record.tutorial != ""


# ---------------------------------------------------------------------------
# Report and summary tests
# ---------------------------------------------------------------------------

class TestReporting:
    def test_get_report_no_errors(self, bot):
        report = bot.get_report()
        assert "No errors detected" in report

    def test_get_report_with_errors(self, bot):
        bot.capture_exception(SyntaxError("oops"))
        report = bot.get_report()
        assert "ERROR DETECTED" in report
        assert "SYNTAX" in report.upper()

    def test_summary_counts(self, bot):
        bot.capture_exception(SyntaxError("a"))
        bot.capture_exception(SyntaxError("b"))
        bot.capture_exception(ModuleNotFoundError("No module named 'x'"))
        summary = bot.get_summary()
        assert summary[ErrorCategory.SYNTAX.value] == 2
        assert summary[ErrorCategory.DEPENDENCY.value] == 1

    def test_clear_resets_records(self, bot):
        bot.capture_exception(SyntaxError("a"))
        bot.clear()
        assert bot.get_records() == []

    def test_full_report_contains_suggestions(self, bot):
        exc = ModuleNotFoundError("No module named 'requests'")
        bot.capture_exception(exc)
        report = bot.get_report()
        assert "Step" in report

    def test_error_record_summary(self, bot):
        exc = SyntaxError("invalid syntax")
        record = bot.capture_exception(exc)
        summary = record.summary()
        assert "Syntax" in summary or "SYNTAX" in summary.upper()


# ---------------------------------------------------------------------------
# Sandbox simulation tests
# ---------------------------------------------------------------------------

class TestSandboxSimulation:
    def test_simulation_returns_records(self, bot):
        records = bot.simulate_bot_run()
        assert len(records) >= 4  # at least 4 error types exercised

    def test_simulation_covers_all_main_categories(self, bot):
        records = bot.simulate_bot_run()
        categories = {r.category for r in records}
        # The simulation should exercise at least these four
        assert ErrorCategory.SYNTAX in categories
        assert ErrorCategory.DEPENDENCY in categories
        assert ErrorCategory.IO in categories
        assert ErrorCategory.HTTP in categories

    def test_simulation_produces_report(self, bot):
        bot.simulate_bot_run()
        report = bot.get_report()
        assert "ERROR DETECTED" in report

    def test_simulation_records_have_suggestions(self, bot):
        records = bot.simulate_bot_run()
        for record in records:
            assert len(record.suggestions) >= 1


# ---------------------------------------------------------------------------
# Lifecycle tests
# ---------------------------------------------------------------------------

class TestLifecycle:
    def test_start_sets_running(self):
        b = ErrorHandlingBot()
        b.start()
        assert b.is_running is True

    def test_stop_clears_running(self):
        b = ErrorHandlingBot()
        b.start()
        b.stop()
        assert b.is_running is False

    def test_bot_alias(self):
        from bots.error_handling_bot.error_handling_bot import Bot
        assert Bot is ErrorHandlingBot
