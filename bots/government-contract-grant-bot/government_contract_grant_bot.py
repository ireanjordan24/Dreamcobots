"""Government Contract & Grant Bot - scrapes and processes government contracts and grants."""
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from bots.bot_base import BotBase

logger = logging.getLogger(__name__)


class GovernmentContractGrantBot(BotBase):
    """Bot for processing government contracts and grants data.

    Inherits from BotBase and provides structured data export
    for DataForge consumption.
    """

    def __init__(self):
        """Initialize the GovernmentContractGrantBot."""
        super().__init__(
            bot_id="gov-contract-grant-001",
            bot_name="Government Contract & Grant Bot"
        )
        self._contracts: list = []
        self._grants: list = []

    def start(self):
        """Start the bot and log initialization."""
        logger.info("Government Contract & Grant Bot is starting...")
        print("Government Contract & Grant Bot is starting...")

    def process_contracts(self):
        """Process government contract data."""
        logger.info("Processing contracts...")
        print("Processing contracts...")
        self._contracts = [
            {
                "id": "CONT-001",
                "title": "IT Infrastructure Services",
                "agency": "Department of Defense",
                "value": 5000000.00,
                "status": "open",
                "type": "contract",
                "synthetic": True,
                "license": "CC-BY-4.0",
            },
            {
                "id": "CONT-002",
                "title": "Cybersecurity Assessment",
                "agency": "Department of Homeland Security",
                "value": 2500000.00,
                "status": "awarded",
                "type": "contract",
                "synthetic": True,
                "license": "CC-BY-4.0",
            },
        ]
        logger.info("Processed %d contracts.", len(self._contracts))

    def process_grants(self):
        """Process government grant data."""
        logger.info("Processing grants...")
        print("Processing grants...")
        self._grants = [
            {
                "id": "GRANT-001",
                "title": "AI Research Initiative",
                "agency": "National Science Foundation",
                "amount": 1000000.00,
                "status": "open",
                "type": "grant",
                "synthetic": True,
                "license": "CC-BY-4.0",
            },
            {
                "id": "GRANT-002",
                "title": "Climate Change Mitigation Study",
                "agency": "Department of Energy",
                "amount": 750000.00,
                "status": "awarded",
                "type": "grant",
                "synthetic": True,
                "license": "CC-BY-4.0",
            },
        ]
        logger.info("Processed %d grants.", len(self._grants))

    def run(self):
        """Run the full government contract and grant pipeline."""
        self.start()
        self.process_contracts()
        self.process_grants()
        logger.info(
            "Government bot pipeline complete: %d contracts, %d grants.",
            len(self._contracts), len(self._grants)
        )
        return {"contracts": self._contracts, "grants": self._grants}

    def export_structured_data(self) -> dict:
        """Export structured government contract and grant data for DataForge.

        Returns:
            Structured data dict with contracts and grants content.
        """
        if not self._contracts and not self._grants:
            self.process_contracts()
            self.process_grants()
        return {
            "type": "government",
            "labels": ["contracts", "grants", "federal", "procurement"],
            "content": self._contracts + self._grants,
            "consent": True,
            "anonymized": True,
            "license": "CC-BY-4.0",
            "record_count": len(self._contracts) + len(self._grants),
        }


# If this module is run directly, start the bot
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    bot = GovernmentContractGrantBot()
    bot.run()
