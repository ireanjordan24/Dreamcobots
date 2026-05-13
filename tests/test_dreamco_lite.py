"""
Tests for dreamco_lite — MoneyBot, DebugBot, and Flask app.

Covers:
  1. MoneyBot.find_leads() — simulation mode returns correct shape
  2. MoneyBot.generate_messages() — template fallback when OPENAI_KEY absent
  3. MoneyBot.run_automation() — one-shot pipeline
  4. MoneyBot validation errors
  5. DebugBot.analyze() — pattern matching for common errors
  6. DebugBot.analyze() — empty / missing log
  7. Flask /api/health
  8. Flask /api/leads — happy path and validation
  9. Flask /api/messages — happy path and validation
  10. Flask /api/run-automation — happy path and validation
  11. Flask /api/debug — happy path and validation
"""

from __future__ import annotations

import os
import sys

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

# Force simulation mode for all tests so no real API keys are needed.
os.environ.setdefault("SIMULATION_MODE", "true")

from dreamco_lite.money_bot import MoneyBot
from dreamco_lite.debug_bot import DebugBot


# ---------------------------------------------------------------------------
# MoneyBot
# ---------------------------------------------------------------------------

class TestMoneyBotFindLeads:
    def setup_method(self):
        self.bot = MoneyBot()

    def test_returns_list(self):
        leads = self.bot.find_leads("real estate agents", "Wisconsin")
        assert isinstance(leads, list)

    def test_returns_non_empty_list(self):
        leads = self.bot.find_leads("dentists", "California")
        assert len(leads) > 0

    def test_lead_has_required_keys(self):
        leads = self.bot.find_leads("plumbers", "Texas")
        for lead in leads:
            for key in ("name", "business", "phone", "email", "location", "source"):
                assert key in lead, f"Missing key '{key}' in lead: {lead}"

    def test_location_stored_in_lead(self):
        leads = self.bot.find_leads("accountants", "New York")
        for lead in leads:
            assert lead["location"] == "New York"

    def test_simulation_source(self):
        leads = self.bot.find_leads("lawyers", "Florida")
        for lead in leads:
            assert lead["source"] == "simulation"

    def test_raises_on_empty_niche(self):
        with pytest.raises(ValueError, match="niche"):
            self.bot.find_leads("", "Texas")

    def test_raises_on_empty_location(self):
        with pytest.raises(ValueError, match="location"):
            self.bot.find_leads("doctors", "")


class TestMoneyBotGenerateMessages:
    def setup_method(self):
        self.bot = MoneyBot()
        self.leads = self.bot.find_leads("real estate agents", "Wisconsin")

    def test_returns_list(self):
        results = self.bot.generate_messages(self.leads, "real estate agents")
        assert isinstance(results, list)

    def test_result_count_matches_leads(self):
        results = self.bot.generate_messages(self.leads, "real estate agents")
        assert len(results) == len(self.leads)

    def test_outreach_message_key_present(self):
        results = self.bot.generate_messages(self.leads, "real estate agents")
        for result in results:
            assert "outreach_message" in result

    def test_outreach_message_is_string(self):
        results = self.bot.generate_messages(self.leads, "real estate agents")
        for result in results:
            assert isinstance(result["outreach_message"], str)
            assert len(result["outreach_message"]) > 10

    def test_empty_leads_returns_empty(self):
        results = self.bot.generate_messages([], "any niche")
        assert results == []

    def test_original_lead_fields_preserved(self):
        results = self.bot.generate_messages(self.leads, "real estate agents")
        for orig, result in zip(self.leads, results):
            for key in ("name", "business", "email"):
                assert result[key] == orig[key]


class TestMoneyBotRunAutomation:
    def setup_method(self):
        self.bot = MoneyBot()

    def test_returns_list(self):
        results = self.bot.run_automation("dentists", "Ohio")
        assert isinstance(results, list)

    def test_results_have_outreach_messages(self):
        results = self.bot.run_automation("dentists", "Ohio")
        assert len(results) > 0
        for r in results:
            assert "outreach_message" in r

    def test_raises_on_missing_niche(self):
        with pytest.raises(ValueError):
            self.bot.run_automation("", "Ohio")

    def test_raises_on_missing_location(self):
        with pytest.raises(ValueError):
            self.bot.run_automation("dentists", "")


# ---------------------------------------------------------------------------
# DebugBot
# ---------------------------------------------------------------------------

class TestDebugBotPatternMatching:
    def setup_method(self):
        self.bot = DebugBot()

    def test_returns_dict_with_required_keys(self):
        result = self.bot.analyze("KeyError: 'api_key'")
        assert "explanation" in result
        assert "fixes" in result
        assert "source" in result

    def test_fixes_is_list(self):
        result = self.bot.analyze("ImportError: No module named 'requests'")
        assert isinstance(result["fixes"], list)
        assert len(result["fixes"]) > 0

    def test_key_error_detected(self):
        result = self.bot.analyze("KeyError: 'user_id'")
        assert "dictionary" in result["explanation"].lower() or "key" in result["explanation"].lower()

    def test_import_error_detected(self):
        result = self.bot.analyze("ModuleNotFoundError: No module named 'pandas'")
        assert any("pip" in fix.lower() or "install" in fix.lower() for fix in result["fixes"])

    def test_connection_error_detected(self):
        result = self.bot.analyze("ConnectionRefusedError: [Errno 111] Connection refused")
        assert len(result["fixes"]) > 0
        assert any("service" in fix.lower() or "running" in fix.lower() or "port" in fix.lower() for fix in result["fixes"])

    def test_syntax_error_detected(self):
        result = self.bot.analyze("SyntaxError: invalid syntax")
        assert len(result["fixes"]) > 0

    def test_timeout_error_detected(self):
        result = self.bot.analyze("requests.exceptions.ReadTimeout: HTTPSConnectionPool")
        assert len(result["fixes"]) > 0

    def test_zero_division_error_detected(self):
        result = self.bot.analyze("ZeroDivisionError: division by zero")
        assert any("zero" in fix.lower() or "denominator" in fix.lower() for fix in result["fixes"])

    def test_http_404_detected(self):
        result = self.bot.analyze("HTTP 404 not found error on /api/leads")
        assert len(result["fixes"]) > 0

    def test_http_500_detected(self):
        result = self.bot.analyze("500 Internal Server Error in production")
        assert len(result["fixes"]) > 0

    def test_fallback_for_unknown_error(self):
        result = self.bot.analyze("Some completely unknown and unusual error XYZ_UNKNOWN_2099")
        assert isinstance(result["explanation"], str)
        assert len(result["fixes"]) > 0

    def test_source_is_pattern_matching(self):
        result = self.bot.analyze("TypeError: unsupported operand type")
        assert result["source"] == "pattern_matching"

    def test_multiple_patterns_merged(self):
        log = "ImportError: missing module\nKeyError: 'key'\nAttributeError: object has no attribute"
        result = self.bot.analyze(log)
        # Multiple patterns detected — fixes should be a non-empty list
        assert len(result["fixes"]) >= 3


class TestDebugBotEmptyInput:
    def setup_method(self):
        self.bot = DebugBot()

    def test_empty_string(self):
        result = self.bot.analyze("")
        assert result["source"] == "none"
        assert "No error log" in result["explanation"]

    def test_whitespace_only(self):
        result = self.bot.analyze("   \n\t  ")
        assert result["source"] == "none"

    def test_fixes_still_present_on_empty(self):
        result = self.bot.analyze("")
        assert isinstance(result["fixes"], list)
        assert len(result["fixes"]) > 0


# ---------------------------------------------------------------------------
# Flask app integration
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    """Return a Flask test client with SIMULATION_MODE forced on."""
    os.environ["SIMULATION_MODE"] = "true"
    from dreamco_lite.app import app as flask_app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


class TestFlaskHealth:
    def test_health_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert "dreamco-lite" in data["service"]


class TestFlaskLeads:
    def test_valid_request(self, client):
        resp = client.post("/api/leads", json={"niche": "dentists", "location": "Texas"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "leads" in data
        assert len(data["leads"]) > 0

    def test_missing_niche(self, client):
        resp = client.post("/api/leads", json={"location": "Texas"})
        assert resp.status_code == 400

    def test_missing_location(self, client):
        resp = client.post("/api/leads", json={"niche": "dentists"})
        assert resp.status_code == 400

    def test_empty_body(self, client):
        resp = client.post("/api/leads", json={})
        assert resp.status_code == 400

    def test_lead_structure(self, client):
        resp = client.post("/api/leads", json={"niche": "plumbers", "location": "Ohio"})
        data = resp.get_json()
        for lead in data["leads"]:
            assert "name" in lead
            assert "business" in lead


class TestFlaskMessages:
    def test_valid_request(self, client):
        # First get some leads
        leads_resp = client.post("/api/leads", json={"niche": "lawyers", "location": "NY"})
        leads = leads_resp.get_json()["leads"]

        resp = client.post("/api/messages", json={"leads": leads, "niche": "lawyers"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "results" in data
        assert len(data["results"]) == len(leads)

    def test_missing_niche(self, client):
        resp = client.post("/api/messages", json={"leads": [{"name": "x"}]})
        assert resp.status_code == 400

    def test_invalid_leads_type(self, client):
        resp = client.post("/api/messages", json={"leads": "not a list", "niche": "test"})
        assert resp.status_code == 400

    def test_empty_leads_returns_empty_results(self, client):
        resp = client.post("/api/messages", json={"leads": [], "niche": "dentists"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["results"] == []


class TestFlaskRunAutomation:
    def test_valid_request(self, client):
        resp = client.post(
            "/api/run-automation", json={"niche": "accountants", "location": "California"}
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "results" in data
        for r in data["results"]:
            assert "outreach_message" in r

    def test_missing_niche(self, client):
        resp = client.post("/api/run-automation", json={"location": "Texas"})
        assert resp.status_code == 400

    def test_missing_location(self, client):
        resp = client.post("/api/run-automation", json={"niche": "doctors"})
        assert resp.status_code == 400


class TestFlaskDebug:
    def test_valid_request(self, client):
        resp = client.post("/api/debug", json={"log": "KeyError: 'api_key'"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "explanation" in data
        assert "fixes" in data

    def test_missing_log(self, client):
        resp = client.post("/api/debug", json={})
        assert resp.status_code == 400

    def test_empty_log(self, client):
        resp = client.post("/api/debug", json={"log": ""})
        assert resp.status_code == 400

    def test_import_error_gives_install_fix(self, client):
        resp = client.post(
            "/api/debug",
            json={"log": "ModuleNotFoundError: No module named 'pandas'"},
        )
        data = resp.get_json()
        assert any("pip" in fix.lower() or "install" in fix.lower() for fix in data["fixes"])
