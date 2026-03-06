"""
bots/dataforge/marketplace/aws_publisher.py

AWSPublisher – simulates publishing datasets to AWS Data Exchange / S3.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class AWSPublisher:
    """
    Simulates publishing DataForge datasets to AWS S3 and Data Exchange.

    No real AWS credentials are used or required.
    """

    def __init__(
        self,
        access_key: str = "SIMULATED_AWS_ACCESS_KEY",
        secret_key: str = "SIMULATED_AWS_SECRET_KEY",
        region: str = "us-east-1",
        default_bucket: str = "dreamcobots-datasets",
    ) -> None:
        """
        Initialise the publisher.

        Args:
            access_key: AWS access key ID (simulated).
            secret_key: AWS secret access key (simulated).
            region: Target AWS region.
            default_bucket: Default S3 bucket name.
        """
        self.region = region
        self.default_bucket = default_bucket
        self._published: list[dict[str, Any]] = []
        logger.info(
            "AWSPublisher initialised (region='%s', bucket='%s')",
            region,
            default_bucket,
        )

    def publish(
        self,
        dataset_name: str,
        data: list[dict[str, Any]],
        bucket: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Simulate uploading a dataset to S3.

        Args:
            dataset_name: Logical name / prefix for the dataset objects.
            data: List of dataset sample dicts.
            bucket: Target S3 bucket (defaults to :attr:`default_bucket`).
            metadata: Optional metadata to attach as S3 object tags.

        Returns:
            A dict describing the simulated upload result.
        """
        bucket = bucket or self.default_bucket
        metadata = metadata or {}
        object_key = f"datasets/{dataset_name}/{uuid.uuid4().hex[:8]}.jsonl"
        etag = uuid.uuid4().hex

        result: dict[str, Any] = {
            "bucket": bucket,
            "key": object_key,
            "s3_uri": f"s3://{bucket}/{object_key}",
            "https_url": f"https://{bucket}.s3.{self.region}.amazonaws.com/{object_key}",
            "etag": etag,
            "region": self.region,
            "num_samples": len(data),
            "size_bytes_simulated": len(data) * 512,
            "metadata_tags": metadata,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "status": "success",
        }
        self._published.append(result)
        logger.info(
            "[AWS] Published '%s' (%d samples) to s3://%s/%s",
            dataset_name,
            len(data),
            bucket,
            object_key,
        )
        return result

    def get_publish_history(self) -> list[dict[str, Any]]:
        """Return all past publication records."""
        return list(self._published)

    def get_stats(self) -> dict[str, Any]:
        """Return summary publishing statistics."""
        return {
            "publisher": "AWSPublisher",
            "region": self.region,
            "default_bucket": self.default_bucket,
            "total_publishes": len(self._published),
            "total_samples_published": sum(
                p.get("num_samples", 0) for p in self._published
            ),
        }
