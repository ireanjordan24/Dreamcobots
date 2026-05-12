"""
Pillar 4 — Data-driven Metrics.

Deploys analytical systems to monitor the effectiveness of AI adoption:
Monthly Active Users (MAU), user segmentation, adoption cycle times,
and adoption maturity scoring.

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
class AdoptionEvent:
    """Represents a single user interaction / adoption signal."""

    event_id: str
    user_id: str
    bot_id: str
    event_type: str         # "activate" | "use" | "upgrade" | "churn"
    segment: str            # "new_user" | "power_user" | "enterprise" | "advocate"
    cycle_time_days: float  # time from first exposure to first active use
    recorded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "user_id": self.user_id,
            "bot_id": self.bot_id,
            "event_type": self.event_type,
            "segment": self.segment,
            "cycle_time_days": self.cycle_time_days,
            "recorded_at": self.recorded_at,
        }


# ---------------------------------------------------------------------------
# Adoption Maturity Levels
# ---------------------------------------------------------------------------

class AdoptionMaturity:
    """Five-level adoption maturity model (1 = Awareness → 5 = Transformative)."""

    AWARENESS = 1
    EXPLORATION = 2
    ADOPTION = 3
    OPTIMIZATION = 4
    TRANSFORMATIVE = 5

    LABELS = {
        1: "Awareness",
        2: "Exploration",
        3: "Adoption",
        4: "Optimization",
        5: "Transformative",
    }

    @classmethod
    def label(cls, level: int) -> str:
        return cls.LABELS.get(level, "Unknown")

    @classmethod
    def from_mau_ratio(cls, mau: int, total_users: int) -> int:
        """Derive maturity level from MAU / total user ratio."""
        if total_users == 0:
            return cls.AWARENESS
        ratio = mau / total_users
        if ratio < 0.10:
            return cls.AWARENESS
        if ratio < 0.25:
            return cls.EXPLORATION
        if ratio < 0.50:
            return cls.ADOPTION
        if ratio < 0.75:
            return cls.OPTIMIZATION
        return cls.TRANSFORMATIVE


VALID_EVENT_TYPES = {"activate", "use", "upgrade", "churn"}
VALID_SEGMENTS = {"new_user", "power_user", "enterprise", "advocate"}


# ---------------------------------------------------------------------------
# Data-driven Metrics engine
# ---------------------------------------------------------------------------

class DataMetrics:
    """
    Monitors AI adoption effectiveness.

    Tracks MAU, user segmentation, cycle times, and outputs an adoption
    maturity score to gauge organisational AI fluency.
    """

    def __init__(self, advanced_segmentation: bool = False) -> None:
        self._advanced_segmentation = advanced_segmentation
        self._events: list[AdoptionEvent] = []
        self._registered_users: set[str] = set()

    # ------------------------------------------------------------------
    # User registration
    # ------------------------------------------------------------------

    def register_user(self, user_id: str) -> None:
        """Register a user in the tracked population."""
        self._registered_users.add(user_id)

    def total_users(self) -> int:
        """Return the number of registered users."""
        return len(self._registered_users)

    # ------------------------------------------------------------------
    # Event recording
    # ------------------------------------------------------------------

    def record_event(
        self,
        user_id: str,
        bot_id: str,
        event_type: str,
        segment: str,
        cycle_time_days: float = 0.0,
    ) -> AdoptionEvent:
        """
        Record an adoption event.

        Parameters
        ----------
        user_id : str
            Identifier of the user.
        bot_id : str
            Bot the event relates to.
        event_type : str
            Type of adoption signal.
        segment : str
            User segment.
        cycle_time_days : float
            Days from first exposure to first productive use.
        """
        if event_type not in VALID_EVENT_TYPES:
            raise ValueError(
                f"Invalid event_type '{event_type}'. Valid: {sorted(VALID_EVENT_TYPES)}"
            )
        if segment not in VALID_SEGMENTS:
            raise ValueError(
                f"Invalid segment '{segment}'. Valid: {sorted(VALID_SEGMENTS)}"
            )

        event = AdoptionEvent(
            event_id=f"mev-{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            bot_id=bot_id,
            event_type=event_type,
            segment=segment,
            cycle_time_days=max(0.0, cycle_time_days),
        )
        self._events.append(event)
        self._registered_users.add(user_id)
        return event

    # ------------------------------------------------------------------
    # MAU calculation
    # ------------------------------------------------------------------

    def mau(self, year: int, month: int) -> int:
        """
        Return Monthly Active Users for a given year/month.

        A user is considered active if they have ≥1 non-churn event in the
        specified calendar month.
        """
        active_users: set[str] = set()
        for event in self._events:
            ts = datetime.fromisoformat(event.recorded_at.replace("Z", "+00:00"))
            if ts.year == year and ts.month == month and event.event_type != "churn":
                active_users.add(event.user_id)
        return len(active_users)

    def current_mau(self) -> int:
        """Return MAU for the current calendar month."""
        now = datetime.now(timezone.utc)
        return self.mau(now.year, now.month)

    # ------------------------------------------------------------------
    # Segmentation
    # ------------------------------------------------------------------

    def segment_distribution(self) -> dict[str, int]:
        """Return event counts by user segment."""
        dist: dict[str, int] = {s: 0 for s in VALID_SEGMENTS}
        for event in self._events:
            dist[event.segment] = dist.get(event.segment, 0) + 1
        return dist

    def segment_mau(self, year: int, month: int) -> dict[str, int]:
        """
        Return MAU broken down by segment.

        Requires advanced_segmentation (PRO+).
        """
        if not self._advanced_segmentation:
            raise PermissionError(
                "Segmented MAU requires PRO or ENTERPRISE tier."
            )
        result: dict[str, set] = {s: set() for s in VALID_SEGMENTS}
        for event in self._events:
            ts = datetime.fromisoformat(event.recorded_at.replace("Z", "+00:00"))
            if ts.year == year and ts.month == month and event.event_type != "churn":
                result[event.segment].add(event.user_id)
        return {seg: len(users) for seg, users in result.items()}

    # ------------------------------------------------------------------
    # Cycle times
    # ------------------------------------------------------------------

    def average_cycle_time(self, bot_id: Optional[str] = None) -> float:
        """Return average adoption cycle time in days."""
        events = [
            e for e in self._events
            if e.event_type == "activate" and (bot_id is None or e.bot_id == bot_id)
        ]
        if not events:
            return 0.0
        return round(sum(e.cycle_time_days for e in events) / len(events), 2)

    # ------------------------------------------------------------------
    # Adoption maturity
    # ------------------------------------------------------------------

    def adoption_maturity(self) -> dict:
        """Compute and return the adoption maturity level."""
        mau_val = self.current_mau()
        total = self.total_users()
        level = AdoptionMaturity.from_mau_ratio(mau_val, total)
        return {
            "maturity_level": level,
            "maturity_label": AdoptionMaturity.label(level),
            "current_mau": mau_val,
            "total_users": total,
            "mau_ratio": round(mau_val / max(total, 1), 4),
        }

    # ------------------------------------------------------------------
    # Dashboard snapshot
    # ------------------------------------------------------------------

    def dashboard(self) -> dict:
        """Return a full metrics dashboard snapshot."""
        maturity = self.adoption_maturity()
        return {
            "total_events": len(self._events),
            "total_users": self.total_users(),
            "current_mau": maturity["current_mau"],
            "mau_ratio": maturity["mau_ratio"],
            "maturity_level": maturity["maturity_level"],
            "maturity_label": maturity["maturity_label"],
            "avg_cycle_time_days": self.average_cycle_time(),
            "segment_distribution": self.segment_distribution(),
        }
