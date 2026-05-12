"""
Tests for bots/ai_enablement_hub/

Covers:
  1. Tiers (FREE / PRO / ENTERPRISE)
  2. AdvocatesProgram (add, list, limits, gating)
  3. PoliciesGuardrails (list, filter, count, gating)
  4. LearningDevelopment (list, filter, count, gating)
  5. DataMetrics (MAU recording, segmentation, maturity assessment)
  6. CommunityOfPractice (list, member tracking)
  7. BotTierClassifier (classify by features, tier gating)
  8. RetrainingOptimizer (drift detection, method selection, gating)
  9. AIEnablementHub orchestrator (get_summary, describe_tier, process)
  10. Bot Library registration
"""

import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Tier imports
# ---------------------------------------------------------------------------
from bots.ai_enablement_hub.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_POLICIES,
    FEATURE_LEARNING,
    FEATURE_COMMUNITY,
    FEATURE_ADVOCATES,
    FEATURE_METRICS,
    FEATURE_ADVANCED_LEARNING,
    FEATURE_MATURITY_ASSESSMENT,
    FEATURE_SEGMENTATION,
    FEATURE_BOT_TIER_CLASSIFIER,
    FEATURE_RETRAINING_OPTIMIZER,
    FEATURE_GOVERNANCE_API,
    FEATURE_DEDICATED_SUPPORT,
)

# ---------------------------------------------------------------------------
# Bot imports
# ---------------------------------------------------------------------------
from bots.ai_enablement_hub.ai_enablement_hub import (
    AIEnablementHub,
    AdvocatesProgram,
    PoliciesGuardrails,
    LearningDevelopment,
    DataMetrics,
    CommunityOfPractice,
    BotTierClassifier,
    RetrainingOptimizer,
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
        assert cfg.max_advocates == 3
        assert cfg.max_policies == 5
        assert cfg.has_feature(FEATURE_POLICIES)
        assert cfg.has_feature(FEATURE_LEARNING)
        assert cfg.has_feature(FEATURE_COMMUNITY)
        assert not cfg.has_feature(FEATURE_ADVOCATES)
        assert not cfg.has_feature(FEATURE_METRICS)

    def test_pro_tier_config(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0
        assert cfg.max_advocates == 25
        assert cfg.max_policies is None
        assert cfg.has_feature(FEATURE_ADVOCATES)
        assert cfg.has_feature(FEATURE_METRICS)
        assert cfg.has_feature(FEATURE_ADVANCED_LEARNING)
        assert cfg.has_feature(FEATURE_MATURITY_ASSESSMENT)
        assert cfg.has_feature(FEATURE_SEGMENTATION)
        assert not cfg.has_feature(FEATURE_BOT_TIER_CLASSIFIER)
        assert not cfg.has_feature(FEATURE_RETRAINING_OPTIMIZER)

    def test_enterprise_tier_config(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0
        assert cfg.max_advocates is None
        assert cfg.has_feature(FEATURE_BOT_TIER_CLASSIFIER)
        assert cfg.has_feature(FEATURE_RETRAINING_OPTIMIZER)
        assert cfg.has_feature(FEATURE_GOVERNANCE_API)
        assert cfg.has_feature(FEATURE_DEDICATED_SUPPORT)
        assert cfg.is_unlimited_advocates()

    def test_list_tiers_returns_all(self):
        tiers = list_tiers()
        assert len(tiers) == 3
        assert all(isinstance(t, TierConfig) for t in tiers)

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_has_feature_unknown_returns_false(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature("nonexistent_feature")


# ===========================================================================
# 2. AdvocatesProgram tests
# ===========================================================================

class TestAdvocatesProgram:
    def _make(self, tier: Tier) -> AdvocatesProgram:
        return AdvocatesProgram(get_tier_config(tier))

    def test_add_advocate_blocked_on_free(self):
        prog = self._make(Tier.FREE)
        result = prog.add_advocate("bob")
        assert result["added"] is False
        assert "PRO" in result["reason"] or "pro" in result["reason"].lower()

    def test_add_advocate_success_on_pro(self):
        prog = self._make(Tier.PRO)
        result = prog.add_advocate("alice", "Core Advocate", "automation")
        assert result["added"] is True
        assert result["advocate"]["username"] == "alice"
        assert result["advocate"]["role"] == "Core Advocate"
        assert result["advocate"]["domain"] == "automation"
        assert "added_at" in result["advocate"]

    def test_add_advocate_default_role(self):
        prog = self._make(Tier.PRO)
        result = prog.add_advocate("carol")
        assert result["added"] is True
        assert result["advocate"]["role"] == "Starter Advocate"

    def test_pro_tier_limit_enforced(self):
        prog = self._make(Tier.PRO)
        for i in range(25):
            prog.add_advocate(f"user_{i}")
        result = prog.add_advocate("overflow_user")
        assert result["added"] is False
        assert "limit" in result["reason"].lower()

    def test_enterprise_has_no_limit(self):
        prog = self._make(Tier.ENTERPRISE)
        for i in range(30):
            result = prog.add_advocate(f"ent_user_{i}")
            assert result["added"] is True

    def test_list_advocates_returns_added(self):
        prog = self._make(Tier.PRO)
        prog.add_advocate("alice")
        prog.add_advocate("bob")
        advocates = prog.list_advocates()
        assert len(advocates) == 2
        assert advocates[0]["username"] == "alice"

    def test_count_increments(self):
        prog = self._make(Tier.PRO)
        assert prog.count() == 0
        prog.add_advocate("dave")
        assert prog.count() == 1

    def test_list_advocates_empty_initially(self):
        prog = self._make(Tier.PRO)
        assert prog.list_advocates() == []


# ===========================================================================
# 3. PoliciesGuardrails tests
# ===========================================================================

class TestPoliciesGuardrails:
    def _make(self, tier: Tier) -> PoliciesGuardrails:
        return PoliciesGuardrails(get_tier_config(tier))

    def test_free_has_5_policies(self):
        pg = self._make(Tier.FREE)
        policies = pg.get_policies()
        assert len(policies) == 5

    def test_pro_has_10_policies(self):
        pg = self._make(Tier.PRO)
        policies = pg.get_policies()
        assert len(policies) == 10

    def test_enterprise_has_10_policies(self):
        pg = self._make(Tier.ENTERPRISE)
        assert pg.count() == 10

    def test_filter_by_category(self):
        pg = self._make(Tier.PRO)
        security = pg.get_policies(category="security")
        assert len(security) >= 1
        assert all(p["category"] == "security" for p in security)

    def test_get_policy_by_id(self):
        pg = self._make(Tier.PRO)
        policy = pg.get_policy("acceptable_use")
        assert policy is not None
        assert policy["id"] == "acceptable_use"
        assert "name" in policy
        assert "path" in policy

    def test_get_policy_unknown_id_returns_none(self):
        pg = self._make(Tier.PRO)
        assert pg.get_policy("does_not_exist") is None

    def test_all_policies_have_required_keys(self):
        pg = self._make(Tier.PRO)
        for p in pg.get_policies():
            assert "id" in p
            assert "name" in p
            assert "path" in p
            assert "category" in p
            assert "status" in p

    def test_policies_are_active(self):
        pg = self._make(Tier.PRO)
        for p in pg.get_policies():
            assert p["status"] == "active"


# ===========================================================================
# 4. LearningDevelopment tests
# ===========================================================================

class TestLearningDevelopment:
    def _make(self, tier: Tier) -> LearningDevelopment:
        return LearningDevelopment(get_tier_config(tier))

    def test_free_has_beginner_resources_only(self):
        ld = self._make(Tier.FREE)
        resources = ld.get_resources()
        assert len(resources) >= 1
        assert all(r["level"] == "beginner" for r in resources)

    def test_pro_has_all_8_resources(self):
        ld = self._make(Tier.PRO)
        assert ld.count() == 8

    def test_enterprise_has_all_8_resources(self):
        ld = self._make(Tier.ENTERPRISE)
        assert ld.count() == 8

    def test_filter_by_level_beginner(self):
        ld = self._make(Tier.PRO)
        beginners = ld.get_resources(level="beginner")
        assert len(beginners) >= 1
        assert all(r["level"] == "beginner" for r in beginners)

    def test_filter_by_level_advanced(self):
        ld = self._make(Tier.PRO)
        advanced = ld.get_resources(level="advanced")
        assert len(advanced) >= 1
        assert all(r["level"] == "advanced" for r in advanced)

    def test_get_resource_by_id(self):
        ld = self._make(Tier.PRO)
        resource = ld.get_resource("beginner_path")
        assert resource is not None
        assert resource["id"] == "beginner_path"
        assert "path" in resource
        assert "estimated_minutes" in resource

    def test_get_resource_unknown_returns_none(self):
        ld = self._make(Tier.PRO)
        assert ld.get_resource("does_not_exist") is None

    def test_all_resources_have_required_keys(self):
        ld = self._make(Tier.PRO)
        for r in ld.get_resources():
            assert "id" in r
            assert "name" in r
            assert "path" in r
            assert "level" in r
            assert "estimated_minutes" in r


# ===========================================================================
# 5. DataMetrics tests
# ===========================================================================

class TestDataMetrics:
    def _make(self, tier: Tier) -> DataMetrics:
        return DataMetrics(get_tier_config(tier))

    def test_record_mau_blocked_on_free(self):
        dm = self._make(Tier.FREE)
        result = dm.record_mau(50)
        assert result["recorded"] is False
        assert "PRO" in result["reason"] or "pro" in result["reason"].lower()

    def test_record_mau_success_on_pro(self):
        dm = self._make(Tier.PRO)
        result = dm.record_mau(42, "2025-01")
        assert result["recorded"] is True
        assert result["entry"]["mau"] == 42
        assert result["entry"]["period"] == "2025-01"

    def test_record_mau_auto_period(self):
        dm = self._make(Tier.PRO)
        result = dm.record_mau(10)
        assert result["recorded"] is True
        assert result["entry"]["period"] != ""

    def test_record_mau_negative_rejected(self):
        dm = self._make(Tier.PRO)
        result = dm.record_mau(-5)
        assert result["recorded"] is False

    def test_current_mau_returns_latest(self):
        dm = self._make(Tier.PRO)
        dm.record_mau(10, "2025-01")
        dm.record_mau(20, "2025-02")
        assert dm.current_mau() == 20

    def test_current_mau_none_when_empty(self):
        dm = self._make(Tier.PRO)
        assert dm.current_mau() is None

    def test_mau_history_accumulates(self):
        dm = self._make(Tier.PRO)
        dm.record_mau(10)
        dm.record_mau(20)
        assert len(dm.get_mau_history()) == 2

    def test_segmentation_blocked_on_free(self):
        dm = self._make(Tier.FREE)
        result = dm.add_segment("enterprise", 5)
        assert result["added"] is False

    def test_segmentation_success_on_pro(self):
        dm = self._make(Tier.PRO)
        result = dm.add_segment("enterprise", 15)
        assert result["added"] is True
        assert dm.get_segments()["enterprise"] == 15

    def test_segmentation_updates_existing(self):
        dm = self._make(Tier.PRO)
        dm.add_segment("pro", 10)
        dm.add_segment("pro", 20)
        assert dm.get_segments()["pro"] == 20

    def test_maturity_blocked_on_free(self):
        dm = self._make(Tier.FREE)
        result = dm.get_maturity_assessment(3, 5, True)
        assert result["assessed"] is False

    def test_maturity_level_4_on_pro(self):
        dm = self._make(Tier.PRO)
        result = dm.get_maturity_assessment(
            active_workflows=5, advocates=5, metrics_tracked=True
        )
        assert result["assessed"] is True
        assert result["maturity"]["level"] == 4

    def test_maturity_level_3(self):
        dm = self._make(Tier.PRO)
        result = dm.get_maturity_assessment(
            active_workflows=2, advocates=0, metrics_tracked=True
        )
        assert result["assessed"] is True
        assert result["maturity"]["level"] == 3

    def test_maturity_level_2(self):
        dm = self._make(Tier.PRO)
        result = dm.get_maturity_assessment(
            active_workflows=2, advocates=0, metrics_tracked=False
        )
        assert result["assessed"] is True
        assert result["maturity"]["level"] == 2

    def test_maturity_level_1(self):
        dm = self._make(Tier.PRO)
        result = dm.get_maturity_assessment(
            active_workflows=0, advocates=0, metrics_tracked=False
        )
        assert result["assessed"] is True
        assert result["maturity"]["level"] == 1


# ===========================================================================
# 6. CommunityOfPractice tests
# ===========================================================================

class TestCommunityOfPractice:
    def _make(self, tier: Tier) -> CommunityOfPractice:
        return CommunityOfPractice(get_tier_config(tier))

    def test_has_7_communities(self):
        cop = self._make(Tier.FREE)
        assert cop.count() == 7

    def test_get_communities_returns_all(self):
        cop = self._make(Tier.FREE)
        communities = cop.get_communities()
        assert len(communities) == 7

    def test_filter_by_domain(self):
        cop = self._make(Tier.FREE)
        automation = cop.get_communities(domain="automation")
        assert len(automation) == 1
        assert automation[0]["channel"] == "#dreamco-automation"

    def test_communities_have_required_keys(self):
        cop = self._make(Tier.FREE)
        for c in cop.get_communities():
            assert "id" in c
            assert "channel" in c
            assert "domain" in c
            assert "members" in c

    def test_add_member_success(self):
        cop = self._make(Tier.FREE)
        result = cop.add_member("general_ai")
        assert result["added"] is True
        assert result["community"]["members"] == 1

    def test_add_member_increments(self):
        cop = self._make(Tier.FREE)
        cop.add_member("dev_bots")
        cop.add_member("dev_bots")
        result = cop.add_member("dev_bots")
        assert result["community"]["members"] == 3

    def test_add_member_invalid_community(self):
        cop = self._make(Tier.FREE)
        result = cop.add_member("does_not_exist")
        assert result["added"] is False

    def test_total_members_across_communities(self):
        cop = self._make(Tier.FREE)
        cop.add_member("general_ai")
        cop.add_member("dev_bots")
        assert cop.total_members() == 2

    def test_initial_members_zero(self):
        cop = self._make(Tier.FREE)
        assert cop.total_members() == 0


# ===========================================================================
# 7. BotTierClassifier tests
# ===========================================================================

class TestBotTierClassifier:
    def _make(self, tier: Tier) -> BotTierClassifier:
        return BotTierClassifier(get_tier_config(tier))

    def test_classify_blocked_on_free(self):
        bc = self._make(Tier.FREE)
        result = bc.classify(["analytics"])
        assert result["classified"] is False
        assert "ENTERPRISE" in result["reason"] or "enterprise" in result["reason"].lower()

    def test_classify_blocked_on_pro(self):
        bc = self._make(Tier.PRO)
        result = bc.classify(["analytics"])
        assert result["classified"] is False

    def test_classify_enterprise_tier(self):
        bc = self._make(Tier.ENTERPRISE)
        result = bc.classify(["governance_api", "white_label", "analytics"])
        assert result["classified"] is True
        assert result["recommended_tier"] == "enterprise"

    def test_classify_pro_tier(self):
        bc = self._make(Tier.ENTERPRISE)
        result = bc.classify(["analytics", "slack_notify"])
        assert result["classified"] is True
        assert result["recommended_tier"] == "pro"

    def test_classify_free_tier(self):
        bc = self._make(Tier.ENTERPRISE)
        result = bc.classify(["basic_tracking", "community"])
        assert result["classified"] is True
        assert result["recommended_tier"] == "free"

    def test_classify_includes_signals(self):
        bc = self._make(Tier.ENTERPRISE)
        result = bc.classify(["analytics", "dedicated_support"])
        assert result["classified"] is True
        assert len(result["detected_signals"]) >= 1

    def test_classify_feature_count(self):
        bc = self._make(Tier.ENTERPRISE)
        features = ["analytics", "slack_notify", "export_csv"]
        result = bc.classify(features)
        assert result["feature_count"] == 3

    def test_classify_empty_features(self):
        bc = self._make(Tier.ENTERPRISE)
        result = bc.classify([])
        assert result["classified"] is True
        assert result["recommended_tier"] == "free"


# ===========================================================================
# 8. RetrainingOptimizer tests
# ===========================================================================

class TestRetrainingOptimizer:
    def _make(self, tier: Tier, threshold: float = 5.0) -> RetrainingOptimizer:
        return RetrainingOptimizer(get_tier_config(tier), threshold)

    def test_evaluate_blocked_on_free(self):
        ro = self._make(Tier.FREE)
        result = ro.evaluate(0.95, 0.90)
        assert result["evaluated"] is False

    def test_evaluate_blocked_on_pro(self):
        ro = self._make(Tier.PRO)
        result = ro.evaluate(0.95, 0.90)
        assert result["evaluated"] is False

    def test_no_drift_no_retrain(self):
        ro = self._make(Tier.ENTERPRISE)
        result = ro.evaluate(0.95, 0.94)
        assert result["evaluated"] is True
        assert result["needs_retraining"] is False
        assert result["recommended_method"] is None

    def test_moderate_drift_transfer_learning(self):
        # 7% drift — exceeds 5% threshold, under 10%
        ro = self._make(Tier.ENTERPRISE)
        result = ro.evaluate(1.0, 0.93)
        assert result["needs_retraining"] is True
        assert result["recommended_method"] == "transfer_learning"

    def test_significant_drift_fine_tuning(self):
        # 15% drift
        ro = self._make(Tier.ENTERPRISE)
        result = ro.evaluate(1.0, 0.85)
        assert result["needs_retraining"] is True
        assert result["recommended_method"] == "fine_tuning"

    def test_large_drift_full_retrain(self):
        # 25% drift
        ro = self._make(Tier.ENTERPRISE)
        result = ro.evaluate(1.0, 0.75)
        assert result["needs_retraining"] is True
        assert result["recommended_method"] == "full_retrain"

    def test_custom_threshold(self):
        ro = self._make(Tier.ENTERPRISE, threshold=15.0)
        # 10% drift — below custom 15% threshold
        result = ro.evaluate(1.0, 0.90)
        assert result["needs_retraining"] is False

    def test_invalid_baseline_rejected(self):
        ro = self._make(Tier.ENTERPRISE)
        result = ro.evaluate(0.0, 0.9)
        assert result["evaluated"] is False

    def test_negative_current_rejected(self):
        ro = self._make(Tier.ENTERPRISE)
        result = ro.evaluate(0.9, -0.1)
        assert result["evaluated"] is False

    def test_drift_pct_in_result(self):
        ro = self._make(Tier.ENTERPRISE)
        result = ro.evaluate(0.95, 0.82)
        assert "drift_pct" in result
        assert result["drift_pct"] > 0

    def test_threshold_in_result(self):
        ro = self._make(Tier.ENTERPRISE)
        result = ro.evaluate(0.95, 0.94)
        assert result["threshold_pct"] == 5.0


# ===========================================================================
# 9. AIEnablementHub orchestrator tests
# ===========================================================================

class TestAIEnablementHub:
    def test_init_free_tier(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        assert hub.tier == Tier.FREE

    def test_init_pro_tier(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        assert hub.tier == Tier.PRO

    def test_init_enterprise_tier(self):
        hub = AIEnablementHub(tier=Tier.ENTERPRISE)
        assert hub.tier == Tier.ENTERPRISE

    def test_default_tier_is_free(self):
        hub = AIEnablementHub()
        assert hub.tier == Tier.FREE

    def test_add_advocate_delegates(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        result = hub.add_advocate("alice")
        assert result["added"] is True

    def test_add_advocate_free_gated(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        result = hub.add_advocate("alice")
        assert result["added"] is False

    def test_get_policies_returns_list(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        policies = hub.get_policies()
        assert isinstance(policies, list)
        assert len(policies) == 5

    def test_get_policies_pro_returns_all(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        assert len(hub.get_policies()) == 10

    def test_get_policies_category_filter(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        security = hub.get_policies(category="security")
        assert all(p["category"] == "security" for p in security)

    def test_get_learning_resources_free(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        resources = hub.get_learning_resources()
        assert len(resources) >= 1

    def test_get_learning_resources_pro_all(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        assert len(hub.get_learning_resources()) == 8

    def test_get_learning_resources_level_filter(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        advanced = hub.get_learning_resources(level="advanced")
        assert all(r["level"] == "advanced" for r in advanced)

    def test_record_mau_pro(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        result = hub.record_mau(100)
        assert result["recorded"] is True

    def test_record_mau_free_gated(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        result = hub.record_mau(100)
        assert result["recorded"] is False

    def test_get_communities_free(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        communities = hub.get_communities()
        assert len(communities) == 7

    def test_get_communities_domain_filter(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        revenue = hub.get_communities(domain="revenue")
        assert len(revenue) == 1

    def test_classify_bot_enterprise(self):
        hub = AIEnablementHub(tier=Tier.ENTERPRISE)
        result = hub.classify_bot(["analytics", "governance_api"])
        assert result["classified"] is True

    def test_classify_bot_pro_gated(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        result = hub.classify_bot(["analytics"])
        assert result["classified"] is False

    def test_evaluate_retraining_enterprise(self):
        hub = AIEnablementHub(tier=Tier.ENTERPRISE)
        result = hub.evaluate_retraining(0.95, 0.80)
        assert result["evaluated"] is True

    def test_evaluate_retraining_free_gated(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        result = hub.evaluate_retraining(0.95, 0.80)
        assert result["evaluated"] is False

    def test_get_summary_has_all_keys(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        summary = hub.get_summary()
        assert "tier" in summary
        assert "advocates" in summary
        assert "policies" in summary
        assert "learning_resources" in summary
        assert "metrics" in summary
        assert "community" in summary
        assert "enterprise_features" in summary

    def test_get_summary_tier_matches(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        assert hub.get_summary()["tier"] == "pro"

    def test_get_summary_enterprise_features_available(self):
        hub = AIEnablementHub(tier=Tier.ENTERPRISE)
        summary = hub.get_summary()
        assert summary["enterprise_features"]["bot_classifier_available"] is True
        assert summary["enterprise_features"]["retraining_optimizer_available"] is True

    def test_get_summary_enterprise_features_unavailable_on_free(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        summary = hub.get_summary()
        assert summary["enterprise_features"]["bot_classifier_available"] is False
        assert summary["enterprise_features"]["retraining_optimizer_available"] is False

    def test_describe_tier_contains_name(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        description = hub.describe_tier()
        assert "Pro" in description
        assert "49" in description

    def test_describe_tier_shows_upgrade(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        description = hub.describe_tier()
        assert "Pro" in description

    def test_describe_tier_no_upgrade_on_enterprise(self):
        hub = AIEnablementHub(tier=Tier.ENTERPRISE)
        description = hub.describe_tier()
        assert "Upgrade" not in description

    def test_process_returns_summary(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        result = hub.process()
        assert isinstance(result, dict)
        assert "tier" in result

    def test_process_with_payload(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        result = hub.process({"key": "value"})
        assert isinstance(result, dict)

    def test_summary_reflects_added_advocates(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        hub.add_advocate("alice")
        hub.add_advocate("bob")
        summary = hub.get_summary()
        assert summary["advocates"]["count"] == 2

    def test_summary_reflects_mau(self):
        hub = AIEnablementHub(tier=Tier.PRO)
        hub.record_mau(77)
        summary = hub.get_summary()
        assert summary["metrics"]["current_mau"] == 77

    def test_summary_community_count(self):
        hub = AIEnablementHub(tier=Tier.FREE)
        summary = hub.get_summary()
        assert summary["community"]["channels"] == 7

    def test_subsystems_are_accessible(self):
        hub = AIEnablementHub(tier=Tier.ENTERPRISE)
        assert hasattr(hub, "advocates")
        assert hasattr(hub, "policies")
        assert hasattr(hub, "learning")
        assert hasattr(hub, "metrics")
        assert hasattr(hub, "community")
        assert hasattr(hub, "bot_classifier")
        assert hasattr(hub, "retraining")


# ===========================================================================
# 10. Bot Library registration test
# ===========================================================================

class TestBotLibraryRegistration:
    def test_ai_enablement_hub_in_library(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        ids = [e["bot_id"] for e in lib.list_bots()]
        assert "ai_enablement_hub" in ids

    def test_ai_enablement_hub_entry_fields(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("ai_enablement_hub")
        assert entry.display_name != ""
        assert entry.description != ""
        assert entry.module_path == "bots.ai_enablement_hub.ai_enablement_hub"
        assert entry.class_name == "AIEnablementHub"
        assert "ai_enablement" in entry.capabilities or "policies" in entry.capabilities
