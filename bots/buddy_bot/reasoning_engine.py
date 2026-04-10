"""
Buddy Bot — Reasoning Engine

Provides intelligent AI model selection for every task BuddyBot performs.
The engine maintains a curated registry of 100 leading AI models, each with
documented strengths, weaknesses, and optimal use-cases.  On every reasoning
request it:

  1. Identifies the task type (coding, creative writing, analysis, …)
  2. Scores each of the top-5 models against that task type
  3. Returns the best-matched model along with a human-readable rationale

Top-5 models (selected from the full 100-model registry by composite score):
  1. Claude Mythos (Anthropic)  — most advanced coding & reasoning model
  2. GPT-4o (OpenAI)            — best multimodal & general-purpose model
  3. Gemini 1.5 Ultra (Google)  — longest context window & research depth
  4. Claude 3.5 Sonnet (Anthropic) — creative writing & nuanced analysis
  5. Llama 3.1 405B (Meta)      — best open-source, privacy-first model

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Task types
# ---------------------------------------------------------------------------

class TaskType(Enum):
    CODING = "coding"
    CREATIVE_WRITING = "creative_writing"
    ANALYSIS = "analysis"
    CONVERSATION = "conversation"
    MATH_REASONING = "math_reasoning"
    RESEARCH = "research"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    BRAINSTORMING = "brainstorming"
    IMAGE_DESCRIPTION = "image_description"
    EMOTIONAL_SUPPORT = "emotional_support"
    GENERAL = "general"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class AIModel:
    """Represents a single AI model in the registry.

    Attributes
    ----------
    model_id : str
        Unique identifier (e.g. ``"claude_mythos"``).
    name : str
        Display name.
    provider : str
        Company / organisation that created the model.
    version : str
        Model version string.
    pros : list[str]
        Key strengths.
    cons : list[str]
        Known limitations.
    best_for : list[TaskType]
        Task types this model excels at.
    context_window_k : int
        Approximate context window in thousands of tokens.
    is_multimodal : bool
        Whether the model accepts non-text inputs (images, audio, …).
    is_open_source : bool
        Whether model weights are publicly available.
    composite_score : float
        Internal quality score 0–100 used to rank the top-5.
    """

    model_id: str
    name: str
    provider: str
    version: str
    pros: list
    cons: list
    best_for: list
    context_window_k: int
    is_multimodal: bool
    is_open_source: bool
    composite_score: float

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "provider": self.provider,
            "version": self.version,
            "pros": self.pros,
            "cons": self.cons,
            "best_for": [t.value for t in self.best_for],
            "context_window_k": self.context_window_k,
            "is_multimodal": self.is_multimodal,
            "is_open_source": self.is_open_source,
            "composite_score": self.composite_score,
        }


@dataclass
class ModelSelectionResult:
    """Result of a model selection operation.

    Attributes
    ----------
    selected_model : AIModel
        The model chosen for the task.
    task_type : TaskType
        The resolved task type.
    rationale : str
        Human-readable explanation of why this model was selected.
    runner_up : AIModel | None
        Second-best option, if any.
    score : float
        Selection confidence score (0–100).
    """

    selected_model: AIModel
    task_type: TaskType
    rationale: str
    runner_up: Optional[AIModel]
    score: float

    def to_dict(self) -> dict:
        return {
            "selected_model": self.selected_model.to_dict(),
            "task_type": self.task_type.value,
            "rationale": self.rationale,
            "runner_up": self.runner_up.to_dict() if self.runner_up else None,
            "score": self.score,
        }


# ---------------------------------------------------------------------------
# Full 100-model registry
# ---------------------------------------------------------------------------

def _build_model_registry() -> list:
    """Build and return the full registry of 100 AI models."""
    return [
        # ── Top 5 (composite_score ≥ 95) ──────────────────────────────────
        AIModel(
            model_id="claude_mythos",
            name="Claude Mythos",
            provider="Anthropic",
            version="1.0",
            pros=[
                "Most advanced coding model ever released",
                "Near-perfect multi-step reasoning chains",
                "Exceptional at debugging and explaining code",
                "Highest HumanEval + SWE-bench scores",
                "Long 200 K context window",
                "Strong safety alignment",
            ],
            cons=[
                "Newest model — limited community tooling",
                "Premium API pricing",
                "Not open-source",
            ],
            best_for=[
                TaskType.CODING,
                TaskType.MATH_REASONING,
                TaskType.ANALYSIS,
            ],
            context_window_k=200,
            is_multimodal=True,
            is_open_source=False,
            composite_score=99.0,
        ),
        AIModel(
            model_id="gpt_4o",
            name="GPT-4o",
            provider="OpenAI",
            version="2024-05",
            pros=[
                "Excellent all-round general intelligence",
                "Native multimodal (text, image, audio, video)",
                "Fastest inference among frontier models",
                "Massive developer ecosystem and tooling",
                "Strong function-calling and tool-use support",
            ],
            cons=[
                "Occasional hallucinations on obscure facts",
                "Context window smaller than Gemini 1.5 Ultra",
                "Closed-source",
                "Can be verbose",
            ],
            best_for=[
                TaskType.GENERAL,
                TaskType.CONVERSATION,
                TaskType.IMAGE_DESCRIPTION,
                TaskType.BRAINSTORMING,
                TaskType.TRANSLATION,
            ],
            context_window_k=128,
            is_multimodal=True,
            is_open_source=False,
            composite_score=97.5,
        ),
        AIModel(
            model_id="gemini_1_5_ultra",
            name="Gemini 1.5 Ultra",
            provider="Google DeepMind",
            version="1.5",
            pros=[
                "Industry-leading 1 M-token context window",
                "Best-in-class for long-document analysis",
                "Superb multilingual coverage (100+ languages)",
                "Native audio/video understanding",
                "Tight Google Workspace integration",
            ],
            cons=[
                "Slower on short interactive tasks",
                "Some reasoning gaps vs. Claude Mythos on code",
                "Closed-source",
            ],
            best_for=[
                TaskType.RESEARCH,
                TaskType.SUMMARIZATION,
                TaskType.TRANSLATION,
                TaskType.ANALYSIS,
                TaskType.IMAGE_DESCRIPTION,
            ],
            context_window_k=1000,
            is_multimodal=True,
            is_open_source=False,
            composite_score=96.5,
        ),
        AIModel(
            model_id="claude_3_5_sonnet",
            name="Claude 3.5 Sonnet",
            provider="Anthropic",
            version="3.5",
            pros=[
                "Best creative writing quality among all models",
                "Nuanced emotional intelligence",
                "Excellent at structured analysis and reports",
                "Reliable instruction-following",
                "Very low hallucination rate",
            ],
            cons=[
                "Not the strongest pure-code model",
                "Slower than GPT-4o on short tasks",
                "No native image generation",
            ],
            best_for=[
                TaskType.CREATIVE_WRITING,
                TaskType.EMOTIONAL_SUPPORT,
                TaskType.ANALYSIS,
                TaskType.SUMMARIZATION,
                TaskType.BRAINSTORMING,
            ],
            context_window_k=200,
            is_multimodal=True,
            is_open_source=False,
            composite_score=95.5,
        ),
        AIModel(
            model_id="llama_3_1_405b",
            name="Llama 3.1 405B",
            provider="Meta AI",
            version="3.1",
            pros=[
                "Best open-source model available",
                "Fully self-hostable — complete data privacy",
                "Strong reasoning for an open model",
                "Large 128 K context window",
                "Free to run locally",
                "Highly customisable via fine-tuning",
            ],
            cons=[
                "Requires significant GPU resources to self-host",
                "Slightly behind frontier closed models on benchmarks",
                "No native multimodal support in base version",
            ],
            best_for=[
                TaskType.CODING,
                TaskType.GENERAL,
                TaskType.ANALYSIS,
                TaskType.RESEARCH,
                TaskType.CONVERSATION,
            ],
            context_window_k=128,
            is_multimodal=False,
            is_open_source=True,
            composite_score=95.0,
        ),
        # ── Models 6–20 (composite_score 80–94) ───────────────────────────
        AIModel(
            model_id="gpt_4_turbo",
            name="GPT-4 Turbo",
            provider="OpenAI",
            version="2024-04",
            pros=["Reliable, well-tested", "Great plugin/tool ecosystem", "Strong JSON mode"],
            cons=["Older than GPT-4o", "Higher latency than GPT-4o"],
            best_for=[TaskType.CODING, TaskType.ANALYSIS, TaskType.GENERAL],
            context_window_k=128,
            is_multimodal=True,
            is_open_source=False,
            composite_score=93.0,
        ),
        AIModel(
            model_id="claude_3_opus",
            name="Claude 3 Opus",
            provider="Anthropic",
            version="3.0",
            pros=["Deep philosophical reasoning", "Highly nuanced writing"],
            cons=["Slow inference", "Expensive"],
            best_for=[TaskType.CREATIVE_WRITING, TaskType.ANALYSIS, TaskType.EMOTIONAL_SUPPORT],
            context_window_k=200,
            is_multimodal=True,
            is_open_source=False,
            composite_score=92.0,
        ),
        AIModel(
            model_id="gemini_1_5_pro",
            name="Gemini 1.5 Pro",
            provider="Google DeepMind",
            version="1.5",
            pros=["1 M context window", "Strong multimodal", "Good for coding"],
            cons=["Slightly behind Gemini Ultra on quality"],
            best_for=[TaskType.RESEARCH, TaskType.SUMMARIZATION, TaskType.CODING],
            context_window_k=1000,
            is_multimodal=True,
            is_open_source=False,
            composite_score=91.5,
        ),
        AIModel(
            model_id="mistral_large",
            name="Mistral Large",
            provider="Mistral AI",
            version="2.0",
            pros=["Excellent European data compliance", "Strong multilingual", "Fast"],
            cons=["Smaller than GPT-4o", "Fewer tools"],
            best_for=[TaskType.TRANSLATION, TaskType.ANALYSIS, TaskType.GENERAL],
            context_window_k=128,
            is_multimodal=False,
            is_open_source=False,
            composite_score=90.0,
        ),
        AIModel(
            model_id="command_r_plus",
            name="Command R+",
            provider="Cohere",
            version="1.0",
            pros=["Best RAG/retrieval augmented generation", "Enterprise search"],
            cons=["Less creative than Claude", "Narrower general use"],
            best_for=[TaskType.RESEARCH, TaskType.SUMMARIZATION, TaskType.ANALYSIS],
            context_window_k=128,
            is_multimodal=False,
            is_open_source=False,
            composite_score=89.0,
        ),
        AIModel(
            model_id="deepseek_r1",
            name="DeepSeek R1",
            provider="DeepSeek",
            version="1.0",
            pros=["Exceptional math and science reasoning", "Open weights", "Cost-efficient"],
            cons=["Limited creative tasks", "Chinese-first training"],
            best_for=[TaskType.MATH_REASONING, TaskType.CODING, TaskType.RESEARCH],
            context_window_k=64,
            is_multimodal=False,
            is_open_source=True,
            composite_score=88.5,
        ),
        AIModel(
            model_id="qwen_2_5_72b",
            name="Qwen 2.5 72B",
            provider="Alibaba Cloud",
            version="2.5",
            pros=["Best-in-class for Chinese/Asian languages", "Strong code gen", "Open-source"],
            cons=["Less polished English output", "Smaller ecosystem"],
            best_for=[TaskType.CODING, TaskType.TRANSLATION, TaskType.ANALYSIS],
            context_window_k=128,
            is_multimodal=False,
            is_open_source=True,
            composite_score=87.5,
        ),
        AIModel(
            model_id="phi_3_5_moe",
            name="Phi-3.5 MoE",
            provider="Microsoft",
            version="3.5",
            pros=["Extremely efficient (Mixture of Experts)", "Great for edge deployment", "Low cost"],
            cons=["Not suited for complex long-form writing"],
            best_for=[TaskType.CODING, TaskType.MATH_REASONING, TaskType.GENERAL],
            context_window_k=128,
            is_multimodal=False,
            is_open_source=True,
            composite_score=86.0,
        ),
        AIModel(
            model_id="nova_pro",
            name="Amazon Nova Pro",
            provider="Amazon",
            version="1.0",
            pros=["Deep AWS integration", "Multimodal", "Cost-effective on AWS"],
            cons=["Newer, less proven", "AWS lock-in"],
            best_for=[TaskType.GENERAL, TaskType.ANALYSIS, TaskType.IMAGE_DESCRIPTION],
            context_window_k=300,
            is_multimodal=True,
            is_open_source=False,
            composite_score=85.0,
        ),
        AIModel(
            model_id="pixtral_large",
            name="Pixtral Large",
            provider="Mistral AI",
            version="1.0",
            pros=["Best vision/image understanding from Mistral", "European compliance"],
            cons=["Less strong on pure text tasks"],
            best_for=[TaskType.IMAGE_DESCRIPTION, TaskType.ANALYSIS],
            context_window_k=128,
            is_multimodal=True,
            is_open_source=False,
            composite_score=84.0,
        ),
        AIModel(
            model_id="yi_large",
            name="Yi-Large",
            provider="01.AI",
            version="1.0",
            pros=["Strong Chinese + English bilingual", "Good reasoning"],
            cons=["Limited third-party tooling"],
            best_for=[TaskType.TRANSLATION, TaskType.ANALYSIS, TaskType.RESEARCH],
            context_window_k=200,
            is_multimodal=False,
            is_open_source=False,
            composite_score=83.0,
        ),
        AIModel(
            model_id="dbrx_instruct",
            name="DBRX Instruct",
            provider="Databricks",
            version="1.0",
            pros=["Enterprise data platform native", "Open weights", "Good for data tasks"],
            cons=["Less conversational", "Niche use-case focus"],
            best_for=[TaskType.ANALYSIS, TaskType.RESEARCH, TaskType.CODING],
            context_window_k=32,
            is_multimodal=False,
            is_open_source=True,
            composite_score=82.0,
        ),
        AIModel(
            model_id="inflection_3",
            name="Inflection-3",
            provider="Inflection AI",
            version="3.0",
            pros=["Highest emotional intelligence", "Best personal AI companion feel"],
            cons=["Limited tool-calling", "Less capable on hard coding"],
            best_for=[TaskType.EMOTIONAL_SUPPORT, TaskType.CONVERSATION, TaskType.CREATIVE_WRITING],
            context_window_k=32,
            is_multimodal=False,
            is_open_source=False,
            composite_score=81.0,
        ),
        AIModel(
            model_id="grok_2",
            name="Grok-2",
            provider="xAI",
            version="2.0",
            pros=["Real-time X/Twitter data access", "Irreverent humor", "Fast"],
            cons=["Inconsistent safety guardrails", "Less proven on academic tasks"],
            best_for=[TaskType.CONVERSATION, TaskType.BRAINSTORMING, TaskType.GENERAL],
            context_window_k=128,
            is_multimodal=True,
            is_open_source=False,
            composite_score=80.5,
        ),
        # ── Models 21–40 (composite_score 70–79) ──────────────────────────
        AIModel(
            model_id="llama_3_1_70b",
            name="Llama 3.1 70B",
            provider="Meta AI",
            version="3.1",
            pros=["Lightweight open-source", "Fast inference", "Good for most tasks"],
            cons=["Weaker than 405B on hard reasoning"],
            best_for=[TaskType.GENERAL, TaskType.CODING, TaskType.CONVERSATION],
            context_window_k=128,
            is_multimodal=False,
            is_open_source=True,
            composite_score=79.5,
        ),
        AIModel(
            model_id="mixtral_8x22b",
            name="Mixtral 8×22B",
            provider="Mistral AI",
            version="1.0",
            pros=["Efficient MoE architecture", "Open-source", "Good multilingual"],
            cons=["Less polished than Mistral Large"],
            best_for=[TaskType.CODING, TaskType.ANALYSIS, TaskType.TRANSLATION],
            context_window_k=64,
            is_multimodal=False,
            is_open_source=True,
            composite_score=78.5,
        ),
        AIModel(
            model_id="gemma_2_27b",
            name="Gemma 2 27B",
            provider="Google DeepMind",
            version="2.0",
            pros=["Compact, deployable on consumer hardware", "Open weights", "Good reasoning"],
            cons=["No multimodal", "Context window limited"],
            best_for=[TaskType.GENERAL, TaskType.CODING, TaskType.MATH_REASONING],
            context_window_k=8,
            is_multimodal=False,
            is_open_source=True,
            composite_score=77.5,
        ),
        AIModel(
            model_id="solar_pro",
            name="SOLAR Pro",
            provider="Upstage",
            version="1.0",
            pros=["Top Korean/English bilingual", "Strong instruction following"],
            cons=["Limited to Korean/English primarily"],
            best_for=[TaskType.TRANSLATION, TaskType.ANALYSIS, TaskType.CONVERSATION],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=False,
            composite_score=76.0,
        ),
        AIModel(
            model_id="falcon_180b",
            name="Falcon 180B",
            provider="TII UAE",
            version="1.0",
            pros=["Large open-source model", "Good for Arabic tasks", "Self-hostable"],
            cons=["Older, less efficient than newer models"],
            best_for=[TaskType.TRANSLATION, TaskType.GENERAL, TaskType.RESEARCH],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=75.0,
        ),
        AIModel(
            model_id="internlm_2_5",
            name="InternLM 2.5",
            provider="Shanghai AI Lab",
            version="2.5",
            pros=["Strong on Chinese NLP", "Long context", "Open-source"],
            cons=["Less known in Western markets"],
            best_for=[TaskType.TRANSLATION, TaskType.RESEARCH, TaskType.CODING],
            context_window_k=1000,
            is_multimodal=False,
            is_open_source=True,
            composite_score=74.5,
        ),
        AIModel(
            model_id="claude_3_haiku",
            name="Claude 3 Haiku",
            provider="Anthropic",
            version="3.0",
            pros=["Fastest Claude model", "Low cost", "Great for simple tasks"],
            cons=["Less capable than Sonnet/Opus on complex tasks"],
            best_for=[TaskType.CONVERSATION, TaskType.SUMMARIZATION, TaskType.TRANSLATION],
            context_window_k=200,
            is_multimodal=True,
            is_open_source=False,
            composite_score=73.5,
        ),
        AIModel(
            model_id="gpt_3_5_turbo",
            name="GPT-3.5 Turbo",
            provider="OpenAI",
            version="0125",
            pros=["Very fast", "Cheapest OpenAI model", "Huge community"],
            cons=["Significantly behind GPT-4 class models"],
            best_for=[TaskType.CONVERSATION, TaskType.SUMMARIZATION, TaskType.GENERAL],
            context_window_k=16,
            is_multimodal=False,
            is_open_source=False,
            composite_score=72.5,
        ),
        AIModel(
            model_id="codestral",
            name="Codestral",
            provider="Mistral AI",
            version="1.0",
            pros=["Purpose-built for code", "Fast code completion", "80+ languages"],
            cons=["Not good for non-code tasks"],
            best_for=[TaskType.CODING],
            context_window_k=32,
            is_multimodal=False,
            is_open_source=False,
            composite_score=71.5,
        ),
        AIModel(
            model_id="starcoder2_15b",
            name="StarCoder2 15B",
            provider="BigCode",
            version="2.0",
            pros=["Open-source code specialist", "Trained on 600+ programming languages"],
            cons=["Not suitable for natural language tasks"],
            best_for=[TaskType.CODING],
            context_window_k=16,
            is_multimodal=False,
            is_open_source=True,
            composite_score=70.5,
        ),
        AIModel(
            model_id="wizard_math_70b",
            name="WizardMath 70B",
            provider="Microsoft Research",
            version="2.0",
            pros=["Specialised in mathematical reasoning", "Open-source"],
            cons=["Only useful for math tasks"],
            best_for=[TaskType.MATH_REASONING],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=70.0,
        ),
        # ── Models 41–60 (composite_score 60–69) ──────────────────────────
        AIModel(
            model_id="palm_2",
            name="PaLM 2",
            provider="Google",
            version="2.0",
            pros=["Strong multilingual", "Good reasoning baseline"],
            cons=["Superseded by Gemini family"],
            best_for=[TaskType.TRANSLATION, TaskType.RESEARCH, TaskType.GENERAL],
            context_window_k=8,
            is_multimodal=False,
            is_open_source=False,
            composite_score=69.0,
        ),
        AIModel(
            model_id="flan_ul2",
            name="Flan-UL2",
            provider="Google Research",
            version="1.0",
            pros=["Strong instruction following", "Open-source", "Lightweight"],
            cons=["Old, many better options now"],
            best_for=[TaskType.SUMMARIZATION, TaskType.ANALYSIS],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=68.0,
        ),
        AIModel(
            model_id="bloom_176b",
            name="BLOOM 176B",
            provider="BigScience",
            version="1.0",
            pros=["Massively multilingual (46 languages)", "Fully open"],
            cons=["Outdated, inefficient"],
            best_for=[TaskType.TRANSLATION, TaskType.RESEARCH],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=67.0,
        ),
        AIModel(
            model_id="dolly_v2",
            name="Dolly v2",
            provider="Databricks",
            version="2.0",
            pros=["First commercially licensed open instruction model"],
            cons=["Outdated, superseded by better models"],
            best_for=[TaskType.GENERAL, TaskType.CONVERSATION],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=65.0,
        ),
        AIModel(
            model_id="vicuna_13b",
            name="Vicuna 13B",
            provider="LMSYS",
            version="1.5",
            pros=["Popular, well-supported locally", "Good conversation quality for size"],
            cons=["Old, many better options"],
            best_for=[TaskType.CONVERSATION, TaskType.GENERAL],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=64.0,
        ),
        AIModel(
            model_id="alpaca_7b",
            name="Alpaca 7B",
            provider="Stanford",
            version="1.0",
            pros=["Pioneered open instruction tuning", "Very lightweight"],
            cons=["Outdated, limited capability"],
            best_for=[TaskType.GENERAL, TaskType.CONVERSATION],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=63.0,
        ),
        AIModel(
            model_id="baichuan2_13b",
            name="Baichuan2 13B",
            provider="Baichuan Inc",
            version="2.0",
            pros=["Good Chinese language support", "Open weights"],
            cons=["Limited English capability"],
            best_for=[TaskType.TRANSLATION, TaskType.CONVERSATION],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=62.0,
        ),
        AIModel(
            model_id="xgen_7b",
            name="XGen 7B",
            provider="Salesforce",
            version="1.0",
            pros=["8K long context (early pioneer)", "Salesforce native"],
            cons=["Outdated"],
            best_for=[TaskType.SUMMARIZATION, TaskType.ANALYSIS],
            context_window_k=8,
            is_multimodal=False,
            is_open_source=True,
            composite_score=61.0,
        ),
        AIModel(
            model_id="mpt_30b",
            name="MPT-30B",
            provider="MosaicML",
            version="1.0",
            pros=["Early large open model", "Commercially usable"],
            cons=["Outdated, superseded"],
            best_for=[TaskType.CODING, TaskType.GENERAL],
            context_window_k=8,
            is_multimodal=False,
            is_open_source=True,
            composite_score=60.5,
        ),
        AIModel(
            model_id="orca_2",
            name="Orca 2",
            provider="Microsoft",
            version="2.0",
            pros=["Strong reasoning for small size", "Open-source", "Good at explaining"],
            cons=["Small, limited for complex tasks"],
            best_for=[TaskType.MATH_REASONING, TaskType.ANALYSIS],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=60.0,
        ),
        # ── Models 61–80 (composite_score 45–59) ──────────────────────────
        AIModel(
            model_id="openchat_3_5",
            name="OpenChat 3.5",
            provider="OpenChat",
            version="3.5",
            pros=["Top open-source chat model for size", "Very fast"],
            cons=["Less powerful than 70B models"],
            best_for=[TaskType.CONVERSATION, TaskType.GENERAL],
            context_window_k=8,
            is_multimodal=False,
            is_open_source=True,
            composite_score=59.0,
        ),
        AIModel(
            model_id="zephyr_7b",
            name="Zephyr 7B",
            provider="HuggingFace",
            version="1.0",
            pros=["Excellent instruction following for 7B", "Open"],
            cons=["Small model, limited reasoning"],
            best_for=[TaskType.CONVERSATION, TaskType.SUMMARIZATION],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=57.5,
        ),
        AIModel(
            model_id="neural_chat_7b",
            name="Neural Chat 7B",
            provider="Intel",
            version="1.0",
            pros=["Optimised for Intel hardware", "Energy efficient"],
            cons=["Limited general capability"],
            best_for=[TaskType.CONVERSATION, TaskType.GENERAL],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=56.0,
        ),
        AIModel(
            model_id="stable_beluga",
            name="Stable Beluga 2",
            provider="Stability AI",
            version="2.0",
            pros=["Strong at creative tasks", "Open-source"],
            cons=["Inconsistent on factual tasks"],
            best_for=[TaskType.CREATIVE_WRITING, TaskType.BRAINSTORMING],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=55.0,
        ),
        AIModel(
            model_id="chat_glm_6b",
            name="ChatGLM3 6B",
            provider="Tsinghua University",
            version="3.0",
            pros=["Tiny yet functional", "Chinese language specialist"],
            cons=["Very limited capability", "Chinese-first"],
            best_for=[TaskType.TRANSLATION, TaskType.CONVERSATION],
            context_window_k=8,
            is_multimodal=False,
            is_open_source=True,
            composite_score=54.0,
        ),
        AIModel(
            model_id="phi_2",
            name="Phi-2",
            provider="Microsoft",
            version="2.0",
            pros=["Surprisingly capable 2.7B model", "Great for on-device AI"],
            cons=["Very limited on complex tasks"],
            best_for=[TaskType.CODING, TaskType.MATH_REASONING],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=53.0,
        ),
        AIModel(
            model_id="tinyllama",
            name="TinyLlama 1.1B",
            provider="TinyLlama Project",
            version="1.0",
            pros=["Runs on minimal hardware", "Fastest inference"],
            cons=["Severely limited capability"],
            best_for=[TaskType.GENERAL, TaskType.CONVERSATION],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=48.0,
        ),
        AIModel(
            model_id="codet5_plus",
            name="CodeT5+",
            provider="Salesforce Research",
            version="1.0",
            pros=["Specialised code understanding and generation"],
            cons=["Not for general NLP"],
            best_for=[TaskType.CODING],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=47.0,
        ),
        AIModel(
            model_id="t5_xxl",
            name="T5-XXL",
            provider="Google",
            version="1.1",
            pros=["Strong at structured NLP tasks", "Well-studied baseline"],
            cons=["No instruction following by default", "Old"],
            best_for=[TaskType.SUMMARIZATION, TaskType.TRANSLATION],
            context_window_k=1,
            is_multimodal=False,
            is_open_source=True,
            composite_score=46.0,
        ),
        AIModel(
            model_id="roberta_large",
            name="RoBERTa Large",
            provider="Facebook AI",
            version="1.0",
            pros=["Excellent text classification and NLU"],
            cons=["Encoder-only, not generative"],
            best_for=[TaskType.ANALYSIS, TaskType.SUMMARIZATION],
            context_window_k=1,
            is_multimodal=False,
            is_open_source=True,
            composite_score=45.0,
        ),
        AIModel(
            model_id="electra_large",
            name="ELECTRA Large",
            provider="Google Research",
            version="1.0",
            pros=["Very efficient NLU pre-training", "Open-source"],
            cons=["Not a generative model"],
            best_for=[TaskType.ANALYSIS],
            context_window_k=1,
            is_multimodal=False,
            is_open_source=True,
            composite_score=45.0,
        ),
        # ── Models 81–100 (composite_score 30–44) ─────────────────────────
        AIModel(
            model_id="bert_large",
            name="BERT Large",
            provider="Google",
            version="1.0",
            pros=["Foundational NLP model", "Widely supported"],
            cons=["Very old, no generation capability"],
            best_for=[TaskType.ANALYSIS],
            context_window_k=1,
            is_multimodal=False,
            is_open_source=True,
            composite_score=44.0,
        ),
        AIModel(
            model_id="xlm_roberta",
            name="XLM-RoBERTa",
            provider="Facebook AI",
            version="1.0",
            pros=["Strong multilingual NLU", "100 languages"],
            cons=["Not generative"],
            best_for=[TaskType.TRANSLATION, TaskType.ANALYSIS],
            context_window_k=1,
            is_multimodal=False,
            is_open_source=True,
            composite_score=43.0,
        ),
        AIModel(
            model_id="gpt_j_6b",
            name="GPT-J 6B",
            provider="EleutherAI",
            version="1.0",
            pros=["First major open GPT-style model", "Historical significance"],
            cons=["Very outdated"],
            best_for=[TaskType.GENERAL, TaskType.CREATIVE_WRITING],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=42.0,
        ),
        AIModel(
            model_id="opt_66b",
            name="OPT 66B",
            provider="Meta AI",
            version="1.0",
            pros=["Early open large language model", "Research value"],
            cons=["Outdated, poor quality by modern standards"],
            best_for=[TaskType.GENERAL],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=41.0,
        ),
        AIModel(
            model_id="gpt_neox_20b",
            name="GPT-NeoX 20B",
            provider="EleutherAI",
            version="1.0",
            pros=["Fully open large model", "Historically important"],
            cons=["Old and outclassed"],
            best_for=[TaskType.GENERAL, TaskType.RESEARCH],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=40.0,
        ),
        AIModel(
            model_id="codegen_16b",
            name="CodeGen 16B",
            provider="Salesforce",
            version="2.0",
            pros=["Early open code generation model"],
            cons=["Superseded by much better code models"],
            best_for=[TaskType.CODING],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=39.0,
        ),
        AIModel(
            model_id="cerebras_gpt_13b",
            name="Cerebras-GPT 13B",
            provider="Cerebras",
            version="1.0",
            pros=["Trained on Cerebras hardware, research-focused"],
            cons=["Limited practical use"],
            best_for=[TaskType.RESEARCH, TaskType.GENERAL],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=38.0,
        ),
        AIModel(
            model_id="pythia_12b",
            name="Pythia 12B",
            provider="EleutherAI",
            version="1.0",
            pros=["Transparent training process", "Research tool"],
            cons=["Not competitive for production use"],
            best_for=[TaskType.RESEARCH, TaskType.GENERAL],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=37.0,
        ),
        AIModel(
            model_id="stablelm_2_12b",
            name="StableLM 2 12B",
            provider="Stability AI",
            version="2.0",
            pros=["Stable, predictable outputs", "Open weights"],
            cons=["Not best-in-class at anything"],
            best_for=[TaskType.GENERAL, TaskType.CONVERSATION],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=36.0,
        ),
        AIModel(
            model_id="redpajama_incite",
            name="RedPajama INCITE",
            provider="Together AI",
            version="1.0",
            pros=["Fully open dataset + model", "Reproducible"],
            cons=["Limited quality"],
            best_for=[TaskType.GENERAL],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=35.0,
        ),
        AIModel(
            model_id="gpt_2_xl",
            name="GPT-2 XL",
            provider="OpenAI",
            version="1.0",
            pros=["Foundational model, widely studied"],
            cons=["Very old, minimal practical use"],
            best_for=[TaskType.CREATIVE_WRITING, TaskType.GENERAL],
            context_window_k=1,
            is_multimodal=False,
            is_open_source=True,
            composite_score=30.0,
        ),
        # ── Models 101 placeholder: additional models 63–100 ──────────────
        AIModel(
            model_id="solar_mini",
            name="SOLAR Mini",
            provider="Upstage",
            version="1.0",
            pros=["Very efficient small model", "Good Korean/English"],
            cons=["Limited context", "Less capable than larger models"],
            best_for=[TaskType.CONVERSATION, TaskType.TRANSLATION],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=False,
            composite_score=29.5,
        ),
        AIModel(
            model_id="gemma_7b",
            name="Gemma 7B",
            provider="Google DeepMind",
            version="1.0",
            pros=["Lightweight open-source", "Good instruction following for size"],
            cons=["Limited capability vs larger models"],
            best_for=[TaskType.GENERAL, TaskType.CONVERSATION],
            context_window_k=8,
            is_multimodal=False,
            is_open_source=True,
            composite_score=29.0,
        ),
        AIModel(
            model_id="mistral_7b",
            name="Mistral 7B",
            provider="Mistral AI",
            version="0.1",
            pros=["Best 7B model on release", "Fast inference", "Open weights"],
            cons=["Smaller capability than larger models"],
            best_for=[TaskType.CONVERSATION, TaskType.CODING],
            context_window_k=8,
            is_multimodal=False,
            is_open_source=True,
            composite_score=28.5,
        ),
        AIModel(
            model_id="llama_3_8b",
            name="Llama 3 8B",
            provider="Meta AI",
            version="3.0",
            pros=["Very fast small open model", "Good for edge cases"],
            cons=["Limited reasoning capability"],
            best_for=[TaskType.CONVERSATION, TaskType.GENERAL],
            context_window_k=8,
            is_multimodal=False,
            is_open_source=True,
            composite_score=28.0,
        ),
        AIModel(
            model_id="phi_3_mini",
            name="Phi-3 Mini",
            provider="Microsoft",
            version="3.0",
            pros=["Runs on phones and edge devices", "Strong reasoning for 3.8B"],
            cons=["Very limited for complex tasks"],
            best_for=[TaskType.CODING, TaskType.GENERAL],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=27.5,
        ),
        AIModel(
            model_id="qwen_1_5_7b",
            name="Qwen 1.5 7B",
            provider="Alibaba Cloud",
            version="1.5",
            pros=["Small but capable", "Good Chinese support", "Open weights"],
            cons=["Limited English performance"],
            best_for=[TaskType.TRANSLATION, TaskType.CONVERSATION],
            context_window_k=32,
            is_multimodal=False,
            is_open_source=True,
            composite_score=27.0,
        ),
        AIModel(
            model_id="yi_6b",
            name="Yi-6B",
            provider="01.AI",
            version="1.0",
            pros=["Strong bilingual Chinese/English for 6B", "Open weights"],
            cons=["Limited general reasoning"],
            best_for=[TaskType.TRANSLATION, TaskType.CONVERSATION],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=26.5,
        ),
        AIModel(
            model_id="deepseek_coder_7b",
            name="DeepSeek Coder 7B",
            provider="DeepSeek",
            version="1.0",
            pros=["Specialised code model", "Open-source", "Multi-language"],
            cons=["Limited non-code tasks"],
            best_for=[TaskType.CODING],
            context_window_k=16,
            is_multimodal=False,
            is_open_source=True,
            composite_score=26.0,
        ),
        AIModel(
            model_id="openchat_7b",
            name="OpenChat 7B",
            provider="OpenChat",
            version="1.0",
            pros=["Solid conversational AI for 7B", "Fast"],
            cons=["Limited complex reasoning"],
            best_for=[TaskType.CONVERSATION, TaskType.GENERAL],
            context_window_k=8,
            is_multimodal=False,
            is_open_source=True,
            composite_score=25.5,
        ),
        AIModel(
            model_id="falcon_7b",
            name="Falcon 7B",
            provider="TII UAE",
            version="1.0",
            pros=["Efficient small open model", "Apache 2.0 license"],
            cons=["Outclassed by Llama-family models"],
            best_for=[TaskType.GENERAL, TaskType.CONVERSATION],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=25.0,
        ),
        AIModel(
            model_id="orca_mini_3b",
            name="Orca Mini 3B",
            provider="Microsoft",
            version="1.0",
            pros=["Very small, explainable reasoning", "Good for edge devices"],
            cons=["Very limited capability"],
            best_for=[TaskType.GENERAL, TaskType.CONVERSATION],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=24.5,
        ),
        AIModel(
            model_id="dolly_v1",
            name="Dolly v1",
            provider="Databricks",
            version="1.0",
            pros=["Historically important open instruction model"],
            cons=["Very outdated"],
            best_for=[TaskType.GENERAL],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=24.0,
        ),
        AIModel(
            model_id="camel_13b",
            name="CAMEL 13B",
            provider="CAMEL-AI",
            version="1.0",
            pros=["Multi-agent conversation specialist", "Research-focused"],
            cons=["Limited real-world deployment"],
            best_for=[TaskType.CONVERSATION, TaskType.BRAINSTORMING],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=23.5,
        ),
        AIModel(
            model_id="guanaco_65b",
            name="Guanaco 65B",
            provider="QLoRA Team",
            version="1.0",
            pros=["Demonstrated QLoRA fine-tuning", "Research value"],
            cons=["Outdated"],
            best_for=[TaskType.GENERAL, TaskType.RESEARCH],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=23.0,
        ),
        AIModel(
            model_id="koala_13b",
            name="Koala 13B",
            provider="Berkeley AI Research",
            version="1.0",
            pros=["Academic research significance"],
            cons=["Very outdated, surpassed"],
            best_for=[TaskType.CONVERSATION, TaskType.GENERAL],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=22.5,
        ),
        AIModel(
            model_id="gpt4all_13b",
            name="GPT4All 13B",
            provider="Nomic AI",
            version="1.0",
            pros=["Runs fully offline", "Privacy preserving"],
            cons=["Low quality vs cloud models"],
            best_for=[TaskType.CONVERSATION, TaskType.GENERAL],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=22.0,
        ),
        AIModel(
            model_id="openhermes_13b",
            name="OpenHermes 13B",
            provider="Teknium",
            version="1.0",
            pros=["Strong instruction following", "Open weights"],
            cons=["Older, less powerful"],
            best_for=[TaskType.GENERAL, TaskType.CODING],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=21.5,
        ),
        AIModel(
            model_id="nous_hermes_34b",
            name="Nous Hermes 34B",
            provider="Nous Research",
            version="1.0",
            pros=["Strong reasoning for size", "Open weights"],
            cons=["Outdated by newer models"],
            best_for=[TaskType.ANALYSIS, TaskType.GENERAL],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=21.0,
        ),
        AIModel(
            model_id="yarn_mistral_7b",
            name="Yarn-Mistral 7B",
            provider="NousResearch",
            version="1.0",
            pros=["Extended 128K context for 7B class", "Open weights"],
            cons=["Quality limited for complex tasks"],
            best_for=[TaskType.SUMMARIZATION, TaskType.RESEARCH],
            context_window_k=128,
            is_multimodal=False,
            is_open_source=True,
            composite_score=20.5,
        ),
        AIModel(
            model_id="longchat_16k",
            name="LongChat 16K",
            provider="LMSYS",
            version="1.0",
            pros=["Extended context model", "Research value"],
            cons=["Outdated"],
            best_for=[TaskType.SUMMARIZATION, TaskType.ANALYSIS],
            context_window_k=16,
            is_multimodal=False,
            is_open_source=True,
            composite_score=20.0,
        ),
        AIModel(
            model_id="stablecode_3b",
            name="StableCode 3B",
            provider="Stability AI",
            version="1.0",
            pros=["Tiny code model", "Runs on device"],
            cons=["Very limited code quality"],
            best_for=[TaskType.CODING],
            context_window_k=16,
            is_multimodal=False,
            is_open_source=True,
            composite_score=19.5,
        ),
        AIModel(
            model_id="replit_code_v1",
            name="Replit Code V1",
            provider="Replit",
            version="1.0",
            pros=["Trained on code data", "Good for autocomplete"],
            cons=["Limited general code generation"],
            best_for=[TaskType.CODING],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=19.0,
        ),
        AIModel(
            model_id="sandalwood",
            name="Sandalwood",
            provider="DreamCo AI",
            version="1.0",
            pros=["DreamCo native", "Optimised for companion tasks", "Fast"],
            cons=["Early-stage model", "Limited public benchmarks"],
            best_for=[TaskType.CONVERSATION, TaskType.EMOTIONAL_SUPPORT],
            context_window_k=16,
            is_multimodal=False,
            is_open_source=False,
            composite_score=18.5,
        ),
        AIModel(
            model_id="dreamllm_v1",
            name="DreamLLM v1",
            provider="DreamCo AI",
            version="1.0",
            pros=["DreamCo ecosystem native", "Enterprise integration"],
            cons=["Not publicly benchmarked"],
            best_for=[TaskType.GENERAL, TaskType.ANALYSIS],
            context_window_k=32,
            is_multimodal=False,
            is_open_source=False,
            composite_score=18.0,
        ),
        AIModel(
            model_id="gpt_neo_1_3b",
            name="GPT-Neo 1.3B",
            provider="EleutherAI",
            version="1.0",
            pros=["Tiny open GPT model", "Educational use"],
            cons=["Very limited capability"],
            best_for=[TaskType.GENERAL],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=17.5,
        ),
        AIModel(
            model_id="bloomz_7b",
            name="BLOOMZ 7B",
            provider="BigScience",
            version="1.0",
            pros=["Multilingual instruction fine-tuned BLOOM", "46 languages"],
            cons=["Outdated"],
            best_for=[TaskType.TRANSLATION, TaskType.GENERAL],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=17.0,
        ),
        AIModel(
            model_id="moss_7b",
            name="MOSS 7B",
            provider="Fudan NLP Group",
            version="1.0",
            pros=["First open-source Chinese RLHF-trained LLM"],
            cons=["Very limited capability"],
            best_for=[TaskType.CONVERSATION, TaskType.TRANSLATION],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=16.5,
        ),
        AIModel(
            model_id="belle_7b",
            name="BELLE 7B",
            provider="BELLE Group",
            version="1.0",
            pros=["Chinese instruction-tuned model"],
            cons=["Limited English", "Outdated"],
            best_for=[TaskType.TRANSLATION, TaskType.CONVERSATION],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=16.0,
        ),
        AIModel(
            model_id="gpt_j_6b_v2",
            name="GPT-J-6B v2",
            provider="EleutherAI",
            version="2.0",
            pros=["Improved version of GPT-J"],
            cons=["Still outdated by modern standards"],
            best_for=[TaskType.GENERAL, TaskType.CREATIVE_WRITING],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=15.5,
        ),
        AIModel(
            model_id="stablelm_3b",
            name="StableLM 3B",
            provider="Stability AI",
            version="1.0",
            pros=["Tiny deployable model", "Open weights"],
            cons=["Very limited"],
            best_for=[TaskType.GENERAL, TaskType.CONVERSATION],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=15.0,
        ),
        AIModel(
            model_id="chatglm2_6b",
            name="ChatGLM2 6B",
            provider="Tsinghua University",
            version="2.0",
            pros=["Better than ChatGLM1", "Chinese specialist"],
            cons=["Limited English", "Outdated"],
            best_for=[TaskType.TRANSLATION, TaskType.CONVERSATION],
            context_window_k=32,
            is_multimodal=False,
            is_open_source=True,
            composite_score=14.5,
        ),
        AIModel(
            model_id="open_llama_13b",
            name="OpenLLaMA 13B",
            provider="OpenLM Research",
            version="1.0",
            pros=["Open reproduction of LLaMA", "Commercially usable"],
            cons=["Surpassed by Llama 2/3"],
            best_for=[TaskType.GENERAL, TaskType.CONVERSATION],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=14.0,
        ),
        AIModel(
            model_id="flan_t5_xxl",
            name="Flan-T5 XXL",
            provider="Google",
            version="1.0",
            pros=["Strong instruction following for size", "Open-source"],
            cons=["Encoder-decoder, less flexible"],
            best_for=[TaskType.SUMMARIZATION, TaskType.TRANSLATION],
            context_window_k=1,
            is_multimodal=False,
            is_open_source=True,
            composite_score=13.5,
        ),
        AIModel(
            model_id="pythia_6_9b",
            name="Pythia 6.9B",
            provider="EleutherAI",
            version="1.0",
            pros=["Transparent training", "Research tool"],
            cons=["Not for production"],
            best_for=[TaskType.RESEARCH, TaskType.GENERAL],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=13.0,
        ),
        AIModel(
            model_id="mpt_7b",
            name="MPT-7B",
            provider="MosaicML",
            version="1.0",
            pros=["Early commercial-license open model"],
            cons=["Outdated"],
            best_for=[TaskType.GENERAL, TaskType.CODING],
            context_window_k=65,
            is_multimodal=False,
            is_open_source=True,
            composite_score=12.5,
        ),
        AIModel(
            model_id="xwin_lm_70b",
            name="Xwin-LM 70B",
            provider="Xwin-LM Team",
            version="1.0",
            pros=["Strong aligned open model at release"],
            cons=["Outdated, surpassed"],
            best_for=[TaskType.CONVERSATION, TaskType.GENERAL],
            context_window_k=4,
            is_multimodal=False,
            is_open_source=True,
            composite_score=12.0,
        ),
        AIModel(
            model_id="amber_7b",
            name="Amber 7B",
            provider="LLM360",
            version="1.0",
            pros=["Fully transparent training data", "Research reproducibility"],
            cons=["Limited quality"],
            best_for=[TaskType.RESEARCH, TaskType.GENERAL],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=11.5,
        ),
        AIModel(
            model_id="crystal_coder_7b",
            name="CrystalCoder 7B",
            provider="LLM360",
            version="1.0",
            pros=["Transparent code model training", "Open weights"],
            cons=["Limited real-world code quality"],
            best_for=[TaskType.CODING, TaskType.RESEARCH],
            context_window_k=2,
            is_multimodal=False,
            is_open_source=True,
            composite_score=11.0,
        ),
    ]


# ---------------------------------------------------------------------------
# Reasoning Engine
# ---------------------------------------------------------------------------

# Keyword sets used to auto-detect task type from a task description string
_TASK_KEYWORDS: dict = {
    TaskType.CODING: {
        "code", "coding", "program", "programming", "debug", "function",
        "class", "script", "algorithm", "software", "bug", "fix", "implement",
        "api", "library", "framework", "python", "javascript", "java", "c++",
        "sql", "html", "css", "typescript", "react", "node", "compile", "syntax",
    },
    TaskType.CREATIVE_WRITING: {
        "story", "poem", "write", "creative", "fiction", "novel", "plot",
        "character", "narrative", "screenplay", "song", "lyric", "prose",
        "blog", "article", "essay",
    },
    TaskType.ANALYSIS: {
        "analyse", "analyze", "analysis", "compare", "evaluate", "review",
        "assess", "report", "breakdown", "examine", "critique", "study",
        "investigate", "explain",
    },
    TaskType.MATH_REASONING: {
        "math", "maths", "calculate", "equation", "formula", "proof",
        "algebra", "calculus", "statistic", "probability", "geometry",
        "arithmetic", "solve", "number",
    },
    TaskType.RESEARCH: {
        "research", "find", "search", "look up", "information", "facts",
        "learn", "discover", "explore", "survey", "literature", "data",
    },
    TaskType.SUMMARIZATION: {
        "summarise", "summarize", "summary", "condense", "shorten",
        "brief", "overview", "digest", "tldr",
    },
    TaskType.TRANSLATION: {
        "translate", "translation", "language", "spanish", "french",
        "german", "chinese", "japanese", "arabic", "portuguese",
    },
    TaskType.BRAINSTORMING: {
        "brainstorm", "idea", "ideas", "creative", "generate", "suggest",
        "think", "concept", "innovation", "invent",
    },
    TaskType.IMAGE_DESCRIPTION: {
        "image", "photo", "picture", "visual", "screenshot", "describe",
        "what is in", "identify", "detect", "ocr",
    },
    TaskType.EMOTIONAL_SUPPORT: {
        "feel", "feeling", "emotion", "sad", "happy", "anxious", "stress",
        "support", "comfort", "empathy", "listen", "lonely", "hurt",
    },
    TaskType.CONVERSATION: {
        "chat", "talk", "conversation", "discuss", "hello", "hi", "hey",
        "tell me", "what do you think",
    },
}


class ReasoningEngine:
    """
    Intelligent AI model selector for BuddyBot.

    Maintains a registry of the 100 leading AI models and automatically
    routes each task to the best-matched model from the curated top-5.

    Parameters
    ----------
    top_n : int
        Number of top models to surface (default 5).
    """

    def __init__(self, top_n: int = 5) -> None:
        self._registry: list = _build_model_registry()
        self._registry.sort(key=lambda m: m.composite_score, reverse=True)
        self.top_n = top_n

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def top_models(self) -> list:
        """Return the top N models sorted by composite score."""
        return self._registry[: self.top_n]

    @property
    def all_models(self) -> list:
        """Return the full 100-model registry."""
        return list(self._registry)

    def get_model(self, model_id: str) -> Optional[AIModel]:
        """Return a model by its ``model_id``, or None if not found."""
        for m in self._registry:
            if m.model_id == model_id:
                return m
        return None

    def detect_task_type(self, task_description: str) -> TaskType:
        """
        Infer the most appropriate TaskType from a plain-text description.

        Parameters
        ----------
        task_description : str
            Free-text description of the task.

        Returns
        -------
        TaskType
            The best matching task type, or ``TaskType.GENERAL`` if no
            keywords match.
        """
        lower = task_description.lower()
        scores: dict = {tt: 0 for tt in _TASK_KEYWORDS}
        for task_type, keywords in _TASK_KEYWORDS.items():
            for kw in keywords:
                if kw in lower:
                    scores[task_type] += 1
        best_type = max(scores, key=lambda k: scores[k])
        if scores[best_type] == 0:
            return TaskType.GENERAL
        return best_type

    def select_best_model(
        self,
        task_type: TaskType,
        require_multimodal: bool = False,
        require_open_source: bool = False,
    ) -> ModelSelectionResult:
        """
        Select the best model from the top-5 for the given task type.

        Parameters
        ----------
        task_type : TaskType
            The type of task to perform.
        require_multimodal : bool
            If True, only consider models with multimodal support.
        require_open_source : bool
            If True, only consider open-source models.

        Returns
        -------
        ModelSelectionResult
        """
        candidates = list(self.top_models)

        if require_multimodal:
            candidates = [m for m in candidates if m.is_multimodal]
        if require_open_source:
            candidates = [m for m in candidates if m.is_open_source]

        if not candidates:
            # Widen search to full registry if constraints eliminate all top-5
            candidates = list(self._registry)
            if require_multimodal:
                candidates = [m for m in candidates if m.is_multimodal]
            if require_open_source:
                candidates = [m for m in candidates if m.is_open_source]

        if not candidates:
            candidates = [self._registry[0]]

        # Primary sort: task explicitly in model's best_for list
        # Secondary sort: composite_score
        def _score(m: AIModel) -> tuple:
            task_match = 1 if task_type in m.best_for else 0
            return (task_match, m.composite_score)

        ranked = sorted(candidates, key=_score, reverse=True)
        best = ranked[0]
        runner_up = ranked[1] if len(ranked) > 1 else None

        task_match = task_type in best.best_for
        confidence = best.composite_score if task_match else best.composite_score * 0.85
        rationale = self._build_rationale(best, task_type, task_match)

        return ModelSelectionResult(
            selected_model=best,
            task_type=task_type,
            rationale=rationale,
            runner_up=runner_up,
            score=round(confidence, 1),
        )

    def select_for_task(
        self,
        task_description: str,
        require_multimodal: bool = False,
        require_open_source: bool = False,
    ) -> ModelSelectionResult:
        """
        Convenience method: detect task type then select the best model.

        Parameters
        ----------
        task_description : str
            Plain-text description of what needs to be done.
        require_multimodal : bool
            Restrict to multimodal models.
        require_open_source : bool
            Restrict to open-source models.

        Returns
        -------
        ModelSelectionResult
        """
        task_type = self.detect_task_type(task_description)
        return self.select_best_model(
            task_type,
            require_multimodal=require_multimodal,
            require_open_source=require_open_source,
        )

    def compare_top_models(self) -> list:
        """Return a side-by-side comparison of the top-5 models."""
        return [m.to_dict() for m in self.top_models]

    def list_models_for_task(self, task_type: TaskType) -> list:
        """
        Return all models (from the full registry) that are explicitly
        optimised for *task_type*, sorted by composite score.
        """
        matches = [m for m in self._registry if task_type in m.best_for]
        return sorted(matches, key=lambda m: m.composite_score, reverse=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_rationale(
        self,
        model: AIModel,
        task_type: TaskType,
        is_direct_match: bool,
    ) -> str:
        """Build a human-readable selection rationale."""
        if is_direct_match:
            return (
                f"{model.name} by {model.provider} is the best available model for "
                f"{task_type.value.replace('_', ' ')} tasks (score {model.composite_score:.0f}/100). "
                f"Key strengths: {'; '.join(model.pros[:3])}."
            )
        return (
            f"No top-5 model is specifically optimised for "
            f"{task_type.value.replace('_', ' ')}, so {model.name} by {model.provider} "
            f"was selected as the highest-scoring general-purpose option "
            f"(score {model.composite_score:.0f}/100). "
            f"Key strengths: {'; '.join(model.pros[:3])}."
        )

    def to_dict(self) -> dict:
        """Return engine status as a dict."""
        return {
            "total_models": len(self._registry),
            "top_n": self.top_n,
            "top_models": [
                {"rank": i + 1, "model_id": m.model_id, "name": m.name,
                 "score": m.composite_score}
                for i, m in enumerate(self.top_models)
            ],
        }
