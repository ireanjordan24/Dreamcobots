"""LeadGenBot: automates lead scraping, outreach, and CSV export."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import csv
import io
import logging
import re
from typing import Dict, List, Optional

from core.bot_base import BotBase
from core.crash_guard import crash_guard, safe_run
from core.dream_core import DreamCore
from core.monetization_hooks import MonetizationHooks
from core.revenue_engine import RevenueEngine

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:  # pragma: no cover
    BS4_AVAILABLE = False

try:
    import psycopg2

    PSYCOPG2_AVAILABLE = True
except ImportError:  # pragma: no cover – Postgres optional in testing
    PSYCOPG2_AVAILABLE = False

OUTREACH_REVENUE_USD = 10.0  # revenue credited per outreach email sent


class LeadGenBot(BotBase):
    """
    Automates lead scraping, PostgreSQL storage, outreach emailing, and CSV export.

    Responsibilities:
    - Parse HTML pages to extract leads (name, email, phone, company, url).
    - Store leads in a PostgreSQL database (when connection is available).
    - Generate outreach emails via DreamCore.
    - Export leads to CSV for batch delivery.
    - Track revenue and funnel stages.
    """

    def __init__(
        self,
        db_dsn: Optional[str] = None,
        revenue_engine: Optional[RevenueEngine] = None,
        monetization_hooks: Optional[MonetizationHooks] = None,
        dream_core: Optional[DreamCore] = None,
    ):
        super().__init__(name="LeadGenBot")
        self.db_dsn = db_dsn
        self.revenue_engine = revenue_engine or RevenueEngine()
        self.monetization_hooks = monetization_hooks or MonetizationHooks()
        self.dream_core = dream_core or DreamCore()
        self._leads: List[Dict] = []
        self._outreach_emails: List[Dict] = []
        self._html_sources: List[str] = []
        self._db_conn = None

    # ------------------------------------------------------------------
    # BotBase lifecycle hooks
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        self.logger.info("LeadGenBot starting. DB DSN provided: %s", bool(self.db_dsn))
        self.monetization_hooks.track("bot_started", {"bot": self.name})
        if self.db_dsn and PSYCOPG2_AVAILABLE:
            self._connect_db()

    def on_stop(self) -> None:
        self.logger.info(
            "LeadGenBot stopped. Leads scraped: %d | Revenue: $%.2f",
            len(self._leads),
            self.revenue_engine.total(),
        )
        self.monetization_hooks.track(
            "bot_stopped",
            {"leads": len(self._leads), "revenue": self.revenue_engine.total()},
        )
        self._close_db()

    def execute(self) -> None:
        """Scrape all queued HTML sources, store leads, and send outreach."""
        for html in self._html_sources:
            with safe_run("scrape_html"):
                leads = self.scrape_html(html)
                for lead in leads:
                    self._store_lead(lead)
        self._html_sources.clear()

        for lead in self._leads:
            with safe_run(f"outreach:{lead.get('email', 'unknown')}"):
                email = self.dream_core.generate_lead_outreach(lead)
                self._outreach_emails.append(email)
                self.revenue_engine.record(source="lead_outreach", amount=OUTREACH_REVENUE_USD)
                self.monetization_hooks.track("outreach_sent", {"lead": lead.get("email")})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_html_source(self, html: str) -> None:
        """Queue an HTML page for lead scraping."""
        self._html_sources.append(html)

    def scrape_html(self, html: str) -> List[Dict]:
        """
        Parse HTML and extract lead data.

        Extracts: name, email, phone, company, url from structured HTML.
        Supports both BeautifulSoup parsing and lightweight regex fallback.
        """
        if BS4_AVAILABLE:
            return self._scrape_with_bs4(html)
        return self._scrape_with_regex(html)

    def export_csv(self) -> str:
        """Export all leads as a CSV string."""
        if not self._leads:
            return ""
        fieldnames = ["name", "email", "phone", "company", "url"]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(self._leads)
        csv_str = output.getvalue()
        self.logger.info("CSV exported: %d leads", len(self._leads))
        return csv_str

    def get_leads(self) -> List[Dict]:
        """Return all scraped leads."""
        return list(self._leads)

    def get_outreach_emails(self) -> List[Dict]:
        """Return all generated outreach emails."""
        return list(self._outreach_emails)

    # ------------------------------------------------------------------
    # HTML scraping helpers
    # ------------------------------------------------------------------

    def _scrape_with_bs4(self, html: str) -> List[Dict]:
        """Extract leads using BeautifulSoup from structured HTML."""
        soup = BeautifulSoup(html, "html.parser")
        leads = []
        for card in soup.select("[class*='lead'], [class*='contact'], article, .card"):
            lead = self._extract_lead_from_element(str(card))
            if lead.get("email") or lead.get("name"):
                leads.append(lead)
        # Fallback: scan entire document if no cards found
        if not leads:
            lead = self._extract_lead_from_element(html)
            if lead.get("email") or lead.get("name"):
                leads.append(lead)
        return leads

    def _scrape_with_regex(self, html: str) -> List[Dict]:
        """Lightweight regex-based lead extraction (no external dependencies)."""
        lead = self._extract_lead_from_element(html)
        return [lead] if (lead.get("email") or lead.get("name")) else []

    def _extract_lead_from_element(self, html_fragment: str) -> Dict:
        """Extract individual lead fields from an HTML fragment using regex."""
        email_match = re.search(
            r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", html_fragment
        )
        phone_match = re.search(
            r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", html_fragment
        )
        url_match = re.search(r"https?://[^\s\"'>]+", html_fragment)
        # Try to extract name from common patterns
        name_match = re.search(
            r'(?:name["\s:=>]+)([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)', html_fragment
        )
        company_match = re.search(
            r'(?:company|org|organisation)["\s:=>]+([A-Za-z0-9\s&.,-]+?)(?:[<"\n]|$)',
            html_fragment,
            re.IGNORECASE,
        )
        return {
            "name": name_match.group(1).strip() if name_match else "",
            "email": email_match.group(0) if email_match else "",
            "phone": phone_match.group(0) if phone_match else "",
            "company": company_match.group(1).strip() if company_match else "",
            "url": url_match.group(0) if url_match else "",
        }

    # ------------------------------------------------------------------
    # PostgreSQL helpers
    # ------------------------------------------------------------------

    def _connect_db(self) -> None:
        """Establish a PostgreSQL connection and create the leads table."""
        try:
            self._db_conn = psycopg2.connect(self.db_dsn)
            self._create_table()
            self.logger.info("Database connection established.")
        except Exception as exc:
            self.logger.error("Failed to connect to database: %s", exc)
            self._db_conn = None

    def _close_db(self) -> None:
        """Close the PostgreSQL connection if open."""
        if self._db_conn:
            try:
                self._db_conn.close()
            except Exception:
                pass
            self._db_conn = None

    @crash_guard
    def _create_table(self) -> None:
        """Create the leads table if it does not exist."""
        if not self._db_conn:
            return
        with self._db_conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS leads (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    company TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
                """
            )
            self._db_conn.commit()

    @crash_guard
    def _insert_lead(self, lead: Dict) -> None:
        """Insert a lead record into PostgreSQL."""
        if not self._db_conn:
            return
        with self._db_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO leads (name, email, phone, company, url) VALUES (%s,%s,%s,%s,%s)",
                (
                    lead.get("name"),
                    lead.get("email"),
                    lead.get("phone"),
                    lead.get("company"),
                    lead.get("url"),
                ),
            )
            self._db_conn.commit()

    def _store_lead(self, lead: Dict) -> None:
        """Store lead in memory and optionally in PostgreSQL."""
        self._leads.append(lead)
        self.monetization_hooks.track("lead_scraped", {"email": lead.get("email")})
        if self._db_conn:
            self._insert_lead(lead)

    def add_lead(self, lead: Dict) -> None:
        """Public method to add a pre-formed lead dict (bypasses scraping)."""
        self._store_lead(lead)
