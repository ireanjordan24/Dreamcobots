"""
Lead Gen Bot — Real Lead Scraper

Scrapes business leads from a configurable directory URL, saves them to
``data/leads.txt`` for downstream consumption by the Outreach Sales Bot.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]
    BeautifulSoup = None  # type: ignore[assignment]

from framework import GlobalAISourcesFlow  # noqa: F401  # GLOBAL AI SOURCES FLOW


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class LeadScraperError(Exception):
    """Raised when a non-recoverable scraping error occurs."""


# ---------------------------------------------------------------------------
# Bot
# ---------------------------------------------------------------------------

class LeadScraperBot:
    """Real Lead Scraper — fetches business leads from a directory site.

    Parameters
    ----------
    url:
        Target directory URL.  Defaults to ``https://example.com/business-directory``.
    data_dir:
        Directory where ``leads.txt`` is written.  Defaults to ``data/``.
    """

    def __init__(
        self,
        url: str = "https://example.com/business-directory",
        data_dir: str = "data",
    ) -> None:
        self.name = "Real Lead Scraper"
        self.url = url
        self.data_dir = data_dir
        self._flow = GlobalAISourcesFlow(bot_name="LeadScraperBot")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Scrape leads and persist them; return a status string."""
        leads = self.scrape()
        self.save(leads)
        return f"🔥 Scraped {len(leads)} real leads"

    def scrape(self) -> list[dict]:
        """Fetch leads from *self.url* and return a list of lead dicts.

        Each lead dict contains ``name`` and ``phone`` keys.  An empty list
        is returned if scraping fails or the required libraries are missing.
        """
        if requests is None or BeautifulSoup is None:
            print("❌ Scraping failed: 'requests' or 'beautifulsoup4' not installed")
            return []

        leads: list[dict] = []

        try:
            res = requests.get(self.url, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")

            for item in soup.find_all("div", class_="business"):
                name_tag = item.find("h2")
                phone_tag = item.find("span", class_="phone")

                if name_tag and phone_tag:
                    leads.append(
                        {
                            "name": name_tag.text.strip(),
                            "phone": phone_tag.text.strip(),
                        }
                    )

        except Exception as exc:  # noqa: BLE001
            print(f"❌ Scraping failed: {exc}")

        return leads

    def save(self, leads: list[dict]) -> None:
        """Append *leads* to ``{data_dir}/leads.txt``."""
        os.makedirs(self.data_dir, exist_ok=True)
        leads_path = os.path.join(self.data_dir, "leads.txt")
        with open(leads_path, "a", encoding="utf-8") as fh:
            for lead in leads:
                fh.write(str(lead) + "\n")


# ---------------------------------------------------------------------------
# Legacy alias expected by problem-statement code snippets
# ---------------------------------------------------------------------------

class Bot(LeadScraperBot):
    """Alias retained for backwards-compatibility with problem-statement usage."""
