"""
Tests for ui/web_dashboard.py

Covers:
  1. App creation
  2. Landing page (HTML)
  3. /api/status
  4. /api/bots (GET)
  5. /api/bots/register (POST)
  6. /api/revenue
  7. /api/leaderboard
  8. /api/underperformers
  9. /api/record_run (POST)
  10. /api/history/<bot_name>
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

# Only import the ai-models-integration tiers path needed by ControlCenter
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)

import json
import pytest

from ui.web_dashboard import create_app
from bots.ai_learning_system.database import BotPerformanceDB
from bots.control_center.control_center import ControlCenter


@pytest.fixture
def client():
    """Return a Flask test client backed by fresh in-memory components."""
    cc = ControlCenter()
    db = BotPerformanceDB()          # in-memory
    app = create_app(control_center=cc, db=db)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    db.close()


@pytest.fixture
def client_with_data():
    """Test client pre-populated with a registered bot and recorded runs."""
    cc = ControlCenter()
    db = BotPerformanceDB()

    class _FakeBot:
        class tier:
            value = "pro"

    cc.register_bot("affiliate_bot", _FakeBot())
    cc.add_income_entry("affiliate_bot", 120.50)
    db.record_run("affiliate_bot", kpis={"revenue_usd": 120.5, "tasks_completed": 6})
    db.record_run("weak_bot", kpis={"revenue_usd": 0.0, "tasks_completed": 0}, status="error")

    app = create_app(control_center=cc, db=db)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    db.close()


# ===========================================================================
# 1. App creation
# ===========================================================================

class TestAppCreation:
    def test_create_app_returns_flask_app(self):
        app = create_app()
        assert app is not None

    def test_create_app_without_args(self):
        app = create_app()
        assert hasattr(app, "test_client")


# ===========================================================================
# 2. Landing page
# ===========================================================================

class TestLandingPage:
    def test_get_root_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_root_content_type_html(self, client):
        resp = client.get("/")
        assert "text/html" in resp.content_type

    def test_root_contains_dreamco(self, client):
        resp = client.get("/")
        assert b"DreamCo" in resp.data

    def test_root_contains_dashboard_title(self, client):
        resp = client.get("/")
        assert b"Dashboard" in resp.data


# ===========================================================================
# 3. /api/status
# ===========================================================================

class TestApiStatus:
    def test_status_returns_200(self, client):
        resp = client.get("/api/status")
        assert resp.status_code == 200

    def test_status_is_json(self, client):
        resp = client.get("/api/status")
        data = json.loads(resp.data)
        assert isinstance(data, dict)

    def test_status_has_registered_bots(self, client):
        resp = client.get("/api/status")
        data = json.loads(resp.data)
        assert "registered_bots" in data

    def test_status_has_avg_composite_kpi(self, client):
        resp = client.get("/api/status")
        data = json.loads(resp.data)
        assert "avg_composite_kpi" in data

    def test_status_has_underperformers(self, client):
        resp = client.get("/api/status")
        data = json.loads(resp.data)
        assert "underperformers" in data

    def test_status_with_bot(self, client_with_data):
        resp = client_with_data.get("/api/status")
        data = json.loads(resp.data)
        assert data["registered_bots"] >= 1


# ===========================================================================
# 4. /api/bots
# ===========================================================================

class TestApiBots:
    def test_bots_returns_200(self, client):
        resp = client.get("/api/bots")
        assert resp.status_code == 200

    def test_bots_has_bots_key(self, client):
        data = json.loads(client.get("/api/bots").data)
        assert "bots" in data

    def test_bots_has_total_key(self, client):
        data = json.loads(client.get("/api/bots").data)
        assert "total" in data

    def test_bots_shows_registered_bots(self, client_with_data):
        data = json.loads(client_with_data.get("/api/bots").data)
        assert data["total"] >= 1


# ===========================================================================
# 5. /api/bots/register
# ===========================================================================

class TestRegisterBot:
    def test_register_returns_201(self, client):
        resp = client.post(
            "/api/bots/register",
            data=json.dumps({"name": "new_bot", "tier": "pro"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_register_response_contains_name(self, client):
        resp = client.post(
            "/api/bots/register",
            data=json.dumps({"name": "my_bot"}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert data["registered"] == "my_bot"

    def test_register_missing_name_returns_400(self, client):
        resp = client.post(
            "/api/bots/register",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_register_empty_name_returns_400(self, client):
        resp = client.post(
            "/api/bots/register",
            data=json.dumps({"name": "   "}),
            content_type="application/json",
        )
        assert resp.status_code == 400


# ===========================================================================
# 6. /api/revenue
# ===========================================================================

class TestApiRevenue:
    def test_revenue_returns_200(self, client):
        assert client.get("/api/revenue").status_code == 200

    def test_revenue_has_total_income(self, client):
        data = json.loads(client.get("/api/revenue").data)
        assert "total_income_usd" in data

    def test_revenue_has_by_source(self, client):
        data = json.loads(client.get("/api/revenue").data)
        assert "by_source" in data

    def test_revenue_reflects_income_entry(self, client_with_data):
        data = json.loads(client_with_data.get("/api/revenue").data)
        assert data["total_income_usd"] >= 120.50


# ===========================================================================
# 7. /api/leaderboard
# ===========================================================================

class TestApiLeaderboard:
    def test_leaderboard_returns_200(self, client):
        assert client.get("/api/leaderboard").status_code == 200

    def test_leaderboard_has_leaderboard_key(self, client):
        data = json.loads(client.get("/api/leaderboard").data)
        assert "leaderboard" in data

    def test_leaderboard_with_data(self, client_with_data):
        data = json.loads(client_with_data.get("/api/leaderboard").data)
        assert len(data["leaderboard"]) >= 1

    def test_leaderboard_top_n_param(self, client_with_data):
        data = json.loads(client_with_data.get("/api/leaderboard?top=1").data)
        assert len(data["leaderboard"]) <= 1


# ===========================================================================
# 8. /api/underperformers
# ===========================================================================

class TestApiUnderperformers:
    def test_underperformers_returns_200(self, client):
        assert client.get("/api/underperformers").status_code == 200

    def test_underperformers_has_list(self, client):
        data = json.loads(client.get("/api/underperformers").data)
        assert "underperformers" in data

    def test_underperformers_detects_weak_bot(self, client_with_data):
        data = json.loads(client_with_data.get("/api/underperformers?threshold=50").data)
        names = [b["bot_name"] for b in data["underperformers"]]
        assert "weak_bot" in names


# ===========================================================================
# 9. /api/record_run
# ===========================================================================

class TestRecordRun:
    def test_record_run_returns_201(self, client):
        resp = client.post(
            "/api/record_run",
            data=json.dumps({"bot_name": "test_bot", "kpis": {"revenue_usd": 50.0}}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_record_run_response_has_bot_name(self, client):
        resp = client.post(
            "/api/record_run",
            data=json.dumps({"bot_name": "my_bot"}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert data["bot_name"] == "my_bot"

    def test_record_run_missing_bot_name_returns_400(self, client):
        resp = client.post(
            "/api/record_run",
            data=json.dumps({"kpis": {}}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_record_run_appears_in_history(self, client):
        client.post(
            "/api/record_run",
            data=json.dumps({"bot_name": "tracked_bot", "kpis": {"revenue_usd": 30.0}}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/history/tracked_bot").data)
        assert len(data["history"]) == 1


# ===========================================================================
# 10. /api/history/<bot_name>
# ===========================================================================

class TestApiHistory:
    def test_history_returns_200(self, client):
        assert client.get("/api/history/some_bot").status_code == 200

    def test_history_has_correct_bot_name(self, client):
        data = json.loads(client.get("/api/history/my_bot").data)
        assert data["bot_name"] == "my_bot"

    def test_history_empty_for_unknown_bot(self, client):
        data = json.loads(client.get("/api/history/nonexistent").data)
        assert data["history"] == []

    def test_history_with_data(self, client_with_data):
        data = json.loads(client_with_data.get("/api/history/affiliate_bot").data)
        assert len(data["history"]) >= 1

    def test_history_limit_param(self, client):
        for _ in range(5):
            client.post(
                "/api/record_run",
                data=json.dumps({"bot_name": "h_bot"}),
                content_type="application/json",
            )
        data = json.loads(client.get("/api/history/h_bot?limit=2").data)
        assert len(data["history"]) <= 2


# ===========================================================================
# 11. /api/bots/catalog
# ===========================================================================

class TestBotCatalog:
    def test_catalog_returns_200(self, client):
        resp = client.get("/api/bots/catalog")
        assert resp.status_code == 200

    def test_catalog_has_catalog_key(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        assert "catalog" in data

    def test_catalog_has_total_key(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        assert "total" in data

    def test_catalog_contains_lead_generator(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        names = [b["name"] for b in data["catalog"]]
        assert "multi_source_lead_scraper" in names

    def test_catalog_contains_real_estate_bot(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        names = [b["name"] for b in data["catalog"]]
        assert "real_estate_bot" in names

    def test_catalog_contains_stripe_payment_bot(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        names = [b["name"] for b in data["catalog"]]
        assert "stripe_payment_bot" in names

    def test_catalog_bots_have_required_fields(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        for bot in data["catalog"]:
            for field in ("name", "display_name", "description", "revenue_model", "category", "is_live"):
                assert field in bot, f"Bot '{bot.get('name')}' missing field '{field}'"

    def test_catalog_not_live_by_default(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        # No bots are registered on a fresh client, so none should be live
        for bot in data["catalog"]:
            assert bot["is_live"] is False

    def test_catalog_bot_becomes_live_after_go_live(self, client):
        client.post(
            "/api/bots/multi_source_lead_scraper/go_live",
            data=json.dumps({"tier": "pro"}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/bots/catalog").data)
        lead_gen = next(b for b in data["catalog"] if b["name"] == "multi_source_lead_scraper")
        assert lead_gen["is_live"] is True

    def test_catalog_total_matches_list_length(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        assert data["total"] == len(data["catalog"])


# ===========================================================================
# 12. /api/bots/<name>/go_live
# ===========================================================================

class TestGoLive:
    def test_go_live_returns_201(self, client):
        resp = client.post(
            "/api/bots/lead_generator/go_live",
            data=json.dumps({"tier": "pro"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_go_live_response_has_status_live(self, client):
        resp = client.post(
            "/api/bots/my_revenue_bot/go_live",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert data["status"] == "live"

    def test_go_live_response_has_bot_name(self, client):
        resp = client.post(
            "/api/bots/test_bot/go_live",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert data["bot_name"] == "test_bot"

    def test_go_live_response_has_deployed_at(self, client):
        resp = client.post(
            "/api/bots/time_bot/go_live",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert "deployed_at" in data

    def test_go_live_response_has_message(self, client):
        resp = client.post(
            "/api/bots/msg_bot/go_live",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert "message" in data

    def test_go_live_registers_bot(self, client):
        client.post(
            "/api/bots/registered_bot/go_live",
            data=json.dumps({"tier": "pro"}),
            content_type="application/json",
        )
        status_data = json.loads(client.get("/api/status").data)
        assert status_data["registered_bots"] >= 1

    def test_go_live_records_run_in_history(self, client):
        client.post(
            "/api/bots/history_bot/go_live",
            data=json.dumps({}),
            content_type="application/json",
        )
        history = json.loads(client.get("/api/history/history_bot").data)
        assert len(history["history"]) >= 1

    def test_go_live_idempotent_second_call(self, client):
        for _ in range(2):
            resp = client.post(
                "/api/bots/idempotent_bot/go_live",
                data=json.dumps({}),
                content_type="application/json",
            )
            assert resp.status_code == 201

    def test_go_live_uses_specified_tier(self, client):
        resp = client.post(
            "/api/bots/tier_bot/go_live",
            data=json.dumps({"tier": "enterprise"}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert data["tier"] == "enterprise"

    def test_go_live_lead_generator(self, client):
        resp = client.post(
            "/api/bots/multi_source_lead_scraper/go_live",
            data=json.dumps({"tier": "pro"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_go_live_real_estate_bot(self, client):
        resp = client.post(
            "/api/bots/real_estate_bot/go_live",
            data=json.dumps({"tier": "enterprise"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_go_live_stripe_payment_bot(self, client):
        resp = client.post(
            "/api/bots/stripe_payment_bot/go_live",
            data=json.dumps({"tier": "growth"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_dashboard_html_contains_go_live_section(self, client):
        resp = client.get("/")
        assert b"Go Live" in resp.data

    def test_dashboard_html_contains_bot_catalog(self, client):
        resp = client.get("/")
        assert b"bot-catalog" in resp.data
