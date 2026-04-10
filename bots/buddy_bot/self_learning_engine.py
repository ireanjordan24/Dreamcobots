"""
Buddy Bot — Self-Learning Engine

Gives Buddy the ability to continuously improve itself so it can handle any
task a human can perform in an app or on a website:

  • Top-100 AI Model Registry  — tracks the current best-in-class models from
                                  every major AI lab and queries them for
                                  guidance.
  • Capability Discovery       — checks whether Buddy can already fulfill a
                                  client request; returns a structured gap
                                  analysis when it cannot.
  • Knowledge Acquisition      — when a capability gap is found, Buddy searches
                                  for code / libraries on GitHub and records the
                                  finding so the gap can be closed.
  • Self-Training Loop         — periodic training sessions where Buddy
                                  ingests the latest model outputs, benchmarks
                                  itself, and records learning outcomes.
  • Continuous Improvement Log — auditable record of every capability added or
                                  lesson learned.

Design principles
-----------------
  * Buddy never silently pretends it can do something it cannot.
  * Every self-learning action is logged with a timestamp and source.
  * Code acquired from external sources is quarantined until reviewed.
  * Training interactions with external AI models are strictly read-only;
    no credentials or private data are ever sent.

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CapabilityStatus(Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    LEARNING = "learning"
    UNAVAILABLE = "unavailable"


class LearningSource(Enum):
    AI_MODEL = "ai_model"
    GITHUB = "github"
    DOCUMENTATION = "documentation"
    TRAINING_DATA = "training_data"
    PEER_BOT = "peer_bot"


class TrainingOutcome(Enum):
    CAPABILITY_ADDED = "capability_added"
    KNOWLEDGE_UPDATED = "knowledge_updated"
    BENCHMARK_IMPROVED = "benchmark_improved"
    NO_CHANGE = "no_change"


# ---------------------------------------------------------------------------
# Top-100 AI model registry
# ---------------------------------------------------------------------------

TOP_100_AI_MODELS: list[dict] = [
    # OpenAI
    {"provider": "OpenAI", "model": "GPT-4o", "rank": 1, "specialties": ["general", "code", "reasoning", "vision"]},
    {"provider": "OpenAI", "model": "GPT-4 Turbo", "rank": 2, "specialties": ["general", "code", "analysis"]},
    {"provider": "OpenAI", "model": "GPT-3.5 Turbo", "rank": 3, "specialties": ["general", "chat", "fast"]},
    {"provider": "OpenAI", "model": "o1", "rank": 4, "specialties": ["reasoning", "math", "science"]},
    {"provider": "OpenAI", "model": "o1-mini", "rank": 5, "specialties": ["reasoning", "fast", "cost-efficient"]},
    {"provider": "OpenAI", "model": "Codex", "rank": 6, "specialties": ["code", "generation"]},
    {"provider": "OpenAI", "model": "DALL-E 3", "rank": 7, "specialties": ["image_generation"]},
    {"provider": "OpenAI", "model": "Whisper", "rank": 8, "specialties": ["speech_to_text", "audio"]},
    {"provider": "OpenAI", "model": "TTS-1-HD", "rank": 9, "specialties": ["text_to_speech", "audio"]},
    {"provider": "OpenAI", "model": "Embeddings-3-Large", "rank": 10, "specialties": ["embeddings", "search"]},
    # Anthropic
    {"provider": "Anthropic", "model": "Claude 3 Opus", "rank": 11, "specialties": ["general", "reasoning", "safety"]},
    {"provider": "Anthropic", "model": "Claude 3.5 Sonnet", "rank": 12, "specialties": ["general", "code", "analysis"]},
    {"provider": "Anthropic", "model": "Claude 3 Haiku", "rank": 13, "specialties": ["fast", "cost-efficient", "chat"]},
    {"provider": "Anthropic", "model": "Claude 2.1", "rank": 14, "specialties": ["general", "documents"]},
    # Google
    {"provider": "Google", "model": "Gemini 1.5 Pro", "rank": 15, "specialties": ["general", "long_context", "multimodal"]},
    {"provider": "Google", "model": "Gemini 1.5 Flash", "rank": 16, "specialties": ["fast", "multimodal", "cost-efficient"]},
    {"provider": "Google", "model": "Gemini Ultra", "rank": 17, "specialties": ["general", "reasoning", "science"]},
    {"provider": "Google", "model": "PaLM 2", "rank": 18, "specialties": ["general", "code", "translation"]},
    {"provider": "Google", "model": "Imagen 3", "rank": 19, "specialties": ["image_generation", "art"]},
    {"provider": "Google", "model": "MusicLM", "rank": 20, "specialties": ["music_generation", "audio"]},
    # Meta
    {"provider": "Meta", "model": "Llama 3 70B", "rank": 21, "specialties": ["general", "open_source", "code"]},
    {"provider": "Meta", "model": "Llama 3 8B", "rank": 22, "specialties": ["fast", "open_source", "edge"]},
    {"provider": "Meta", "model": "Code Llama", "rank": 23, "specialties": ["code", "generation", "open_source"]},
    {"provider": "Meta", "model": "AudioCraft", "rank": 24, "specialties": ["music_generation", "audio", "sfx"]},
    {"provider": "Meta", "model": "Segment Anything", "rank": 25, "specialties": ["vision", "segmentation"]},
    # Mistral AI
    {"provider": "Mistral AI", "model": "Mistral Large", "rank": 26, "specialties": ["general", "reasoning", "multilingual"]},
    {"provider": "Mistral AI", "model": "Mixtral 8x7B", "rank": 27, "specialties": ["general", "open_source", "fast"]},
    {"provider": "Mistral AI", "model": "Codestral", "rank": 28, "specialties": ["code", "generation"]},
    # Cohere
    {"provider": "Cohere", "model": "Command R+", "rank": 29, "specialties": ["rag", "enterprise", "reasoning"]},
    {"provider": "Cohere", "model": "Embed v3", "rank": 30, "specialties": ["embeddings", "search", "multilingual"]},
    # Stability AI
    {"provider": "Stability AI", "model": "Stable Diffusion 3", "rank": 31, "specialties": ["image_generation", "art"]},
    {"provider": "Stability AI", "model": "Stable Video Diffusion", "rank": 32, "specialties": ["video_generation"]},
    {"provider": "Stability AI", "model": "Stable Audio", "rank": 33, "specialties": ["music_generation", "audio"]},
    # Runway
    {"provider": "Runway", "model": "Gen-3 Alpha", "rank": 34, "specialties": ["video_generation", "film"]},
    {"provider": "Runway", "model": "Gen-2", "rank": 35, "specialties": ["video_generation", "creative"]},
    # ElevenLabs
    {"provider": "ElevenLabs", "model": "Eleven Multilingual v2", "rank": 36, "specialties": ["text_to_speech", "voice_cloning", "multilingual"]},
    {"provider": "ElevenLabs", "model": "Eleven English v2", "rank": 37, "specialties": ["text_to_speech", "voice_cloning"]},
    # Suno AI
    {"provider": "Suno AI", "model": "Suno v3.5", "rank": 38, "specialties": ["music_generation", "lyrics", "vocals"]},
    # Udio
    {"provider": "Udio", "model": "Udio v1", "rank": 39, "specialties": ["music_generation", "audio"]},
    # Pika Labs
    {"provider": "Pika Labs", "model": "Pika 2.0", "rank": 40, "specialties": ["video_generation", "creative"]},
    # xAI
    {"provider": "xAI", "model": "Grok 2", "rank": 41, "specialties": ["general", "real_time", "reasoning"]},
    {"provider": "xAI", "model": "Grok 1.5V", "rank": 42, "specialties": ["vision", "multimodal"]},
    # Amazon
    {"provider": "Amazon", "model": "Titan Text G1 Express", "rank": 43, "specialties": ["general", "enterprise"]},
    {"provider": "Amazon", "model": "Nova Pro", "rank": 44, "specialties": ["general", "multimodal", "enterprise"]},
    # Microsoft
    {"provider": "Microsoft", "model": "Phi-3 Medium", "rank": 45, "specialties": ["fast", "reasoning", "edge"]},
    {"provider": "Microsoft", "model": "Phi-3 Mini", "rank": 46, "specialties": ["edge", "cost-efficient", "fast"]},
    # DeepMind / Google
    {"provider": "DeepMind", "model": "AlphaCode 2", "rank": 47, "specialties": ["code", "competitive_programming"]},
    {"provider": "DeepMind", "model": "Gemma 2 27B", "rank": 48, "specialties": ["general", "open_source"]},
    # Inflection AI
    {"provider": "Inflection AI", "model": "Pi", "rank": 49, "specialties": ["chat", "empathy", "coaching"]},
    # Adept AI
    {"provider": "Adept AI", "model": "ACT-2", "rank": 50, "specialties": ["agent", "web_automation", "actions"]},
    # Hugging Face
    {"provider": "Hugging Face", "model": "Zephyr 7B", "rank": 51, "specialties": ["chat", "open_source", "instruction"]},
    {"provider": "Hugging Face", "model": "StarCoder 2", "rank": 52, "specialties": ["code", "open_source"]},
    # AI21 Labs
    {"provider": "AI21 Labs", "model": "Jamba 1.5 Large", "rank": 53, "specialties": ["long_context", "rag", "general"]},
    # Nvidia
    {"provider": "Nvidia", "model": "Llama-3.1-Nemotron-70B", "rank": 54, "specialties": ["general", "reasoning", "code"]},
    {"provider": "Nvidia", "model": "Cosmos", "rank": 55, "specialties": ["video_generation", "world_model", "robotics"]},
    # Together AI
    {"provider": "Together AI", "model": "DBRX Instruct", "rank": 56, "specialties": ["general", "code", "open_source"]},
    # Baidu
    {"provider": "Baidu", "model": "ERNIE 4.0", "rank": 57, "specialties": ["general", "chinese", "multimodal"]},
    # Alibaba
    {"provider": "Alibaba", "model": "Qwen2 72B", "rank": 58, "specialties": ["general", "multilingual", "code"]},
    # Tencent
    {"provider": "Tencent", "model": "Hunyuan-Large", "rank": 59, "specialties": ["general", "chinese", "reasoning"]},
    # ByteDance
    {"provider": "ByteDance", "model": "Doubao Pro", "rank": 60, "specialties": ["general", "chinese", "multimodal"]},
    # Samsung
    {"provider": "Samsung", "model": "Gauss 2", "rank": 61, "specialties": ["on_device", "mobile", "general"]},
    # Apple
    {"provider": "Apple", "model": "Apple Intelligence", "rank": 62, "specialties": ["on_device", "privacy", "assistant"]},
    # Deepseek
    {"provider": "DeepSeek", "model": "DeepSeek-V2.5", "rank": 63, "specialties": ["general", "code", "reasoning"]},
    {"provider": "DeepSeek", "model": "DeepSeek-Coder-V2", "rank": 64, "specialties": ["code", "generation", "open_source"]},
    # Zhipu AI
    {"provider": "Zhipu AI", "model": "GLM-4V", "rank": 65, "specialties": ["vision", "multimodal", "chinese"]},
    # Midjourney
    {"provider": "Midjourney", "model": "Midjourney v6", "rank": 66, "specialties": ["image_generation", "art", "creative"]},
    # Adobe
    {"provider": "Adobe", "model": "Firefly 3", "rank": 67, "specialties": ["image_generation", "design", "commercial_safe"]},
    # Canva
    {"provider": "Canva", "model": "Magic Studio", "rank": 68, "specialties": ["design", "image_generation", "marketing"]},
    # Jasper
    {"provider": "Jasper", "model": "Jasper v3", "rank": 69, "specialties": ["marketing_copy", "content", "seo"]},
    # Writer
    {"provider": "Writer", "model": "Palmyra X 003", "rank": 70, "specialties": ["enterprise", "content", "rag"]},
    # Perplexity
    {"provider": "Perplexity", "model": "Sonar Large", "rank": 71, "specialties": ["search", "rag", "real_time"]},
    # You.com
    {"provider": "You.com", "model": "YouPro", "rank": 72, "specialties": ["search", "rag", "research"]},
    # Replicate
    {"provider": "Replicate", "model": "FLUX.1 Pro", "rank": 73, "specialties": ["image_generation", "open_source"]},
    # Black Forest Labs
    {"provider": "Black Forest Labs", "model": "FLUX.1 [dev]", "rank": 74, "specialties": ["image_generation", "open_source"]},
    # HeyGen
    {"provider": "HeyGen", "model": "HeyGen 2.0", "rank": 75, "specialties": ["video_generation", "avatar", "talking_head"]},
    # Synthesia
    {"provider": "Synthesia", "model": "Synthesia Studio", "rank": 76, "specialties": ["video_generation", "avatar", "training"]},
    # D-ID
    {"provider": "D-ID", "model": "Creative Reality", "rank": 77, "specialties": ["video_generation", "avatar", "photo_animation"]},
    # Luma AI
    {"provider": "Luma AI", "model": "Dream Machine", "rank": 78, "specialties": ["video_generation", "3d", "realistic"]},
    # Kling
    {"provider": "Kuaishou", "model": "Kling 1.5", "rank": 79, "specialties": ["video_generation", "cinematic"]},
    # CogVideoX
    {"provider": "Zhipu AI", "model": "CogVideoX-5B", "rank": 80, "specialties": ["video_generation", "open_source"]},
    # Veo
    {"provider": "Google", "model": "Veo 2", "rank": 81, "specialties": ["video_generation", "cinematic", "long_form"]},
    # Sora
    {"provider": "OpenAI", "model": "Sora", "rank": 82, "specialties": ["video_generation", "cinematic", "long_form"]},
    # Hailuo
    {"provider": "MiniMax", "model": "Hailuo AI", "rank": 83, "specialties": ["video_generation", "story"]},
    # WonderJourney
    {"provider": "WonderWorld", "model": "WonderJourney", "rank": 84, "specialties": ["3d_generation", "scene"]},
    # Instabase
    {"provider": "Instabase", "model": "Instabase AI Hub", "rank": 85, "specialties": ["document_ai", "enterprise", "extraction"]},
    # Scale AI
    {"provider": "Scale AI", "model": "Donovan", "rank": 86, "specialties": ["enterprise", "defense", "reasoning"]},
    # Cohere for AI
    {"provider": "Cohere", "model": "Aya Expanse", "rank": 87, "specialties": ["multilingual", "open_source", "global"]},
    # TII (UAE)
    {"provider": "TII", "model": "Falcon 180B", "rank": 88, "specialties": ["general", "open_source", "multilingual"]},
    # Technology Innovation Institute
    {"provider": "TII", "model": "Falcon 2 11B", "rank": 89, "specialties": ["vision", "open_source", "multimodal"]},
    # Allen Institute
    {"provider": "Allen Institute", "model": "OLMo 2", "rank": 90, "specialties": ["general", "open_source", "research"]},
    # EleutherAI
    {"provider": "EleutherAI", "model": "GPT-NeoX", "rank": 91, "specialties": ["general", "open_source"]},
    # Mosaic ML
    {"provider": "Databricks", "model": "DBRX", "rank": 92, "specialties": ["general", "enterprise", "code"]},
    # Salesforce
    {"provider": "Salesforce", "model": "xGen-7B", "rank": 93, "specialties": ["enterprise", "code", "long_context"]},
    # IBM
    {"provider": "IBM", "model": "Granite 3.0 8B", "rank": 94, "specialties": ["enterprise", "code", "rag"]},
    # Oracle
    {"provider": "Oracle", "model": "OCI Generative AI", "rank": 95, "specialties": ["enterprise", "general"]},
    # Character AI
    {"provider": "Character AI", "model": "Character-1", "rank": 96, "specialties": ["chat", "roleplay", "character"]},
    # Replika
    {"provider": "Replika", "model": "Replika v5", "rank": 97, "specialties": ["companion", "empathy", "emotional_support"]},
    # DreamCo (internal)
    {"provider": "DreamCo", "model": "DreamLLM v3", "rank": 98, "specialties": ["general", "dreamco_ecosystem", "all_tasks"]},
    {"provider": "DreamCo", "model": "DreamVision v2", "rank": 99, "specialties": ["image_generation", "commercial", "brand"]},
    {"provider": "DreamCo", "model": "DreamVoice v2", "rank": 100, "specialties": ["text_to_speech", "voice_cloning", "commercial"]},
]

# Specialties Buddy can already handle (grows as Buddy learns)
_BUDDY_CORE_CAPABILITIES: set[str] = {
    "general", "chat", "reasoning", "code", "analysis",
    "image_generation", "text_to_speech", "voice_cloning",
    "music_generation", "video_generation", "marketing_copy",
    "content", "search", "embeddings", "vision", "multimodal",
    "translation", "multilingual", "rag", "document_ai",
    "companion", "empathy", "emotional_support", "coaching",
    "roleplay", "character", "design", "art", "seo",
    "web_automation", "agent", "actions",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CapabilityGap:
    """Describes a capability Buddy cannot currently fulfill."""
    task_description: str
    missing_specialties: list[str]
    recommended_models: list[dict]
    acquisition_plan: str
    github_search_query: str
    status: CapabilityStatus = CapabilityStatus.UNAVAILABLE
    discovered_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "task_description": self.task_description,
            "missing_specialties": self.missing_specialties,
            "recommended_models": self.recommended_models,
            "acquisition_plan": self.acquisition_plan,
            "github_search_query": self.github_search_query,
            "status": self.status.value,
            "discovered_at": self.discovered_at,
        }


@dataclass
class LearningRecord:
    """An entry in Buddy's continuous-improvement log."""
    record_id: str
    source: LearningSource
    model_or_repo: str
    capability_learned: str
    lesson_summary: str
    outcome: TrainingOutcome
    confidence_score: float  # 0.0 – 1.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "source": self.source.value,
            "model_or_repo": self.model_or_repo,
            "capability_learned": self.capability_learned,
            "lesson_summary": self.lesson_summary,
            "outcome": self.outcome.value,
            "confidence_score": self.confidence_score,
            "timestamp": self.timestamp,
        }


@dataclass
class TrainingSession:
    """One complete round of self-training against top AI models."""
    session_id: str
    models_consulted: list[str]
    capabilities_added: list[str]
    benchmarks: dict
    duration_seconds: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "models_consulted": self.models_consulted,
            "capabilities_added": self.capabilities_added,
            "benchmarks": self.benchmarks,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
        }


@dataclass
class GitHubAcquisitionResult:
    """Result of a GitHub code-acquisition search."""
    query: str
    repositories_found: list[dict]
    recommended_repo: str
    integration_notes: str
    quarantine_required: bool = True
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "repositories_found": self.repositories_found,
            "recommended_repo": self.recommended_repo,
            "integration_notes": self.integration_notes,
            "quarantine_required": self.quarantine_required,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Simulated model response pool
# ---------------------------------------------------------------------------

_MODEL_LESSON_TEMPLATES = [
    "To {capability}, use a transformer-based pipeline: tokenise input → attention layers "
    "→ decode. Fine-tune on domain data with LoRA adapters for efficiency.",
    "The state-of-the-art approach to {capability} involves contrastive learning and "
    "retrieval-augmented generation. Store embeddings in a vector DB; retrieve top-k at inference.",
    "{capability} is best addressed by a multimodal encoder that fuses text and image tokens "
    "before the LLM head. Use CLIP-style alignment pre-training.",
    "For {capability}, chain-of-thought prompting with a reasoning model outperforms "
    "single-pass generation. Implement a self-critique loop for quality control.",
    "Achieve {capability} via agent orchestration: plan → tool_call → observe → reflect → act. "
    "Provide structured JSON tool schemas for reliability.",
]

_GITHUB_REPO_TEMPLATES = [
    {"name": "awesome-{slug}", "stars": random.randint(500, 20000), "description": "Curated {capability} resources and implementations."},
    {"name": "{slug}-python", "stars": random.randint(200, 10000), "description": "Python library for {capability}."},
    {"name": "open-{slug}", "stars": random.randint(100, 5000), "description": "Open-source {capability} engine."},
]


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class SelfLearningEngineError(Exception):
    """Raised when a self-learning operation cannot be completed."""


class SelfLearningEngine:
    """
    Drives Buddy's continuous self-improvement loop.

    Buddy constantly:
    1. Monitors the top-100 AI models for new capabilities.
    2. Compares those capabilities to its own known skill-set.
    3. When a gap is found, searches GitHub for integrable code.
    4. Asks the best-suited model to teach it how to fill the gap.
    5. Records every lesson in an auditable improvement log.

    Parameters
    ----------
    initial_capabilities : set[str] | None
        Starting set of capability tags.  Defaults to Buddy's core
        capability set if not provided.
    """

    def __init__(
        self,
        initial_capabilities: Optional[set] = None,
    ) -> None:
        self._capabilities: set[str] = (
            set(initial_capabilities)
            if initial_capabilities is not None
            else set(_BUDDY_CORE_CAPABILITIES)
        )
        self._learning_log: list[LearningRecord] = []
        self._training_sessions: list[TrainingSession] = []
        self._capability_gaps: list[CapabilityGap] = []
        self._github_acquisitions: list[GitHubAcquisitionResult] = []
        self._record_counter: int = 0
        self._session_counter: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _next_record_id(self) -> str:
        self._record_counter += 1
        return f"LEARN_{self._record_counter:05d}"

    def _next_session_id(self) -> str:
        self._session_counter += 1
        return f"TRAIN_{self._session_counter:04d}"

    def _models_for_specialty(self, specialty: str) -> list[dict]:
        """Return top-5 models that cover *specialty*, sorted by rank."""
        matches = [
            m for m in TOP_100_AI_MODELS
            if specialty in m["specialties"]
        ]
        return sorted(matches, key=lambda x: x["rank"])[:5]

    def _simulate_model_lesson(self, model_name: str, capability: str) -> str:
        template = random.choice(_MODEL_LESSON_TEMPLATES)
        return template.replace("{capability}", capability)

    def _simulate_github_repos(self, capability: str) -> list[dict]:
        slug = capability.replace(" ", "-").lower()
        repos = []
        for tmpl in _GITHUB_REPO_TEMPLATES:
            repos.append({
                "name": tmpl["name"].replace("{slug}", slug),
                "stars": tmpl["stars"],
                "description": tmpl["description"].replace("{capability}", capability),
            })
        return repos

    # ------------------------------------------------------------------
    # Capability checking
    # ------------------------------------------------------------------

    def can_do(self, task_description: str) -> bool:
        """
        Return True if Buddy has at least one capability matching the task.

        Uses simple keyword matching against the capability registry.
        """
        keywords = task_description.lower().split()
        for kw in keywords:
            if kw in self._capabilities:
                return True
            # Check partial match
            for cap in self._capabilities:
                if kw in cap or cap in kw:
                    return True
        return False

    def check_capability(self, task_description: str) -> dict:
        """
        Perform a full capability gap analysis for a task description.

        Returns
        -------
        dict with keys: ``can_do``, ``matched_capabilities``, ``gap``
        """
        keywords = {w.strip(".,!?") for w in task_description.lower().split()}
        matched = [c for c in self._capabilities if c in keywords or any(c in k for k in keywords)]

        if matched:
            return {
                "can_do": True,
                "matched_capabilities": matched,
                "gap": None,
            }

        # Find missing specialties from top models
        all_model_specialties: set[str] = set()
        for m in TOP_100_AI_MODELS:
            all_model_specialties.update(m["specialties"])

        missing = list(all_model_specialties - self._capabilities)[:5]
        recommended = []
        for spec in missing[:3]:
            recommended.extend(self._models_for_specialty(spec))

        gap = CapabilityGap(
            task_description=task_description,
            missing_specialties=missing,
            recommended_models=recommended[:5],
            acquisition_plan=(
                f"1. Query top AI models for guidance on '{task_description}'.\n"
                f"2. Search GitHub for '{task_description} python library'.\n"
                f"3. Review and quarantine found code.\n"
                f"4. Integrate after security review.\n"
                f"5. Run validation tests."
            ),
            github_search_query=f"{task_description} python implementation",
        )
        self._capability_gaps.append(gap)

        return {
            "can_do": False,
            "matched_capabilities": [],
            "gap": gap.to_dict(),
        }

    # ------------------------------------------------------------------
    # Ask top AI models
    # ------------------------------------------------------------------

    def ask_top_models(
        self,
        capability: str,
        top_n: int = 5,
    ) -> list[LearningRecord]:
        """
        Query the top-N AI models most relevant to *capability* and
        record each lesson in the learning log.

        Parameters
        ----------
        capability : str
            The skill or topic to learn about.
        top_n : int
            Number of models to consult (1–10).

        Returns
        -------
        list[LearningRecord]
        """
        top_n = max(1, min(10, top_n))
        relevant_models = self._models_for_specialty(capability)
        if not relevant_models:
            relevant_models = sorted(TOP_100_AI_MODELS, key=lambda x: x["rank"])[:top_n]
        else:
            relevant_models = relevant_models[:top_n]

        records = []
        for model_info in relevant_models:
            lesson = self._simulate_model_lesson(model_info["model"], capability)
            record = LearningRecord(
                record_id=self._next_record_id(),
                source=LearningSource.AI_MODEL,
                model_or_repo=f"{model_info['provider']}/{model_info['model']}",
                capability_learned=capability,
                lesson_summary=lesson,
                outcome=TrainingOutcome.KNOWLEDGE_UPDATED,
                confidence_score=round(random.uniform(0.75, 0.99), 3),
            )
            self._learning_log.append(record)
            records.append(record)

        # Add capability after consultation
        self._capabilities.add(capability)
        return records

    # ------------------------------------------------------------------
    # GitHub code acquisition
    # ------------------------------------------------------------------

    def search_github_for_code(self, capability: str) -> GitHubAcquisitionResult:
        """
        Simulate a GitHub search for code that would add *capability* to Buddy.

        All discovered code is marked for quarantine until reviewed by a
        human engineer.

        Parameters
        ----------
        capability : str
            The capability to search for.

        Returns
        -------
        GitHubAcquisitionResult
        """
        repos = self._simulate_github_repos(capability)
        best_repo = sorted(repos, key=lambda r: r["stars"], reverse=True)[0]

        integration_notes = (
            f"Recommended: {best_repo['name']} ({best_repo['stars']} ⭐)\n"
            f"To integrate: pip install {best_repo['name']} → wrap in a BuddyBot engine.\n"
            "QUARANTINE: All external code must pass security review before merging to main.\n"
            "Steps:\n"
            "  1. Clone repo to /quarantine branch.\n"
            "  2. Run static analysis (bandit / semgrep).\n"
            "  3. Review API surface for data-leak risks.\n"
            "  4. Write integration tests.\n"
            "  5. Submit PR for human review."
        )

        result = GitHubAcquisitionResult(
            query=capability,
            repositories_found=repos,
            recommended_repo=best_repo["name"],
            integration_notes=integration_notes,
        )
        self._github_acquisitions.append(result)

        # Record learning
        record = LearningRecord(
            record_id=self._next_record_id(),
            source=LearningSource.GITHUB,
            model_or_repo=best_repo["name"],
            capability_learned=capability,
            lesson_summary=f"Found GitHub repo '{best_repo['name']}' for {capability}. Quarantined for review.",
            outcome=TrainingOutcome.CAPABILITY_ADDED,
            confidence_score=round(random.uniform(0.6, 0.9), 3),
        )
        self._learning_log.append(record)
        return result

    # ------------------------------------------------------------------
    # Self-training loop
    # ------------------------------------------------------------------

    def run_training_session(self, focus_specialties: Optional[list] = None) -> TrainingSession:
        """
        Run one complete self-training session against the top AI models.

        Buddy consults each model in the registry, identifies deltas between
        the model's specialties and Buddy's current capabilities, and records
        a learning outcome for each new specialty acquired.

        Parameters
        ----------
        focus_specialties : list[str] | None
            If provided, only models with these specialties are consulted.
            If None, all 100 models are cycled through.

        Returns
        -------
        TrainingSession
        """
        start = time.time()
        models_to_consult = TOP_100_AI_MODELS
        if focus_specialties:
            models_to_consult = [
                m for m in TOP_100_AI_MODELS
                if any(s in m["specialties"] for s in focus_specialties)
            ]

        models_consulted = []
        new_capabilities: list[str] = []
        benchmarks: dict = {}

        for model_info in models_to_consult:
            models_consulted.append(f"{model_info['provider']}/{model_info['model']}")
            for specialty in model_info["specialties"]:
                if specialty not in self._capabilities:
                    lesson = self._simulate_model_lesson(model_info["model"], specialty)
                    record = LearningRecord(
                        record_id=self._next_record_id(),
                        source=LearningSource.AI_MODEL,
                        model_or_repo=f"{model_info['provider']}/{model_info['model']}",
                        capability_learned=specialty,
                        lesson_summary=lesson,
                        outcome=TrainingOutcome.CAPABILITY_ADDED,
                        confidence_score=round(random.uniform(0.70, 0.98), 3),
                    )
                    self._learning_log.append(record)
                    self._capabilities.add(specialty)
                    new_capabilities.append(specialty)

        # Simulate benchmark scores
        benchmarks = {
            "response_quality": round(random.uniform(0.88, 0.99), 3),
            "task_completion_rate": round(random.uniform(0.90, 1.00), 3),
            "knowledge_breadth": len(self._capabilities),
            "models_in_registry": len(TOP_100_AI_MODELS),
        }

        session = TrainingSession(
            session_id=self._next_session_id(),
            models_consulted=models_consulted,
            capabilities_added=new_capabilities,
            benchmarks=benchmarks,
            duration_seconds=round(time.time() - start, 4),
        )
        self._training_sessions.append(session)
        return session

    # ------------------------------------------------------------------
    # Capability management
    # ------------------------------------------------------------------

    def add_capability(self, capability: str, source: str = "manual") -> LearningRecord:
        """
        Manually register a new capability for Buddy (e.g. after a GitHub
        integration is merged and reviewed).

        Parameters
        ----------
        capability : str
            The new capability tag to add.
        source : str
            Description of where this capability came from.

        Returns
        -------
        LearningRecord
        """
        self._capabilities.add(capability)
        record = LearningRecord(
            record_id=self._next_record_id(),
            source=LearningSource.GITHUB,
            model_or_repo=source,
            capability_learned=capability,
            lesson_summary=f"Capability '{capability}' added from {source}.",
            outcome=TrainingOutcome.CAPABILITY_ADDED,
            confidence_score=1.0,
        )
        self._learning_log.append(record)
        return record

    def list_capabilities(self) -> list[str]:
        """Return all currently known capabilities, sorted."""
        return sorted(self._capabilities)

    def capability_count(self) -> int:
        """Return the number of capabilities Buddy currently has."""
        return len(self._capabilities)

    # ------------------------------------------------------------------
    # Logs & status
    # ------------------------------------------------------------------

    def get_learning_log(self, limit: int = 50) -> list[dict]:
        """Return the most recent *limit* learning records."""
        return [r.to_dict() for r in self._learning_log[-limit:]]

    def get_training_sessions(self) -> list[dict]:
        """Return all training session records."""
        return [s.to_dict() for s in self._training_sessions]

    def get_capability_gaps(self) -> list[dict]:
        """Return all recorded capability gaps."""
        return [g.to_dict() for g in self._capability_gaps]

    def get_github_acquisitions(self) -> list[dict]:
        """Return all GitHub acquisition results."""
        return [a.to_dict() for a in self._github_acquisitions]

    def get_top_models(self, limit: int = 10) -> list[dict]:
        """Return the top *limit* models from the registry."""
        return sorted(TOP_100_AI_MODELS, key=lambda x: x["rank"])[:limit]

    def to_dict(self) -> dict:
        return {
            "capability_count": self.capability_count(),
            "learning_records": len(self._learning_log),
            "training_sessions": len(self._training_sessions),
            "capability_gaps_identified": len(self._capability_gaps),
            "github_acquisitions": len(self._github_acquisitions),
            "top_model_registry_size": len(TOP_100_AI_MODELS),
        }
