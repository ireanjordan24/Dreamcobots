"""
AI Course Engine — DreamCo AI University

Provides the 10-level AI University curriculum structure for the DreamCo
AI Level-Up Bot.  Each level contains a set of modules covering theory,
practical labs, simulations, and readings.

Level structure
---------------
Level 1  — AI Basics
Level 2  — Prompt Engineering
Level 3  — AI Content Creation
Level 4  — AI Automation
Level 5  — AI Business Building
Level 6  — AI Agent Development
Level 7  — AI Infrastructure
Level 8  — AI Research
Level 9  — AI Company Creation
Level 10 — AI Superintelligence Architecture

Teaching modes
--------------
- VIDEO       : Pre-recorded video lessons
- SIMULATION  : Challenge-based mission simulations
- READING     : PDFs, research papers, case studies
- CODING_LAB  : Sandbox coding environments

Note: DreamCo certifications are issued as "DreamCo Professional Certificate"
or "AI Master Certification" and are NOT US-government-accredited degrees.

Usage
-----
    from bots.ai_level_up_bot.ai_course_engine import AICourseEngine

    engine = AICourseEngine()
    level = engine.get_level(1)
    print(level.title, level.modules)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Teaching modes
# ---------------------------------------------------------------------------

class TeachingMode(Enum):
    """Available teaching modalities for course modules."""

    VIDEO = "video"
    SIMULATION = "simulation"
    READING = "reading"
    CODING_LAB = "coding_lab"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CourseModule:
    """
    A single instructional module within a course level.

    Attributes
    ----------
    title : str
        Module title.
    description : str
        Short description of what is covered.
    teaching_mode : TeachingMode
        Primary delivery method.
    duration_minutes : int
        Estimated completion time in minutes.
    xp_reward : int
        XP granted upon completing this module.
    """

    title: str
    description: str
    teaching_mode: TeachingMode
    duration_minutes: int = 30
    xp_reward: int = 100


@dataclass
class CourseLevel:
    """
    One of the 10 progressive levels of the DreamCo AI University.

    Attributes
    ----------
    level_number : int
        Level identifier (1–10).
    title : str
        Human-readable level title.
    description : str
        Overview of what students achieve at this level.
    modules : list[CourseModule]
        Ordered list of modules for this level.
    prerequisite_level : int | None
        Previous level required to unlock this one (None for Level 1).
    certificate_name : str
        Name of the DreamCo certificate awarded upon completion.
    """

    level_number: int
    title: str
    description: str
    modules: list[CourseModule] = field(default_factory=list)
    prerequisite_level: Optional[int] = None
    certificate_name: str = ""

    @property
    def total_xp(self) -> int:
        """Return the total XP available across all modules."""
        return sum(m.xp_reward for m in self.modules)

    @property
    def total_duration_minutes(self) -> int:
        """Return the combined duration of all modules in minutes."""
        return sum(m.duration_minutes for m in self.modules)

    def module_count(self) -> int:
        """Return the number of modules in this level."""
        return len(self.modules)


# ---------------------------------------------------------------------------
# Curriculum builder
# ---------------------------------------------------------------------------

def _build_curriculum() -> list[CourseLevel]:
    """Return the full 10-level DreamCo AI University curriculum."""
    return [
        # ── Level 1 — AI Basics ───────────────────────────────────────────
        CourseLevel(
            level_number=1,
            title="AI Basics",
            description=(
                "Introduction to artificial intelligence: history, core concepts, "
                "key terminology, and an overview of the global AI landscape."
            ),
            prerequisite_level=None,
            certificate_name="DreamCo AI Foundations Certificate",
            modules=[
                CourseModule(
                    title="What is Artificial Intelligence?",
                    description="History, definitions, and major milestones in AI.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=20,
                    xp_reward=100,
                ),
                CourseModule(
                    title="AI Terminology Glossary",
                    description="Key terms: LLM, tokens, inference, embeddings, RAG.",
                    teaching_mode=TeachingMode.READING,
                    duration_minutes=15,
                    xp_reward=50,
                ),
                CourseModule(
                    title="Your First AI Interaction",
                    description="Hands-on exercise chatting with GPT-4 and Claude.",
                    teaching_mode=TeachingMode.SIMULATION,
                    duration_minutes=30,
                    xp_reward=150,
                ),
                CourseModule(
                    title="AI Categories Overview",
                    description="Survey of NLP, Vision, Voice, Code, and Generative AI.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=25,
                    xp_reward=100,
                ),
            ],
        ),
        # ── Level 2 — Prompt Engineering ─────────────────────────────────
        CourseLevel(
            level_number=2,
            title="Prompt Engineering",
            description=(
                "Master the craft of writing effective prompts for GPT and other "
                "LLMs, including zero-shot, few-shot, chain-of-thought, and role prompting."
            ),
            prerequisite_level=1,
            certificate_name="DreamCo Prompt Engineering Certificate",
            modules=[
                CourseModule(
                    title="Prompt Anatomy",
                    description="Breaking down instructions, context, examples, and output format.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=20,
                    xp_reward=100,
                ),
                CourseModule(
                    title="Zero-Shot vs Few-Shot Prompting",
                    description="Comparing prompting styles with live examples.",
                    teaching_mode=TeachingMode.CODING_LAB,
                    duration_minutes=45,
                    xp_reward=200,
                ),
                CourseModule(
                    title="Chain-of-Thought Reasoning",
                    description="Guiding models to reason step-by-step for complex tasks.",
                    teaching_mode=TeachingMode.SIMULATION,
                    duration_minutes=40,
                    xp_reward=200,
                ),
                CourseModule(
                    title="Prompt Library Challenge",
                    description="Build your personal 20-prompt library for common tasks.",
                    teaching_mode=TeachingMode.CODING_LAB,
                    duration_minutes=60,
                    xp_reward=300,
                ),
            ],
        ),
        # ── Level 3 — AI Content Creation ────────────────────────────────
        CourseLevel(
            level_number=3,
            title="AI Content Creation",
            description=(
                "Generate AI-powered blogs, ads, social posts, images, and videos "
                "using the leading creative AI platforms."
            ),
            prerequisite_level=2,
            certificate_name="DreamCo AI Content Creator Certificate",
            modules=[
                CourseModule(
                    title="AI Copywriting Fundamentals",
                    description="Using GPT to write ads, emails, and landing pages.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=30,
                    xp_reward=150,
                ),
                CourseModule(
                    title="AI Image Generation Workshop",
                    description="Create marketing visuals with DALL-E and Midjourney.",
                    teaching_mode=TeachingMode.CODING_LAB,
                    duration_minutes=60,
                    xp_reward=250,
                ),
                CourseModule(
                    title="AI Video & Voice Production",
                    description="Produce videos with Synthesia and voice-overs with ElevenLabs.",
                    teaching_mode=TeachingMode.SIMULATION,
                    duration_minutes=60,
                    xp_reward=250,
                ),
                CourseModule(
                    title="Content Calendar Automation",
                    description="Build a 30-day AI-generated social media content calendar.",
                    teaching_mode=TeachingMode.SIMULATION,
                    duration_minutes=45,
                    xp_reward=300,
                ),
            ],
        ),
        # ── Level 4 — AI Automation ───────────────────────────────────────
        CourseLevel(
            level_number=4,
            title="AI Automation",
            description=(
                "Automate repetitive workflows using AI tools, no-code platforms, "
                "and API integrations for marketing, operations, and support."
            ),
            prerequisite_level=3,
            certificate_name="DreamCo AI Automation Specialist Certificate",
            modules=[
                CourseModule(
                    title="No-Code Automation Basics",
                    description="Zapier, Make.com, and n8n for AI workflow automation.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=30,
                    xp_reward=150,
                ),
                CourseModule(
                    title="Marketing Agency Automation Mission",
                    description="Automate a full marketing agency using AI tools.",
                    teaching_mode=TeachingMode.SIMULATION,
                    duration_minutes=90,
                    xp_reward=500,
                ),
                CourseModule(
                    title="AI Customer Support Bot",
                    description="Build and deploy an AI customer support chatbot.",
                    teaching_mode=TeachingMode.CODING_LAB,
                    duration_minutes=60,
                    xp_reward=300,
                ),
                CourseModule(
                    title="Data Pipeline Automation",
                    description="Automate data collection, cleaning, and reporting.",
                    teaching_mode=TeachingMode.CODING_LAB,
                    duration_minutes=60,
                    xp_reward=300,
                ),
            ],
        ),
        # ── Level 5 — AI Business Building ───────────────────────────────
        CourseLevel(
            level_number=5,
            title="AI Business Building",
            description=(
                "Create and scale AI-powered businesses: revenue models, "
                "customer acquisition, and AI-driven operations."
            ),
            prerequisite_level=4,
            certificate_name="DreamCo AI Entrepreneur Certificate",
            modules=[
                CourseModule(
                    title="AI Business Models",
                    description="SaaS, marketplace, and service models powered by AI.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=40,
                    xp_reward=200,
                ),
                CourseModule(
                    title="DreamCo Token Marketplace Deep Dive",
                    description="Leverage DreamCo's 25 % markup model in your own platform.",
                    teaching_mode=TeachingMode.READING,
                    duration_minutes=30,
                    xp_reward=150,
                ),
                CourseModule(
                    title="AI Startup Launch Mission",
                    description="Build a pitch deck and MVP plan for an AI startup.",
                    teaching_mode=TeachingMode.SIMULATION,
                    duration_minutes=120,
                    xp_reward=600,
                ),
                CourseModule(
                    title="Pricing & Monetisation Strategy",
                    description="Design subscription tiers and token pricing for an AI product.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=45,
                    xp_reward=250,
                ),
            ],
        ),
        # ── Level 6 — AI Agent Development ───────────────────────────────
        CourseLevel(
            level_number=6,
            title="AI Agent Development",
            description=(
                "Build autonomous AI agents that can plan, act, and integrate "
                "with external APIs to complete complex multi-step tasks."
            ),
            prerequisite_level=5,
            certificate_name="DreamCo AI Agent Developer Certificate",
            modules=[
                CourseModule(
                    title="What are AI Agents?",
                    description="ReAct, tool-use, memory, and planning in LLM agents.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=30,
                    xp_reward=150,
                ),
                CourseModule(
                    title="Building Your First Agent",
                    description="Code a GPT-based agent with tool calling from scratch.",
                    teaching_mode=TeachingMode.CODING_LAB,
                    duration_minutes=90,
                    xp_reward=500,
                ),
                CourseModule(
                    title="Multi-Agent Orchestration",
                    description="Coordinate a team of specialised AI agents on a shared goal.",
                    teaching_mode=TeachingMode.SIMULATION,
                    duration_minutes=90,
                    xp_reward=500,
                ),
                CourseModule(
                    title="Agent Safety & Guardrails",
                    description="Implement output filtering and rate-limiting for production agents.",
                    teaching_mode=TeachingMode.CODING_LAB,
                    duration_minutes=60,
                    xp_reward=300,
                ),
            ],
        ),
        # ── Level 7 — AI Infrastructure ───────────────────────────────────
        CourseLevel(
            level_number=7,
            title="AI Infrastructure",
            description=(
                "Design and deploy scalable AI application infrastructure on "
                "cloud platforms, including model serving, caching, and cost optimisation."
            ),
            prerequisite_level=6,
            certificate_name="DreamCo AI Infrastructure Engineer Certificate",
            modules=[
                CourseModule(
                    title="Cloud AI Platforms Overview",
                    description="AWS SageMaker, GCP Vertex AI, Azure ML compared.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=40,
                    xp_reward=200,
                ),
                CourseModule(
                    title="Model Serving & APIs",
                    description="Deploy open-source models as REST APIs with FastAPI.",
                    teaching_mode=TeachingMode.CODING_LAB,
                    duration_minutes=90,
                    xp_reward=500,
                ),
                CourseModule(
                    title="Vector Databases & RAG",
                    description="Build retrieval-augmented generation pipelines with Pinecone/Weaviate.",
                    teaching_mode=TeachingMode.CODING_LAB,
                    duration_minutes=90,
                    xp_reward=500,
                ),
                CourseModule(
                    title="Cost Optimisation Strategies",
                    description="Batching, caching, and model selection for cost-efficient inference.",
                    teaching_mode=TeachingMode.READING,
                    duration_minutes=30,
                    xp_reward=200,
                ),
            ],
        ),
        # ── Level 8 — AI Research ─────────────────────────────────────────
        CourseLevel(
            level_number=8,
            title="AI Research",
            description=(
                "Conduct AI experiments, interpret research papers, fine-tune "
                "models, and contribute to the open-source AI community."
            ),
            prerequisite_level=7,
            certificate_name="DreamCo AI Research Practitioner Certificate",
            modules=[
                CourseModule(
                    title="Reading AI Research Papers",
                    description="Decoding transformer architecture and attention mechanism papers.",
                    teaching_mode=TeachingMode.READING,
                    duration_minutes=60,
                    xp_reward=300,
                ),
                CourseModule(
                    title="Fine-Tuning LLMs",
                    description="LoRA and QLoRA fine-tuning on custom datasets.",
                    teaching_mode=TeachingMode.CODING_LAB,
                    duration_minutes=120,
                    xp_reward=600,
                ),
                CourseModule(
                    title="Experiment Tracking",
                    description="Use Weights & Biases and MLflow to track model experiments.",
                    teaching_mode=TeachingMode.CODING_LAB,
                    duration_minutes=60,
                    xp_reward=300,
                ),
                CourseModule(
                    title="Publishing Your First AI Project",
                    description="Share a model card and demo on Hugging Face Hub.",
                    teaching_mode=TeachingMode.SIMULATION,
                    duration_minutes=60,
                    xp_reward=400,
                ),
            ],
        ),
        # ── Level 9 — AI Company Creation ────────────────────────────────
        CourseLevel(
            level_number=9,
            title="AI Company Creation",
            description=(
                "Turn an AI prototype into a fundable, scalable AI company: "
                "legal setup, fundraising, team building, and go-to-market execution."
            ),
            prerequisite_level=8,
            certificate_name="DreamCo AI Founder Certificate",
            modules=[
                CourseModule(
                    title="AI Company Legal Foundations",
                    description="IP, data licensing, and entity structure for AI startups.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=45,
                    xp_reward=250,
                ),
                CourseModule(
                    title="Fundraising for AI Startups",
                    description="Venture capital, grants, and accelerators for AI companies.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=45,
                    xp_reward=250,
                ),
                CourseModule(
                    title="AI Team Building",
                    description="Hiring AI engineers, data scientists, and product managers.",
                    teaching_mode=TeachingMode.SIMULATION,
                    duration_minutes=60,
                    xp_reward=300,
                ),
                CourseModule(
                    title="Go-To-Market for AI Products",
                    description="Sales, partnerships, and distribution for AI SaaS products.",
                    teaching_mode=TeachingMode.SIMULATION,
                    duration_minutes=90,
                    xp_reward=500,
                ),
            ],
        ),
        # ── Level 10 — AI Superintelligence Architecture ──────────────────
        CourseLevel(
            level_number=10,
            title="AI Superintelligence Architecture",
            description=(
                "Advanced multimodal, multi-agent system design: scalable AI "
                "architectures, alignment research, and the frontier of AGI."
            ),
            prerequisite_level=9,
            certificate_name="DreamCo AI Master Certification",
            modules=[
                CourseModule(
                    title="Multimodal AI System Design",
                    description="Designing systems that combine vision, speech, and language models.",
                    teaching_mode=TeachingMode.VIDEO,
                    duration_minutes=60,
                    xp_reward=400,
                ),
                CourseModule(
                    title="AI Alignment Fundamentals",
                    description="RLHF, constitutional AI, and the alignment problem.",
                    teaching_mode=TeachingMode.READING,
                    duration_minutes=60,
                    xp_reward=400,
                ),
                CourseModule(
                    title="Large-Scale Multi-Agent Systems",
                    description="Orchestrating thousands of specialised agents on global infrastructure.",
                    teaching_mode=TeachingMode.SIMULATION,
                    duration_minutes=120,
                    xp_reward=800,
                ),
                CourseModule(
                    title="The Frontier of AGI",
                    description="Current research trajectories, timelines, and safety considerations.",
                    teaching_mode=TeachingMode.READING,
                    duration_minutes=60,
                    xp_reward=500,
                ),
            ],
        ),
    ]


# ---------------------------------------------------------------------------
# Course Engine
# ---------------------------------------------------------------------------

class AICourseEngineError(Exception):
    """Raised for invalid course engine operations."""


class AICourseEngine:
    """
    DreamCo AI University course management engine.

    Provides access to the 10-level curriculum and tracks per-user
    completion progress.

    Methods
    -------
    get_level(level_number)
        Return the CourseLevel for the given level number.
    list_levels()
        Return all 10 CourseLevel objects.
    complete_module(user_id, level_number, module_title)
        Mark a module as completed for a user.
    get_user_progress(user_id)
        Return the completion state for a user.
    is_level_unlocked(user_id, level_number, max_allowed_level)
        Return True if the user may access the given level.
    """

    def __init__(self) -> None:
        self._levels: list[CourseLevel] = _build_curriculum()
        self._level_map: dict[int, CourseLevel] = {
            lv.level_number: lv for lv in self._levels
        }
        # Tracks completed modules per user: {user_id: {(level, module_title)}}
        self._completions: dict[str, set[tuple[int, str]]] = {}

    # ------------------------------------------------------------------
    # Level access
    # ------------------------------------------------------------------

    def get_level(self, level_number: int) -> CourseLevel:
        """
        Return the CourseLevel for the given *level_number* (1–10).

        Raises
        ------
        AICourseEngineError
            If the level number is out of range.
        """
        if level_number not in self._level_map:
            raise AICourseEngineError(
                f"Level {level_number} does not exist. Valid levels: 1–10."
            )
        return self._level_map[level_number]

    def list_levels(self) -> list[CourseLevel]:
        """Return all 10 CourseLevel objects in order."""
        return list(self._levels)

    # ------------------------------------------------------------------
    # Progress tracking
    # ------------------------------------------------------------------

    def complete_module(
        self,
        user_id: str,
        level_number: int,
        module_title: str,
    ) -> dict:
        """
        Mark *module_title* in *level_number* as completed for *user_id*.

        Returns
        -------
        dict
            Completion summary including XP awarded and level progress.
        """
        level = self.get_level(level_number)
        module = next(
            (m for m in level.modules if m.title == module_title), None
        )
        if module is None:
            raise AICourseEngineError(
                f"Module '{module_title}' not found in Level {level_number}."
            )

        if user_id not in self._completions:
            self._completions[user_id] = set()

        key = (level_number, module_title)
        already_done = key in self._completions[user_id]
        self._completions[user_id].add(key)

        completed_in_level = sum(
            1 for (ln, _) in self._completions[user_id] if ln == level_number
        )
        level_complete = completed_in_level == level.module_count()

        return {
            "user_id": user_id,
            "level_number": level_number,
            "module_title": module_title,
            "xp_awarded": 0 if already_done else module.xp_reward,
            "modules_completed_in_level": completed_in_level,
            "level_complete": level_complete,
            "certificate": level.certificate_name if level_complete else None,
        }

    def get_user_progress(self, user_id: str) -> dict:
        """
        Return a summary of *user_id*'s course progress.

        Returns
        -------
        dict
            Per-level completion counts and total XP earned.
        """
        completed = self._completions.get(user_id, set())
        progress = {}
        total_xp = 0

        for level in self._levels:
            done = [
                m for m in level.modules
                if (level.level_number, m.title) in completed
            ]
            progress[level.level_number] = {
                "title": level.title,
                "modules_completed": len(done),
                "total_modules": level.module_count(),
                "xp_earned": sum(m.xp_reward for m in done),
                "complete": len(done) == level.module_count(),
            }
            total_xp += sum(m.xp_reward for m in done)

        return {"user_id": user_id, "total_xp": total_xp, "levels": progress}

    def is_level_unlocked(
        self,
        user_id: str,
        level_number: int,
        max_allowed_level: int,
    ) -> bool:
        """
        Return True if *user_id* may access *level_number*.

        A level is unlocked when:
        1. It is within the user's subscription ``max_allowed_level``.
        2. The prerequisite level (if any) has been fully completed.
        """
        if level_number > max_allowed_level:
            return False

        level = self.get_level(level_number)
        if level.prerequisite_level is None:
            return True  # Level 1 has no prerequisite

        # Check that the prerequisite level is fully completed
        progress = self.get_user_progress(user_id)
        prereq = progress["levels"].get(level.prerequisite_level, {})
        return prereq.get("complete", False)
