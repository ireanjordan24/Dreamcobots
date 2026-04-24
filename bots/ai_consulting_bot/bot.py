"""
Dreamcobots AIConsultingBot — tier-aware AI consulting service.

Pairs businesses with AI transition experts and manages the full consulting
lifecycle from expert matching through roadmap delivery and session tracking.

Key capabilities:
  1. Expert Matching      — find an AI consultant suited to the client's
     industry, company size, and transition goals.
  2. Session Management   — book, run, and log consulting sessions with
     structured agendas and outcome notes.
  3. Roadmap Generation   — produce a phased AI adoption roadmap based on
     the company's readiness profile and business objectives.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config
from bots.ai_consulting_bot.tiers import AI_CONSULTING_FEATURES, get_ai_consulting_tier_info


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AIConsultingBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class AIConsultingBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Expert domains for matching
EXPERT_DOMAINS = [
    "general_ai_strategy",
    "healthcare_ai",
    "real_estate_ai",
    "manufacturing_ai",
    "logistics_ai",
    "finance_ai",
    "retail_ai",
    "education_ai",
    "legal_ai",
    "hr_ai",
]

# Roadmap phases
ROADMAP_PHASES = [
    "discovery_and_assessment",
    "strategy_and_planning",
    "pilot_implementation",
    "full_deployment",
    "optimisation_and_scaling",
]

# Monthly session caps per tier
SESSION_CAPS = {
    Tier.FREE.value: 1,
    Tier.PRO.value: 10,
    Tier.ENTERPRISE.value: None,  # unlimited
}


# ---------------------------------------------------------------------------
# Main Bot Class
# ---------------------------------------------------------------------------

class AIConsultingBot:
    """Tier-aware AI consulting service for companies transitioning to AI.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE, PRO, ENTERPRISE).
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._sessions: list[dict] = []
        self._roadmaps: list[dict] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise AIConsultingBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_session_cap(self) -> None:
        cap = SESSION_CAPS[self.tier.value]
        if cap is not None and len(self._sessions) >= cap:
            raise AIConsultingBotTierError(
                f"Session limit of {cap} reached on the {self.config.name} tier. "
                "Please upgrade to book additional sessions."
            )

    def _check_feature(self, feature: str) -> None:
        features = AI_CONSULTING_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise AIConsultingBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                "Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    # ------------------------------------------------------------------
    # 1. Expert Matching
    # ------------------------------------------------------------------

    def match_expert(self, client: dict) -> dict:
        """Match a business with the most suitable AI consulting expert.

        Parameters
        ----------
        client : dict
            Keys: ``company_name`` (str), ``industry`` (str),
            ``company_size`` (str — small / medium / enterprise),
            ``goals`` (list[str] — optional).

        Returns
        -------
        dict
            Expert profile including name, domain, experience, and
            contact stub.
        """
        self._check_request_limit()
        self._request_count += 1

        company = client.get("company_name", "Unknown Company")
        industry = client.get("industry", "general").lower().replace(" ", "_")
        size = client.get("size", "small")
        goals = client.get("goals", ["general AI adoption"])

        # Map industry to expert domain
        domain_key = f"{industry}_ai"
        if domain_key not in EXPERT_DOMAINS:
            domain_key = "general_ai_strategy"

        # PRO/ENTERPRISE get dedicated experts; FREE gets community pool
        if self.tier == Tier.FREE:
            expert = {
                "expert_id": str(uuid.uuid4()),
                "name": "DreamCo Community Expert",
                "domain": domain_key,
                "experience_years": 3,
                "availability": "async (72h response)",
                "match_score": 70,
                "tier": self.tier.value,
                "upgrade_hint": "Upgrade to PRO for a dedicated expert with faster response.",
            }
        elif self.tier == Tier.PRO:
            expert = {
                "expert_id": str(uuid.uuid4()),
                "name": f"DreamCo Expert — {domain_key.replace('_', ' ').title()}",
                "domain": domain_key,
                "experience_years": 7,
                "availability": "scheduled (24h response)",
                "match_score": 88,
                "assigned_company": company,
                "tier": self.tier.value,
            }
        else:  # ENTERPRISE
            expert = {
                "expert_id": str(uuid.uuid4()),
                "name": f"DreamCo Senior Strategist — {domain_key.replace('_', ' ').title()}",
                "domain": domain_key,
                "experience_years": 12,
                "availability": "dedicated (2h response)",
                "match_score": 97,
                "assigned_company": company,
                "company_size": size,
                "goals_addressed": goals,
                "tier": self.tier.value,
            }

        return expert

    # ------------------------------------------------------------------
    # 2. Session Management
    # ------------------------------------------------------------------

    def book_session(self, session_request: dict) -> dict:
        """Book a consulting session.

        Parameters
        ----------
        session_request : dict
            Keys: ``company_name`` (str), ``expert_id`` (str),
            ``topic`` (str), ``scheduled_at`` (str — ISO 8601, optional).

        Returns
        -------
        dict
            Session confirmation with session ID, agenda stub, and status.

        Raises
        ------
        AIConsultingBotTierError
            If the tier's session cap has been reached.
        """
        self._check_request_limit()
        self._check_session_cap()
        self._request_count += 1

        company = session_request.get("company_name", "Unknown Company")
        expert_id = session_request.get("expert_id", str(uuid.uuid4()))
        topic = session_request.get("topic", "AI Transition Strategy")
        scheduled_at = session_request.get(
            "scheduled_at", datetime.now(timezone.utc).isoformat()
        )

        session = {
            "session_id": str(uuid.uuid4()),
            "company_name": company,
            "expert_id": expert_id,
            "topic": topic,
            "scheduled_at": scheduled_at,
            "status": "confirmed",
            "agenda": [
                "Current-state review",
                f"Discussion: {topic}",
                "Action items & next steps",
            ],
            "tier": self.tier.value,
        }

        # PRO/ENTERPRISE include transcript stub
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            session["transcript_url"] = (
                f"https://docs.dreamcobots.ai/sessions/{session['session_id']}"
            )

        self._sessions.append(session)
        return session

    # ------------------------------------------------------------------
    # 3. Roadmap Generation
    # ------------------------------------------------------------------

    def generate_roadmap(self, company: dict) -> dict:
        """Generate a phased AI adoption roadmap.

        Parameters
        ----------
        company : dict
            Keys: ``company_name`` (str), ``industry`` (str),
            ``readiness_score`` (int 0-100), ``objectives`` (list[str] —
            optional).

        Returns
        -------
        dict
            Roadmap with phases, timelines, and milestones.

        Raises
        ------
        AIConsultingBotTierError
            If roadmap generation is not available on the current tier.
        """
        if self.tier == Tier.FREE:
            raise AIConsultingBotTierError(
                "Roadmap generation is not available on the Free tier. "
                "Please upgrade to PRO to access this feature."
            )

        self._check_request_limit()
        self._request_count += 1

        name = company.get("company_name", "Unknown Company")
        industry = company.get("industry", "general")
        score = int(company.get("readiness_score", 50))
        objectives = company.get("objectives", ["automate workflows", "reduce costs"])

        # Estimate phase durations based on readiness score
        duration_multiplier = max(1, (100 - score) // 20)

        phases = []
        base_weeks = [2, 4, 8, 12, 8]
        for i, (phase, weeks) in enumerate(zip(ROADMAP_PHASES, base_weeks)):
            adjusted = weeks * duration_multiplier // 2 or weeks
            phases.append({
                "phase_number": i + 1,
                "phase_name": phase.replace("_", " ").title(),
                "estimated_weeks": adjusted,
                "milestones": [
                    f"Complete {phase.replace('_', ' ')} review",
                    f"Deliver {phase.replace('_', ' ')} report",
                ],
            })

        roadmap = {
            "roadmap_id": str(uuid.uuid4()),
            "company_name": name,
            "industry": industry,
            "readiness_score": score,
            "objectives": objectives,
            "total_phases": len(phases),
            "phases": phases,
            "estimated_total_weeks": sum(p["estimated_weeks"] for p in phases),
            "tier": self.tier.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # ENTERPRISE adds executive briefing flag
        if self.tier == Tier.ENTERPRISE:
            roadmap["executive_briefing"] = True
            roadmap["change_management_playbook"] = True

        self._roadmaps.append(roadmap)
        return roadmap

    # ------------------------------------------------------------------
    # Stats / introspection
    # ------------------------------------------------------------------

    def get_stats(self) -> dict:
        """Return a summary of activity for this session."""
        cap = SESSION_CAPS[self.tier.value]
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "sessions_booked": len(self._sessions),
            "sessions_remaining": (
                "unlimited" if cap is None else str(max(cap - len(self._sessions), 0))
            ),
            "roadmaps_generated": len(self._roadmaps),
            "buddy_integration": True,
        }

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        command = payload.get("command", "")
        if command == "match_expert":
            return self.match_expert(payload.get("client", {}))
        if command == "book_session":
            return self.book_session(payload.get("session_request", {}))
        if command == "generate_roadmap":
            return self.generate_roadmap(payload.get("company", {}))
        if command == "stats":
            return self.get_stats()
        return {"error": f"Unknown command '{command}'."}
