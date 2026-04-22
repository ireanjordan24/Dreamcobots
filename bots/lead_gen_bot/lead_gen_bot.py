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
from typing import List, Dict

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


class _SimpleRevenueEngine:
    """Minimal stub revenue engine used when no real revenue_engine is passed."""

    def __init__(self) -> None:
        self._total: float = 0.0

    def add(self, amount: float) -> None:
        self._total += amount

    def total(self) -> float:
        return self._total


class Bot:
    """
    Lead Generation Bot.

    Generates simulated business leads and persists them to disk so that
    the Sales Bot and other downstream bots can act on them.
    Replace ``generate_leads()`` internals with real scraping / API calls
    for production use.
    """

    def __init__(self, leads_file: str = _DEFAULT_LEADS_FILE, **kwargs) -> None:
        self.name = "Lead Generator Bot"
        self.leads_file = leads_file
        self._total_generated: int = 0
        self._scraped_leads: List[Dict] = []
        self.revenue_engine = _SimpleRevenueEngine()
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
            leads.append({
                "business": f"{industry.title()} Business #{i + 1}",
                "industry": industry,
                "phone": f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "email": f"contact{random.randint(1, 9999)}@{industry.replace(' ', '')}.example.com",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            })
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

    def scrape_html(self, html: str) -> List[Dict]:
        """Extract leads (name + email) from an HTML snippet.

        Parses ``href="mailto:..."`` links and bare email addresses using
        a simple regex.  Returns a list of dicts with the fields required by
        the ``LeadResponse`` schema (name, email, phone, company, url).
        """
        import re
        email_re = re.compile(
            r"(?:mailto:)?([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})"
        )
        found = []
        for match in email_re.finditer(html or ""):
            email = match.group(1)
            name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
            found.append({
                "name": name,
                "email": email,
                "phone": "",
                "company": email.split("@")[1] if "@" in email else "",
                "url": "",
                "type": "scraped",
            })
        return found

    def add_html_source(self, html: str) -> None:
        """Store an HTML snippet for later scraping.

        Scraped leads are accessible via :meth:`get_leads` after calling
        :meth:`run` or :meth:`scrape_html`.
        """
        leads = self.scrape_html(html)
        self._scraped_leads.extend(leads)

    def add_lead(self, lead: Dict) -> None:
        """Append a lead dict to the internal scraped leads list."""
        self._scraped_leads.append(lead)

    def get_leads(self) -> List[Dict]:
        """Return all scraped/added leads."""
        return list(self._scraped_leads)

    def get_outreach_emails(self) -> List[str]:
        """Return a mock list of outreach emails (one per scraped lead)."""
        return [lead["email"] for lead in self._scraped_leads if lead.get("email")]

    def export_csv(self) -> str:
        """Export scraped leads to a CSV string."""
        import csv
        import io
        if not self._scraped_leads:
            return "name,email,type\n"
        output = io.StringIO()
        fields = list(self._scraped_leads[0].keys())
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(self._scraped_leads)
        return output.getvalue()


# Alias for external imports expecting the standard naming convention
LeadGenBot = Bot
