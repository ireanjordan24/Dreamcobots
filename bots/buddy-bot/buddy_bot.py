"""
bots/buddy-bot/buddy_bot.py

BuddyBot — personal AI companion with memory, mood, and customisable personality.
"""

from __future__ import annotations

import logging
import random
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

logger = logging.getLogger(__name__)

_DEFAULT_RESPONSES: dict[str, list[str]] = {
    "greeting": [
        "Hey there! Great to hear from you!",
        "Hello! How are you doing today?",
        "Hi! I'm happy to chat!",
    ],
    "farewell": [
        "Take care! Chat again soon.",
        "Goodbye! It was lovely talking to you.",
        "See you next time!",
    ],
    "unknown": [
        "That's interesting — tell me more.",
        "I hear you. What's on your mind?",
        "I'm listening. Go on.",
    ],
}

_MOODS: list[str] = ["happy", "curious", "calm", "enthusiastic", "thoughtful", "playful"]


class BuddyBot(BotBase):
    """
    Personal AI companion bot with in-memory key-value recall,
    mood simulation, and personality customisation.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="BuddyBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._memory: dict[str, str] = {}
        self._mood: str = random.choice(_MOODS)
        self._personality: dict[str, Any] = {
            "tone": "friendly",
            "verbosity": "medium",
            "emoji": True,
        }
        self._conversation_history: list[dict[str, str]] = []
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("BuddyBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("BuddyBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def chat(self, message: str) -> str:
        """
        Respond to a chat message.

        Args:
            message: User message.

        Returns:
            Bot response string.
        """
        msg_lower = message.lower().strip()
        if any(w in msg_lower for w in ("hello", "hi", "hey", "greetings")):
            response = random.choice(_DEFAULT_RESPONSES["greeting"])
        elif any(w in msg_lower for w in ("bye", "goodbye", "see you")):
            response = random.choice(_DEFAULT_RESPONSES["farewell"])
        elif "how are you" in msg_lower or "how do you feel" in msg_lower:
            emoji = " 😊" if self._personality.get("emoji") else ""
            response = f"I'm feeling {self._mood} today!{emoji}"
        elif "remember" in msg_lower or "recall" in msg_lower:
            response = "Sure, I keep notes! Use remember(key, value) to save something for me."
        elif "what do you know about me" in msg_lower:
            with self._lock_extra:
                keys = list(self._memory.keys())
            if keys:
                response = f"I remember these things about you: {', '.join(keys)}."
            else:
                response = "I don't have anything stored about you yet."
        else:
            response = random.choice(_DEFAULT_RESPONSES["unknown"])

        # Apply tone modifier
        tone = self._personality.get("tone", "friendly")
        if tone == "formal":
            response = response.replace("Hey", "Good day").replace("Hi!", "Hello.")

        with self._lock_extra:
            self._conversation_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user": message,
                "bot": response,
            })
        self.log_activity(f"Chat message processed.")
        return response

    def remember(self, key: str, value: str) -> None:
        """
        Store a key-value pair in the bot's memory.

        Args:
            key: Memory key.
            value: Value to associate with *key*.
        """
        with self._lock_extra:
            self._memory[key] = value
        self.log_activity(f"Remembered key='{key}'.")

    def recall(self, key: str) -> str:
        """
        Retrieve a stored memory value.

        Args:
            key: Memory key.

        Returns:
            The stored value, or a polite "I don't remember" message.
        """
        with self._lock_extra:
            value = self._memory.get(key)
        if value is None:
            return f"I don't remember anything about '{key}'."
        return value

    def get_mood(self) -> str:
        """Return the bot's current mood string."""
        return self._mood

    def customize_personality(self, traits: dict[str, Any]) -> None:
        """
        Update the bot's personality traits.

        Args:
            traits: Dict of trait overrides (``tone``, ``verbosity``, ``emoji``).
        """
        with self._lock_extra:
            self._personality.update(traits)
        self.log_activity(f"Personality customised: {traits}")
