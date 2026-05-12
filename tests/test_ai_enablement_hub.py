"""
Tests for bots/ai_enablement_hub/ and framework/retraining_optimizer.py

Covers all five pillars, BotTierClassifier, RetrainingOptimizer, and the
AIEnablementHub tier-gate logic.
"""

from __future__ import annotations

import sys
import os
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bots.ai_enablement_hub.tiers import (
    Tier,
    BOT_FEATURES,
    FEATURE_ADVOCATES_PROGRAM,
    FEATURE_POLICIES_GUARDRAILS,
    FEATURE_LEARNING_DEVELOPMENT,
    FEATURE_DATA_METRICS,
    FEATURE_COMMUNITY_PRACTICE,
    FEATURE_BOT_TIER_CLASSIFIER,
    FEATURE_RETRAINING_OPTIMIZER,
    FEATURE_ADVANCED_SEGMENTATION,
    FEATURE_CUSTOM_POLICIES,
    get_bot_tier_info,
)
from bots.ai_enablement_hub.advocates import AdvocatesProgram, VALID_CHANNELS, VALID_OUTCOMES
from bots.ai_enablement_hub.policies import PoliciesGuardrails, _DEFAULT_POLICIES
from bots.ai_enablement_hub.learning import LearningDevelopment, _DEFAULT_RESOURCES
from bots.ai_enablement_hub.metrics import DataMetrics, AdoptionMaturity
from bots.ai_enablement_hub.community import CommunityOfPractice
from bots.ai_enablement_hub.bot_tier_classifier import BotTierClassifier, ScalabilityTier
from bots.ai_enablement_hub.ai_enablement_hub import (
    AIEnablementHub,
    AIEnablementTierError,
)
from framework.retraining_optimizer import (
    RetrainingOptimizer,
    DEFAULT_DRIFT_THRESHOLD,
    _select_retraining_method,
)


# ===========================================================================
# Tiers
# ===========================================================================

class TestTiers:
    def test_free_has_advocates_and_metrics(self):
        assert FEATURE_ADVOCATES_PROGRAM in BOT_FEATURES[Tier.FREE.value]
        assert FEATURE_DATA_METRICS in BOT_FEATURES[Tier.FREE.value]

    def test_pro_has_all_five_pillars(self):
        pro = BOT_FEATURES[Tier.PRO.value]
        for feat in [
            FEATURE_ADVOCATES_PROGRAM, FEATURE_POLICIES_GUARDRAILS,
            FEATURE_LEARNING_DEVELOPMENT, FEATURE_DATA_METRICS,
            FEATURE_COMMUNITY_PRACTICE, FEATURE_BOT_TIER_CLASSIFIER,
        ]:
            assert feat in pro

    def test_enterprise_has_retraining_optimizer(self):
        assert FEATURE_RETRAINING_OPTIMIZER in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_has_custom_policies(self):
        assert FEATURE_CUSTOM_POLICIES in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_get_bot_tier_info_returns_dict(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert "features" in info
        assert info["price_usd_monthly"] == 49.0


# ===========================================================================
# Pillar 1 — Advocates Program
# ===========================================================================

class TestAdvocatesProgram:
    def setup_method(self):
        self.prog = AdvocatesProgram()

    def test_enroll_advocate(self):
        adv = self.prog.enroll_advocate("Alice", "alice@example.com", ["nlp", "bots"])
        assert adv.name == "Alice"
        assert adv.advocate_id.startswith("adv-")
        assert adv.influence_score == 0.0

    def test_get_advocate(self):
        adv = self.prog.enroll_advocate("Bob", "bob@example.com")
        fetched = self.prog.get_advocate(adv.advocate_id)
        assert fetched.advocate_id == adv.advocate_id

    def test_get_advocate_not_found(self):
        with pytest.raises(KeyError):
            self.prog.get_advocate("adv-nonexistent")

    def test_record_influence_adopted_updates_score(self):
        adv = self.prog.enroll_advocate("Carol", "carol@example.com")
        event = self.prog.record_influence(adv.advocate_id, "user1", "slack", "adopted")
        assert event.outcome == "adopted"
        updated = self.prog.get_advocate(adv.advocate_id)
        assert updated.influence_score == 2.0
        assert updated.peers_influenced == 1

    def test_record_influence_all_outcomes(self):
        adv = self.prog.enroll_advocate("Dan", "dan@example.com")
        for outcome in VALID_OUTCOMES:
            self.prog.record_influence(adv.advocate_id, f"u-{outcome}", "mentorship", outcome)
        assert self.prog.get_advocate(adv.advocate_id).peers_influenced == len(VALID_OUTCOMES)

    def test_record_influence_invalid_channel(self):
        adv = self.prog.enroll_advocate("Eve", "eve@example.com")
        with pytest.raises(ValueError, match="Invalid channel"):
            self.prog.record_influence(adv.advocate_id, "user2", "telegram", "adopted")

    def test_record_influence_invalid_outcome(self):
        adv = self.prog.enroll_advocate("Frank", "frank@example.com")
        with pytest.raises(ValueError, match="Invalid outcome"):
            self.prog.record_influence(adv.advocate_id, "user3", "slack", "unknown")

    def test_network_summary_adoption_rate(self):
        adv = self.prog.enroll_advocate("Grace", "grace@example.com")
        self.prog.record_influence(adv.advocate_id, "u1", "slack", "adopted")
        self.prog.record_influence(adv.advocate_id, "u2", "slack", "declined")
        summary = self.prog.network_summary()
        assert summary["total_adopted"] == 1
        assert summary["adoption_rate"] == 0.5

    def test_list_advocates_sorted_by_score(self):
        a1 = self.prog.enroll_advocate("H1", "h1@x.com")
        a2 = self.prog.enroll_advocate("H2", "h2@x.com")
        self.prog.record_influence(a1.advocate_id, "u", "slack", "adopted")
        self.prog.record_influence(a1.advocate_id, "u2", "slack", "adopted")
        advocates = self.prog.list_advocates()
        assert advocates[0]["advocate_id"] == a1.advocate_id

    def test_get_influence_events_filtered(self):
        a1 = self.prog.enroll_advocate("I1", "i1@x.com")
        a2 = self.prog.enroll_advocate("I2", "i2@x.com")
        self.prog.record_influence(a1.advocate_id, "u", "slack", "adopted")
        self.prog.record_influence(a2.advocate_id, "v", "discord", "interested")
        events = self.prog.get_influence_events(advocate_id=a1.advocate_id)
        assert len(events) == 1
        assert events[0]["advocate_id"] == a1.advocate_id


# ===========================================================================
# Pillar 2 — Policies & Guardrails
# ===========================================================================

class TestPoliciesGuardrails:
    def setup_method(self):
        self.pg = PoliciesGuardrails(allow_custom=True)

    def test_default_policies_loaded(self):
        policies = self.pg.list_policies()
        assert len(policies) == len(_DEFAULT_POLICIES)

    def test_get_policy(self):
        p = self.pg.get_policy("pol-001")
        assert p.name == "Vetted AI Tool Registry"

    def test_get_policy_not_found(self):
        with pytest.raises(KeyError):
            self.pg.get_policy("pol-999")

    def test_enable_disable_policy(self):
        self.pg.disable_policy("pol-010")
        assert not self.pg.get_policy("pol-010").enabled
        self.pg.enable_policy("pol-010")
        assert self.pg.get_policy("pol-010").enabled

    def test_add_custom_policy(self):
        p = self.pg.add_custom_policy(
            "Custom Bot Safety", "Do not allow bots to send unsolicited messages.",
            "ethics", "high"
        )
        assert p.is_custom is True
        assert p.policy_id.startswith("custom-")

    def test_add_custom_policy_invalid_category(self):
        with pytest.raises(ValueError, match="Invalid category"):
            self.pg.add_custom_policy("X", "Y", "invalid_cat", "high")

    def test_add_custom_policy_invalid_severity(self):
        with pytest.raises(ValueError, match="Invalid severity"):
            self.pg.add_custom_policy("X", "Y", "ethics", "ultra")

    def test_custom_policy_denied_on_free(self):
        pg_free = PoliciesGuardrails(allow_custom=False)
        with pytest.raises(PermissionError):
            pg_free.add_custom_policy("X", "Y", "security", "low")

    def test_record_and_resolve_violation(self):
        v = self.pg.record_violation("pol-001", "bot_xyz", "Used unapproved tool.")
        assert v.violation_id.startswith("vio-")
        assert v.resolved is False
        self.pg.resolve_violation(v.violation_id)
        violations = self.pg.list_violations(resolved=True)
        assert any(v2["violation_id"] == v.violation_id for v2 in violations)

    def test_resolve_violation_not_found(self):
        with pytest.raises(KeyError):
            self.pg.resolve_violation("vio-nonexistent")

    def test_compliance_score_perfect_no_violations(self):
        pg = PoliciesGuardrails()
        assert pg.compliance_score() == 100.0

    def test_compliance_score_drops_on_unresolved_critical_violation(self):
        v = self.pg.record_violation("pol-001", "actor", "critical breach")
        score = self.pg.compliance_score()
        assert score < 100.0

    def test_guardrails_report_structure(self):
        report = self.pg.guardrails_report()
        assert "total_policies" in report
        assert "compliance_score" in report
        assert "unresolved_violations" in report


# ===========================================================================
# Pillar 3 — Learning & Development
# ===========================================================================

class TestLearningDevelopment:
    def setup_method(self):
        self.ld = LearningDevelopment()

    def test_default_resources_loaded(self):
        resources = self.ld.list_resources()
        assert len(resources) == len(_DEFAULT_RESOURCES)

    def test_add_resource(self):
        r = self.ld.add_resource(
            "Advanced Retraining", "Deep dive into retraining cycles.",
            "workshop", "advanced", tags=["retraining"]
        )
        assert r.resource_id.startswith("res-")
        assert r.skill_level == "advanced"

    def test_add_resource_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid resource_type"):
            self.ld.add_resource("X", "Y", "podcast", "beginner")

    def test_add_resource_invalid_skill_level(self):
        with pytest.raises(ValueError, match="Invalid skill_level"):
            self.ld.add_resource("X", "Y", "guide", "expert")

    def test_list_resources_filter_skill(self):
        resources = self.ld.list_resources(skill_level="beginner")
        assert all(r["skill_level"] == "beginner" for r in resources)

    def test_get_resource_not_found(self):
        with pytest.raises(KeyError):
            self.ld.get_resource("res-000000")

    def test_learner_progress_mark_started_completed(self):
        rid = list(self.ld._resources.keys())[0]
        self.ld.mark_started("learner1", rid)
        progress = self.ld.get_learner_progress("learner1")
        assert progress["in_progress_count"] == 1

        self.ld.mark_completed("learner1", rid)
        progress = self.ld.get_learner_progress("learner1")
        assert progress["completed_count"] == 1
        assert progress["in_progress_count"] == 0

    def test_learner_not_enrolled_raises(self):
        with pytest.raises(KeyError):
            self.ld.get_learner_progress("unknown_learner")

    def test_programme_summary(self):
        summary = self.ld.programme_summary()
        assert "total_resources" in summary
        assert summary["total_resources"] == len(_DEFAULT_RESOURCES)


# ===========================================================================
# Pillar 4 — Data Metrics
# ===========================================================================

class TestDataMetrics:
    def setup_method(self):
        self.dm = DataMetrics(advanced_segmentation=True)

    def test_record_event_and_mau(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        self.dm.record_event("u1", "bot_a", "activate", "new_user", 5.0)
        self.dm.record_event("u2", "bot_a", "use", "power_user", 3.0)
        mau = self.dm.mau(now.year, now.month)
        assert mau >= 2

    def test_churn_does_not_count_for_mau(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        self.dm.record_event("u_churn", "bot_a", "churn", "new_user", 0.0)
        mau = self.dm.mau(now.year, now.month)
        assert mau == 0  # churn excluded

    def test_record_event_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid event_type"):
            self.dm.record_event("u1", "b", "click", "new_user")

    def test_record_event_invalid_segment(self):
        with pytest.raises(ValueError, match="Invalid segment"):
            self.dm.record_event("u1", "b", "activate", "vip")

    def test_segment_distribution(self):
        self.dm.record_event("u1", "b", "activate", "new_user", 2.0)
        self.dm.record_event("u2", "b", "use", "power_user", 1.0)
        dist = self.dm.segment_distribution()
        assert dist["new_user"] == 1
        assert dist["power_user"] == 1

    def test_segment_mau_requires_advanced(self):
        dm_basic = DataMetrics(advanced_segmentation=False)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        with pytest.raises(PermissionError):
            dm_basic.segment_mau(now.year, now.month)

    def test_average_cycle_time(self):
        self.dm.record_event("u1", "b", "activate", "new_user", 10.0)
        self.dm.record_event("u2", "b", "activate", "new_user", 20.0)
        avg = self.dm.average_cycle_time()
        assert avg == 15.0

    def test_adoption_maturity_levels(self):
        dm = DataMetrics()
        for _ in range(10):
            dm.register_user(f"user-{_}")
        # zero MAU → Awareness
        maturity = dm.adoption_maturity()
        assert maturity["maturity_level"] == AdoptionMaturity.AWARENESS

    def test_dashboard_structure(self):
        dash = self.dm.dashboard()
        for key in ["total_events", "current_mau", "maturity_label", "avg_cycle_time_days"]:
            assert key in dash

    def test_register_user_increases_total(self):
        dm = DataMetrics()
        dm.register_user("x")
        dm.register_user("y")
        assert dm.total_users() == 2


# ===========================================================================
# Pillar 5 — Communities of Practice
# ===========================================================================

class TestCommunityOfPractice:
    def setup_method(self):
        self.cop = CommunityOfPractice()

    def test_create_community(self):
        c = self.cop.create_community("Revenue Bots CoP", "Scaling revenue bots.", "slack", "revenue_bots")
        assert c.community_id.startswith("cop-")
        assert c.channel_type == "slack"

    def test_create_community_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid channel_type"):
            self.cop.create_community("X", "Y", "twitter", "z")

    def test_join_and_leave(self):
        c = self.cop.create_community("Test CoP", ".", "discord", "ai_governance")
        self.cop.join_community(c.community_id, "user1")
        self.cop.join_community(c.community_id, "user1")  # idempotent
        assert "user1" in self.cop.get_members(c.community_id)
        self.cop.leave_community(c.community_id, "user1")
        assert "user1" not in self.cop.get_members(c.community_id)

    def test_get_community_not_found(self):
        with pytest.raises(KeyError):
            self.cop.get_community("cop-nonexistent")

    def test_post_idea_and_upvote(self):
        c = self.cop.create_community("Scaling CoP", ".", "github_discussion", "scaling")
        post = self.cop.post_idea(c.community_id, "author1", "Scale bot revenue", "Idea body", ["revenue"])
        assert post.post_id.startswith("post-")
        self.cop.upvote_post(post.post_id)
        posts = self.cop.list_posts(community_id=c.community_id)
        assert posts[0]["upvotes"] == 1

    def test_upvote_not_found(self):
        with pytest.raises(KeyError):
            self.cop.upvote_post("post-nonexistent")

    def test_list_posts_sorted_by_upvotes(self):
        c = self.cop.create_community("CoP", ".", "forum", "onboarding")
        p1 = self.cop.post_idea(c.community_id, "a", "Low", "body")
        p2 = self.cop.post_idea(c.community_id, "a", "High", "body")
        self.cop.upvote_post(p2.post_id)
        self.cop.upvote_post(p2.post_id)
        posts = self.cop.list_posts(top_n=1)
        assert posts[0]["post_id"] == p2.post_id

    def test_collaboration_report(self):
        c = self.cop.create_community("X", ".", "slack", "y")
        self.cop.join_community(c.community_id, "u1")
        self.cop.post_idea(c.community_id, "u1", "T", "B")
        report = self.cop.collaboration_report()
        assert report["total_communities"] == 1
        assert report["total_members"] == 1
        assert report["total_posts"] == 1


# ===========================================================================
# BotTierClassifier
# ===========================================================================

class TestBotTierClassifier:
    def setup_method(self):
        self.clf = BotTierClassifier()

    def test_classify_basic(self):
        profile = self.clf.classify(
            bot_id="test_bot",
            subscription_tier="enterprise",
            feature_count=15,
            monthly_active_users=500,
            avg_cycle_time_days=5.0,
            revenue_usd=10000.0,
            has_retraining=True,
            has_governance=True,
        )
        assert profile.bot_id == "test_bot"
        assert profile.composite_score > 0
        assert profile.scalability_tier in ScalabilityTier.ALL

    def test_classify_emerging_for_minimal_bot(self):
        profile = self.clf.classify(
            bot_id="minimal_bot",
            subscription_tier="free",
            feature_count=1,
            monthly_active_users=0,
            avg_cycle_time_days=60.0,
            revenue_usd=0.0,
        )
        assert profile.scalability_tier == ScalabilityTier.EMERGING

    def test_classify_enterprise_grade(self):
        profile = self.clf.classify(
            bot_id="top_bot",
            subscription_tier="enterprise",
            feature_count=20,
            monthly_active_users=10000,
            avg_cycle_time_days=3.0,
            revenue_usd=1_000_000.0,
            has_retraining=True,
            has_governance=True,
        )
        assert profile.scalability_tier == ScalabilityTier.ENTERPRISE_GRADE

    def test_recommendations_for_free_tier(self):
        profile = self.clf.classify(
            "r_bot", "free", 2, 5, 45.0, 0.0
        )
        assert any("PRO" in r for r in profile.recommendations)

    def test_get_profile(self):
        self.clf.classify("p_bot", "pro", 10, 100, 15.0, 5000.0)
        p = self.clf.get_profile("p_bot")
        assert p.bot_id == "p_bot"

    def test_get_profile_not_found(self):
        with pytest.raises(KeyError):
            self.clf.get_profile("ghost_bot")

    def test_list_profiles_filtered(self):
        self.clf.classify("e_bot", "enterprise", 20, 9999, 1.0, 999999.0, True, True)
        self.clf.classify("f_bot", "free", 1, 0, 90.0, 0.0)
        emerging = self.clf.list_profiles(scalability_tier=ScalabilityTier.EMERGING)
        assert all(p["scalability_tier"] == ScalabilityTier.EMERGING for p in emerging)

    def test_score_capped_at_100(self):
        profile = self.clf.classify(
            "max_bot", "enterprise", 100, 1_000_000, 1.0, 10_000_000.0, True, True
        )
        assert profile.composite_score <= 100.0


# ===========================================================================
# RetrainingOptimizer (framework)
# ===========================================================================

class TestRetrainingOptimizer:
    def setup_method(self):
        self.opt = RetrainingOptimizer()

    def test_default_threshold(self):
        assert self.opt.drift_threshold == DEFAULT_DRIFT_THRESHOLD

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError):
            RetrainingOptimizer(drift_threshold=0.0)
        with pytest.raises(ValueError):
            RetrainingOptimizer(drift_threshold=1.5)

    def test_set_and_get_baseline(self):
        self.opt.set_baseline("bot_a", 0.92)
        assert self.opt.get_baseline("bot_a") == 0.92

    def test_baseline_defaults_to_constant(self):
        from framework.retraining_optimizer import DEFAULT_BASELINE_ACCURACY
        assert self.opt.get_baseline("unknown_bot") == DEFAULT_BASELINE_ACCURACY

    def test_evaluate_no_retraining_needed(self):
        self.opt.set_baseline("bot_b", 0.90)
        result = self.opt.evaluate("bot_b", 0.88)  # drift = 0.02 < 0.05
        assert result["requires_retraining"] is False
        assert result["drift"] == pytest.approx(0.02, abs=1e-6)
        assert "job_id" not in result

    def test_evaluate_retraining_triggered(self):
        self.opt.set_baseline("bot_c", 0.90)
        result = self.opt.evaluate("bot_c", 0.80)  # drift = 0.10 >= 0.05
        assert result["requires_retraining"] is True
        assert "job_id" in result

    def test_retraining_method_selection(self):
        assert _select_retraining_method(0.03) == "transfer_learning"
        assert _select_retraining_method(0.08) == "fine_tuning"
        assert _select_retraining_method(0.20) == "full_retrain"

    def test_complete_job(self):
        self.opt.set_baseline("bot_d", 0.90)
        result = self.opt.evaluate("bot_d", 0.80)
        job_id = result["job_id"]
        self.opt.complete_job(job_id)
        jobs = self.opt.list_jobs(bot_id="bot_d", status="completed")
        assert len(jobs) == 1

    def test_complete_job_not_found(self):
        with pytest.raises(KeyError):
            self.opt.complete_job("rtjob-nonexistent")

    def test_list_snapshots(self):
        self.opt.set_baseline("bot_e", 0.85)
        self.opt.evaluate("bot_e", 0.84)
        self.opt.evaluate("bot_e", 0.70)
        snaps = self.opt.list_snapshots(bot_id="bot_e")
        assert len(snaps) == 2

    def test_invalid_accuracy_raises(self):
        with pytest.raises(ValueError):
            self.opt.evaluate("bot_f", -0.1)
        with pytest.raises(ValueError):
            self.opt.evaluate("bot_f", 1.5)

    def test_invalid_baseline_raises(self):
        with pytest.raises(ValueError):
            self.opt.set_baseline("bot_g", 1.1)

    def test_status_summary(self):
        self.opt.set_baseline("bot_h", 0.90)
        self.opt.evaluate("bot_h", 0.80)
        status = self.opt.status()
        assert status["monitored_bots"] == 1
        assert status["total_jobs"] == 1
        assert status["queued_jobs"] == 1


# ===========================================================================
# AIEnablementHub — tier gating
# ===========================================================================

class TestAIEnablementHubFree:
    def setup_method(self):
        self.hub = AIEnablementHub(tier=Tier.FREE)

    def test_repr(self):
        assert "free" in repr(self.hub)

    def test_enroll_advocate_allowed(self):
        adv = self.hub.enroll_advocate("Alice", "alice@x.com")
        assert adv.name == "Alice"

    def test_record_adoption_event_allowed(self):
        evt = self.hub.record_adoption_event("u1", "bot_a", "activate", "new_user", 5.0)
        assert evt.user_id == "u1"

    def test_metrics_dashboard_allowed(self):
        dash = self.hub.metrics_dashboard()
        assert "current_mau" in dash

    def test_policies_blocked_on_free(self):
        with pytest.raises(AIEnablementTierError):
            self.hub.list_policies()

    def test_learning_blocked_on_free(self):
        with pytest.raises(AIEnablementTierError):
            self.hub.list_learning_resources()

    def test_community_blocked_on_free(self):
        with pytest.raises(AIEnablementTierError):
            self.hub.create_community("X", "Y", "slack", "z")

    def test_classifier_blocked_on_free(self):
        with pytest.raises(AIEnablementTierError):
            self.hub.classify_bot("b", "free", 1, 0, 0.0, 0.0)

    def test_retraining_blocked_on_free(self):
        with pytest.raises(AIEnablementTierError):
            self.hub.check_retraining("b", 0.85)

    def test_hub_status_free(self):
        status = self.hub.hub_status()
        assert status["tier"] == "free"
        assert "advocates" in status["pillars"]
        assert "metrics" in status["pillars"]
        assert "policies" not in status["pillars"]


class TestAIEnablementHubPro:
    def setup_method(self):
        self.hub = AIEnablementHub(tier=Tier.PRO)

    def test_list_policies_allowed(self):
        policies = self.hub.list_policies()
        assert len(policies) > 0

    def test_list_learning_resources_allowed(self):
        resources = self.hub.list_learning_resources()
        assert len(resources) > 0

    def test_create_community_allowed(self):
        c = self.hub.create_community("Pro CoP", ".", "slack", "scaling")
        assert c.community_id.startswith("cop-")

    def test_classify_bot_allowed(self):
        profile = self.hub.classify_bot("b1", "pro", 10, 200, 10.0, 5000.0)
        assert profile.bot_id == "b1"

    def test_retraining_blocked_on_pro(self):
        with pytest.raises(AIEnablementTierError):
            self.hub.check_retraining("b", 0.85)

    def test_hub_status_pro(self):
        status = self.hub.hub_status()
        assert "policies" in status["pillars"]
        assert "learning" in status["pillars"]
        assert "community" in status["pillars"]
        assert "retraining_optimizer" not in status


class TestAIEnablementHubEnterprise:
    def setup_method(self):
        self.hub = AIEnablementHub(tier=Tier.ENTERPRISE)

    def test_check_retraining_allowed(self):
        result = self.hub.check_retraining("bot_ent", 0.75)
        assert "requires_retraining" in result

    def test_record_violation_allowed(self):
        v = self.hub.record_violation("pol-001", "actor", "detail")
        assert v.violation_id.startswith("vio-")

    def test_guardrails_report_allowed(self):
        report = self.hub.guardrails_report()
        assert "compliance_score" in report

    def test_hub_status_enterprise_includes_retraining(self):
        status = self.hub.hub_status()
        assert "retraining_optimizer" in status

    def test_full_workflow(self):
        """End-to-end: enroll → classify → record event → check retraining."""
        adv = self.hub.enroll_advocate("CEO", "ceo@dreamco.ai", ["leadership"])
        self.hub.record_influence(adv.advocate_id, "team_member", "workshop", "adopted")
        self.hub.record_adoption_event("ceo", "ai_enablement_hub", "activate", "enterprise", 2.0)
        c = self.hub.create_community("Enterprise CoP", "Flagship community", "slack", "scaling")
        self.hub.post_idea(c.community_id, "ceo", "AI first culture", "Adopt AI everywhere")
        profile = self.hub.classify_bot(
            "ai_enablement_hub", "enterprise", 8, 1000, 2.0, 50000.0,
            has_retraining=True, has_governance=True,
        )
        retraining = self.hub.check_retraining("ai_enablement_hub", 0.72)
        status = self.hub.hub_status()
        assert status["tier"] == "enterprise"
        assert profile.scalability_tier in ScalabilityTier.ALL
        assert "requires_retraining" in retraining


# ===========================================================================
# Bot Library registration
# ===========================================================================

class TestBotLibraryRegistration:
    def test_ai_enablement_hub_registered(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("ai_enablement_hub")
        assert entry.display_name == "AI Enablement Hub"
        assert "ai_advocates_program" in entry.capabilities
        assert "retraining_optimizer" in entry.capabilities


# ===========================================================================
# Framework exports
# ===========================================================================

class TestFrameworkExports:
    def test_retraining_optimizer_exported(self):
        from framework import RetrainingOptimizer as RO
        assert RO is not None

    def test_retraining_optimizer_usable(self):
        from framework import RetrainingOptimizer as RO
        opt = RO(drift_threshold=0.10)
        opt.set_baseline("b", 0.95)
        result = opt.evaluate("b", 0.80)
        assert result["requires_retraining"] is True
