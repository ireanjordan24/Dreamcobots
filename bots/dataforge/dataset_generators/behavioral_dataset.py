"""
bots/dataforge/dataset_generators/behavioral_dataset.py

BehavioralDatasetGenerator – generates simulated user-behavioral dataset
samples (clicks, navigation paths, time-on-page, preferences, etc.).
"""

import logging
import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

_PAGE_TYPES = [
    "home",
    "product_listing",
    "product_detail",
    "cart",
    "checkout",
    "search_results",
    "account",
    "help",
    "blog",
]
_DEVICES = ["desktop", "mobile", "tablet"]
_OS_LIST = ["Windows", "macOS", "Android", "iOS", "Linux"]
_BROWSERS = ["Chrome", "Firefox", "Safari", "Edge", "Opera"]
_EVENT_TYPES = ["click", "scroll", "hover", "keypress", "form_submit", "page_view"]


class BehavioralDatasetGenerator:
    """
    Generates simulated user-behavioral dataset samples.

    Each sample represents a single user session with a sequence of
    interaction events, navigation history, and derived engagement metrics.
    """

    def __init__(self) -> None:
        """Initialise the generator."""
        self._sample_count = 0
        self._batch_count = 0
        logger.info("BehavioralDatasetGenerator initialised")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_sample(self, user_id: str | None = None) -> dict[str, Any]:
        """
        Generate a single simulated behavioral session sample.

        Args:
            user_id: Optional user identifier.  A UUID is generated if omitted.

        Returns:
            A dict representing one user session with events and metrics.
        """
        uid = user_id or str(uuid.uuid4())
        session_start = datetime.now(timezone.utc) - timedelta(
            seconds=random.randint(60, 3600)
        )
        session_duration = random.randint(10, 1800)  # seconds
        num_events = random.randint(3, 50)

        events: list[dict[str, Any]] = []
        current_time = session_start
        for _ in range(num_events):
            current_time += timedelta(seconds=random.randint(1, 30))
            events.append(
                {
                    "event_id": str(uuid.uuid4()),
                    "event_type": random.choice(_EVENT_TYPES),
                    "page_type": random.choice(_PAGE_TYPES),
                    "timestamp": current_time.isoformat(),
                    "element_id": f"el_{uuid.uuid4().hex[:6]}",
                    "x_pos": random.randint(0, 1920),
                    "y_pos": random.randint(0, 1080),
                    "duration_ms": random.randint(50, 5000),
                }
            )

        nav_path = random.sample(_PAGE_TYPES, k=random.randint(2, min(6, len(_PAGE_TYPES))))

        self._sample_count += 1
        session_id = str(uuid.uuid4())

        sample: dict[str, Any] = {
            "session_id": session_id,
            "user_id": uid,
            "session_start": session_start.isoformat(),
            "session_duration_seconds": session_duration,
            "device_type": random.choice(_DEVICES),
            "operating_system": random.choice(_OS_LIST),
            "browser": random.choice(_BROWSERS),
            "screen_resolution": random.choice(
                ["1920x1080", "1366x768", "390x844", "768x1024"]
            ),
            "num_events": num_events,
            "events": events,
            "navigation_path": nav_path,
            "pages_visited": len(set(ev["page_type"] for ev in events)),
            "click_count": sum(1 for ev in events if ev["event_type"] == "click"),
            "scroll_depth_pct": round(random.uniform(10.0, 100.0), 1),
            "bounce": random.random() < 0.2,
            "converted": random.random() < 0.05,
            "referrer": random.choice(
                ["google", "direct", "facebook", "twitter", "email", "other"]
            ),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.debug(
            "Generated behavioral sample %s for user '%s' (%d events)",
            session_id,
            uid,
            num_events,
        )
        return sample

    def generate_batch(
        self,
        num_samples: int,
        output_dir: str = "/tmp/behavioral_dataset",
    ) -> list[dict[str, Any]]:
        """
        Generate a batch of behavioral samples.

        Args:
            num_samples: Number of samples to generate.
            output_dir: Directory path (created if necessary; no files written).

        Returns:
            A list of sample dicts.
        """
        os.makedirs(output_dir, exist_ok=True)
        batch = [self.generate_sample() for _ in range(num_samples)]
        self._batch_count += 1
        logger.info(
            "Behavioral batch %d complete: %d samples in %s",
            self._batch_count,
            num_samples,
            output_dir,
        )
        return batch

    def validate_sample(self, sample: dict) -> bool:
        """
        Validate a behavioral sample dict.

        Args:
            sample: Sample produced by :meth:`generate_sample`.

        Returns:
            ``True`` if valid, ``False`` otherwise.
        """
        required = {"session_id", "user_id", "events", "num_events"}
        if not required.issubset(sample.keys()):
            logger.warning("Behavioral sample missing required keys")
            return False
        if not isinstance(sample["events"], list):
            logger.warning("Behavioral sample 'events' is not a list")
            return False
        if len(sample["events"]) != sample["num_events"]:
            logger.warning("Behavioral sample event count mismatch")
            return False
        return True

    def get_metadata(self) -> dict[str, Any]:
        """
        Return metadata describing this generator.

        Returns:
            A metadata dict.
        """
        return {
            "generator": "BehavioralDatasetGenerator",
            "version": "1.0.0",
            "page_types": _PAGE_TYPES,
            "event_types": _EVENT_TYPES,
            "devices": _DEVICES,
            "samples_generated": self._sample_count,
            "batches_generated": self._batch_count,
            "description": "Simulated user session events, navigation paths, and engagement metrics",
        }
