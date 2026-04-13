"""
TaskEngine - Core task execution engine for Buddy.

Maps parsed intents to registered capability handlers and executes them.
New capabilities are registered dynamically, enabling a modular,
extensible architecture.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from BuddyAI.text_handler import ParsedCommand, TextHandler

logger = logging.getLogger(__name__)


class UnknownIntentError(ValueError):
    """Raised when no capability is registered for a given intent."""


class TaskEngine:
    """Dispatches parsed commands to registered capability handlers.

    Capabilities are plain callables that accept a ``params`` dict and
    return a result dict.

    Example::

        engine = TaskEngine()
        engine.register_capability("greet", lambda p: {"message": "Hello!"})
        result = engine.execute("greet", {})
        # {"message": "Hello!"}
    """

    def __init__(self) -> None:
        self._capabilities: Dict[str, Callable] = {}
        self._text_handler = TextHandler()

    # ------------------------------------------------------------------
    # Capability management
    # ------------------------------------------------------------------

    def register_capability(self, intent: str, handler: Callable) -> None:
        """Register *handler* for *intent*.

        Args:
            intent: Intent label string (e.g. ``"add_todo"``).
            handler: Callable that accepts ``params: dict`` and returns a dict.
        """
        self._capabilities[intent] = handler
        logger.debug("Registered capability for intent '%s'.", intent)

    def unregister_capability(self, intent: str) -> bool:
        """Remove the handler for *intent*.

        Returns:
            ``True`` if the capability existed and was removed.
        """
        if intent in self._capabilities:
            del self._capabilities[intent]
            logger.debug("Unregistered capability for intent '%s'.", intent)
            return True
        return False

    def list_capabilities(self) -> List[str]:
        """Return a sorted list of all registered intent names."""
        return sorted(self._capabilities.keys())

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the capability registered for *intent*.

        Args:
            intent: Intent label string.
            params: Parameters to pass to the handler.

        Returns:
            Result dict from the handler.

        Raises:
            UnknownIntentError: If no capability is registered for *intent*.
        """
        handler = self._capabilities.get(intent)
        if handler is None:
            raise UnknownIntentError(
                f"No capability registered for intent '{intent}'. "
                f"Available: {self.list_capabilities()}"
            )
        logger.debug("Executing intent '%s' with params: %s", intent, params)
        try:
            result = handler(params)
            return result if isinstance(result, dict) else {"result": result}
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Handler for '%s' raised: %s", intent, exc)
            return {"success": False, "error": str(exc)}

    def process_text(self, text: str) -> Dict[str, Any]:
        """Parse *text* and execute the matched capability.

        This is the high-level entry point that combines text parsing and
        task execution in a single call.

        Args:
            text: Free-form user command string.

        Returns:
            Result dict from the matching capability handler,
            or an error dict when the intent is unknown or text is empty.
        """
        if not text or not text.strip():
            return {"success": False, "message": "Empty input received."}

        command: ParsedCommand = self._text_handler.parse(text)
        logger.info(
            "Parsed command: intent='%s' params=%s", command.intent, command.params
        )

        if command.intent == "unknown":
            return {
                "success": False,
                "message": (
                    f"Sorry, I didn't understand: \"{text}\". "
                    "Type 'help' to see what I can do."
                ),
            }

        if command.intent not in self._capabilities:
            return {
                "success": False,
                "message": (
                    f"I understood '{command.intent}' but don't have that "
                    "capability yet.  You can install a library or plugin to "
                    "add it."
                ),
            }

        return self.execute(command.intent, command.params)
