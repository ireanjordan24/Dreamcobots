"""
Tests for bots/integration_feedback_bot/

Covers:
  1. Tiers (FREE / PRO / ENTERPRISE)
  2. IntegrationLogger (load / save / append / filter)
  3. SlackNotifier (unit test — no live HTTP)
  4. AutoHealAdvisor
  5. IntegrationAnalytics
  6. IntegrationFeedbackBot orchestrator (log_integration / get_summary)
  7. Tier gating (feature access + tracking limits)
  8. Error handling & edge cases
  9. Bot Library registration
"""

import json
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Tier imports
# ---------------------------------------------------------------------------
from bots.integration_feedback_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_BASIC_TRACKING,
    FEATURE_SLACK_NOTIFY,
    FEATURE_EXPORT_CSV,
    FEATURE_AUTO_HEAL,
    FEATURE_ANALYTICS,
    FEATURE_WEBHOOK,
    FEATURE_EMAIL_ALERTS,
)

# ---------------------------------------------------------------------------
# Bot imports
# ---------------------------------------------------------------------------
from bots.integration_feedback_bot.integration_feedback_bot import (
    IntegrationFeedbackBot,
    IntegrationLogger,
    SlackNotifier,
    AutoHealAdvisor,
    IntegrationAnalytics,
)


# ===========================================================================
# 1. Tier tests
# ===========================================================================

class TestTiers:
    def test_tier_enum_values(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_tier_catalogue_has_all_tiers(self):
        for tier in Tier:
            assert tier.value in TIER_CATALOGUE

    def test_free_tier_config(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0
        assert cfg.max_integrations == 10
        assert cfg.has_feature(FEATURE_BASIC_TRACKING)
        assert not cfg.has_feature(FEATURE_SLACK_NOTIFY)
        assert not cfg.has_feature(FEATURE_ANALYTICS)

    def test_pro_tier_config(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0
        assert cfg.max_integrations is None
        assert cfg.is_unlimited()
        assert cfg.has_feature(FEATURE_SLACK_NOTIFY)
        assert cfg.has_feature(FEATURE_AUTO_HEAL)
        assert not cfg.has_feature(FEATURE_WEBHOOK)

    def test_enterprise_tier_config(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0
        assert cfg.has_feature(FEATURE_WEBHOOK)
        assert cfg.has_feature(FEATURE_EMAIL_ALERTS)

    def test_list_tiers_returns_all(self):
        tiers = list_tiers()
        assert len(tiers) == 3
        assert tiers[0].tier == Tier.FREE

    def test_upgrade_path(self):
        assert get_upgrade_path(Tier.FREE).tier == Tier.PRO
        assert get_upgrade_path(Tier.PRO).tier == Tier.ENTERPRISE
        assert get_upgrade_path(Tier.ENTERPRISE) is None


# ===========================================================================
# 2. IntegrationLogger tests
# ===========================================================================

class TestIntegrationLogger:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.log_path = os.path.join(self.tmpdir, "integration_log.json")
        self.logger = IntegrationLogger(log_path=self.log_path)

    def test_load_creates_empty_store_when_missing(self):
        store = self.logger.load()
        assert store["entries"] == []
        assert store["total_entries"] == 0

    def test_append_entry(self):
        entry = {"platform": "WordPress", "status": "success", "details": "Deployed v1.0"}
        self.logger.append(entry)
        entries = self.logger.get_all()
        assert len(entries) == 1
        assert entries[0]["platform"] == "WordPress"

    def test_append_multiple_entries(self):
        for i in range(3):
            self.logger.append({"platform": f"Platform{i}", "status": "success"})
        assert len(self.logger.get_all()) == 3

    def test_get_by_platform(self):
        self.logger.append({"platform": "WordPress", "status": "success"})
        self.logger.append({"platform": "Streamlit", "status": "failure"})
        wp_entries = self.logger.get_by_platform("WordPress")
        assert len(wp_entries) == 1
        assert wp_entries[0]["platform"] == "WordPress"

    def test_get_by_platform_case_insensitive(self):
        self.logger.append({"platform": "WordPress", "status": "success"})
        assert len(self.logger.get_by_platform("wordpress")) == 1

    def test_get_by_status_success(self):
        self.logger.append({"platform": "A", "status": "success"})
        self.logger.append({"platform": "B", "status": "failure"})
        successes = self.logger.get_by_status("success")
        assert len(successes) == 1
        assert successes[0]["platform"] == "A"

    def test_save_updates_metadata(self):
        self.logger.append({"platform": "WP", "status": "success"})
        store = self.logger.load()
        assert store["total_entries"] == 1
        assert store["last_updated"] is not None

    def test_export_csv(self):
        self.logger.append({"platform": "WordPress", "status": "success", "details": "OK"})
        csv_path = os.path.join(self.tmpdir, "export.csv")
        result = self.logger.export_csv(csv_path)
        assert os.path.exists(result)
        with open(result) as f:
            content = f.read()
        assert "WordPress" in content

    def test_export_csv_empty(self):
        csv_path = os.path.join(self.tmpdir, "empty.csv")
        result = self.logger.export_csv(csv_path)
        assert result == csv_path  # returns path without writing anything


# ===========================================================================
# 3. SlackNotifier tests
# ===========================================================================

class TestSlackNotifier:
    def test_send_returns_false_on_bad_url(self):
        notifier = SlackNotifier("https://invalid.example.com/webhook")
        entry = {"platform": "WordPress", "status": "success", "details": "OK", "timestamp": "now"}
        result = notifier.send(entry)
        assert result is False

    def test_send_with_suggestions(self):
        notifier = SlackNotifier("https://invalid.example.com/webhook")
        entry = {"platform": "WordPress", "status": "failure", "details": "Error", "timestamp": "now"}
        suggestions = ["Check credentials", "Retry deployment"]
        result = notifier.send(entry, suggestions)
        assert result is False  # still fails on bad URL, but no exception raised


# ===========================================================================
# 4. AutoHealAdvisor tests
# ===========================================================================

class TestAutoHealAdvisor:
    def setup_method(self):
        self.advisor = AutoHealAdvisor()

    def test_suggest_wordpress(self):
        suggestions = self.advisor.suggest("WordPress")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert any("SFTP" in s or "WordPress" in s or "wp-" in s for s in suggestions)

    def test_suggest_wix(self):
        suggestions = self.advisor.suggest("Wix")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_suggest_streamlit(self):
        suggestions = self.advisor.suggest("Streamlit")
        assert isinstance(suggestions, list)
        assert any("streamlit" in s.lower() or "requirements" in s.lower() for s in suggestions)

    def test_suggest_stripe(self):
        suggestions = self.advisor.suggest("Stripe")
        assert any("Stripe" in s or "webhook" in s.lower() for s in suggestions)

    def test_suggest_github_actions(self):
        suggestions = self.advisor.suggest("GitHub Actions")
        assert len(suggestions) > 0

    def test_suggest_unknown_platform_returns_defaults(self):
        suggestions = self.advisor.suggest("MysteryPlatform")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_suggest_returns_at_most_4(self):
        suggestions = self.advisor.suggest("WordPress")
        assert len(suggestions) <= 4


# ===========================================================================
# 5. IntegrationAnalytics tests
# ===========================================================================

class TestIntegrationAnalytics:
    def setup_method(self):
        self.analytics = IntegrationAnalytics()

    def _make_entries(self, successes=3, failures=2, platform="WordPress"):
        entries = []
        for i in range(successes):
            entries.append({"platform": platform, "status": "success", "details": f"OK {i}"})
        for i in range(failures):
            entries.append({"platform": platform, "status": "failure", "details": f"Err {i}"})
        return entries

    def test_compute_totals(self):
        entries = self._make_entries(3, 2)
        result = self.analytics.compute(entries)
        assert result["total_integrations"] == 5
        assert result["success_count"] == 3
        assert result["failure_count"] == 2

    def test_compute_success_rate(self):
        entries = self._make_entries(4, 1)
        result = self.analytics.compute(entries)
        assert result["success_rate_pct"] == 80.0

    def test_compute_empty(self):
        result = self.analytics.compute([])
        assert result["total_integrations"] == 0
        assert result["success_rate_pct"] == 0.0

    def test_compute_by_platform(self):
        entries = (
            self._make_entries(2, 1, platform="WordPress") +
            self._make_entries(1, 2, platform="Streamlit")
        )
        result = self.analytics.compute(entries)
        assert "WordPress" in result["by_platform"]
        assert "Streamlit" in result["by_platform"]
        assert result["by_platform"]["WordPress"]["success"] == 2

    def test_recent_failures(self):
        entries = self._make_entries(2, 3, platform="Wix")
        result = self.analytics.compute(entries)
        assert len(result["recent_failures"]) <= 5
        for f in result["recent_failures"]:
            assert f["status"] == "failure"


# ===========================================================================
# 6. IntegrationFeedbackBot tests
# ===========================================================================

class TestIntegrationFeedbackBot:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.log_path = os.path.join(self.tmpdir, "integration_log.json")

    def _make_bot(self, tier=Tier.FREE):
        return IntegrationFeedbackBot(tier=tier, log_path=self.log_path)

    def test_log_success(self):
        bot = self._make_bot(Tier.FREE)
        result = bot.log_integration(
            platform="WordPress",
            status="success",
            details="Plugin deployed.",
        )
        assert result["entry"]["status"] == "success"
        assert result["entry"]["platform"] == "WordPress"
        assert result["slack_sent"] is False  # no webhook on FREE

    def test_log_failure_free_no_suggestions(self):
        bot = self._make_bot(Tier.FREE)
        result = bot.log_integration(
            platform="Streamlit",
            status="failure",
            details="Deployment failed.",
        )
        assert result["entry"]["status"] == "failure"
        assert result["suggestions"] == []  # FREE tier — no auto-heal

    def test_log_failure_pro_has_suggestions(self):
        bot = self._make_bot(Tier.PRO)
        result = bot.log_integration(
            platform="WordPress",
            status="failure",
            details="Upload failed.",
        )
        assert len(result["suggestions"]) > 0
        assert "auto_heal_suggestions" in result["entry"]

    def test_log_saves_to_file(self):
        bot = self._make_bot(Tier.FREE)
        bot.log_integration(platform="Wix", status="success")
        assert os.path.exists(self.log_path)
        with open(self.log_path) as f:
            store = json.load(f)
        assert store["total_entries"] == 1

    def test_get_log_all(self):
        bot = self._make_bot(Tier.FREE)
        bot.log_integration(platform="WordPress", status="success")
        bot.log_integration(platform="Streamlit", status="failure")
        entries = bot.get_log()
        assert len(entries) == 2

    def test_get_log_filtered_by_platform(self):
        bot = self._make_bot(Tier.FREE)
        bot.log_integration(platform="WordPress", status="success")
        bot.log_integration(platform="Streamlit", status="failure")
        entries = bot.get_log(platform="WordPress")
        assert len(entries) == 1

    def test_get_log_filtered_by_status(self):
        bot = self._make_bot(Tier.FREE)
        bot.log_integration(platform="WordPress", status="success")
        bot.log_integration(platform="Wix", status="failure")
        failures = bot.get_log(status="failure")
        assert len(failures) == 1
        assert failures[0]["platform"] == "Wix"

    def test_log_with_version(self):
        bot = self._make_bot(Tier.FREE)
        result = bot.log_integration(
            platform="WordPress", status="success", version="2.3.1"
        )
        assert result["entry"]["version"] == "2.3.1"

    def test_log_triggered_by(self):
        bot = self._make_bot(Tier.FREE)
        result = bot.log_integration(
            platform="Streamlit", status="success", triggered_by="GitHub Actions run #42"
        )
        assert "GitHub Actions" in result["entry"]["triggered_by"]

    def test_get_summary(self):
        bot = self._make_bot(Tier.FREE)
        bot.log_integration(platform="WordPress", status="success")
        bot.log_integration(platform="Wix", status="failure")
        summary = bot.get_summary()
        assert summary["bot"] == "IntegrationFeedbackBot"
        assert summary["tier"] == "free"
        assert summary["total_logged"] == 2
        assert summary["success_count"] == 1
        assert summary["failure_count"] == 1
        assert summary["generated_by"] == "GLOBAL AI SOURCES FLOW"

    def test_success_rate_calculation(self):
        bot = self._make_bot(Tier.FREE)
        bot.log_integration(platform="A", status="success")
        bot.log_integration(platform="B", status="success")
        bot.log_integration(platform="C", status="failure")
        bot.log_integration(platform="D", status="failure")
        summary = bot.get_summary()
        assert summary["success_rate_pct"] == 50.0

    def test_supported_platforms_list(self):
        bot = self._make_bot(Tier.FREE)
        assert "WordPress" in bot.SUPPORTED_PLATFORMS
        assert "Wix" in bot.SUPPORTED_PLATFORMS
        assert "Streamlit" in bot.SUPPORTED_PLATFORMS


# ===========================================================================
# 7. Tier gating tests
# ===========================================================================

class TestTierGating:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.log_path = os.path.join(self.tmpdir, "integration_log.json")

    def _make_bot(self, tier):
        return IntegrationFeedbackBot(tier=tier, log_path=self.log_path)

    def test_free_cannot_get_analytics(self):
        bot = self._make_bot(Tier.FREE)
        bot.log_integration(platform="WP", status="success")
        with pytest.raises(PermissionError, match="analytics"):
            bot.get_analytics()

    def test_pro_can_get_analytics(self):
        bot = self._make_bot(Tier.PRO)
        bot.log_integration(platform="WP", status="success")
        analytics = bot.get_analytics()
        assert analytics["total_integrations"] == 1

    def test_free_cannot_export_csv(self):
        bot = self._make_bot(Tier.FREE)
        with pytest.raises(PermissionError):
            bot.export_csv()

    def test_pro_can_export_csv(self):
        bot = self._make_bot(Tier.PRO)
        bot.log_integration(platform="WP", status="success")
        csv_path = os.path.join(self.tmpdir, "export.csv")
        result = bot.export_csv(csv_path)
        assert os.path.exists(result)

    def test_free_cannot_get_suggestions(self):
        bot = self._make_bot(Tier.FREE)
        with pytest.raises(PermissionError, match="auto_heal"):
            bot.get_suggestions("WordPress")

    def test_pro_can_get_suggestions(self):
        bot = self._make_bot(Tier.PRO)
        suggestions = bot.get_suggestions("WordPress")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_free_tracking_limit_enforced(self):
        bot = self._make_bot(Tier.FREE)
        # Pre-fill the log to its limit (10)
        for i in range(10):
            bot.log_integration(platform=f"P{i}", status="success")
        with pytest.raises(RuntimeError, match="limit"):
            bot.log_integration(platform="Overflow", status="success")

    def test_pro_no_tracking_limit(self):
        bot = self._make_bot(Tier.PRO)
        for i in range(20):
            bot.log_integration(platform=f"P{i}", status="success")
        summary = bot.get_summary()
        assert summary["total_logged"] == 20


# ===========================================================================
# 8. Error handling & edge cases
# ===========================================================================

class TestEdgeCases:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.log_path = os.path.join(self.tmpdir, "integration_log.json")

    def test_log_with_empty_details(self):
        bot = IntegrationFeedbackBot(tier=Tier.FREE, log_path=self.log_path)
        result = bot.log_integration(platform="WordPress", status="success")
        assert result["entry"]["details"] == ""

    def test_log_custom_platform(self):
        bot = IntegrationFeedbackBot(tier=Tier.FREE, log_path=self.log_path)
        result = bot.log_integration(platform="Custom", status="success")
        assert result["entry"]["platform"] == "Custom"

    def test_summary_with_no_entries(self):
        bot = IntegrationFeedbackBot(tier=Tier.FREE, log_path=self.log_path)
        summary = bot.get_summary()
        assert summary["success_rate_pct"] == 0.0
        assert summary["total_logged"] == 0

    def test_analytics_with_multiple_platforms(self):
        bot = IntegrationFeedbackBot(tier=Tier.PRO, log_path=self.log_path)
        bot.log_integration(platform="WordPress", status="success")
        bot.log_integration(platform="Wix", status="failure")
        bot.log_integration(platform="Streamlit", status="success")
        analytics = bot.get_analytics()
        assert len(analytics["by_platform"]) == 3


# ===========================================================================
# 9. Bot Library registration
# ===========================================================================

class TestBotLibraryRegistration:
    def test_integration_feedback_bot_registered(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("integration_feedback_bot")
        assert entry.bot_id == "integration_feedback_bot"
        assert entry.class_name == "IntegrationFeedbackBot"

    def test_integration_feedback_bot_capabilities(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("integration_feedback_bot")
        caps = entry.capabilities
        assert "integration_tracking" in caps
        assert "slack_notifications" in caps
        assert "auto_heal" in caps
        assert "wordpress_support" in caps
        assert "wix_support" in caps
        assert "streamlit_support" in caps

    def test_integration_feedback_bot_category(self):
        from bots.global_bot_network.bot_library import BotLibrary, BotCategory
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("integration_feedback_bot")
        assert entry.category == BotCategory.AUTOMATION
