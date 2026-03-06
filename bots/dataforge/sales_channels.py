"""
bots/dataforge/sales_channels.py

SalesChannelManager – coordinates publishing of DataForge datasets to
HuggingFace, Kaggle, AWS Data Exchange, and direct API endpoints.

All publish methods *simulate* the real operations so that no actual
credentials or network access are required.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class SalesChannelManager:
    """
    Manages dataset publishing across multiple distribution channels.

    Each ``publish_*`` method simulates the corresponding platform's
    upload workflow and records a sales event for reporting.
    """

    def __init__(self) -> None:
        """Initialise the manager with an empty sales ledger."""
        self._sales_events: list[dict[str, Any]] = []
        logger.info("SalesChannelManager initialised")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _record_sale(
        self,
        channel: str,
        dataset_name: str,
        metadata: dict[str, Any],
        success: bool,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        """Append a sales event and return it."""
        event: dict[str, Any] = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "channel": channel,
            "dataset_name": dataset_name,
            "metadata": metadata,
            "success": success,
            "details": details,
        }
        self._sales_events.append(event)
        return event

    # ------------------------------------------------------------------
    # HuggingFace
    # ------------------------------------------------------------------

    def publish_to_huggingface(
        self,
        dataset_name: str,
        dataset_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Simulate publishing a dataset to HuggingFace Hub.

        Args:
            dataset_name: The name/repo-id for the dataset on HuggingFace.
            dataset_path: Local filesystem path to the packaged dataset.
            metadata: Optional additional metadata to attach to the dataset card.

        Returns:
            A dict describing the (simulated) publish result.
        """
        metadata = metadata or {}
        logger.info(
            "[HuggingFace] Simulating publish of '%s' from '%s'",
            dataset_name,
            dataset_path,
        )
        repo_url = f"https://huggingface.co/datasets/dreamcobots/{dataset_name}"
        details = {
            "repo_url": repo_url,
            "commit_hash": uuid.uuid4().hex[:8],
            "files_uploaded": [dataset_path],
            "visibility": metadata.get("visibility", "public"),
            "license": metadata.get("license", "cc-by-4.0"),
        }
        event = self._record_sale("huggingface", dataset_name, metadata, True, details)
        logger.info("[HuggingFace] Published successfully – %s", repo_url)
        return event

    # ------------------------------------------------------------------
    # Kaggle
    # ------------------------------------------------------------------

    def publish_to_kaggle(
        self,
        dataset_name: str,
        dataset_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Simulate publishing a dataset to Kaggle Datasets.

        Args:
            dataset_name: Slug for the Kaggle dataset.
            dataset_path: Local filesystem path to the packaged dataset.
            metadata: Optional additional metadata (description, tags, etc.).

        Returns:
            A dict describing the (simulated) publish result.
        """
        metadata = metadata or {}
        logger.info(
            "[Kaggle] Simulating publish of '%s' from '%s'",
            dataset_name,
            dataset_path,
        )
        dataset_url = f"https://www.kaggle.com/datasets/dreamcobots/{dataset_name}"
        details = {
            "dataset_url": dataset_url,
            "version": 1,
            "files_uploaded": [dataset_path],
            "subtitle": metadata.get("subtitle", f"{dataset_name} dataset"),
            "is_private": metadata.get("is_private", False),
        }
        event = self._record_sale("kaggle", dataset_name, metadata, True, details)
        logger.info("[Kaggle] Published successfully – %s", dataset_url)
        return event

    # ------------------------------------------------------------------
    # AWS Data Exchange
    # ------------------------------------------------------------------

    def publish_to_aws(
        self,
        dataset_name: str,
        dataset_path: str,
        bucket: str = "dreamcobots-datasets",
    ) -> dict[str, Any]:
        """
        Simulate uploading a dataset to an AWS S3 bucket (Data Exchange).

        Args:
            dataset_name: Logical name for the dataset.
            dataset_path: Local filesystem path to the packaged dataset.
            bucket: Target S3 bucket name.

        Returns:
            A dict describing the (simulated) publish result.
        """
        logger.info(
            "[AWS] Simulating upload of '%s' to s3://%s", dataset_name, bucket
        )
        s3_key = f"datasets/{dataset_name}/{uuid.uuid4().hex[:8]}.zip"
        details = {
            "s3_uri": f"s3://{bucket}/{s3_key}",
            "bucket": bucket,
            "key": s3_key,
            "etag": uuid.uuid4().hex,
            "region": "us-east-1",
        }
        event = self._record_sale(
            "aws", dataset_name, {"bucket": bucket}, True, details
        )
        logger.info("[AWS] Upload simulated – s3://%s/%s", bucket, s3_key)
        return event

    # ------------------------------------------------------------------
    # Direct API
    # ------------------------------------------------------------------

    def publish_via_direct_api(
        self,
        dataset_name: str,
        endpoint: str,
        api_key: str = "SIMULATED_KEY",
    ) -> dict[str, Any]:
        """
        Simulate publishing a dataset via a direct REST API endpoint.

        Args:
            dataset_name: Name of the dataset being published.
            endpoint: Target API URL.
            api_key: API key used for authentication (simulated).

        Returns:
            A dict describing the (simulated) publish result.
        """
        logger.info(
            "[DirectAPI] Simulating publish of '%s' to %s", dataset_name, endpoint
        )
        details = {
            "endpoint": endpoint,
            "http_status": 201,
            "response_body": {
                "dataset_id": str(uuid.uuid4()),
                "dataset_name": dataset_name,
                "status": "accepted",
            },
            "api_key_hint": api_key[:4] + "****",
        }
        metadata: dict[str, Any] = {"endpoint": endpoint}
        event = self._record_sale("direct_api", dataset_name, metadata, True, details)
        logger.info(
            "[DirectAPI] Publish simulated – dataset_id=%s",
            details["response_body"]["dataset_id"],
        )
        return event

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_sales_stats(self) -> dict[str, Any]:
        """
        Return aggregate sales statistics across all channels.

        Returns:
            A dict with total events, per-channel counts, and success rate.
        """
        total = len(self._sales_events)
        by_channel: dict[str, int] = {}
        successes = 0
        for ev in self._sales_events:
            ch = ev["channel"]
            by_channel[ch] = by_channel.get(ch, 0) + 1
            if ev["success"]:
                successes += 1

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_publish_events": total,
            "successful_events": successes,
            "failed_events": total - successes,
            "success_rate": (successes / total) if total else 1.0,
            "events_by_channel": by_channel,
        }
