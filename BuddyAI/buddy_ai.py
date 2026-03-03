"""
BuddyAI/buddy_ai.py

BuddyAI — central AI manager that orchestrates all DreamCobots bots.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


def _load_bot_class(dir_name: str, file_name: str, class_name: str) -> Any:
    """Dynamically load a bot class from a hyphenated directory."""
    bots_dir = os.path.join(os.path.dirname(__file__), "..", "bots")
    bot_path = os.path.join(bots_dir, dir_name, f"{file_name}.py")
    if not os.path.exists(bot_path):
        raise ImportError(f"Bot file not found: {bot_path}")
    spec = importlib.util.spec_from_file_location(file_name, bot_path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[file_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return getattr(mod, class_name)


_BOT_REGISTRY_CONFIG: list[tuple[str, str, str, list[str]]] = [
    # (dir_name, file_name, class_name, keywords)
    ("hustle-bot",        "hustle_bot",        "HustleBot",        ["hustle", "goal", "opportunity", "earn"]),
    ("referral-bot",      "referral_bot",      "ReferralBot",      ["referral", "invite", "refer", "affiliate"]),
    ("buddy-bot",         "buddy_bot",         "BuddyBot",         ["chat", "talk", "companion", "friend", "mood"]),
    ("entrepreneur-bot",  "entrepreneur_bot",  "EntrepreneurBot",  ["business", "startup", "entrepreneur", "idea", "market"]),
    ("medical-bot",       "medical_bot",       "MedicalBot",       ["health", "medical", "medication", "doctor", "condition"]),
    ("legal-bot",         "legal_bot",         "LegalBot",         ["legal", "law", "contract", "attorney", "lawyer"]),
    ("finance-bot",       "finance_bot",       "FinanceBot",       ["finance", "budget", "invest", "money", "financial"]),
    ("real-estate-bot",   "real_estate_bot",   "RealEstateBot",    ["real estate", "property", "mortgage", "house", "rent"]),
    ("ecommerce-bot",     "ecommerce_bot",     "EcommerceBot",     ["ecommerce", "product", "shop", "sell", "marketplace"]),
    ("marketing-bot",     "marketing_bot",     "MarketingBot",     ["marketing", "campaign", "content", "audience", "brand"]),
    ("education-bot",     "education_bot",     "EducationBot",     ["education", "learn", "lesson", "quiz", "study"]),
    ("cybersecurity-bot", "cybersecurity_bot", "CybersecurityBot", ["security", "vulnerability", "password", "hack", "cyber"]),
    ("hr-bot",            "hr_bot",            "HRBot",            ["hr", "hiring", "resume", "interview", "job", "employee"]),
    ("farewell-bot",      "farewell_bot",      "FarewellBot",      ["farewell", "offboard", "goodbye", "exit", "leave"]),
]


class BuddyAI:
    """
    Central AI manager for DreamCobots.

    Initialises and manages all bots, routes user requests to the most
    appropriate bot, and provides system-level operations.
    """

    def __init__(self) -> None:
        self._bots: dict[str, Any] = {}
        self._bot_keywords: dict[str, list[str]] = {}
        self._lock: threading.RLock = threading.RLock()
        self.logger = logging.getLogger("BuddyAI")
        self._initialise_bots()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _initialise_bots(self) -> None:
        """Load and register all configured bots."""
        for dir_name, file_name, class_name, keywords in _BOT_REGISTRY_CONFIG:
            try:
                bot_cls = _load_bot_class(dir_name, file_name, class_name)
                bot_instance = bot_cls()
                self.register_bot(file_name, bot_instance)
                self._bot_keywords[file_name] = keywords
                self.logger.info("Loaded bot: %s", class_name)
            except Exception as exc:
                self.logger.warning("Failed to load bot '%s': %s", class_name, exc)

    # ------------------------------------------------------------------
    # Bot management
    # ------------------------------------------------------------------

    def register_bot(self, bot_name: str, bot_instance: Any) -> None:
        """
        Register a bot instance under *bot_name*.

        Args:
            bot_name: Unique key for the bot.
            bot_instance: The bot object to register.
        """
        with self._lock:
            self._bots[bot_name] = bot_instance
        self.logger.debug("Registered bot: %s", bot_name)

    def start_all_bots(self) -> None:
        """Start all registered bots."""
        with self._lock:
            bots = dict(self._bots)
        for name, bot in bots.items():
            try:
                if hasattr(bot, "run"):
                    bot.run()
                elif hasattr(bot, "start"):
                    bot.start()
                self.logger.debug("Started bot: %s", name)
            except Exception as exc:
                self.logger.warning("Error starting bot '%s': %s", name, exc)

    def stop_all_bots(self) -> None:
        """Stop all registered bots."""
        with self._lock:
            bots = dict(self._bots)
        for name, bot in bots.items():
            try:
                bot.stop()
                self.logger.debug("Stopped bot: %s", name)
            except Exception as exc:
                self.logger.warning("Error stopping bot '%s': %s", name, exc)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def get_best_bot(self, query: str) -> str:
        """
        Determine which bot is best suited to handle *query*.

        Uses keyword matching; falls back to ``buddy_bot`` if no match.

        Args:
            query: User query string.

        Returns:
            Bot name (key in ``_bots``).
        """
        query_lower = query.lower()
        best: str = "buddy_bot"
        best_score = 0
        with self._lock:
            keywords_snapshot = dict(self._bot_keywords)
        for bot_name, keywords in keywords_snapshot.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > best_score:
                best_score = score
                best = bot_name
        return best

    def route_request(self, user_id: str, message: str) -> str:
        """
        Route a user's message to the most appropriate bot and return its response.

        Args:
            user_id: ID of the requesting user.
            message: User's message.

        Returns:
            Response string from the selected bot.
        """
        bot_name = self.get_best_bot(message)
        with self._lock:
            bot = self._bots.get(bot_name)
        if bot is None:
            return f"[BuddyAI] No suitable bot found for: {message}"

        try:
            if hasattr(bot, "process_message"):
                response = bot.process_message(message)
            elif hasattr(bot, "chat"):
                response = bot.chat(message)
            else:
                response = f"[{bot_name}] Request received."
            self.logger.debug("Routed '%s' → %s", message[:50], bot_name)
            return response
        except Exception as exc:
            self.logger.error("Bot '%s' failed to handle request: %s", bot_name, exc)
            return f"[BuddyAI] Error processing request: {exc}"

    # ------------------------------------------------------------------
    # Broadcast
    # ------------------------------------------------------------------

    def broadcast_message(self, message: str) -> dict[str, str]:
        """
        Send *message* to all registered bots and collect responses.

        Args:
            message: Broadcast message string.

        Returns:
            Dict mapping bot name to its response.
        """
        responses: dict[str, str] = {}
        with self._lock:
            bots = dict(self._bots)
        for name, bot in bots.items():
            try:
                if hasattr(bot, "process_message"):
                    responses[name] = bot.process_message(message)
                elif hasattr(bot, "chat"):
                    responses[name] = bot.chat(message)
                else:
                    responses[name] = "acknowledged"
            except Exception as exc:
                responses[name] = f"error: {exc}"
        return responses

    # ------------------------------------------------------------------
    # Data collection & status
    # ------------------------------------------------------------------

    def collect_all_data(self) -> dict[str, Any]:
        """
        Collect structured data from all registered bots.

        Returns:
            Dict mapping bot name to exported data.
        """
        all_data: dict[str, Any] = {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "bot_count": len(self._bots),
            "bots": {},
        }
        with self._lock:
            bots = dict(self._bots)
        for name, bot in bots.items():
            try:
                if hasattr(bot, "export_structured_data"):
                    all_data["bots"][name] = bot.export_structured_data()
                elif hasattr(bot, "get_stats"):
                    all_data["bots"][name] = bot.get_stats()
                else:
                    all_data["bots"][name] = {"status": "no_export_method"}
            except Exception as exc:
                all_data["bots"][name] = {"error": str(exc)}
        return all_data

    def get_system_status(self) -> dict[str, Any]:
        """
        Return a high-level status summary for the entire BuddyAI system.

        Returns:
            Dict with bot count, running status per bot, and timestamp.
        """
        with self._lock:
            bots = dict(self._bots)
        bot_statuses: dict[str, Any] = {}
        for name, bot in bots.items():
            try:
                if hasattr(bot, "get_status"):
                    bot_statuses[name] = bot.get_status()
                elif hasattr(bot, "get_stats"):
                    bot_statuses[name] = bot.get_stats()
                elif hasattr(bot, "is_running"):
                    bot_statuses[name] = {"running": bot.is_running}
                else:
                    bot_statuses[name] = {"status": "unknown"}
            except Exception as exc:
                bot_statuses[name] = {"error": str(exc)}

        return {
            "system": "BuddyAI",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_bots": len(bots),
            "bots": bot_statuses,
        }
