"""
211 Resource and Eligibility Checker Bot
=========================================
A conversational chatbot that helps users locate 211 resources (housing,
food, mental health, utilities, etc.) and check their eligibility for
assistance programs such as SNAP, Medicaid, CHIP, WIC, and rent assistance.

Key Features
------------
* **Resource Search** – integrates with the 211 API (with graceful mock
  fallback) to surface local resources by category.
* **Eligibility Checker** – applies FPL-based rules to determine program
  qualifications given household income and size.
* **Geolocation Matching** – uses user-supplied city/ZIP to narrow results.
* **Multilingual Support** – English and Spanish built in; easily extensible.
* **Privacy-first** – all session data is ephemeral (in-memory only) and
  purged after configurable TTL.

Usage
-----
Run interactively from the command line::

    python bot.py

Or import and embed in a Flask/FastAPI web service::

    from bot import ResourceEligibilityBot
    bot = ResourceEligibilityBot()
    session_id = bot.start_session()
    response = bot.handle_message(session_id, "I need food assistance")
"""

import re
import sys
from typing import Optional

from api_client import APIClient211
from config import RESOURCE_CATEGORIES, SUPPORTED_LANGUAGES, TRANSLATIONS
from database import SessionDatabase
from eligibility_engine import check_eligibility, format_eligibility_results

# ---------------------------------------------------------------------------
# Intent detection helpers
# ---------------------------------------------------------------------------

_RESOURCE_KEYWORDS: dict[str, list[str]] = {
    "housing": ["housing", "shelter", "rent", "evict", "homeless", "home", "apartment"],
    "food": ["food", "groceries", "hungry", "hunger", "snap", "eat", "meal", "nutrition"],
    "mental_health": ["mental", "depression", "anxiety", "crisis", "suicide", "counseling", "therapy"],
    "health": ["health", "medical", "doctor", "clinic", "insurance", "medicaid", "chip", "medication"],
    "utilities": ["utility", "utilities", "electricity", "gas", "water", "liheap", "energy", "bill"],
    "employment": ["job", "work", "employment", "career", "resume", "interview", "unemployed"],
    "childcare": ["childcare", "child care", "daycare", "preschool", "babysitter", "kids"],
    "transportation": ["transport", "bus", "ride", "car", "commute", "transit"],
    "legal": ["legal", "lawyer", "attorney", "court", "eviction", "domestic"],
    "education": ["education", "school", "ged", "literacy", "college", "tuition"],
}

_ELIGIBILITY_KEYWORDS = [
    "eligible", "eligibility", "qualify", "qualification", "benefits",
    "snap", "medicaid", "wic", "chip", "assistance program",
]

_LANGUAGE_MAP = {
    "english": "en",
    "inglés": "en",
    "spanish": "es",
    "español": "es",
    "french": "fr",
    "français": "fr",
    "chinese": "zh",
    "中文": "zh",
    "vietnamese": "vi",
    "arabic": "ar",
}

_QUIT_WORDS = {"quit", "exit", "bye", "goodbye", "done", "salir", "adiós"}


def _detect_category(text: str) -> Optional[str]:
    """Return the best matching resource category for *text*, or None."""
    lower = text.lower()
    for category, keywords in _RESOURCE_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return category
    return None


def _detect_intent(text: str) -> str:
    """
    Classify user *text* into one of:
    'resource', 'eligibility', 'language_change', 'help', 'quit', 'unknown'.
    """
    lower = text.strip().lower()
    if lower in _QUIT_WORDS:
        return "quit"
    if lower in ("help", "ayuda", "aide", "帮助"):
        return "help"
    # Language-change request
    if any(lang in lower for lang in _LANGUAGE_MAP):
        return "language_change"
    # Eligibility intent
    if any(kw in lower for kw in _ELIGIBILITY_KEYWORDS):
        return "eligibility"
    # Resource search intent
    if _detect_category(lower):
        return "resource"
    return "unknown"


def _t(lang: str, key: str) -> str:
    """Return translated string for *key* in *lang*, fallback to English."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(
        key, TRANSLATIONS["en"].get(key, key)
    )


# ---------------------------------------------------------------------------
# Main Bot class
# ---------------------------------------------------------------------------


class ResourceEligibilityBot:
    """
    Core bot logic.  Stateless between sessions; all user data is isolated
    to the per-session store in :class:`~database.SessionDatabase`.
    """

    def __init__(self):
        self._db = SessionDatabase()
        self._api = APIClient211()

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def start_session(self, language: str = "en") -> str:
        """Create a new conversation session and return its ID."""
        if language not in SUPPORTED_LANGUAGES:
            language = "en"
        session_id = self._db.create_session()
        self._db.set(session_id, "language", language)
        self._db.set(session_id, "state", "idle")
        return session_id

    def end_session(self, session_id: str) -> None:
        """Explicitly terminate a session and purge its data."""
        self._db.delete_session(session_id)

    # ------------------------------------------------------------------
    # Public message handler
    # ------------------------------------------------------------------

    def handle_message(self, session_id: str, user_text: str) -> str:
        """
        Process *user_text* for the given session and return the bot's reply.

        Parameters
        ----------
        session_id : str
            Active session identifier from :meth:`start_session`.
        user_text : str
            Raw message from the user.

        Returns
        -------
        str
            Bot response text.
        """
        if not self._db.session_exists(session_id):
            return "Session expired. Please start a new conversation."

        lang = self._db.get(session_id, "language", "en")
        state = self._db.get(session_id, "state", "idle")
        text = user_text.strip()

        # --- Continuation states take priority ---
        if state == "awaiting_location_for_resource":
            return self._handle_location_input(session_id, text)
        if state == "awaiting_income":
            return self._handle_income_input(session_id, text)
        if state == "awaiting_household_size":
            return self._handle_household_size_input(session_id, text)
        if state == "awaiting_location_for_eligibility":
            return self._handle_location_for_eligibility(session_id, text)

        # --- Intent detection for idle state ---
        intent = _detect_intent(text)

        if intent == "quit":
            reply = _t(lang, "goodbye")
            self.end_session(session_id)
            return reply

        if intent == "help":
            return _t(lang, "help")

        if intent == "language_change":
            return self._handle_language_change(session_id, text)

        if intent == "resource":
            return self._start_resource_flow(session_id, text)

        if intent == "eligibility":
            return self._start_eligibility_flow(session_id)

        return _t(lang, "unknown_input")

    def get_welcome_message(self, session_id: str) -> str:
        """Return the welcome/greeting message for a session."""
        lang = self._db.get(session_id, "language", "en")
        return _t(lang, "welcome")

    # ------------------------------------------------------------------
    # Resource flow
    # ------------------------------------------------------------------

    def _start_resource_flow(self, session_id: str, text: str) -> str:
        lang = self._db.get(session_id, "language", "en")
        category = _detect_category(text) or "housing"
        self._db.set(session_id, "pending_category", category)
        self._db.set(session_id, "state", "awaiting_location_for_resource")
        return _t(lang, "ask_location")

    def _handle_location_input(self, session_id: str, location: str) -> str:
        lang = self._db.get(session_id, "language", "en")
        category = self._db.get(session_id, "pending_category", "housing")
        self._db.set(session_id, "location", location)
        self._db.set(session_id, "state", "idle")

        resources = self._api.search_resources(category, location)
        if not resources:
            return _t(lang, "no_results")

        lines = [_t(lang, "resource_header")]
        for i, r in enumerate(resources, 1):
            mock_note = " (demo data)" if r.get("_mock") else ""
            lines.append(
                f"\n{i}. {r['name']}{mock_note}\n"
                f"   📍 {r['address']}\n"
                f"   📞 {r['phone']}\n"
                f"   {r['description']}"
            )
            if r.get("url"):
                lines.append(f"   🔗 {r['url']}")
        lines.append(
            "\n\nWould you like to check your eligibility for assistance programs? "
            "(Type 'check eligibility' or ask about another resource.)"
        )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Eligibility flow
    # ------------------------------------------------------------------

    def _start_eligibility_flow(self, session_id: str) -> str:
        lang = self._db.get(session_id, "language", "en")
        self._db.set(session_id, "state", "awaiting_income")
        return _t(lang, "ask_income")

    def _handle_income_input(self, session_id: str, text: str) -> str:
        lang = self._db.get(session_id, "language", "en")
        income = self._parse_number(text)
        if income is None:
            return "Please enter a numeric income value (e.g., '24000')."
        self._db.set(session_id, "income", income)
        self._db.set(session_id, "state", "awaiting_household_size")
        return _t(lang, "ask_household_size")

    def _handle_household_size_input(self, session_id: str, text: str) -> str:
        lang = self._db.get(session_id, "language", "en")
        size_val = self._parse_number(text)
        if size_val is None or int(size_val) < 1:
            return "Please enter the number of people in your household (e.g., '3')."
        household_size = int(size_val)
        income = self._db.get(session_id, "income", 0)
        self._db.set(session_id, "household_size", household_size)
        self._db.set(session_id, "state", "idle")

        results = check_eligibility(income, household_size)
        header = _t(lang, "eligibility_header")
        formatted = format_eligibility_results(results, lang)
        return (
            f"{header}\n\n{formatted}\n\n"
            "Note: This is an estimate based on federal guidelines. "
            "Contact your local 211 or program office for official determination.\n\n"
            "Is there anything else I can help you with? "
            "(Type 'help' for options or 'quit' to exit.)"
        )

    def _handle_location_for_eligibility(self, session_id: str, location: str) -> str:
        self._db.set(session_id, "location", location)
        self._db.set(session_id, "state", "awaiting_income")
        lang = self._db.get(session_id, "language", "en")
        return _t(lang, "ask_income")

    # ------------------------------------------------------------------
    # Language change
    # ------------------------------------------------------------------

    def _handle_language_change(self, session_id: str, text: str) -> str:
        lower = text.lower()
        new_lang = None
        for keyword, code in _LANGUAGE_MAP.items():
            if keyword in lower:
                new_lang = code
                break
        if new_lang and new_lang in SUPPORTED_LANGUAGES:
            self._db.set(session_id, "language", new_lang)
            return _t(new_lang, "welcome")
        return f"Sorry, that language is not yet supported. Available: {', '.join(SUPPORTED_LANGUAGES)}"

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_number(text: str) -> Optional[float]:
        """Extract the first numeric value from *text*, or return None."""
        # Remove currency symbols and commas
        cleaned = re.sub(r"[$,]", "", text.strip())
        match = re.search(r"\d+(\.\d+)?", cleaned)
        if match:
            return float(match.group())
        return None


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def run_cli():
    """Run the bot interactively in the terminal."""
    print("=" * 60)
    print("  211 Resource & Eligibility Checker Bot")
    print("  Type 'help' for options or 'quit' to exit.")
    print("=" * 60)

    bot = ResourceEligibilityBot()
    session_id = bot.start_session(language="en")
    print(f"\nBot: {bot.get_welcome_message(session_id)}\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye!")
            bot.end_session(session_id)
            break

        if not user_input:
            continue

        response = bot.handle_message(session_id, user_input)
        print(f"\nBot: {response}\n")

        # Session may have been deleted on "quit"
        if not bot._db.session_exists(session_id):
            break


if __name__ == "__main__":
    run_cli()
