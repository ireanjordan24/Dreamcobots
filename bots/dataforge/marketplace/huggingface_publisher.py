"""
bots/dataforge/marketplace/huggingface_publisher.py

HuggingFacePublisher – simulates publishing datasets to HuggingFace Hub.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class HuggingFacePublisher:
    """
    Simulates publishing DataForge datasets to the HuggingFace Hub.

    No real network calls are made; all publish actions are recorded in
    an internal ledger for reporting.
    """

    def __init__(
        self,
        token: str = "SIMULATED_HF_TOKEN",
        organization: str = "dreamcobots",
    ) -> None:
        """
        Initialise the publisher.

        Args:
            token: HuggingFace Hub access token (simulated).
            organization: HuggingFace organization / username namespace.
        """
        self.token = token
        self.organization = organization
        self._published: list[dict[str, Any]] = []
        logger.info(
            "HuggingFacePublisher initialised (org='%s')", organization
        )

    def publish(
        self,
        dataset_name: str,
        data: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
        private: bool = False,
    ) -> dict[str, Any]:
        """
        Simulate uploading a dataset to HuggingFace Hub.

        Args:
            dataset_name: Repository name for the dataset.
            data: List of dataset sample dicts.
            metadata: Optional dataset card metadata.
            private: If ``True``, the dataset is marked private (simulated).

        Returns:
            A dict describing the simulated publication result.
        """
        metadata = metadata or {}
        repo_id = f"{self.organization}/{dataset_name}"
        commit_hash = uuid.uuid4().hex[:8]
        result: dict[str, Any] = {
            "repo_id": repo_id,
            "url": f"https://huggingface.co/datasets/{repo_id}",
            "commit": commit_hash,
            "num_samples": len(data),
            "private": private,
            "license": metadata.get("license", "cc-by-4.0"),
            "tags": metadata.get("tags", []),
            "published_at": datetime.now(timezone.utc).isoformat(),
            "status": "success",
        }
        self._published.append(result)
        logger.info(
            "[HuggingFace] Published '%s' (%d samples) – %s",
            repo_id,
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
            "publisher": "HuggingFacePublisher",
            "organization": self.organization,
            "total_publishes": len(self._published),
            "total_samples_published": sum(
                p.get("num_samples", 0) for p in self._published
            ),
        }
