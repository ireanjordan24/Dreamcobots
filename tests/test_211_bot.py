"""
Tests for the 211 Resource and Eligibility Checker Bot.

Run with:
    pytest tests/test_211_bot.py -v
"""

import sys
import os

# Allow importing the bot modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bots", "211-resource-eligibility-bot"))

import pytest

from config import FPL_BASE, FPL_ADDITIONAL_PER_PERSON, PROGRAMS, SUPPORTED_LANGUAGES
from database import SessionDatabase
from eligibility_engine import check_eligibility, format_eligibility_results, get_fpl
from api_client import APIClient211
from bot import ResourceEligibilityBot, _detect_category, _detect_intent


# ---------------------------------------------------------------------------
# eligibility_engine tests
# ---------------------------------------------------------------------------


class TestGetFpl:
    def test_known_sizes(self):
        for size, expected in FPL_BASE.items():
            assert get_fpl(size) == float(expected)

    def test_size_9_extrapolates(self):
        expected = FPL_BASE[8] + FPL_ADDITIONAL_PER_PERSON
        assert get_fpl(9) == float(expected)

    def test_invalid_size_raises(self):
        with pytest.raises(ValueError):
            get_fpl(0)
        with pytest.raises(ValueError):
            get_fpl(-1)


class TestCheckEligibility:
    def test_snap_eligible_low_income(self):
        # A family of 4 earning $30,000/yr; SNAP threshold is 130% of FPL (~$40,560)
        results = check_eligibility(annual_income=30_000, household_size=4)
        assert results["SNAP"]["eligible"] is True

    def test_snap_not_eligible_high_income(self):
        # A family of 1 earning $60,000/yr; SNAP threshold is 130% of FPL (~$19,578)
        results = check_eligibility(annual_income=60_000, household_size=1)
        assert results["SNAP"]["eligible"] is False

    def test_medicaid_eligible(self):
        # Single person, $15,000/yr; Medicaid threshold 138% FPL (~$20,783)
        results = check_eligibility(annual_income=15_000, household_size=1)
        assert results["Medicaid"]["eligible"] is True

    def test_all_programs_present(self):
        results = check_eligibility(annual_income=20_000, household_size=2)
        for program in PROGRAMS:
            assert program in results

    def test_fpl_percent_calculated(self):
        fpl = get_fpl(1)
        results = check_eligibility(annual_income=fpl, household_size=1)
        for info in results.values():
            assert info["fpl_percent"] == pytest.approx(100.0, rel=0.01)

    def test_zero_income_all_eligible(self):
        results = check_eligibility(annual_income=0, household_size=4)
        for info in results.values():
            assert info["eligible"] is True

    def test_negative_income_raises(self):
        with pytest.raises(ValueError):
            check_eligibility(annual_income=-1, household_size=1)

    def test_returns_threshold_percent(self):
        results = check_eligibility(annual_income=20_000, household_size=3)
        assert results["SNAP"]["threshold_percent"] == 130
        assert results["Medicaid"]["threshold_percent"] == 138


class TestFormatEligibilityResults:
    def test_contains_program_names(self):
        results = check_eligibility(annual_income=20_000, household_size=3)
        formatted = format_eligibility_results(results)
        for program in PROGRAMS:
            assert program in formatted

    def test_eligible_checkmark(self):
        results = check_eligibility(annual_income=5_000, household_size=1)
        formatted = format_eligibility_results(results)
        assert "✓" in formatted

    def test_not_eligible_cross(self):
        results = check_eligibility(annual_income=500_000, household_size=1)
        formatted = format_eligibility_results(results)
        assert "✗" in formatted


# ---------------------------------------------------------------------------
# database tests
# ---------------------------------------------------------------------------


class TestSessionDatabase:
    def test_create_and_exists(self):
        db = SessionDatabase(ttl=60)
        sid = db.create_session()
        assert db.session_exists(sid)

    def test_set_and_get(self):
        db = SessionDatabase(ttl=60)
        sid = db.create_session()
        db.set(sid, "foo", "bar")
        assert db.get(sid, "foo") == "bar"

    def test_get_default(self):
        db = SessionDatabase(ttl=60)
        sid = db.create_session()
        assert db.get(sid, "nonexistent", "default_val") == "default_val"

    def test_delete_session(self):
        db = SessionDatabase(ttl=60)
        sid = db.create_session()
        db.delete_session(sid)
        assert not db.session_exists(sid)

    def test_get_session_excludes_internal_keys(self):
        db = SessionDatabase(ttl=60)
        sid = db.create_session()
        db.set(sid, "lang", "en")
        snapshot = db.get_session(sid)
        assert "lang" in snapshot
        assert "_created_at" not in snapshot
        assert "_last_active" not in snapshot

    def test_set_nonexistent_session_raises(self):
        db = SessionDatabase(ttl=60)
        with pytest.raises(KeyError):
            db.set("nonexistent-session", "key", "value")

    def test_expired_session_removed(self):
        import time
        db = SessionDatabase(ttl=0)  # instant expiry
        sid = db.create_session()
        time.sleep(0.01)
        # Trigger eviction via any method
        assert not db.session_exists(sid)


# ---------------------------------------------------------------------------
# api_client tests
# ---------------------------------------------------------------------------


class TestAPIClient211:
    def test_mock_results_no_key(self):
        client = APIClient211(api_key="")
        results = client.search_resources(category="food", location="10001")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_invalid_base_url_raises(self):
        with pytest.raises(ValueError):
            APIClient211(api_key="key", base_url="ftp://bad.example.com")
        with pytest.raises(ValueError):
            APIClient211(api_key="key", base_url="not-a-url")

    def test_mock_results_structure(self):
        client = APIClient211(api_key="")
        results = client.search_resources(category="housing", location="10001")
        required_keys = {"name", "address", "phone", "description"}
        for r in results:
            assert required_keys.issubset(r.keys())

    def test_mock_unknown_category_fallback(self):
        client = APIClient211(api_key="")
        results = client.search_resources(category="unknown_xyz", location="10001")
        assert isinstance(results, list)

    def test_limit_respected(self):
        client = APIClient211(api_key="")
        results = client.search_resources(category="food", location="10001", limit=1)
        assert len(results) <= 1


# ---------------------------------------------------------------------------
# Intent detection tests
# ---------------------------------------------------------------------------


class TestDetectIntent:
    def test_resource_intent(self):
        assert _detect_intent("I need food assistance") == "resource"
        assert _detect_intent("help me find housing") == "resource"

    def test_eligibility_intent(self):
        assert _detect_intent("Am I eligible for SNAP?") == "eligibility"
        assert _detect_intent("check my eligibility") == "eligibility"

    def test_quit_intent(self):
        assert _detect_intent("quit") == "quit"
        assert _detect_intent("exit") == "quit"

    def test_help_intent(self):
        assert _detect_intent("help") == "help"

    def test_language_change_intent(self):
        assert _detect_intent("Speak Spanish") == "language_change"
        assert _detect_intent("switch to english") == "language_change"

    def test_unknown_intent(self):
        assert _detect_intent("foobar xyz 123") == "unknown"


class TestDetectCategory:
    def test_food_keywords(self):
        assert _detect_category("I'm hungry") == "food"
        assert _detect_category("need groceries") == "food"

    def test_housing_keywords(self):
        assert _detect_category("I can't pay rent") == "housing"
        assert _detect_category("facing eviction") == "housing"

    def test_mental_health_keywords(self):
        assert _detect_category("I'm having a mental health crisis") == "mental_health"

    def test_no_match_returns_none(self):
        assert _detect_category("xyzzy plugh") is None


# ---------------------------------------------------------------------------
# Bot integration tests
# ---------------------------------------------------------------------------


class TestResourceEligibilityBot:
    def setup_method(self):
        self.bot = ResourceEligibilityBot()
        self.session_id = self.bot.start_session(language="en")

    def teardown_method(self):
        if self.bot._db.session_exists(self.session_id):
            self.bot.end_session(self.session_id)

    def test_welcome_message(self):
        msg = self.bot.get_welcome_message(self.session_id)
        assert len(msg) > 10

    def test_help_response(self):
        reply = self.bot.handle_message(self.session_id, "help")
        assert "help" in reply.lower() or "you can" in reply.lower()

    def test_unknown_input_response(self):
        reply = self.bot.handle_message(self.session_id, "asdfghjkl qwerty")
        assert len(reply) > 0

    def test_quit_ends_session(self):
        self.bot.handle_message(self.session_id, "quit")
        assert not self.bot._db.session_exists(self.session_id)

    def test_resource_flow_food(self):
        # Step 1: express food need
        reply1 = self.bot.handle_message(self.session_id, "I need food")
        assert "zip" in reply1.lower() or "city" in reply1.lower() or "location" in reply1.lower()
        # Step 2: provide location
        reply2 = self.bot.handle_message(self.session_id, "10001")
        assert "food" in reply2.lower() or "resource" in reply2.lower() or "result" in reply2.lower() or len(reply2) > 20

    def test_eligibility_flow(self):
        # Step 1: express eligibility intent
        reply1 = self.bot.handle_message(self.session_id, "check my eligibility")
        assert "income" in reply1.lower()
        # Step 2: provide income
        reply2 = self.bot.handle_message(self.session_id, "24000")
        assert "household" in reply2.lower()
        # Step 3: provide household size
        reply3 = self.bot.handle_message(self.session_id, "3")
        assert "SNAP" in reply3 or "eligible" in reply3.lower()

    def test_eligibility_flow_invalid_income(self):
        self.bot.handle_message(self.session_id, "Am I eligible for SNAP?")
        reply = self.bot.handle_message(self.session_id, "not a number")
        assert "numeric" in reply.lower() or "number" in reply.lower()

    def test_language_switch_to_spanish(self):
        reply = self.bot.handle_message(self.session_id, "Speak Spanish")
        assert "Hola" in reply or "español" in reply.lower() or "ayuda" in reply.lower()

    def test_unsupported_language(self):
        reply = self.bot.handle_message(self.session_id, "Speak Klingon")
        assert "not" in reply.lower() or "support" in reply.lower()

    def test_expired_session_returns_message(self):
        reply = self.bot.handle_message("nonexistent-session-id", "hello")
        assert "expired" in reply.lower() or "session" in reply.lower()

    def test_start_session_unsupported_lang_defaults_en(self):
        sid = self.bot.start_session(language="xx")
        assert self.bot._db.get(sid, "language") == "en"
        self.bot.end_session(sid)

    def test_multiple_concurrent_sessions(self):
        sid2 = self.bot.start_session(language="es")
        sid3 = self.bot.start_session(language="en")
        assert sid2 != sid3
        assert self.bot._db.get(sid2, "language") == "es"
        assert self.bot._db.get(sid3, "language") == "en"
        self.bot.end_session(sid2)
        self.bot.end_session(sid3)
