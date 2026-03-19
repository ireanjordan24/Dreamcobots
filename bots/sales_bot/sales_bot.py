"""
DreamCo Sales Bot
==================

Reads persisted leads from the Lead Generation Bot and prepares them
for outbound sales pipelines, CRM upload, or direct outreach.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import ast
import os
import sys
from datetime import datetime, timezone
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

# ---------------------------------------------------------------------------
# Default leads file (relative to repo root)
# ---------------------------------------------------------------------------
_DEFAULT_LEADS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "leads.txt"
)


class Bot:
    """
    Sales Bot.

    Reads the leads file produced by the Lead Generation Bot and surfaces
    an actionable sales-readiness report.  In a production deployment,
    extend ``process_leads()`` with real CRM integration, email outreach,
    or paid-traffic automation.
    """

    def __init__(self, leads_file: str = _DEFAULT_LEADS_FILE) -> None:
        self.name = "Sales Bot"
        self.leads_file = leads_file
        self._processed_count: int = 0

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Read available leads and report sales readiness."""
        leads = self.read_leads()
        if not leads:
            return "Sales Bot: no leads available yet — waiting for Lead Generator Bot"
        self._processed_count += len(leads)
        return f"💰 Sales Bot ready to act on {len(leads)} leads (processed so far: {self._processed_count})"

    def read_leads(self) -> List[Dict]:
        """Read and parse leads from the leads file."""
        if not os.path.exists(self.leads_file):
            return []
        leads: List[Dict] = []
        try:
            with open(self.leads_file, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        leads.append(ast.literal_eval(line))
                    except Exception:  # noqa: BLE001
                        leads.append({"raw": line})
        except OSError:
            return []
        return leads

    def process_leads(self) -> List[Dict]:
        """
        Return leads enriched with a basic sales-priority score.

        Override or extend this method to integrate real scoring logic
        (e.g. lead source quality, industry value, recency).
        """
        leads = self.read_leads()
        enriched = []
        for lead in leads:
            enriched.append({
                **lead,
                "priority": "high" if "real estate" in str(lead).lower() else "normal",
                "processed_at": datetime.now(timezone.utc).isoformat(),
            })
        return enriched

    # ------------------------------------------------------------------
    # Status / reporting
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return current bot status."""
        lead_count = len(self.read_leads())
        return {
            "name": self.name,
            "available_leads": lead_count,
            "processed_count": self._processed_count,
            "leads_file": self.leads_file,
            "status": "active",
        }
