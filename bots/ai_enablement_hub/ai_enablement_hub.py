"""
AI Enablement Hub — DreamCo AI fluency and governance platform.

Central hub for AI policy management, advocate programs, learning paths,
community governance, and data metrics across DreamCo.

Sub-systems
-----------
  • AdvocatesProgram     — manage the DreamCo Advocate Network (FREE: 3, PRO: 25, ENTERPRISE: unlimited)
  • PoliciesGuardrails   — 10 vetted policies covering acceptable use, security, automation rules
  • LearningDevelopment  — 8 curated learning resources with structured paths
  • DataMetrics          — MAU tracking, user segmentation, and AI maturity assessment
  • CommunityOfPractice  — 7 collaboration channels with member tracking
  • BotTierClassifier    — classify bots by tier based on feature analysis (ENTERPRISE only)
  • RetrainingOptimizer  — detect accuracy drift and schedule retraining (ENTERPRISE only)

Tier access
-----------
  FREE:       Core policies (5), basic learning (8 resources), community access.
  PRO:        Full advocate network (25), metrics dashboards, advanced learning,
              maturity assessment, user segmentation.
  ENTERPRISE: All PRO + BotTierClassifier, RetrainingOptimizer, governance APIs,
              dedicated support.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.ai_enablement_hub import AIEnablementHub, Tier

    hub = AIEnablementHub(tier=Tier.PRO)
    hub.add_advocate("alice", "Core Advocate", "automation")
    hub.record_mau(42)
    print(hub.get_summary())
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)
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
)

# ---------------------------------------------------------------------------
# Vetted policy catalogue (10 policies)
# ---------------------------------------------------------------------------

_POLICIES: List[Dict[str, str]] = [
    {
        "id": "acceptable_use",
        "name": "Acceptable Use Policy",
        "path": "DreamCo_AI_For_Everyone/Policies/acceptable_use.md",
        "category": "governance",
        "status": "active",
    },
    {
        "id": "approved_tools",
        "name": "Approved Tools Policy",
        "path": "DreamCo_AI_For_Everyone/Policies/approved_tools.md",
        "category": "tooling",
        "status": "active",
    },
    {
        "id": "data_security",
        "name": "Data Security Policy",
        "path": "DreamCo_AI_For_Everyone/Policies/data_security.md",
        "category": "security",
        "status": "active",
    },
    {
        "id": "automation_rules",
        "name": "Automation Rules",
        "path": "DreamCo_AI_For_Everyone/Policies/automation_rules.md",
        "category": "automation",
        "status": "active",
    },
    {
        "id": "prompt_guidelines",
        "name": "Prompt Engineering Guidelines",
        "path": "DreamCo_AI_For_Everyone/Policies/prompt_guidelines.md",
        "category": "ai_usage",
        "status": "active",
    },
    {
        "id": "tier1_tooling",
        "name": "Tier 1 Approved Tools",
        "path": "DreamCo_AI_For_Everyone/Tooling/tier1_approved.md",
        "category": "tooling",
        "status": "active",
    },
    {
        "id": "tier2_tooling",
        "name": "Tier 2 Public Tools",
        "path": "DreamCo_AI_For_Everyone/Tooling/tier2_public_tools.md",
        "category": "tooling",
        "status": "active",
    },
    {
        "id": "leadership_governance",
        "name": "Leadership Governance",
        "path": "governance/leadership_roles.md",
        "category": "governance",
        "status": "active",
    },
    {
        "id": "communities_of_practice",
        "name": "Communities of Practice",
        "path": "DreamCo_AI_For_Everyone/Communities/communities_of_practice.md",
        "category": "community",
        "status": "active",
    },
    {
        "id": "onboarding_security",
        "name": "Security Setup & Onboarding",
        "path": "DreamCo_AI_For_Everyone/Onboarding/security_setup.md",
        "category": "security",
        "status": "active",
    },
]

# ---------------------------------------------------------------------------
# Learning resources catalogue (8 resources)
# ---------------------------------------------------------------------------

_LEARNING_RESOURCES: List[Dict[str, str]] = [
    {
        "id": "beginner_path",
        "name": "Beginner Learning Path",
        "path": "DreamCo_AI_For_Everyone/Learning/beginner_path.md",
        "level": "beginner",
        "estimated_minutes": "30",
    },
    {
        "id": "advanced_path",
        "name": "Advanced Learning Path",
        "path": "DreamCo_AI_For_Everyone/Learning/advanced_path.md",
        "level": "advanced",
        "estimated_minutes": "120",
    },
    {
        "id": "prompt_engineering",
        "name": "Prompt Engineering Mastery",
        "path": "DreamCo_AI_For_Everyone/Learning/prompt_engineering.md",
        "level": "intermediate",
        "estimated_minutes": "60",
    },
    {
        "id": "automation_mastery",
        "name": "Automation Mastery Guide",
        "path": "DreamCo_AI_For_Everyone/Learning/automation_mastery.md",
        "level": "intermediate",
        "estimated_minutes": "90",
    },
    {
        "id": "advocate_training",
        "name": "Advocate Training Guide",
        "path": "DreamCo_AI_For_Everyone/Advocates/advocate_training.md",
        "level": "intermediate",
        "estimated_minutes": "125",
    },
    {
        "id": "new_user_setup",
        "name": "New User Setup Guide",
        "path": "DreamCo_AI_For_Everyone/Onboarding/new_user_setup.md",
        "level": "beginner",
        "estimated_minutes": "30",
    },
    {
        "id": "first_bot_launch",
        "name": "First Bot Launch Guide",
        "path": "DreamCo_AI_For_Everyone/Onboarding/first_bot_launch.md",
        "level": "beginner",
        "estimated_minutes": "20",
    },
    {
        "id": "dreamco_installation",
        "name": "DreamCo Installation Guide",
        "path": "DreamCo_AI_For_Everyone/Onboarding/dreamco_installation.md",
        "level": "beginner",
        "estimated_minutes": "15",
    },
]

# ---------------------------------------------------------------------------
# Communities catalogue (7 communities)
# ---------------------------------------------------------------------------

_COMMUNITIES: List[Dict[str, Any]] = [
    {"id": "general_ai", "channel": "#dreamco-general-ai", "domain": "general", "members": 0},
    {"id": "dev_bots", "channel": "#dreamco-dev-bots", "domain": "engineering", "members": 0},
    {"id": "money_systems", "channel": "#dreamco-money-systems", "domain": "revenue", "members": 0},
    {"id": "real_estate_ai", "channel": "#dreamco-real-estate-ai", "domain": "real_estate", "members": 0},
    {"id": "trading_ai", "channel": "#dreamco-trading-ai", "domain": "trading", "members": 0},
    {"id": "growth_hacks", "channel": "#dreamco-growth-hacks", "domain": "marketing", "members": 0},
    {"id": "automation", "channel": "#dreamco-automation", "domain": "automation", "members": 0},
]

# ---------------------------------------------------------------------------
# Maturity levels
# ---------------------------------------------------------------------------

_MATURITY_LEVELS = [
    {"level": 1, "name": "Aware", "description": "Know AI tools exist; ran 1 bot manually"},
    {"level": 2, "name": "Experimenting", "description": "Regular manual bot use; 2+ active workflows"},
    {"level": 3, "name": "Integrating", "description": "Bots in daily workflows; scheduling; metrics tracked"},
    {"level": 4, "name": "Optimizing", "description": "Cross-system orchestration; revenue tracked; advocates active"},
    {"level": 5, "name": "Leading", "description": "Full AI operating system; all 4 phases complete; contributing back"},
]


# ===========================================================================
# Sub-systems
# ===========================================================================

class AdvocatesProgram:
    """Manage the DreamCo Advocate Network."""

    def __init__(self, config: TierConfig) -> None:
        self._config = config
        self._advocates: List[Dict[str, Any]] = []

    def add_advocate(
        self,
        username: str,
        role: str = "Starter Advocate",
        domain: str = "general",
    ) -> Dict[str, Any]:
        """Add a new advocate.  Returns the advocate record or a tier-gate error."""
        limit = self._config.max_advocates
        if not self._config.has_feature(FEATURE_ADVOCATES):
            return {
                "added": False,
                "reason": f"Advocates feature requires PRO tier or above. "
                          f"Current tier: {self._config.tier.value}",
                "upgrade_to": "pro",
            }
        if limit is not None and len(self._advocates) >= limit:
            return {
                "added": False,
                "reason": f"Advocate limit reached ({limit}). Upgrade to unlock more.",
                "upgrade_to": "enterprise",
            }
        record: Dict[str, Any] = {
            "username": username,
            "role": role,
            "domain": domain,
            "added_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        self._advocates.append(record)
        return {"added": True, "advocate": record}

    def list_advocates(self) -> List[Dict[str, Any]]:
        return list(self._advocates)

    def count(self) -> int:
        return len(self._advocates)


class PoliciesGuardrails:
    """Provide access to the 10 vetted DreamCo AI policies."""

    def __init__(self, config: TierConfig) -> None:
        self._config = config
        # FREE tier: first 5 policies; higher tiers: all 10
        limit = None if config.has_feature(FEATURE_ADVOCATES) else 5
        self._policies = _POLICIES[:limit] if limit else _POLICIES

    def get_policies(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """Return all policies, optionally filtered by category."""
        if not self._config.has_feature(FEATURE_POLICIES):
            return []
        if category:
            return [p for p in self._policies if p["category"] == category]
        return list(self._policies)

    def count(self) -> int:
        return len(self._policies)

    def get_policy(self, policy_id: str) -> Optional[Dict[str, str]]:
        for p in self._policies:
            if p["id"] == policy_id:
                return p
        return None


class LearningDevelopment:
    """Manage structured learning resources (8 available)."""

    def __init__(self, config: TierConfig) -> None:
        self._config = config
        # FREE: beginner resources; PRO+: all
        if config.has_feature(FEATURE_ADVANCED_LEARNING):
            self._resources = _LEARNING_RESOURCES
        else:
            self._resources = [r for r in _LEARNING_RESOURCES if r["level"] == "beginner"]

    def get_resources(self, level: Optional[str] = None) -> List[Dict[str, str]]:
        """Return learning resources, optionally filtered by level."""
        if not self._config.has_feature(FEATURE_LEARNING):
            return []
        if level:
            return [r for r in self._resources if r["level"] == level]
        return list(self._resources)

    def count(self) -> int:
        return len(self._resources)

    def get_resource(self, resource_id: str) -> Optional[Dict[str, str]]:
        for r in self._resources:
            if r["id"] == resource_id:
                return r
        return None


class DataMetrics:
    """Track Monthly Active Users, segmentation, and AI maturity."""

    def __init__(self, config: TierConfig) -> None:
        self._config = config
        self._mau_history: List[Dict[str, Any]] = []
        self._segments: Dict[str, int] = {}

    def record_mau(self, count: int, period: Optional[str] = None) -> Dict[str, Any]:
        """Record a Monthly Active User count."""
        if not self._config.has_feature(FEATURE_METRICS):
            return {
                "recorded": False,
                "reason": "Metrics feature requires PRO tier or above.",
            }
        if count < 0:
            return {"recorded": False, "reason": "MAU count cannot be negative."}
        entry: Dict[str, Any] = {
            "mau": count,
            "period": period or datetime.now(tz=timezone.utc).strftime("%Y-%m"),
            "recorded_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        self._mau_history.append(entry)
        return {"recorded": True, "entry": entry}

    def get_mau_history(self) -> List[Dict[str, Any]]:
        return list(self._mau_history)

    def current_mau(self) -> Optional[int]:
        if not self._mau_history:
            return None
        return self._mau_history[-1]["mau"]

    def add_segment(self, segment_name: str, user_count: int) -> Dict[str, Any]:
        """Add or update a user segment (PRO+)."""
        if not self._config.has_feature(FEATURE_SEGMENTATION):
            return {
                "added": False,
                "reason": "Segmentation requires PRO tier or above.",
            }
        self._segments[segment_name] = user_count
        return {"added": True, "segment": segment_name, "count": user_count}

    def get_segments(self) -> Dict[str, int]:
        return dict(self._segments)

    def get_maturity_assessment(self, active_workflows: int, advocates: int, metrics_tracked: bool) -> Dict[str, Any]:
        """Return a maturity level assessment (PRO+)."""
        if not self._config.has_feature(FEATURE_MATURITY_ASSESSMENT):
            return {
                "assessed": False,
                "reason": "Maturity assessment requires PRO tier or above.",
            }
        if active_workflows >= 5 and advocates >= 5 and metrics_tracked:
            level = 4
        elif active_workflows >= 2 and metrics_tracked:
            level = 3
        elif active_workflows >= 2:
            level = 2
        elif active_workflows >= 1:
            level = 2
        else:
            level = 1
        maturity = next(m for m in _MATURITY_LEVELS if m["level"] == level)
        return {"assessed": True, "maturity": maturity, "inputs": {
            "active_workflows": active_workflows,
            "advocates": advocates,
            "metrics_tracked": metrics_tracked,
        }}


class CommunityOfPractice:
    """Manage DreamCo Communities of Practice (7 channels)."""

    def __init__(self, config: TierConfig) -> None:
        self._config = config
        self._communities: List[Dict[str, Any]] = [dict(c) for c in _COMMUNITIES]

    def get_communities(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return all communities, optionally filtered by domain."""
        if not self._config.has_feature(FEATURE_COMMUNITY):
            return []
        if domain:
            return [c for c in self._communities if c["domain"] == domain]
        return list(self._communities)

    def add_member(self, community_id: str) -> Dict[str, Any]:
        """Increment member count for a community."""
        for c in self._communities:
            if c["id"] == community_id:
                c["members"] += 1
                return {"added": True, "community": c}
        return {"added": False, "reason": f"Community '{community_id}' not found."}

    def count(self) -> int:
        return len(self._communities)

    def total_members(self) -> int:
        return sum(c["members"] for c in self._communities)


class BotTierClassifier:
    """Classify bots by tier based on feature analysis (ENTERPRISE only)."""

    def __init__(self, config: TierConfig) -> None:
        self._config = config

    def classify(self, bot_features: List[str]) -> Dict[str, Any]:
        """Classify a bot's tier based on its feature list."""
        if not self._config.has_feature(FEATURE_BOT_TIER_CLASSIFIER):
            return {
                "classified": False,
                "reason": "BotTierClassifier requires ENTERPRISE tier.",
            }
        enterprise_signals = {"governance_api", "retraining", "white_label", "multi_tenant", "dedicated_support"}
        pro_signals = {"analytics", "slack_notify", "export_csv", "auto_heal", "segmentation", "metrics"}

        feature_set = set(f.lower() for f in bot_features)
        if feature_set & enterprise_signals:
            tier = "enterprise"
        elif feature_set & pro_signals:
            tier = "pro"
        else:
            tier = "free"

        return {
            "classified": True,
            "recommended_tier": tier,
            "detected_signals": list(feature_set & (enterprise_signals | pro_signals)),
            "feature_count": len(bot_features),
        }


class RetrainingOptimizer:
    """Detect accuracy drift and schedule retraining (ENTERPRISE only)."""

    _DEFAULT_THRESHOLD = 5.0  # 5% accuracy drop triggers retraining

    def __init__(self, config: TierConfig, threshold_pct: float = _DEFAULT_THRESHOLD) -> None:
        self._config = config
        self.threshold_pct = threshold_pct

    def evaluate(self, baseline_accuracy: float, current_accuracy: float) -> Dict[str, Any]:
        """Compare accuracy values and recommend a retraining method if drift exceeds threshold."""
        if not self._config.has_feature(FEATURE_RETRAINING_OPTIMIZER):
            return {
                "evaluated": False,
                "reason": "RetrainingOptimizer requires ENTERPRISE tier.",
            }
        if baseline_accuracy <= 0 or current_accuracy < 0:
            return {"evaluated": False, "reason": "Accuracy values must be positive."}

        drift_pct = ((baseline_accuracy - current_accuracy) / baseline_accuracy) * 100.0
        needs_retraining = drift_pct >= self.threshold_pct

        if drift_pct >= 20.0:
            method = "full_retrain"
        elif drift_pct >= 10.0:
            method = "fine_tuning"
        else:
            method = "transfer_learning"

        return {
            "evaluated": True,
            "baseline_accuracy": baseline_accuracy,
            "current_accuracy": current_accuracy,
            "drift_pct": round(drift_pct, 2),
            "needs_retraining": needs_retraining,
            "recommended_method": method if needs_retraining else None,
            "threshold_pct": self.threshold_pct,
        }


# ===========================================================================
# Main orchestrator
# ===========================================================================

class AIEnablementHub:
    """DreamCo AI Enablement Hub — central platform for AI fluency and governance.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)

        # Five core pillars
        self.advocates = AdvocatesProgram(self.config)
        self.policies = PoliciesGuardrails(self.config)
        self.learning = LearningDevelopment(self.config)
        self.metrics = DataMetrics(self.config)
        self.community = CommunityOfPractice(self.config)

        # ENTERPRISE sub-systems
        self.bot_classifier = BotTierClassifier(self.config)
        self.retraining = RetrainingOptimizer(self.config)

    # ------------------------------------------------------------------
    # Delegate convenience methods
    # ------------------------------------------------------------------

    def add_advocate(self, username: str, role: str = "Starter Advocate", domain: str = "general") -> Dict[str, Any]:
        """Add an advocate to the network."""
        return self.advocates.add_advocate(username, role, domain)

    def get_policies(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """Return available policies."""
        return self.policies.get_policies(category)

    def get_learning_resources(self, level: Optional[str] = None) -> List[Dict[str, str]]:
        """Return available learning resources."""
        return self.learning.get_resources(level)

    def record_mau(self, count: int, period: Optional[str] = None) -> Dict[str, Any]:
        """Record Monthly Active Users."""
        return self.metrics.record_mau(count, period)

    def get_communities(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return communities of practice."""
        return self.community.get_communities(domain)

    def classify_bot(self, bot_features: List[str]) -> Dict[str, Any]:
        """Classify a bot's recommended tier (ENTERPRISE)."""
        return self.bot_classifier.classify(bot_features)

    def evaluate_retraining(self, baseline: float, current: float) -> Dict[str, Any]:
        """Evaluate whether a bot needs retraining (ENTERPRISE)."""
        return self.retraining.evaluate(baseline, current)

    # ------------------------------------------------------------------
    # Summary & tier info
    # ------------------------------------------------------------------

    def get_summary(self) -> Dict[str, Any]:
        """Return a comprehensive summary of the enablement hub state."""
        return {
            "tier": self.tier.value,
            "advocates": {
                "count": self.advocates.count(),
                "limit": self.config.max_advocates,
            },
            "policies": {
                "count": self.policies.count(),
                "categories": list({p["category"] for p in self.policies.get_policies()}),
            },
            "learning_resources": {
                "count": self.learning.count(),
            },
            "metrics": {
                "current_mau": self.metrics.current_mau(),
                "mau_periods_recorded": len(self.metrics.get_mau_history()),
                "segments": self.metrics.get_segments(),
            },
            "community": {
                "channels": self.community.count(),
                "total_members": self.community.total_members(),
            },
            "enterprise_features": {
                "bot_classifier_available": self.config.has_feature(FEATURE_BOT_TIER_CLASSIFIER),
                "retraining_optimizer_available": self.config.has_feature(FEATURE_RETRAINING_OPTIMIZER),
            },
        }

    def describe_tier(self) -> str:
        """Return a human-readable tier description."""
        cfg = self.config
        lines = [
            f"=== AIEnablementHub — {cfg.name} Tier ===",
            f"  Monthly price     : ${cfg.price_usd_monthly}/month",
            f"  Max advocates     : {cfg.max_advocates if cfg.max_advocates else 'Unlimited'}",
            f"  Max policies      : {cfg.max_policies if cfg.max_policies else 'Unlimited'}",
            f"  Max learning res. : {cfg.max_learning_resources if cfg.max_learning_resources else 'Unlimited'}",
            f"  Support           : {cfg.support_level}",
            f"  Features          : {', '.join(cfg.features)}",
        ]
        upgrade = get_upgrade_path(self.tier)
        if upgrade:
            lines.append(f"  Upgrade to        : {upgrade.name} (${upgrade.price_usd_monthly}/mo)")
        return "\n".join(lines)

    def process(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return self.get_summary()
