"""
AI Companies Database — Global AI Tools Registry

Provides a searchable, filterable registry of global AI tools and companies.
Seeded with 30+ representative entries across all major categories; additional
tools can be added at runtime via AICompanyDatabase.add_tool() to grow the
registry toward 500–1 000 entries.

Categories
----------
- Core AI         : OpenAI, Google, Anthropic, Meta, Microsoft
- Open Source AI  : Hugging Face, Stability AI, Together AI
- Chinese AI      : Baidu, Alibaba, Tencent, DeepSeek
- Image AI        : Midjourney, Runway, Freepik, DALL-E
- Voice AI        : ElevenLabs, PlayHT, Fliki
- Video AI        : Synthesia, Pika Labs, Wonder Studio
- Music AI        : Suno AI, Udio, Amper Music
- Coding AI       : GitHub Copilot, Replit, DeepMind AlphaCode
- Research AI     : Perplexity AI, Elicit, Consensus

Usage
-----
    from bots.ai_level_up_bot.ai_companies_database import AICompanyDatabase

    db = AICompanyDatabase()
    tool = db.get_tool("OpenAI")
    print(tool.name, tool.pricing_model, tool.token_cost_usd)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class AICategory(Enum):
    """Top-level category for an AI company or tool."""

    CORE_AI = "Core AI"
    OPEN_SOURCE = "Open Source AI"
    CHINESE_AI = "Chinese AI"
    IMAGE_AI = "Image AI"
    VOICE_AI = "Voice AI"
    VIDEO_AI = "Video AI"
    MUSIC_AI = "Music AI"
    CODING_AI = "Coding AI"
    RESEARCH_AI = "Research AI"
    HEALTH_AI = "Health AI"
    LEGAL_AI = "Legal AI"
    EDUCATION_AI = "Education AI"
    OTHER = "Other"


class PricingModel(Enum):
    """How an AI tool charges its users."""

    FREE = "free"
    FREEMIUM = "freemium"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class AITool:
    """
    Represents a single AI company or tool in the global registry.

    Attributes
    ----------
    name : str
        Display name of the tool (e.g. "OpenAI").
    category : AICategory
        Primary category.
    pricing_model : PricingModel
        How the tool is monetised.
    token_cost_usd : float
        Base cost per token/unit in USD.  0.0 for fully free tools.
    capabilities : list[str]
        Short human-readable capability tags.
    region : str
        Primary region or country of origin.
    website : str
        Official website URL.
    description : str
        Brief one-line description.
    tags : list[str]
        Additional search tags.
    """

    name: str
    category: AICategory
    pricing_model: PricingModel
    token_cost_usd: float = 0.0
    capabilities: list[str] = field(default_factory=list)
    region: str = "Global"
    website: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def is_free(self) -> bool:
        """Return True if the tool has a free access tier."""
        return self.pricing_model in (PricingModel.FREE, PricingModel.FREEMIUM)

    def to_dict(self) -> dict:
        """Serialise the tool to a plain dictionary."""
        return {
            "name": self.name,
            "category": self.category.value,
            "pricing_model": self.pricing_model.value,
            "token_cost_usd": self.token_cost_usd,
            "capabilities": self.capabilities,
            "region": self.region,
            "website": self.website,
            "description": self.description,
            "tags": self.tags,
        }


# ---------------------------------------------------------------------------
# Seed data loader
# ---------------------------------------------------------------------------

def _build_seed_tools() -> list[AITool]:
    """
    Return the initial seed list of AI tools.

    This list covers representative entries from each major category.
    Additional tools can be appended at runtime via AICompanyDatabase.add_tool().
    """
    return [
        # ── Core AI ──────────────────────────────────────────────────────────
        AITool(
            name="OpenAI",
            category=AICategory.CORE_AI,
            pricing_model=PricingModel.PAY_PER_USE,
            token_cost_usd=1.0,
            capabilities=["GPT models", "DALL-E", "Whisper", "Codex", "Embeddings"],
            region="USA",
            website="https://openai.com",
            description="Creator of GPT-4, ChatGPT, and DALL-E.",
            tags=["llm", "chatgpt", "gpt4", "image", "speech"],
        ),
        AITool(
            name="Google Gemini",
            category=AICategory.CORE_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.5,
            capabilities=["Multimodal AI", "Language models", "Search AI", "Enterprise automation"],
            region="USA",
            website="https://deepmind.google/technologies/gemini/",
            description="Google's flagship multimodal AI family.",
            tags=["llm", "multimodal", "google", "bard"],
        ),
        AITool(
            name="Anthropic Claude",
            category=AICategory.CORE_AI,
            pricing_model=PricingModel.PAY_PER_USE,
            token_cost_usd=0.8,
            capabilities=["Long-context reasoning", "Safety-focused LLM", "Code generation"],
            region="USA",
            website="https://anthropic.com",
            description="Safety-focused LLM provider behind the Claude model family.",
            tags=["llm", "claude", "safety", "long-context"],
        ),
        AITool(
            name="Microsoft Copilot",
            category=AICategory.CORE_AI,
            pricing_model=PricingModel.SUBSCRIPTION,
            token_cost_usd=0.0,
            capabilities=["Office 365 integration", "Code completion", "Web search"],
            region="USA",
            website="https://copilot.microsoft.com",
            description="AI assistant embedded across the Microsoft 365 ecosystem.",
            tags=["copilot", "office", "enterprise", "bing"],
        ),
        AITool(
            name="Meta Llama",
            category=AICategory.CORE_AI,
            pricing_model=PricingModel.FREE,
            token_cost_usd=0.0,
            capabilities=["Open-weight LLM", "Fine-tuning", "On-premise deployment"],
            region="USA",
            website="https://ai.meta.com/llama/",
            description="Meta's open-weight large language model series.",
            tags=["llm", "open-weight", "meta", "llama"],
        ),
        # ── Open Source AI ───────────────────────────────────────────────────
        AITool(
            name="Hugging Face",
            category=AICategory.OPEN_SOURCE,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.0,
            capabilities=["Model hub", "Datasets", "Transformers library", "Inference API"],
            region="Global",
            website="https://huggingface.co",
            description="The GitHub of AI – open-source model and dataset hub.",
            tags=["transformers", "datasets", "hub", "nlp"],
        ),
        AITool(
            name="Stability AI",
            category=AICategory.OPEN_SOURCE,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.02,
            capabilities=["Stable Diffusion", "Image generation", "Fine-tuning"],
            region="UK",
            website="https://stability.ai",
            description="Open-source image generation via Stable Diffusion.",
            tags=["stable-diffusion", "image", "open-source"],
        ),
        AITool(
            name="Together AI",
            category=AICategory.OPEN_SOURCE,
            pricing_model=PricingModel.PAY_PER_USE,
            token_cost_usd=0.2,
            capabilities=["Inference API", "Open-source model hosting", "Fine-tuning"],
            region="USA",
            website="https://www.together.ai",
            description="Cloud platform for running open-source AI models at scale.",
            tags=["inference", "open-source", "cloud", "llm"],
        ),
        # ── Chinese AI ───────────────────────────────────────────────────────
        AITool(
            name="Baidu ERNIE Bot",
            category=AICategory.CHINESE_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.3,
            capabilities=["Mandarin NLP", "Search AI", "Enterprise automation"],
            region="China",
            website="https://yiyan.baidu.com",
            description="Baidu's conversational AI assistant powered by ERNIE.",
            tags=["ernie", "mandarin", "china", "baidu"],
        ),
        AITool(
            name="Alibaba Tongyi Qianwen",
            category=AICategory.CHINESE_AI,
            pricing_model=PricingModel.PAY_PER_USE,
            token_cost_usd=0.3,
            capabilities=["E-commerce AI", "Cloud AI", "Multimodal reasoning"],
            region="China",
            website="https://tongyi.aliyun.com",
            description="Alibaba's large language model for enterprise and cloud.",
            tags=["alibaba", "china", "cloud", "qianwen"],
        ),
        AITool(
            name="Tencent Hunyuan",
            category=AICategory.CHINESE_AI,
            pricing_model=PricingModel.ENTERPRISE,
            token_cost_usd=0.4,
            capabilities=["Translation AI", "Content moderation", "Social AI"],
            region="China",
            website="https://hunyuan.tencent.com",
            description="Tencent's LLM powering WeChat and enterprise applications.",
            tags=["tencent", "china", "wechat", "hunyuan"],
        ),
        AITool(
            name="DeepSeek",
            category=AICategory.CHINESE_AI,
            pricing_model=PricingModel.FREE,
            token_cost_usd=0.0,
            capabilities=["Open-source LLM", "Coding AI", "Math reasoning"],
            region="China",
            website="https://deepseek.com",
            description="Chinese open-source AI model with strong coding capabilities.",
            tags=["deepseek", "china", "open-source", "coding"],
        ),
        # ── Image AI ─────────────────────────────────────────────────────────
        AITool(
            name="Midjourney",
            category=AICategory.IMAGE_AI,
            pricing_model=PricingModel.SUBSCRIPTION,
            token_cost_usd=0.1,
            capabilities=["Text-to-image", "Concept art", "Product visualisation"],
            region="USA",
            website="https://midjourney.com",
            description="Premium AI image generation via Discord interface.",
            tags=["image", "art", "midjourney", "discord"],
        ),
        AITool(
            name="Runway",
            category=AICategory.IMAGE_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.1,
            capabilities=["Image generation", "Video editing", "Inpainting"],
            region="USA",
            website="https://runwayml.com",
            description="AI-powered creative suite for image and video generation.",
            tags=["image", "video", "creative", "runway"],
        ),
        AITool(
            name="Freepik AI",
            category=AICategory.IMAGE_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.05,
            capabilities=["Stock image AI", "Vector generation", "Background removal"],
            region="Spain",
            website="https://freepik.com",
            description="AI-powered asset generation integrated into the Freepik platform.",
            tags=["stock", "vector", "image", "freepik"],
        ),
        AITool(
            name="DALL-E",
            category=AICategory.IMAGE_AI,
            pricing_model=PricingModel.PAY_PER_USE,
            token_cost_usd=0.1,
            capabilities=["Text-to-image", "Image editing", "Outpainting"],
            region="USA",
            website="https://openai.com/dall-e",
            description="OpenAI's text-to-image model series.",
            tags=["dall-e", "openai", "image", "text-to-image"],
        ),
        # ── Voice AI ─────────────────────────────────────────────────────────
        AITool(
            name="ElevenLabs",
            category=AICategory.VOICE_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.2,
            capabilities=["Voice cloning", "Text-to-speech", "Multilingual TTS"],
            region="USA",
            website="https://elevenlabs.io",
            description="Industry-leading AI voice cloning and text-to-speech.",
            tags=["tts", "voice-clone", "speech", "elevenlabs"],
        ),
        AITool(
            name="PlayHT",
            category=AICategory.VOICE_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.2,
            capabilities=["Text-to-speech", "Voice cloning", "Podcast automation"],
            region="USA",
            website="https://play.ht",
            description="AI voice generation platform for podcasters and creators.",
            tags=["tts", "podcast", "voice-clone", "playht"],
        ),
        AITool(
            name="Fliki",
            category=AICategory.VOICE_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.15,
            capabilities=["Text-to-video", "AI voice", "Stock media"],
            region="USA",
            website="https://fliki.ai",
            description="Turn text scripts into videos with AI voice narration.",
            tags=["tts", "video", "fliki", "creator"],
        ),
        # ── Video AI ─────────────────────────────────────────────────────────
        AITool(
            name="Synthesia",
            category=AICategory.VIDEO_AI,
            pricing_model=PricingModel.SUBSCRIPTION,
            token_cost_usd=0.5,
            capabilities=["AI avatars", "Text-to-video", "Multilingual video"],
            region="UK",
            website="https://synthesia.io",
            description="Create professional AI avatar videos without a camera.",
            tags=["avatar", "video", "synthesia", "corporate"],
        ),
        AITool(
            name="Pika Labs",
            category=AICategory.VIDEO_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.3,
            capabilities=["Text-to-video", "Image-to-video", "Video editing"],
            region="USA",
            website="https://pika.art",
            description="AI-powered video generation from text and images.",
            tags=["video", "generation", "pika", "creative"],
        ),
        AITool(
            name="Wonder Studio",
            category=AICategory.VIDEO_AI,
            pricing_model=PricingModel.SUBSCRIPTION,
            token_cost_usd=0.4,
            capabilities=["CGI character animation", "VFX", "Scene rendering"],
            region="USA",
            website="https://wonderdynamics.com",
            description="Automate CGI character integration into live-action footage.",
            tags=["cgi", "vfx", "animation", "film"],
        ),
        # ── Music AI ─────────────────────────────────────────────────────────
        AITool(
            name="Suno AI",
            category=AICategory.MUSIC_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.05,
            capabilities=["Text-to-music", "Song generation", "Vocal synthesis"],
            region="USA",
            website="https://suno.ai",
            description="Generate full songs with vocals from a text prompt.",
            tags=["music", "song", "suno", "vocals"],
        ),
        AITool(
            name="Udio",
            category=AICategory.MUSIC_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.05,
            capabilities=["Music generation", "Custom genre", "Lyric writing"],
            region="USA",
            website="https://udio.com",
            description="AI music generation platform supporting diverse genres.",
            tags=["music", "genre", "udio", "lyrics"],
        ),
        AITool(
            name="Amper Music",
            category=AICategory.MUSIC_AI,
            pricing_model=PricingModel.SUBSCRIPTION,
            token_cost_usd=0.1,
            capabilities=["Background music", "Royalty-free tracks", "Mood-based generation"],
            region="USA",
            website="https://www.ampermusic.com",
            description="AI composition tool for royalty-free background music.",
            tags=["music", "royalty-free", "background", "amper"],
        ),
        # ── Coding AI ────────────────────────────────────────────────────────
        AITool(
            name="GitHub Copilot",
            category=AICategory.CODING_AI,
            pricing_model=PricingModel.SUBSCRIPTION,
            token_cost_usd=0.0,
            capabilities=["Code completion", "Test generation", "PR review"],
            region="USA",
            website="https://github.com/features/copilot",
            description="AI pair-programmer integrated into GitHub and VS Code.",
            tags=["copilot", "code", "github", "completion"],
        ),
        AITool(
            name="Replit Ghostwriter",
            category=AICategory.CODING_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.0,
            capabilities=["Code generation", "Debugging", "Browser-based IDE"],
            region="USA",
            website="https://replit.com",
            description="AI coding assistant built into the Replit cloud IDE.",
            tags=["replit", "code", "ide", "ghostwriter"],
        ),
        AITool(
            name="DeepMind AlphaCode",
            category=AICategory.CODING_AI,
            pricing_model=PricingModel.FREE,
            token_cost_usd=0.0,
            capabilities=["Competitive programming", "Algorithm generation", "Code synthesis"],
            region="UK",
            website="https://deepmind.google/alphacode",
            description="DeepMind's system for solving complex programming challenges.",
            tags=["alphacode", "competitive", "deepmind", "algorithms"],
        ),
        # ── Research AI ──────────────────────────────────────────────────────
        AITool(
            name="Perplexity AI",
            category=AICategory.RESEARCH_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.0,
            capabilities=["Web search", "Cited answers", "Research summaries"],
            region="USA",
            website="https://perplexity.ai",
            description="AI-powered answer engine with real-time web citations.",
            tags=["search", "research", "citations", "perplexity"],
        ),
        AITool(
            name="Elicit",
            category=AICategory.RESEARCH_AI,
            pricing_model=PricingModel.FREEMIUM,
            token_cost_usd=0.0,
            capabilities=["Literature review", "Paper summarisation", "Data extraction"],
            region="USA",
            website="https://elicit.com",
            description="AI research assistant for academic literature review.",
            tags=["research", "papers", "elicit", "academic"],
        ),
    ]


# ---------------------------------------------------------------------------
# Database class
# ---------------------------------------------------------------------------

class AICompanyDatabase:
    """
    In-memory registry of global AI tools and companies.

    The registry is seeded with representative entries on initialisation.
    Additional tools can be added at runtime with :meth:`add_tool`.

    Methods
    -------
    get_tool(name)
        Retrieve a tool by exact name (case-insensitive).
    search(query)
        Return tools whose name, description, or tags contain *query*.
    filter_by_category(category)
        Return all tools in the given AICategory.
    filter_by_pricing(pricing_model)
        Return all tools with the given PricingModel.
    filter_by_region(region)
        Return all tools whose region matches (case-insensitive).
    add_tool(tool)
        Register a new AITool in the database.
    list_all()
        Return a copy of all registered tools.
    count()
        Return the number of tools registered.
    """

    def __init__(self) -> None:
        self._tools: list[AITool] = _build_seed_tools()
        # Build a fast name→tool index (lower-cased)
        self._index: dict[str, AITool] = {t.name.lower(): t for t in self._tools}

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_tool(self, name: str) -> AITool:
        """
        Return the AITool with the given name.

        Parameters
        ----------
        name : str
            Tool name (case-insensitive).

        Raises
        ------
        KeyError
            If no tool with that name exists.
        """
        key = name.lower()
        if key not in self._index:
            raise KeyError(f"AI tool not found: '{name}'")
        return self._index[key]

    def search(self, query: str) -> list[AITool]:
        """
        Return tools whose name, description, or tags contain *query*.

        The search is case-insensitive.
        """
        q = query.lower()
        results = []
        for tool in self._tools:
            if (
                q in tool.name.lower()
                or q in tool.description.lower()
                or any(q in tag.lower() for tag in tool.tags)
                or any(q in cap.lower() for cap in tool.capabilities)
            ):
                results.append(tool)
        return results

    def filter_by_category(self, category: AICategory) -> list[AITool]:
        """Return all tools belonging to *category*."""
        return [t for t in self._tools if t.category == category]

    def filter_by_pricing(self, pricing_model: PricingModel) -> list[AITool]:
        """Return all tools with the given *pricing_model*."""
        return [t for t in self._tools if t.pricing_model == pricing_model]

    def filter_by_region(self, region: str) -> list[AITool]:
        """Return all tools whose region matches *region* (case-insensitive)."""
        r = region.lower()
        return [t for t in self._tools if t.region.lower() == r]

    def add_tool(self, tool: AITool) -> None:
        """
        Register a new *tool* in the database.

        If a tool with the same name already exists, it is replaced.
        """
        self._tools.append(tool)
        self._index[tool.name.lower()] = tool

    def list_all(self) -> list[AITool]:
        """Return a copy of all registered tools."""
        return list(self._tools)

    def count(self) -> int:
        """Return the total number of registered tools."""
        return len(self._tools)
