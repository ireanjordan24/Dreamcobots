"""
bots/dataforge/apis/connectors/aws_connector.py

AWSConnector – simulated connector for AWS services (S3, Data Exchange).
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from bots.dataforge.apis.connectors.base_connector import BaseAPIConnector


class AWSConnector(BaseAPIConnector):
    """Simulated connector for AWS S3 and Data Exchange services."""

    def __init__(
        self,
        api_key: str = "SIMULATED_AWS_ACCESS_KEY",
        region: str = "us-east-1",
        default_bucket: str = "dreamcobots-datasets",
    ) -> None:
        """
        Initialise the AWS connector.

        Args:
            api_key: AWS access key ID (simulated).
            region: AWS region.
            default_bucket: Default S3 bucket name.
        """
        super().__init__(
            name="aws",
            api_key=api_key,
            base_url=f"https://s3.{region}.amazonaws.com",
        )
        self.region = region
        self.default_bucket = default_bucket
        self._rate_limit = 1000

    def connect(self) -> bool:
        """Simulate connecting to AWS."""
        self._connected = True
        self.logger.info("AWS connector connected (simulated, region=%s)", self.region)
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from AWS."""
        self._connected = False
        self.logger.info("AWS connector disconnected")

    def call(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, Any]:
        """
        Simulate an AWS API call.

        Args:
            method: HTTP method.
            endpoint: API endpoint (e.g. ``"/bucket/key"``).
            data: Optional request payload.

        Returns:
            A simulated response dict.
        """
        data = data or {}
        self._record_call()
        self.logger.debug("AWS call: %s %s", method, endpoint)

        if endpoint == "/health":
            return {"status": "ok"}

        if method.upper() == "PUT":
            key = data.get("key", f"objects/{uuid.uuid4().hex}")
            bucket = data.get("bucket", self.default_bucket)
            return {
                "ETag": f'"{uuid.uuid4().hex}"',
                "Location": f"https://{bucket}.s3.{self.region}.amazonaws.com/{key}",
                "Bucket": bucket,
                "Key": key,
            }

        if method.upper() == "GET":
            return {
                "Contents": [
                    {
                        "Key": f"datasets/file_{i}.json",
                        "Size": i * 1024,
                        "LastModified": datetime.now(timezone.utc).isoformat(),
                    }
                    for i in range(1, 4)
                ]
            }

        return {"status": "ok", "endpoint": endpoint, "simulated": True}
