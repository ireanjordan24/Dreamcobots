"""
Pillar 1 — AI Advocates Program.

Builds and manages peer-to-peer AI influence networks within the DreamCo
ecosystem.  Passionate contributors can be enrolled as Advocates who help
drive AI adoption across their teams and communities.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

@dataclass
class Advocate:
    """Represents a registered AI Advocate in the peer network."""

    advocate_id: str
    name: str
    email: str
    expertise: list[str]
    influence_score: float = 0.0
    peers_influenced: int = 0
    enrolled_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "advocate_id": self.advocate_id,
            "name": self.name,
            "email": self.email,
            "expertise": list(self.expertise),
            "influence_score": self.influence_score,
            "peers_influenced": self.peers_influenced,
            "enrolled_at": self.enrolled_at,
        }


@dataclass
class InfluenceEvent:
    """Records a peer influence interaction."""

    event_id: str
    advocate_id: str
    target_user: str
    channel: str  # e.g. "slack", "github_pr", "workshop", "mentorship"
    outcome: str  # "adopted", "interested", "neutral", "declined"
    recorded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "advocate_id": self.advocate_id,
            "target_user": self.target_user,
            "channel": self.channel,
            "outcome": self.outcome,
            "recorded_at": self.recorded_at,
        }


# ---------------------------------------------------------------------------
# Advocates Program
# ---------------------------------------------------------------------------

VALID_CHANNELS = {"slack", "github_pr", "workshop", "mentorship", "discord", "email", "demo"}
VALID_OUTCOMES = {"adopted", "interested", "neutral", "declined"}

OUTCOME_SCORE_MAP: dict[str, float] = {
    "adopted": 2.0,
    "interested": 1.0,
    "neutral": 0.2,
    "declined": 0.0,
}


class AdvocatesProgram:
    """
    Manages peer-to-peer AI influence networks.

    Advocates are enrolled contributors who actively promote AI adoption.
    Influence events record every peer interaction and automatically update
    each advocate's influence score.
    """

    def __init__(self) -> None:
        self._advocates: dict[str, Advocate] = {}
        self._events: list[InfluenceEvent] = []

    # ------------------------------------------------------------------
    # Advocate management
    # ------------------------------------------------------------------

    def enroll_advocate(
        self,
        name: str,
        email: str,
        expertise: Optional[list[str]] = None,
    ) -> Advocate:
        """Enrol a new advocate in the peer network."""
        advocate_id = f"adv-{uuid.uuid4().hex[:8]}"
        advocate = Advocate(
            advocate_id=advocate_id,
            name=name,
            email=email,
            expertise=expertise or [],
        )
        self._advocates[advocate_id] = advocate
        return advocate

    def get_advocate(self, advocate_id: str) -> Advocate:
        """Return an advocate by ID."""
        if advocate_id not in self._advocates:
            raise KeyError(f"Advocate '{advocate_id}' not found.")
        return self._advocates[advocate_id]

    def list_advocates(self) -> list[dict]:
        """Return all advocates sorted by influence score descending."""
        return [
            a.to_dict()
            for a in sorted(
                self._advocates.values(),
                key=lambda a: a.influence_score,
                reverse=True,
            )
        ]

    # ------------------------------------------------------------------
    # Influence tracking
    # ------------------------------------------------------------------

    def record_influence(
        self,
        advocate_id: str,
        target_user: str,
        channel: str,
        outcome: str,
    ) -> InfluenceEvent:
        """
        Record a peer-to-peer influence interaction.

        Parameters
        ----------
        advocate_id : str
            ID of the advocate performing the outreach.
        target_user : str
            Username or identifier of the person being influenced.
        channel : str
            Communication channel used.
        outcome : str
            Result of the interaction.
        """
        if advocate_id not in self._advocates:
            raise KeyError(f"Advocate '{advocate_id}' not found.")
        if channel not in VALID_CHANNELS:
            raise ValueError(f"Invalid channel '{channel}'. Valid: {sorted(VALID_CHANNELS)}")
        if outcome not in VALID_OUTCOMES:
            raise ValueError(f"Invalid outcome '{outcome}'. Valid: {sorted(VALID_OUTCOMES)}")

        event = InfluenceEvent(
            event_id=f"evt-{uuid.uuid4().hex[:8]}",
            advocate_id=advocate_id,
            target_user=target_user,
            channel=channel,
            outcome=outcome,
        )
        self._events.append(event)

        # Update advocate stats
        advocate = self._advocates[advocate_id]
        advocate.peers_influenced += 1
        advocate.influence_score = round(
            advocate.influence_score + OUTCOME_SCORE_MAP[outcome], 2
        )

        return event

    def get_influence_events(
        self, advocate_id: Optional[str] = None
    ) -> list[dict]:
        """Return influence events, optionally filtered by advocate."""
        events = self._events
        if advocate_id is not None:
            events = [e for e in events if e.advocate_id == advocate_id]
        return [e.to_dict() for e in events]

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def network_summary(self) -> dict:
        """Return a high-level summary of the influence network."""
        total_adopted = sum(
            1 for e in self._events if e.outcome == "adopted"
        )
        total_interested = sum(
            1 for e in self._events if e.outcome == "interested"
        )
        return {
            "total_advocates": len(self._advocates),
            "total_influence_events": len(self._events),
            "total_adopted": total_adopted,
            "total_interested": total_interested,
            "adoption_rate": round(
                total_adopted / max(len(self._events), 1), 4
            ),
        }
