"""
Tests for bots/saas-selling-bot.

Conflict resolution notes:
- PR #36 tests were written for a different version of the saas-selling-bot.
- This version has been updated to test the current API from PR #55/56.
"""

import json
import os
import sys
import pytest

# Make the bot module importable without depending on working directory
BOT_DIR = os.path.join(os.path.dirname(__file__), "..", "bots", "saas-selling-bot")
sys.path.insert(0, os.path.abspath(BOT_DIR))

# Use an in-memory database for tests
os.environ["SAAS_BOT_DB"] = ":memory:"

import database as db  # noqa: E402
from nlp import get_faq_response, _keyword_score  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Each test gets its own in-memory database."""
    db_file = str(tmp_path / "test.db")
    monkeypatch.setattr(db, "DB_PATH", db_file)
    db.init_db()
    yield


@pytest.fixture()
def client(monkeypatch, tmp_path):
    """Flask test client with an isolated temp database."""
    import sys
    db_file = str(tmp_path / "client_test.db")
    monkeypatch.setattr(db, "DB_PATH", db_file)
    db.init_db()
    # Clear any previously cached 'bot' module to ensure we load the right one
    sys.modules.pop("bot", None)
    import importlib
    import bot as b
    importlib.reload(b)
    b.app.config["TESTING"] = True
    with b.app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# database.py tests
# ---------------------------------------------------------------------------

class TestDatabase:
    def test_init_creates_tables(self):
        conn = db.get_connection()
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        assert "tools" in tables

    def test_get_all_tools_returns_list(self):
        tools = db.get_all_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_get_tool_by_id_returns_dict(self):
        tool = db.get_tool_by_id(1)
        assert tool is not None
        assert "name" in tool

    def test_get_tool_by_id_not_found(self):
        tool = db.get_tool_by_id(9999)
        assert tool is None

    def test_get_categories_returns_list(self):
        cats = db.get_categories()
        assert isinstance(cats, list)

    def test_search_tools_returns_list(self):
        results = db.search_tools("bot")
        assert isinstance(results, list)

    def test_get_revenue_summary_returns_dict(self):
        summary = db.get_revenue_summary()
        assert isinstance(summary, dict)


# ---------------------------------------------------------------------------
# nlp.py tests
# ---------------------------------------------------------------------------

class TestNLP:
    def test_keyword_score_increases_with_matches(self):
        score = _keyword_score("discount savings coupon offer", ["discount", "savings"])
        assert score >= 2

    def test_keyword_score_zero_for_no_match(self):
        score = _keyword_score("hello world", ["discount"])
        assert score == 0

    def test_faq_response_returns_string(self):
        reply = get_faq_response("What does this bot do?")
        assert isinstance(reply, str)
        assert len(reply) > 0

    def test_faq_response_not_empty(self):
        reply = get_faq_response("pricing plans")
        assert reply != ""


# ---------------------------------------------------------------------------
# Flask route tests
# ---------------------------------------------------------------------------

class TestRoutes:
    def test_api_tools_returns_response(self, client):
        resp = client.get("/api/tools")
        assert resp.status_code == 200
        data = resp.get_json()
        # API returns either a list or a dict with 'tools' key
        assert isinstance(data, (list, dict))

    def test_api_categories_returns_list(self, client):
        resp = client.get("/api/categories")
        assert resp.status_code == 200
        data = resp.get_json()
        # API returns either a list or a dict with 'categories' key
        cats = data if isinstance(data, list) else data.get("categories", data)
        assert isinstance(cats, list)

    def test_api_plans_returns_list(self, client):
        resp = client.get("/api/plans")
        assert resp.status_code == 200
        data = resp.get_json()
        # API returns either a list or a dict with 'plans' key
        plans = data if isinstance(data, list) else data.get("plans", data)
        assert isinstance(plans, list)

    def test_api_search_returns_list(self, client):
        resp = client.get("/api/search?q=bot")
        assert resp.status_code == 200
        data = resp.get_json()
        # API returns either a list or a dict with 'results' key
        results = data if isinstance(data, list) else data.get("results", data)
        assert isinstance(results, list)

    def test_api_chat_valid(self, client):
        resp = client.post(
            "/api/chat",
            data=json.dumps({"message": "What can you do?"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "response" in data

    def test_api_chat_missing_message(self, client):
        resp = client.post(
            "/api/chat",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_api_revenue_returns_dict(self, client):
        resp = client.get("/api/revenue")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, dict)

    def test_api_recommend_returns_dict(self, client):
        resp = client.post(
            "/api/recommend",
            data=json.dumps({"query": "I need marketing automation"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, dict)
