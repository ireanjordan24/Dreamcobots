"""
bots/dataforge/marketplace/kaggle_publisher.py

KagglePublisher – simulates publishing datasets to Kaggle Datasets.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class KagglePublisher:
    """
    Simulates publishing DataForge datasets to Kaggle Datasets.

    All publish actions are logged internally; no real Kaggle API calls
    are made.
    """

    def __init__(
        self,
        api_key: str = "SIMULATED_KAGGLE_KEY",
        username: str = "dreamcobots",
    ) -> None:
        """
        Initialise the publisher.

        Args:
            api_key: Kaggle API key (simulated).
            username: Kaggle username / organization.
        """
        self.api_key = api_key
        self.username = username
        self._published: list[dict[str, Any]] = []
        logger.info("KagglePublisher initialised (username='%s')", username)

    def publish(
        self,
        dataset_name: str,
        data: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
        is_private: bool = False,
    ) -> dict[str, Any]:
        """
        Simulate uploading a dataset to Kaggle Datasets.

        Args:
            dataset_name: Dataset slug / title.
            data: List of dataset sample dicts.
            metadata: Optional metadata (description, tags, etc.).
            is_private: If ``True``, the dataset is marked private.

        Returns:
            A dict describing the simulated publication result.
        """
        metadata = metadata or {}
        slug = dataset_name.lower().replace(" ", "-")
        dataset_id = uuid.uuid4().int % 10_000_000
        result: dict[str, Any] = {
            "ref": f"{self.username}/{slug}",
            "url": f"https://www.kaggle.com/datasets/{self.username}/{slug}",
            "dataset_id": dataset_id,
            "num_samples": len(data),
            "is_private": is_private,
            "subtitle": metadata.get("subtitle", f"{dataset_name} dataset"),
            "description": metadata.get("description", ""),
            "tags": metadata.get("tags", []),
            "published_at": datetime.now(timezone.utc).isoformat(),
            "status": "success",
        }
        self._published.append(result)
        logger.info(
            "[Kaggle] Published '%s' (%d samples) – %s",
            result["ref"],
            len(data),
            result["url"],
        )
        return result

    def get_publish_history(self) -> list[dict[str, Any]]:
        """Return all past publication records."""
        return list(self._published)

    def get_stats(self) -> dict[str, Any]:
        """Return summary publishing statistics."""
        return {
            "publisher": "KagglePublisher",
            "username": self.username,
            "total_publishes": len(self._published),
            "total_samples_published": sum(
                p.get("num_samples", 0) for p in self._published
            ),
        }
