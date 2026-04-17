"""
DreamCo Lead Generation Bot
============================

Generates and stores industry-specific business leads, feeding the
downstream Sales Bot and other monetisation bots in the DreamCo network.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import random
import sys
from datetime import datetime, timezone
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

# ---------------------------------------------------------------------------
# Default data file (relative to repo root)
# ---------------------------------------------------------------------------
_DEFAULT_LEADS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "leads.txt"
)

INDUSTRIES = [
    "real estate",
    "roofing",
    "plumbing",
    "barbershops",
    "landscaping",
    "HVAC",
    "electricians",
    "restaurants",
    "retail",
    "dental offices",
]


class Bot:
    """
    Lead Generation Bot.

    Generates simulated business leads and persists them to disk so that
    the Sales Bot and other downstream bots can act on them.
    Replace ``generate_leads()`` internals with real scraping / API calls
    for production use.
    """

    def __init__(self, leads_file: str = _DEFAULT_LEADS_FILE) -> None:
        self.name = "Lead Generator Bot"
        self.leads_file = leads_file
        self._total_generated: int = 0
        os.makedirs(os.path.dirname(os.path.abspath(self.leads_file)), exist_ok=True)

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Generate a batch of leads and persist them."""
        leads = self.generate_leads()
        self.save_leads(leads)
        self._total_generated += len(leads)
        return f"Generated {len(leads)} leads (total: {self._total_generated})"

    def generate_leads(self, count: int | None = None) -> List[Dict]:
        """
        Produce a batch of placeholder leads.

        Parameters
        ----------
        count : int, optional
            Number of leads to generate.  Defaults to a random value
            between 2 and 5.
        """
        if count is None:
            count = random.randint(2, 5)

        leads: List[Dict] = []
        for i in range(count):
            industry = random.choice(INDUSTRIES)
            leads.append(
                {
                    "business": f"{industry.title()} Business #{i + 1}",
                    "industry": industry,
                    "phone": f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    "email": f"contact{random.randint(1, 9999)}@{industry.replace(' ', '')}.example.com",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        return leads

    def save_leads(self, leads: List[Dict]) -> None:
        """Append *leads* to the persistent leads file."""
        with open(self.leads_file, "a", encoding="utf-8") as fh:
            for lead in leads:
                fh.write(str(lead) + "\n")

    # ------------------------------------------------------------------
    # Status / reporting
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return current bot status."""
        return {
            "name": self.name,
            "total_generated": self._total_generated,
            "leads_file": self.leads_file,
            "status": "active",
        }
