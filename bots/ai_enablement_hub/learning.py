"""
Pillar 3 — Learning & Development.

Provides developer resources for accelerated onboarding into each bot's
specific tasks, enabling rapid AI fluency across the workforce.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

@dataclass
class LearningResource:
    """A single learning or onboarding resource."""

    resource_id: str
    title: str
    description: str
    resource_type: str      # "tutorial" | "workshop" | "guide" | "video" | "code_lab"
    skill_level: str        # "beginner" | "intermediate" | "advanced"
    bot_target: str         # e.g. "all", "ai_brain", "revenue_engine_bot"
    url: str = ""
    estimated_minutes: int = 30
    tags: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "resource_id": self.resource_id,
            "title": self.title,
            "description": self.description,
            "resource_type": self.resource_type,
            "skill_level": self.skill_level,
            "bot_target": self.bot_target,
            "url": self.url,
            "estimated_minutes": self.estimated_minutes,
            "tags": list(self.tags),
            "created_at": self.created_at,
        }


@dataclass
class LearnerProgress:
    """Tracks a learner's progress through available resources."""

    learner_id: str
    completed_resources: list[str] = field(default_factory=list)
    in_progress: list[str] = field(default_factory=list)
    last_activity: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "learner_id": self.learner_id,
            "completed_count": len(self.completed_resources),
            "in_progress_count": len(self.in_progress),
            "last_activity": self.last_activity,
        }


# ---------------------------------------------------------------------------
# Built-in resource catalogue
# ---------------------------------------------------------------------------

VALID_RESOURCE_TYPES = {"tutorial", "workshop", "guide", "video", "code_lab"}
VALID_SKILL_LEVELS = {"beginner", "intermediate", "advanced"}

_DEFAULT_RESOURCES: list[LearningResource] = [
    LearningResource(
        "res-001", "DreamCobots Quickstart",
        "Zero-to-hero guide for new contributors: repo structure, bot patterns, and tier system.",
        "guide", "beginner", "all",
        tags=["onboarding", "architecture"],
    ),
    LearningResource(
        "res-002", "AI Sources Flow Deep Dive",
        "Interactive workshop walking through all 8 stages of the GLOBAL AI SOURCES FLOW.",
        "workshop", "intermediate", "all",
        tags=["framework", "pipeline"],
    ),
    LearningResource(
        "res-003", "Bot Tier Customization",
        "Tutorial covering FREE/PRO/ENTERPRISE tier design and feature flag patterns.",
        "tutorial", "intermediate", "all",
        tags=["tiers", "feature_flags"],
    ),
    LearningResource(
        "res-004", "Revenue Engine Bot Mastery",
        "Advanced code lab — build a Stripe + affiliate pipeline from scratch.",
        "code_lab", "advanced", "revenue_engine_bot",
        tags=["stripe", "revenue", "automation"],
    ),
    LearningResource(
        "res-005", "AI Fluency Foundations",
        "Short video series covering supervised/unsupervised/RL learning concepts.",
        "video", "beginner", "all",
        tags=["ai_fluency", "machine_learning"],
    ),
    LearningResource(
        "res-006", "Governance & Security Patterns",
        "Guide to RBAC, audit logging, and compliance in DreamCo bots.",
        "guide", "advanced", "all",
        tags=["governance", "security", "compliance"],
    ),
    LearningResource(
        "res-007", "BuddyOrchestrator Integration",
        "Tutorial on registering bots with BuddyOrchestrator and tracking revenue.",
        "tutorial", "intermediate", "buddy_orchestrator",
        tags=["orchestration", "integration"],
    ),
    LearningResource(
        "res-008", "Performance Metrics & Retraining",
        "Workshop on monitoring MAU, cycle time, and triggering retraining cycles.",
        "workshop", "advanced", "all",
        tags=["metrics", "retraining", "performance"],
    ),
]


# ---------------------------------------------------------------------------
# Learning & Development system
# ---------------------------------------------------------------------------

class LearningDevelopment:
    """
    Manages developer learning resources and tracks learner progress.

    Built-in resources cover onboarding, architecture, tier design, and
    advanced AI enablement topics.
    """

    def __init__(self) -> None:
        self._resources: dict[str, LearningResource] = {
            r.resource_id: r for r in _DEFAULT_RESOURCES
        }
        self._learners: dict[str, LearnerProgress] = {}

    # ------------------------------------------------------------------
    # Resource management
    # ------------------------------------------------------------------

    def add_resource(
        self,
        title: str,
        description: str,
        resource_type: str,
        skill_level: str,
        bot_target: str = "all",
        url: str = "",
        estimated_minutes: int = 30,
        tags: Optional[list[str]] = None,
    ) -> LearningResource:
        """Add a new learning resource to the catalogue."""
        if resource_type not in VALID_RESOURCE_TYPES:
            raise ValueError(
                f"Invalid resource_type '{resource_type}'. "
                f"Valid: {sorted(VALID_RESOURCE_TYPES)}"
            )
        if skill_level not in VALID_SKILL_LEVELS:
            raise ValueError(
                f"Invalid skill_level '{skill_level}'. "
                f"Valid: {sorted(VALID_SKILL_LEVELS)}"
            )
        resource_id = f"res-{uuid.uuid4().hex[:8]}"
        resource = LearningResource(
            resource_id=resource_id,
            title=title,
            description=description,
            resource_type=resource_type,
            skill_level=skill_level,
            bot_target=bot_target,
            url=url,
            estimated_minutes=estimated_minutes,
            tags=tags or [],
        )
        self._resources[resource_id] = resource
        return resource

    def get_resource(self, resource_id: str) -> LearningResource:
        """Return a resource by ID."""
        if resource_id not in self._resources:
            raise KeyError(f"Resource '{resource_id}' not found.")
        return self._resources[resource_id]

    def list_resources(
        self,
        skill_level: Optional[str] = None,
        bot_target: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> list[dict]:
        """List resources with optional filters."""
        resources = self._resources.values()
        if skill_level is not None:
            resources = [r for r in resources if r.skill_level == skill_level]
        if bot_target is not None:
            resources = [r for r in resources if r.bot_target in (bot_target, "all")]
        if resource_type is not None:
            resources = [r for r in resources if r.resource_type == resource_type]
        return [r.to_dict() for r in resources]

    # ------------------------------------------------------------------
    # Learner progress tracking
    # ------------------------------------------------------------------

    def enroll_learner(self, learner_id: str) -> LearnerProgress:
        """Enrol a learner in the L&D system."""
        if learner_id not in self._learners:
            self._learners[learner_id] = LearnerProgress(learner_id=learner_id)
        return self._learners[learner_id]

    def mark_started(self, learner_id: str, resource_id: str) -> None:
        """Mark a resource as in-progress for a learner."""
        self.get_resource(resource_id)  # validate resource exists
        progress = self.enroll_learner(learner_id)
        if resource_id not in progress.in_progress:
            progress.in_progress.append(resource_id)
        progress.last_activity = datetime.now(timezone.utc).isoformat()

    def mark_completed(self, learner_id: str, resource_id: str) -> None:
        """Mark a resource as completed for a learner."""
        self.get_resource(resource_id)  # validate resource exists
        progress = self.enroll_learner(learner_id)
        if resource_id not in progress.completed_resources:
            progress.completed_resources.append(resource_id)
        if resource_id in progress.in_progress:
            progress.in_progress.remove(resource_id)
        progress.last_activity = datetime.now(timezone.utc).isoformat()

    def get_learner_progress(self, learner_id: str) -> dict:
        """Return progress summary for a learner."""
        if learner_id not in self._learners:
            raise KeyError(f"Learner '{learner_id}' not enrolled.")
        return self._learners[learner_id].to_dict()

    # ------------------------------------------------------------------
    # Programme summary
    # ------------------------------------------------------------------

    def programme_summary(self) -> dict:
        """Return L&D programme statistics."""
        total_completions = sum(
            len(lp.completed_resources) for lp in self._learners.values()
        )
        return {
            "total_resources": len(self._resources),
            "total_learners": len(self._learners),
            "total_completions": total_completions,
            "avg_completions_per_learner": round(
                total_completions / max(len(self._learners), 1), 2
            ),
        }
