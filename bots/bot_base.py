"""Base class for all Dreamcobots bots."""
import logging

logger = logging.getLogger(__name__)


class BotBase:
    """Base class providing common interface for all bots."""

    def __init__(self, bot_id: str, bot_name: str):
        """Initialize the bot with an ID and name.

        Args:
            bot_id: Unique identifier for this bot instance.
            bot_name: Human-readable name for this bot.
        """
        self.bot_id = bot_id
        self.bot_name = bot_name
        logger.info("Initialized bot: %s (%s)", bot_name, bot_id)

    def run(self):
        """Run the bot. Must be overridden by subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement run()")

    def export_structured_data(self) -> dict:
        """Export structured data from this bot for DataForge consumption.

        Returns:
            A dict with keys: type, labels, content, consent, anonymized, license.
        """
        return {
            "type": "generic",
            "labels": [],
            "content": [],
            "consent": True,
            "anonymized": True,
            "license": "CC-BY-4.0"
        }
