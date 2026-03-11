"""
AI Skill Tree — Gamified Learning Progression System

Users earn XP by completing course modules, unlock skill nodes, and level up
through the DreamCo AI University.  Unlocking skills grants token discounts
and feature access.

Skill tree structure mirrors the 10 course levels, with each level containing
multiple skill nodes that become available as prerequisites are met.

Usage
-----
    from bots.ai_level_up_bot.ai_skill_tree import AISkillTree

    tree = AISkillTree(user_id="user_001")
    result = tree.award_xp(150)
    print(result)

    unlocked = tree.unlock_skill("prompt_engineering_basics")
    print(unlocked)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class SkillRarity(Enum):
    """Rarity tier of a skill node."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class SkillNode:
    """
    A single node in the AI skill tree.

    Attributes
    ----------
    skill_id : str
        Unique identifier used to reference this skill.
    name : str
        Human-readable skill name.
    description : str
        What this skill enables or represents.
    course_level : int
        The DreamCo AI University level this skill belongs to.
    rarity : SkillRarity
        Rarity tier affecting XP cost to unlock.
    xp_cost : int
        XP required to unlock this skill.
    prerequisites : list[str]
        skill_ids that must be unlocked before this one.
    token_discount_pct : float
        Percentage discount applied to token purchases once unlocked.
    unlocked : bool
        Whether this skill has been unlocked by the user.
    """

    skill_id: str
    name: str
    description: str
    course_level: int
    rarity: SkillRarity = SkillRarity.COMMON
    xp_cost: int = 100
    prerequisites: list[str] = field(default_factory=list)
    token_discount_pct: float = 0.0
    unlocked: bool = False


@dataclass
class Badge:
    """
    An achievement badge awarded for reaching a milestone.

    Attributes
    ----------
    badge_id : str
        Unique badge identifier.
    name : str
        Human-readable badge name.
    description : str
        What must be done to earn this badge.
    xp_required : int
        Minimum total XP to automatically earn this badge.
    earned : bool
        Whether the user has earned this badge.
    """

    badge_id: str
    name: str
    description: str
    xp_required: int = 0
    earned: bool = False


# ---------------------------------------------------------------------------
# Skill tree seed data
# ---------------------------------------------------------------------------

def _build_skill_nodes() -> list[SkillNode]:
    """Return the full set of skill nodes for the DreamCo AI skill tree."""
    return [
        # ── Level 1 Skills ────────────────────────────────────────────────
        SkillNode(
            skill_id="ai_fundamentals",
            name="AI Fundamentals",
            description="Understand core AI concepts and terminology.",
            course_level=1,
            rarity=SkillRarity.COMMON,
            xp_cost=100,
            prerequisites=[],
            token_discount_pct=0.0,
        ),
        SkillNode(
            skill_id="ai_tool_explorer",
            name="AI Tool Explorer",
            description="Navigate and use the global AI companies database.",
            course_level=1,
            rarity=SkillRarity.COMMON,
            xp_cost=150,
            prerequisites=["ai_fundamentals"],
            token_discount_pct=1.0,
        ),
        # ── Level 2 Skills ────────────────────────────────────────────────
        SkillNode(
            skill_id="prompt_engineering_basics",
            name="Prompt Engineering Basics",
            description="Write zero-shot and few-shot prompts effectively.",
            course_level=2,
            rarity=SkillRarity.UNCOMMON,
            xp_cost=300,
            prerequisites=["ai_tool_explorer"],
            token_discount_pct=2.0,
        ),
        SkillNode(
            skill_id="advanced_prompting",
            name="Advanced Prompting",
            description="Chain-of-thought reasoning and role-based prompts.",
            course_level=2,
            rarity=SkillRarity.UNCOMMON,
            xp_cost=400,
            prerequisites=["prompt_engineering_basics"],
            token_discount_pct=3.0,
        ),
        # ── Level 3 Skills ────────────────────────────────────────────────
        SkillNode(
            skill_id="ai_content_creator",
            name="AI Content Creator",
            description="Produce AI-generated blogs, ads, and social content.",
            course_level=3,
            rarity=SkillRarity.UNCOMMON,
            xp_cost=500,
            prerequisites=["advanced_prompting"],
            token_discount_pct=3.0,
        ),
        SkillNode(
            skill_id="ai_image_master",
            name="AI Image Master",
            description="Create professional visuals with DALL-E and Midjourney.",
            course_level=3,
            rarity=SkillRarity.RARE,
            xp_cost=600,
            prerequisites=["ai_content_creator"],
            token_discount_pct=5.0,
        ),
        # ── Level 4 Skills ────────────────────────────────────────────────
        SkillNode(
            skill_id="automation_specialist",
            name="Automation Specialist",
            description="Automate workflows using no-code AI platforms.",
            course_level=4,
            rarity=SkillRarity.RARE,
            xp_cost=800,
            prerequisites=["ai_image_master"],
            token_discount_pct=5.0,
        ),
        SkillNode(
            skill_id="ai_workflow_architect",
            name="AI Workflow Architect",
            description="Design end-to-end AI-powered business workflows.",
            course_level=4,
            rarity=SkillRarity.RARE,
            xp_cost=900,
            prerequisites=["automation_specialist"],
            token_discount_pct=7.0,
        ),
        # ── Level 5 Skills ────────────────────────────────────────────────
        SkillNode(
            skill_id="ai_entrepreneur",
            name="AI Entrepreneur",
            description="Build and monetise an AI-powered product or service.",
            course_level=5,
            rarity=SkillRarity.EPIC,
            xp_cost=1200,
            prerequisites=["ai_workflow_architect"],
            token_discount_pct=8.0,
        ),
        SkillNode(
            skill_id="token_economy_master",
            name="Token Economy Master",
            description="Design token-based revenue models with DreamCo markup.",
            course_level=5,
            rarity=SkillRarity.EPIC,
            xp_cost=1200,
            prerequisites=["ai_entrepreneur"],
            token_discount_pct=10.0,
        ),
        # ── Level 6 Skills ────────────────────────────────────────────────
        SkillNode(
            skill_id="ai_agent_developer",
            name="AI Agent Developer",
            description="Build autonomous LLM-powered agents with tool use.",
            course_level=6,
            rarity=SkillRarity.EPIC,
            xp_cost=1500,
            prerequisites=["token_economy_master"],
            token_discount_pct=10.0,
        ),
        SkillNode(
            skill_id="multi_agent_orchestrator",
            name="Multi-Agent Orchestrator",
            description="Coordinate teams of specialised AI agents.",
            course_level=6,
            rarity=SkillRarity.EPIC,
            xp_cost=2000,
            prerequisites=["ai_agent_developer"],
            token_discount_pct=12.0,
        ),
        # ── Level 7 Skills ────────────────────────────────────────────────
        SkillNode(
            skill_id="ai_infrastructure_engineer",
            name="AI Infrastructure Engineer",
            description="Deploy scalable AI apps on cloud platforms.",
            course_level=7,
            rarity=SkillRarity.EPIC,
            xp_cost=2500,
            prerequisites=["multi_agent_orchestrator"],
            token_discount_pct=13.0,
        ),
        # ── Level 8 Skills ────────────────────────────────────────────────
        SkillNode(
            skill_id="ai_research_practitioner",
            name="AI Research Practitioner",
            description="Fine-tune LLMs and publish open-source AI research.",
            course_level=8,
            rarity=SkillRarity.LEGENDARY,
            xp_cost=3000,
            prerequisites=["ai_infrastructure_engineer"],
            token_discount_pct=15.0,
        ),
        # ── Level 9 Skills ────────────────────────────────────────────────
        SkillNode(
            skill_id="ai_founder",
            name="AI Founder",
            description="Launch a funded AI company from idea to product-market fit.",
            course_level=9,
            rarity=SkillRarity.LEGENDARY,
            xp_cost=4000,
            prerequisites=["ai_research_practitioner"],
            token_discount_pct=18.0,
        ),
        # ── Level 10 Skills ───────────────────────────────────────────────
        SkillNode(
            skill_id="ai_superintelligence_architect",
            name="AI Superintelligence Architect",
            description="Design frontier multimodal, multi-agent AI systems.",
            course_level=10,
            rarity=SkillRarity.LEGENDARY,
            xp_cost=5000,
            prerequisites=["ai_founder"],
            token_discount_pct=20.0,
        ),
    ]


def _build_badges() -> list[Badge]:
    """Return the full set of milestone badges."""
    return [
        Badge("first_step",     "First Step",        "Earn your first 100 XP.",                 xp_required=100),
        Badge("apprentice",     "AI Apprentice",     "Reach 500 XP.",                           xp_required=500),
        Badge("practitioner",   "AI Practitioner",   "Reach 1 000 XP.",                         xp_required=1_000),
        Badge("specialist",     "AI Specialist",     "Reach 3 000 XP.",                         xp_required=3_000),
        Badge("master",         "AI Master",         "Reach 7 500 XP.",                         xp_required=7_500),
        Badge("grandmaster",    "AI Grandmaster",    "Reach 15 000 XP.",                        xp_required=15_000),
        Badge("legend",         "AI Legend",         "Reach 25 000 XP — the ultimate title.",   xp_required=25_000),
    ]


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class SkillTreeError(Exception):
    """Raised for invalid skill tree operations."""


# ---------------------------------------------------------------------------
# AI Skill Tree
# ---------------------------------------------------------------------------

class AISkillTree:
    """
    Gamified skill progression system for a single DreamCo user.

    Parameters
    ----------
    user_id : str
        Unique user identifier.

    Attributes
    ----------
    xp : int
        Current accumulated XP.
    level : int
        Current gamification level (derived from XP).
    """

    # XP required to reach each gamification level (index = level number).
    # Level 1 = 0 XP, Level 2 = 200, Level 3 = 500, …
    _LEVEL_THRESHOLDS = [0, 200, 500, 1_000, 2_000, 3_500, 5_500, 8_000, 11_000, 15_000, 20_000]

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.xp: int = 0
        self.level: int = 1

        # Build per-instance mutable copies so users don't share state
        self._skills: dict[str, SkillNode] = {
            s.skill_id: SkillNode(
                skill_id=s.skill_id,
                name=s.name,
                description=s.description,
                course_level=s.course_level,
                rarity=s.rarity,
                xp_cost=s.xp_cost,
                prerequisites=list(s.prerequisites),
                token_discount_pct=s.token_discount_pct,
                unlocked=False,
            )
            for s in _build_skill_nodes()
        }
        self._badges: list[Badge] = _build_badges()

    # ------------------------------------------------------------------
    # XP & levelling
    # ------------------------------------------------------------------

    def award_xp(self, amount: int) -> dict:
        """
        Add *amount* XP to the user's total and check for level-ups.

        Parameters
        ----------
        amount : int
            XP to award (must be positive).

        Returns
        -------
        dict
            Summary including new total XP, level, and any level-up or
            badges earned.
        """
        if amount <= 0:
            raise SkillTreeError("XP amount must be positive.")

        self.xp += amount
        leveled_up = self._recalculate_level()
        new_badges = self._check_badges()

        return {
            "user_id": self.user_id,
            "xp_awarded": amount,
            "total_xp": self.xp,
            "level": self.level,
            "leveled_up": leveled_up,
            "xp_to_next_level": self._xp_to_next_level(),
            "new_badges": [b.name for b in new_badges],
        }

    def _recalculate_level(self) -> bool:
        """Recalculate level from current XP.  Return True if level increased."""
        new_level = 1
        for i, threshold in enumerate(self._LEVEL_THRESHOLDS):
            if self.xp >= threshold:
                new_level = i + 1
            else:
                break
        if new_level > self.level:
            self.level = new_level
            return True
        return False

    def _xp_to_next_level(self) -> Optional[int]:
        """Return XP needed to reach the next gamification level, or None at max."""
        if self.level >= len(self._LEVEL_THRESHOLDS):
            return None
        return self._LEVEL_THRESHOLDS[self.level] - self.xp

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------

    def unlock_skill(self, skill_id: str) -> dict:
        """
        Attempt to unlock the skill identified by *skill_id*.

        Prerequisites must be met and the user must have enough XP.

        Returns
        -------
        dict
            Result of the unlock attempt.

        Raises
        ------
        SkillTreeError
            If the skill does not exist, prerequisites are unmet, or the
            user has insufficient XP.
        """
        if skill_id not in self._skills:
            raise SkillTreeError(f"Skill '{skill_id}' does not exist.")

        skill = self._skills[skill_id]

        if skill.unlocked:
            return {
                "skill_id": skill_id,
                "status": "already_unlocked",
                "message": f"'{skill.name}' is already unlocked.",
            }

        # Check prerequisites
        unmet = [p for p in skill.prerequisites if not self._skills[p].unlocked]
        if unmet:
            raise SkillTreeError(
                f"Prerequisites not met for '{skill.name}': {unmet}"
            )

        # Check XP
        if self.xp < skill.xp_cost:
            raise SkillTreeError(
                f"Insufficient XP to unlock '{skill.name}'. "
                f"Need {skill.xp_cost}, have {self.xp}."
            )

        skill.unlocked = True

        return {
            "skill_id": skill_id,
            "status": "unlocked",
            "skill_name": skill.name,
            "token_discount_pct": skill.token_discount_pct,
            "message": f"🎉 '{skill.name}' unlocked! {skill.token_discount_pct}% token discount granted.",
        }

    def get_skill(self, skill_id: str) -> SkillNode:
        """Return the SkillNode for *skill_id*.

        Raises
        ------
        SkillTreeError
            If the skill does not exist.
        """
        if skill_id not in self._skills:
            raise SkillTreeError(f"Skill '{skill_id}' does not exist.")
        return self._skills[skill_id]

    def list_skills(self, unlocked_only: bool = False) -> list[SkillNode]:
        """Return all skill nodes, optionally filtered to unlocked ones."""
        skills = list(self._skills.values())
        if unlocked_only:
            skills = [s for s in skills if s.unlocked]
        return skills

    def get_total_token_discount(self) -> float:
        """Return the cumulative token discount from all unlocked skills."""
        return sum(
            s.token_discount_pct
            for s in self._skills.values()
            if s.unlocked
        )

    # ------------------------------------------------------------------
    # Badges
    # ------------------------------------------------------------------

    def _check_badges(self) -> list[Badge]:
        """Evaluate badge thresholds and award any newly earned badges."""
        newly_earned = []
        for badge in self._badges:
            if not badge.earned and self.xp >= badge.xp_required:
                badge.earned = True
                newly_earned.append(badge)
        return newly_earned

    def list_badges(self, earned_only: bool = False) -> list[Badge]:
        """Return all badges, optionally filtered to earned ones."""
        if earned_only:
            return [b for b in self._badges if b.earned]
        return list(self._badges)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def skill_tree_summary(self) -> dict:
        """Return a summary of the user's skill tree progress."""
        unlocked = [s for s in self._skills.values() if s.unlocked]
        earned_badges = [b for b in self._badges if b.earned]

        return {
            "user_id": self.user_id,
            "xp": self.xp,
            "level": self.level,
            "xp_to_next_level": self._xp_to_next_level(),
            "skills_unlocked": len(unlocked),
            "total_skills": len(self._skills),
            "token_discount_pct": self.get_total_token_discount(),
            "badges_earned": len(earned_badges),
            "total_badges": len(self._badges),
        }
