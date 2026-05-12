"""
RetrainingOptimizer — next-generation retraining optimization for DreamCo bots.

Monitors model performance and triggers optimized retraining cycles when
interconnected algorithms detect accuracy degradation beyond configurable
thresholds.

This module is part of the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_DRIFT_THRESHOLD: float = 0.05   # 5 % accuracy drop triggers retraining
DEFAULT_BASELINE_ACCURACY: float = 0.90  # 90 % assumed baseline when unset


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

@dataclass
class PerformanceSnapshot:
    """A recorded accuracy measurement for a bot."""

    snapshot_id: str
    bot_id: str
    accuracy: float
    baseline_accuracy: float
    drift: float            # baseline_accuracy - accuracy (positive = degradation)
    retraining_triggered: bool
    recorded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "bot_id": self.bot_id,
            "accuracy": self.accuracy,
            "baseline_accuracy": self.baseline_accuracy,
            "drift": round(self.drift, 6),
            "retraining_triggered": self.retraining_triggered,
            "recorded_at": self.recorded_at,
        }


@dataclass
class RetrainingJob:
    """Represents a retraining job queued or completed for a bot."""

    job_id: str
    bot_id: str
    trigger_drift: float
    method: str         # e.g. "transfer_learning", "fine_tuning", "full_retrain"
    status: str = "queued"    # queued | running | completed | failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "bot_id": self.bot_id,
            "trigger_drift": round(self.trigger_drift, 6),
            "method": self.method,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


# ---------------------------------------------------------------------------
# Retraining method selection
# ---------------------------------------------------------------------------

def _select_retraining_method(drift: float) -> str:
    """
    Choose the most efficient retraining strategy based on degradation severity.

    - drift < 0.05  → transfer_learning   (lightweight, fastest)
    - drift < 0.15  → fine_tuning          (moderate cost)
    - drift ≥ 0.15  → full_retrain         (comprehensive, costliest)
    """
    if drift < 0.05:
        return "transfer_learning"
    if drift < 0.15:
        return "fine_tuning"
    return "full_retrain"


# ---------------------------------------------------------------------------
# RetrainingOptimizer
# ---------------------------------------------------------------------------

class RetrainingOptimizer:
    """
    Monitors bot model performance and triggers optimized retraining cycles.

    Parameters
    ----------
    drift_threshold : float
        Accuracy drop (absolute) that triggers a retraining job.
        Default: 0.05 (5 %).
    """

    def __init__(self, drift_threshold: float = DEFAULT_DRIFT_THRESHOLD) -> None:
        if not (0.0 < drift_threshold <= 1.0):
            raise ValueError(
                f"drift_threshold must be in (0, 1]. Got: {drift_threshold}"
            )
        self.drift_threshold = drift_threshold
        self._baselines: dict[str, float] = {}
        self._snapshots: list[PerformanceSnapshot] = []
        self._jobs: list[RetrainingJob] = []

    # ------------------------------------------------------------------
    # Baseline management
    # ------------------------------------------------------------------

    def set_baseline(self, bot_id: str, accuracy: float) -> None:
        """Set the baseline (reference) accuracy for a bot."""
        if not (0.0 <= accuracy <= 1.0):
            raise ValueError(f"Accuracy must be in [0, 1]. Got: {accuracy}")
        self._baselines[bot_id] = accuracy

    def get_baseline(self, bot_id: str) -> float:
        """Return the current baseline accuracy for a bot."""
        return self._baselines.get(bot_id, DEFAULT_BASELINE_ACCURACY)

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def evaluate(self, bot_id: str, current_accuracy: float) -> dict:
        """
        Evaluate whether *bot_id* requires retraining.

        Records a performance snapshot and, if drift exceeds the threshold,
        queues a retraining job with an optimized method.

        Parameters
        ----------
        bot_id : str
            Identifier of the bot to evaluate.
        current_accuracy : float
            Latest measured accuracy (0.0–1.0).

        Returns
        -------
        dict
            ``requires_retraining`` (bool), ``drift`` (float),
            ``reason`` (str), ``recommended_method`` (str), and optionally
            ``job_id`` (str) if a job was queued.
        """
        if not (0.0 <= current_accuracy <= 1.0):
            raise ValueError(f"current_accuracy must be in [0, 1]. Got: {current_accuracy}")

        baseline = self.get_baseline(bot_id)
        drift = baseline - current_accuracy

        requires_retraining = drift >= self.drift_threshold
        method = _select_retraining_method(drift) if requires_retraining else "none"

        snapshot = PerformanceSnapshot(
            snapshot_id=f"snap-{uuid.uuid4().hex[:8]}",
            bot_id=bot_id,
            accuracy=current_accuracy,
            baseline_accuracy=baseline,
            drift=drift,
            retraining_triggered=requires_retraining,
        )
        self._snapshots.append(snapshot)

        result: dict = {
            "requires_retraining": requires_retraining,
            "drift": round(drift, 6),
            "current_accuracy": current_accuracy,
            "baseline_accuracy": baseline,
            "threshold": self.drift_threshold,
            "reason": (
                f"Accuracy dropped {drift:.2%} from baseline {baseline:.2%} "
                f"(threshold: {self.drift_threshold:.2%})."
                if requires_retraining
                else f"Accuracy within acceptable range (drift {drift:.2%} < threshold {self.drift_threshold:.2%})."
            ),
            "recommended_method": method,
        }

        if requires_retraining:
            job = self._queue_job(bot_id, drift, method)
            result["job_id"] = job.job_id

        return result

    # ------------------------------------------------------------------
    # Job management
    # ------------------------------------------------------------------

    def _queue_job(self, bot_id: str, drift: float, method: str) -> RetrainingJob:
        """Queue a retraining job."""
        job = RetrainingJob(
            job_id=f"rtjob-{uuid.uuid4().hex[:8]}",
            bot_id=bot_id,
            trigger_drift=drift,
            method=method,
        )
        self._jobs.append(job)
        return job

    def complete_job(self, job_id: str) -> None:
        """Mark a retraining job as completed and update the baseline."""
        for job in self._jobs:
            if job.job_id == job_id:
                job.status = "completed"
                job.completed_at = datetime.now(timezone.utc).isoformat()
                # Restore baseline — assume retraining recovers to original baseline
                if job.bot_id in self._baselines:
                    pass  # baseline remains unchanged; new measurements will validate
                return
        raise KeyError(f"Retraining job '{job_id}' not found.")

    def list_jobs(self, bot_id: Optional[str] = None, status: Optional[str] = None) -> list[dict]:
        """Return retraining jobs with optional filters."""
        jobs = self._jobs
        if bot_id is not None:
            jobs = [j for j in jobs if j.bot_id == bot_id]
        if status is not None:
            jobs = [j for j in jobs if j.status == status]
        return [j.to_dict() for j in jobs]

    def list_snapshots(self, bot_id: Optional[str] = None) -> list[dict]:
        """Return performance snapshots, optionally filtered by bot."""
        snapshots = self._snapshots
        if bot_id is not None:
            snapshots = [s for s in snapshots if s.bot_id == bot_id]
        return [s.to_dict() for s in snapshots]

    # ------------------------------------------------------------------
    # Status summary
    # ------------------------------------------------------------------

    def status(self) -> dict:
        """Return a summary of all monitored bots and retraining activity."""
        queued = sum(1 for j in self._jobs if j.status == "queued")
        completed = sum(1 for j in self._jobs if j.status == "completed")
        monitored_bots = len({s.bot_id for s in self._snapshots})
        return {
            "drift_threshold": self.drift_threshold,
            "monitored_bots": monitored_bots,
            "total_snapshots": len(self._snapshots),
            "total_jobs": len(self._jobs),
            "queued_jobs": queued,
            "completed_jobs": completed,
        }
