"""
chatbot.py – AI Chatbot engine for Dreamcobots.

Supports multiple tiers (Free / Intermediate / Premium) and multiple
AI backends, including the KimiK model available on the Premium tier.

Usage (standalone CLI)::

    python chatbot.py --tier premium --model kimi-k

Usage (as a library)::

    from bots.ai_chatbot.chatbot import AIChatbot, Tier
    bot = AIChatbot(user_id="u_001", tier=Tier.PREMIUM)
    reply = bot.chat("Tell me about AI partner recruitment.")
    print(reply)
"""

from __future__ import annotations

import datetime
import json
import re
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .tiers import Tier, TierConfig, TIER_CONFIGS, require_feature, has_feature


# ---------------------------------------------------------------------------
# Message & Session models
# ---------------------------------------------------------------------------

@dataclass
class Message:
    role: str          # "user" | "assistant" | "system"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ChatSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    tier: Tier = Tier.FREE
    model: str = "basic-llm"
    messages: List[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    messages_today: int = 0


# ---------------------------------------------------------------------------
# AI model adapters
# ---------------------------------------------------------------------------

class _BaseModelAdapter:
    """Minimal interface every model adapter must implement."""

    name: str = "base"

    def generate(self, history: List[Message], user_input: str) -> str:
        raise NotImplementedError


class BasicLLMAdapter(_BaseModelAdapter):
    """Lightweight rule/keyword model – always available on the Free tier."""

    name = "basic-llm"

    _RESPONSES = {
        r"hello|hi|hey": "Hello! I'm your Dreamcobots AI assistant. How can I help you today?",
        r"tier|plan|price|cost|upgrade": (
            "We offer three tiers: Free, Intermediate ($29.99/mo), and Premium ($99.99/mo). "
            "Each tier unlocks more AI capabilities and features. Would you like details?"
        ),
        r"feature|what can you do": (
            "I can answer questions, guide onboarding, look up resources, and more. "
            "Upgrade to Intermediate or Premium for analytics, integrations, and KimiK AI!"
        ),
        r"help|support": "I'm here to help! What do you need assistance with?",
        r"bye|goodbye|exit": "Goodbye! Feel free to come back anytime.",
    }

    def generate(self, history: List[Message], user_input: str) -> str:
        lower = user_input.lower()
        for pattern, response in self._RESPONSES.items():
            if re.search(pattern, lower):
                return response
        return (
            "I received your message. For more advanced AI responses, "
            "consider upgrading to the Intermediate or Premium tier."
        )


class AdvancedLLMAdapter(_BaseModelAdapter):
    """Intermediate-tier model with richer contextual responses."""

    name = "advanced-llm"

    def generate(self, history: List[Message], user_input: str) -> str:
        context_length = len(history)
        lower = user_input.lower()

        if re.search(r"analytic|dashboard|report", lower):
            return (
                "Your analytics dashboard shows engagement trends, message volumes, "
                "and user satisfaction scores. Use the /analytics endpoint to pull live data."
            )
        if re.search(r"integrat|webhook|api|connect", lower):
            return (
                "Intermediate-tier integrations include Slack, Zapier, and REST webhooks. "
                "Head to Settings → Integrations to connect your tools."
            )
        if re.search(r"campaign|email|market", lower):
            return (
                "Email campaigns can be launched directly from the Marketing module. "
                "I can help draft copy, set schedules, and track open rates."
            )
        return (
            f"[Advanced LLM | {context_length} messages in context] "
            f"Processing your query: '{user_input}'. "
            "My enhanced reasoning gives you deeper, more relevant responses."
        )


class KimiKAdapter(_BaseModelAdapter):
    """
    Premium-tier KimiK AI adapter.

    KimiK is a state-of-the-art reasoning model designed for complex tasks:
    partner recruitment analysis, market intelligence, and ecosystem mapping.

    In production, this adapter wraps the KimiK API (api.kimi.ai).  The
    ``api_key`` and ``endpoint`` are read from the environment or the
    platform's secrets store at runtime.
    """

    name = "kimi-k"
    DEFAULT_ENDPOINT = "https://api.moonshot.cn/v1/chat/completions"  # KimiK public API

    def __init__(self, api_key: str = "", endpoint: str = ""):
        self.api_key = api_key or "YOUR_KIMI_K_API_KEY"
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT

    def generate(self, history: List[Message], user_input: str) -> str:
        """
        Build a KimiK-compatible request payload and call the API.

        For demonstration purposes (no live network calls) a rich mock
        response is returned.  Replace the body of this method with a
        real ``requests.post`` call when your API key is configured.
        """
        lower = user_input.lower()

        if re.search(r"partner|recruit|ecosystem|organiz", lower):
            return (
                "[KimiK AI] Partner Recruitment Analysis:\n"
                "• Identified 12 high-potential AI ecosystem organisations matching your profile.\n"
                "• Top match: DeepMind (AI Research) – 94% fit score.\n"
                "• Recommended outreach: personalised OnSite signup flow + developer portal invite.\n"
                "• Next step: review the AI Ecosystem Directory in the Analytics module."
            )
        if re.search(r"market|document|layout|design", lower):
            return (
                "[KimiK AI] Marketing Documentation Manager:\n"
                "• 5 layout templates loaded (B2B Landing, Developer Portal, Enterprise Pitch, "
                "Partner Brief, Product Hunt).\n"
                "• Auto-populated with your brand assets and value propositions.\n"
                "• Export to PDF, Notion, or Confluence with one click."
            )
        if re.search(r"premium|capability|extend|power", lower):
            return (
                "[KimiK AI] Extended capabilities active:\n"
                "• Long-context reasoning (128k tokens)\n"
                "• Multimodal document understanding\n"
                "• Real-time web retrieval (via search grounding)\n"
                "• Autonomous task planning and multi-step tool use"
            )

        # Generic premium response
        payload_preview = {
            "model": "moonshot-v1-128k",
            "messages": [
                {"role": m.role, "content": m.content[:80]}
                for m in history[-5:]
            ] + [{"role": "user", "content": user_input}],
            "temperature": 0.7,
        }
        return (
            f"[KimiK AI | Premium] Sending to {self.endpoint}:\n"
            f"{json.dumps(payload_preview, indent=2)}\n\n"
            "KimiK would return a deeply reasoned, context-aware answer here. "
            "Configure your KIMI_K_API_KEY environment variable to activate live responses."
        )


# Model registry
MODEL_ADAPTERS: Dict[str, _BaseModelAdapter] = {
    "basic-llm": BasicLLMAdapter(),
    "advanced-llm": AdvancedLLMAdapter(),
    "kimi-k": KimiKAdapter(),
}


# ---------------------------------------------------------------------------
# Main chatbot class
# ---------------------------------------------------------------------------

class AIChatbot:
    """
    Tier-aware AI chatbot for the Dreamcobots platform.

    Parameters
    ----------
    user_id : str
        Unique identifier for the user (or organisation).
    tier : Tier
        The user's subscription tier (FREE / INTERMEDIATE / PREMIUM).
    model : str | None
        Override the default model for this tier. Must be allowed on the tier.
    """

    def __init__(
        self,
        user_id: str = "",
        tier: Tier = Tier.FREE,
        model: Optional[str] = None,
    ) -> None:
        self.user_id = user_id or str(uuid.uuid4())
        self.tier = tier
        self.tier_config: TierConfig = TIER_CONFIGS[tier]

        # Determine model
        if model is None:
            # Default to the most capable model available on this tier
            self.model = self.tier_config.ai_models[-1]
        else:
            if model not in self.tier_config.ai_models:
                available = ", ".join(self.tier_config.ai_models)
                raise ValueError(
                    f"Model '{model}' is not available on the {self.tier_config.name} tier. "
                    f"Available models: {available}"
                )
            self.model = model

        self.adapter = MODEL_ADAPTERS.get(self.model, BasicLLMAdapter())
        self.session = ChatSession(user_id=self.user_id, tier=self.tier, model=self.model)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, user_input: str) -> str:
        """
        Send a message to the bot and return the assistant's reply.

        Enforces daily message limits per tier.
        """
        require_feature(self.tier, "core_chat")
        self._check_rate_limit()

        user_msg = Message(role="user", content=user_input)
        self.session.messages.append(user_msg)
        self.session.messages_today += 1

        reply = self.adapter.generate(self.session.messages[:-1], user_input)

        assistant_msg = Message(role="assistant", content=reply)
        self.session.messages.append(assistant_msg)
        return reply

    def get_history(self) -> List[Dict]:
        """Return the conversation history as a list of dicts."""
        require_feature(self.tier, "conversation_history")
        return [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp,
                "message_id": m.message_id,
            }
            for m in self.session.messages
        ]

    def customize(self, persona: str = "", system_prompt: str = "") -> None:
        """
        Apply custom persona / system prompt (Intermediate+ tier only).
        """
        require_feature(self.tier, "advanced_customisation")
        if system_prompt:
            self.session.messages.insert(
                0, Message(role="system", content=system_prompt)
            )
        if persona:
            self.session.messages.insert(
                0,
                Message(
                    role="system",
                    content=f"You are {persona}, a Dreamcobots AI assistant.",
                ),
            )

    def export_session(self) -> Dict:
        """Export session data as a dictionary for persistence / analytics."""
        return {
            "session_id": self.session.session_id,
            "user_id": self.session.user_id,
            "tier": self.tier.value,
            "model": self.model,
            "created_at": self.session.created_at,
            "messages_today": self.session.messages_today,
            "history": self.get_history() if has_feature(self.tier, "conversation_history") else [],
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _check_rate_limit(self) -> None:
        limit = self.tier_config.max_messages_per_day
        if limit != -1 and self.session.messages_today >= limit:
            raise RuntimeError(
                f"Daily message limit ({limit}) reached for the "
                f"{self.tier_config.name} tier. Upgrade to send more messages."
            )


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Dreamcobots AI Chatbot CLI")
    parser.add_argument(
        "--tier",
        choices=[t.value for t in Tier],
        default=Tier.FREE.value,
        help="Subscription tier (default: free)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="AI model to use (default: best available for tier)",
    )
    parser.add_argument(
        "--user-id",
        default="cli-user",
        help="User identifier",
    )
    args = parser.parse_args()

    tier = Tier(args.tier)
    bot = AIChatbot(user_id=args.user_id, tier=tier, model=args.model)
    cfg = TIER_CONFIGS[tier]

    print(f"\nDreamcobots AI Chatbot  |  Tier: {cfg.name}  |  Model: {bot.model}")
    print("Type 'exit' to quit, 'history' to view conversation, 'export' to export session.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        if user_input.lower() == "history":
            try:
                for msg in bot.get_history():
                    print(f"  [{msg['role']}] {msg['content']}")
            except PermissionError as exc:
                print(f"  {exc}")
            continue
        if user_input.lower() == "export":
            print(json.dumps(bot.export_session(), indent=2))
            continue

        try:
            reply = bot.chat(user_input)
            print(f"Bot: {reply}\n")
        except (PermissionError, RuntimeError) as exc:
            print(f"[Error] {exc}\n")


if __name__ == "__main__":
    _cli()
