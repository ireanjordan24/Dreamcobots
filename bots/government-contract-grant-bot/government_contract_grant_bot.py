"""
bots/government-contract-grant-bot/government_contract_grant_bot.py

Fully implemented Government Contract & Grant Bot.
Searches SAM.gov and Grants.gov (simulated) for relevant opportunities,
processes results, and exports structured data for downstream consumption.
"""

import sys
import os
import random
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Any

# Allow absolute imports when the package is not installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.bot_base import BotBase


# ---------------------------------------------------------------------------
# Simulated data pools
# ---------------------------------------------------------------------------

_SAM_GOV_POOL: list[dict[str, Any]] = [
    {
        "id": "SAM-2024-001",
        "title": "AI Research and Development Services",
        "agency": "Department of Defense",
        "value_usd": 2_500_000,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=30)).date().isoformat(),
        "naics": "541715",
        "type": "contract",
        "set_aside": "Small Business",
        "description": "R&D services for advanced artificial intelligence applications.",
        "url": "https://sam.gov/opp/SAM-2024-001",
    },
    {
        "id": "SAM-2024-002",
        "title": "Cybersecurity Infrastructure Upgrade",
        "agency": "Department of Homeland Security",
        "value_usd": 4_800_000,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=45)).date().isoformat(),
        "naics": "541512",
        "type": "contract",
        "set_aside": "8(a)",
        "description": "Modernize cybersecurity infrastructure across agency offices using advanced technology solutions.",
        "url": "https://sam.gov/opp/SAM-2024-002",
    },
    {
        "id": "SAM-2024-003",
        "title": "Cloud Migration Professional Services",
        "agency": "General Services Administration",
        "value_usd": 1_200_000,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=20)).date().isoformat(),
        "naics": "541511",
        "type": "contract",
        "set_aside": "Total Small Business",
        "description": "Migrate legacy on-premise systems to FedRAMP cloud environments.",
        "url": "https://sam.gov/opp/SAM-2024-003",
    },
    {
        "id": "SAM-2024-004",
        "title": "Data Analytics Platform Development",
        "agency": "Department of Energy",
        "value_usd": 3_100_000,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=60)).date().isoformat(),
        "naics": "541519",
        "type": "contract",
        "set_aside": "SDVOSB",
        "description": "Build an enterprise data analytics platform for energy grid monitoring.",
        "url": "https://sam.gov/opp/SAM-2024-004",
    },
    {
        "id": "SAM-2024-005",
        "title": "Machine Learning Model Training Infrastructure",
        "agency": "National Institutes of Health",
        "value_usd": 900_000,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=15)).date().isoformat(),
        "naics": "541715",
        "type": "contract",
        "set_aside": "WOSB",
        "description": "Provide GPU compute infrastructure for biomedical ML model training.",
        "url": "https://sam.gov/opp/SAM-2024-005",
    },
]

_GRANTS_GOV_POOL: list[dict[str, Any]] = [
    {
        "id": "GRANTS-2024-001",
        "title": "Small Business Innovation Research - Phase II",
        "agency": "National Science Foundation",
        "award_ceiling_usd": 750_000,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=40)).date().isoformat(),
        "cfda": "47.041",
        "type": "grant",
        "eligibility": "Small Businesses",
        "description": "Phase II SBIR funding for commercially viable deep-tech innovations.",
        "url": "https://grants.gov/web/grants/view-opportunity.html?oppId=GRANTS-2024-001",
    },
    {
        "id": "GRANTS-2024-002",
        "title": "Advanced Manufacturing Technology Development",
        "agency": "Department of Commerce",
        "award_ceiling_usd": 500_000,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=55)).date().isoformat(),
        "cfda": "11.611",
        "type": "grant",
        "eligibility": "Nonprofits, Universities, Small Businesses",
        "description": "Grant for developing next-generation advanced manufacturing technologies.",
        "url": "https://grants.gov/web/grants/view-opportunity.html?oppId=GRANTS-2024-002",
    },
    {
        "id": "GRANTS-2024-003",
        "title": "Clean Energy Innovation Fund",
        "agency": "Department of Energy",
        "award_ceiling_usd": 2_000_000,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=70)).date().isoformat(),
        "cfda": "81.087",
        "type": "grant",
        "eligibility": "Any Organization",
        "description": "Fund clean energy R&D projects with commercial potential.",
        "url": "https://grants.gov/web/grants/view-opportunity.html?oppId=GRANTS-2024-003",
    },
    {
        "id": "GRANTS-2024-004",
        "title": "Rural Broadband Infrastructure Grant",
        "agency": "USDA",
        "award_ceiling_usd": 5_000_000,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=90)).date().isoformat(),
        "cfda": "10.886",
        "type": "grant",
        "eligibility": "State/Local Government, Nonprofits",
        "description": "Expand broadband connectivity to underserved rural communities.",
        "url": "https://grants.gov/web/grants/view-opportunity.html?oppId=GRANTS-2024-004",
    },
    {
        "id": "GRANTS-2024-005",
        "title": "Health IT Modernisation Initiative",
        "agency": "Department of Health and Human Services",
        "award_ceiling_usd": 1_500_000,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=35)).date().isoformat(),
        "cfda": "93.778",
        "type": "grant",
        "eligibility": "State Agencies, Hospitals, Health Systems",
        "description": "Grants to modernise health information technology infrastructure.",
        "url": "https://grants.gov/web/grants/view-opportunity.html?oppId=GRANTS-2024-005",
    },
]


class GovernmentContractGrantBot(BotBase):
    """
    Bot that discovers government contract and grant opportunities from
    SAM.gov and Grants.gov and exposes them as structured data.
    """

    def __init__(
        self,
        bot_id: str = "gov-contract-grant-bot-001",
        search_query: str = "technology services",
        poll_interval_seconds: int = 60,
    ) -> None:
        """
        Initialise the bot.

        Args:
            bot_id: Unique identifier for this bot instance.
            search_query: Default keyword query used when searching portals.
            poll_interval_seconds: Seconds between each polling cycle.
        """
        super().__init__(
            bot_name="GovernmentContractGrantBot",
            bot_id=bot_id,
        )
        self.search_query: str = search_query
        self.poll_interval_seconds: int = poll_interval_seconds

        self._contracts: list[dict[str, Any]] = []
        self._grants: list[dict[str, Any]] = []
        self._data_lock: threading.Lock = threading.Lock()
        self._stop_event: threading.Event = threading.Event()

    # ------------------------------------------------------------------
    # SAM.gov simulation
    # ------------------------------------------------------------------

    def search_sam_gov(self, query: str) -> list[dict[str, Any]]:
        """
        Search SAM.gov for contract opportunities matching *query*.

        Args:
            query: Keywords to match against opportunity titles and descriptions.

        Returns:
            A list of matching contract opportunity dicts.
        """
        self.logger.debug("Searching SAM.gov for query=%r", query)
        keywords = [kw.lower() for kw in query.split()]
        results: list[dict[str, Any]] = []

        for record in _SAM_GOV_POOL:
            text = (record["title"] + " " + record["description"]).lower()
            if any(kw in text for kw in keywords) or not keywords:
                enriched = dict(record)
                enriched["retrieved_at"] = datetime.now(timezone.utc).isoformat()
                enriched["source"] = "sam.gov"
                results.append(enriched)

        time.sleep(random.uniform(0.05, 0.15))
        self.logger.info("SAM.gov returned %d results for query=%r", len(results), query)
        return results

    # ------------------------------------------------------------------
    # Grants.gov simulation
    # ------------------------------------------------------------------

    def search_grants_gov(self, query: str) -> list[dict[str, Any]]:
        """
        Search Grants.gov for grant opportunities matching *query*.

        Args:
            query: Keywords to match against grant titles and descriptions.

        Returns:
            A list of matching grant opportunity dicts.
        """
        self.logger.debug("Searching Grants.gov for query=%r", query)
        keywords = [kw.lower() for kw in query.split()]
        results: list[dict[str, Any]] = []

        for record in _GRANTS_GOV_POOL:
            text = (record["title"] + " " + record["description"]).lower()
            if any(kw in text for kw in keywords) or not keywords:
                enriched = dict(record)
                enriched["retrieved_at"] = datetime.now(timezone.utc).isoformat()
                enriched["source"] = "grants.gov"
                results.append(enriched)

        time.sleep(random.uniform(0.05, 0.15))
        self.logger.info(
            "Grants.gov returned %d results for query=%r", len(results), query
        )
        return results

    # ------------------------------------------------------------------
    # Processing helpers
    # ------------------------------------------------------------------

    def process_contracts(self) -> None:
        """Fetch and store contract opportunities from SAM.gov, deduplicating by ID."""
        self.log_activity(f"Processing contracts for query={self.search_query!r}")
        try:
            raw = self.search_sam_gov(self.search_query)
            with self._data_lock:
                existing_ids = {c["id"] for c in self._contracts}
                new_records = [r for r in raw if r["id"] not in existing_ids]
                self._contracts.extend(new_records)
            self.log_activity(
                f"Stored {len(new_records)} new contract(s); total={len(self._contracts)}"
            )
        except Exception as exc:
            self.handle_error(exc)

    def process_grants(self) -> None:
        """Fetch and store grant opportunities from Grants.gov, deduplicating by ID."""
        self.log_activity(f"Processing grants for query={self.search_query!r}")
        try:
            raw = self.search_grants_gov(self.search_query)
            with self._data_lock:
                existing_ids = {g["id"] for g in self._grants}
                new_records = [r for r in raw if r["id"] not in existing_ids]
                self._grants.extend(new_records)
            self.log_activity(
                f"Stored {len(new_records)} new grant(s); total={len(self._grants)}"
            )
        except Exception as exc:
            self.handle_error(exc)

    # ------------------------------------------------------------------
    # BotBase interface
    # ------------------------------------------------------------------

    def run(self) -> None:
        """
        Start the bot's polling loop.

        Calls :meth:`process_contracts` and :meth:`process_grants` each cycle
        until :meth:`stop` is called.
        """
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self._stop_event.clear()
        self.log_activity("Bot started")

        try:
            while not self._stop_event.is_set():
                self.process_contracts()
                self.process_grants()
                self._stop_event.wait(timeout=self.poll_interval_seconds)
        except Exception as exc:
            self.handle_error(exc)
        finally:
            self._set_running(False)
            self.log_activity("Bot stopped")

    def stop(self) -> None:
        """Signal the polling loop to stop gracefully."""
        self.logger.info("Stop requested for bot_id=%s", self.bot_id)
        self._stop_event.set()

    # ------------------------------------------------------------------
    # Data export
    # ------------------------------------------------------------------

    def export_structured_data(self) -> dict[str, Any]:
        """
        Export all discovered contracts and grants as structured data.

        Returns:
            A dict with base bot metadata plus ``contracts`` and ``grants``
            lists ready for DataForge ingestion.
        """
        base = super().export_structured_data()
        with self._data_lock:
            base["contracts"] = list(self._contracts)
            base["grants"] = list(self._grants)
            base["summary"] = {
                "total_contracts": len(self._contracts),
                "total_grants": len(self._grants),
                "total_opportunities": len(self._contracts) + len(self._grants),
                "total_contract_value_usd": sum(
                    c.get("value_usd", 0) for c in self._contracts
                ),
                "total_grant_ceiling_usd": sum(
                    g.get("award_ceiling_usd", 0) for g in self._grants
                ),
            }
        return base


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    bot = GovernmentContractGrantBot(poll_interval_seconds=5)
    thread = threading.Thread(target=bot.run, daemon=True)
    thread.start()

    time.sleep(3)
    bot.stop()
    thread.join(timeout=10)

    data = bot.export_structured_data()
    print(json.dumps(data, indent=2, default=str))
