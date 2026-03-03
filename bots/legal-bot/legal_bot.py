"""
bots/legal-bot/legal_bot.py

LegalBot — legal information assistant.

DISCLAIMER: This bot provides general legal information only.
It is NOT legal advice and does NOT create an attorney-client relationship.
Always consult a licensed attorney for legal matters.
"""

from __future__ import annotations

import re
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

_DISCLAIMER = (
    "⚖️ LEGAL DISCLAIMER: This information is for general educational purposes only "
    "and does NOT constitute legal advice. No attorney-client relationship is created. "
    "Always consult a licensed attorney for advice about your specific legal situation."
)

_LAW_DB: dict[str, dict[str, Any]] = {
    "gdpr": {
        "full_name": "General Data Protection Regulation",
        "jurisdiction": "European Union",
        "summary": "Comprehensive data protection and privacy regulation for EU residents.",
        "key_provisions": ["right to access", "right to erasure", "data portability", "consent requirements"],
        "penalties": "Up to €20M or 4% of global annual turnover",
    },
    "dmca": {
        "full_name": "Digital Millennium Copyright Act",
        "jurisdiction": "United States",
        "summary": "US copyright law that criminalises circumvention of digital protection measures.",
        "key_provisions": ["safe harbour for ISPs", "takedown notices", "anti-circumvention"],
        "penalties": "Up to $150,000 per infringement",
    },
    "hipaa": {
        "full_name": "Health Insurance Portability and Accountability Act",
        "jurisdiction": "United States",
        "summary": "Sets standards for protecting sensitive patient health information.",
        "key_provisions": ["privacy rule", "security rule", "breach notification rule"],
        "penalties": "Up to $1.9M per violation category per year",
    },
}

_CONTRACT_RISK_TERMS: list[tuple[str, str]] = [
    (r"\bindemnif", "Indemnification clause found — review liability exposure."),
    (r"\blimitation of liability\b", "Liability cap present — verify limits are acceptable."),
    (r"\bnon-compete\b", "Non-compete clause found — check enforceability in your jurisdiction."),
    (r"\bperpetual\b.*\blicense\b", "Perpetual license grant — confirm IP rights implications."),
    (r"\bautomatic renewal\b", "Auto-renewal clause — ensure cancellation terms are clear."),
    (r"\barbitration\b", "Arbitration clause found — you may waive jury trial rights."),
    (r"\bgoverning law\b", "Governing law clause — verify jurisdiction is acceptable."),
]

_DOCUMENT_TEMPLATES: dict[str, str] = {
    "nda": (
        "NON-DISCLOSURE AGREEMENT\n\nThis Non-Disclosure Agreement ('Agreement') is entered into "
        "as of {date} by and between {party_a} ('Disclosing Party') and {party_b} ('Receiving Party').\n\n"
        "1. CONFIDENTIAL INFORMATION: The Receiving Party agrees to keep confidential all information "
        "disclosed by the Disclosing Party.\n"
        "2. TERM: This Agreement shall remain in effect for {term} years.\n"
        "3. GOVERNING LAW: This Agreement shall be governed by the laws of {jurisdiction}.\n\n"
        "{disclaimer}"
    ),
    "service_agreement": (
        "SERVICE AGREEMENT\n\nThis Service Agreement ('Agreement') is entered into "
        "as of {date} by and between {party_a} ('Service Provider') and {party_b} ('Client').\n\n"
        "1. SERVICES: Service Provider agrees to provide {services}.\n"
        "2. PAYMENT: Client agrees to pay {payment} for the services.\n"
        "3. TERM: This Agreement commences {date} and terminates upon completion of services.\n"
        "4. GOVERNING LAW: This Agreement shall be governed by the laws of {jurisdiction}.\n\n"
        "{disclaimer}"
    ),
}


class LegalBot(BotBase):
    """
    Legal information bot. All responses include mandatory legal disclaimers.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="LegalBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("LegalBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("LegalBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def search_law(self, query: str) -> dict[str, Any]:
        """
        Search for information about a law or regulation.

        Args:
            query: Law name or acronym (e.g. ``"GDPR"``).

        Returns:
            Dict with law details and disclaimer.
        """
        key = query.lower().strip()
        info = _LAW_DB.get(key, {
            "full_name": query,
            "jurisdiction": "N/A",
            "summary": f"No specific data found for '{query}'. Consult a legal professional.",
            "key_provisions": [],
            "penalties": "Varies by jurisdiction",
        })
        self.log_activity(f"Law searched: '{query}'.")
        return {**info, "query": query, "disclaimer": _DISCLAIMER}

    def analyze_contract(self, text: str) -> dict[str, Any]:
        """
        Analyse contract text for common risk clauses.

        Args:
            text: Full contract text.

        Returns:
            Dict with identified clauses, risk level, and disclaimer.
        """
        findings: list[str] = []
        for pattern, message in _CONTRACT_RISK_TERMS:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append(message)

        risk_level = (
            "High" if len(findings) >= 4
            else "Medium" if len(findings) >= 2
            else "Low"
        )
        self.log_activity("Contract analysed.")
        return {
            "findings": findings,
            "clause_count": len(findings),
            "risk_level": risk_level,
            "word_count": len(text.split()),
            "recommendations": [
                "Have a licensed attorney review before signing.",
                "Negotiate any clauses that limit your rights.",
            ],
            "disclaimer": _DISCLAIMER,
        }

    def find_attorney(self, location: str, specialty: str) -> list[dict[str, Any]]:
        """
        Simulate finding licensed attorneys in *location* with *specialty*.

        Args:
            location: City or state.
            specialty: Legal specialty (e.g. ``"employment law"``).

        Returns:
            List of attorney dicts with disclaimer.
        """
        attorneys = [
            {
                "name": f"Law Offices of A. Johnson — {specialty.title()}",
                "address": f"100 Legal Lane, {location}",
                "phone": "(555) 200-0001",
                "bar_number": "BAR-001",
                "disclaimer": _DISCLAIMER,
            },
            {
                "name": f"B. Williams & Associates — {specialty.title()}",
                "address": f"200 Court St, {location}",
                "phone": "(555) 200-0002",
                "bar_number": "BAR-002",
                "disclaimer": _DISCLAIMER,
            },
        ]
        self.log_activity(f"Attorney search: location='{location}', specialty='{specialty}'.")
        return attorneys

    def generate_legal_document(self, template: str, params: dict[str, Any]) -> str:
        """
        Fill a legal document template with *params*.

        Args:
            template: Template name (``nda`` or ``service_agreement``).
            params: Dict of template variables.

        Returns:
            Filled document string with disclaimer appended.

        Raises:
            ValueError: If the template name is not supported.
        """
        tmpl_key = template.lower().strip()
        tmpl = _DOCUMENT_TEMPLATES.get(tmpl_key)
        if tmpl is None:
            raise ValueError(
                f"Template '{template}' not supported. "
                f"Available: {list(_DOCUMENT_TEMPLATES.keys())}"
            )
        doc_params = {
            "date": datetime.now(timezone.utc).strftime("%B %d, %Y"),
            "party_a": "Party A",
            "party_b": "Party B",
            "term": "2",
            "jurisdiction": "California",
            "services": "as described in Schedule A",
            "payment": "as agreed",
            "disclaimer": _DISCLAIMER,
        }
        doc_params.update(params)
        document = tmpl.format(**doc_params)
        self.log_activity(f"Legal document generated: template='{template}'.")
        return document
