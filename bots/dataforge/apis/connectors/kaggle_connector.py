"""
bots/dataforge/apis/connectors/kaggle_connector.py

KaggleConnector – simulated connector for the Kaggle API.
"""

import uuid
from typing import Any

from bots.dataforge.apis.connectors.base_connector import BaseAPIConnector


class KaggleConnector(BaseAPIConnector):
    """Simulated connector for the Kaggle Public API."""

    def __init__(
        self,
        api_key: str = "SIMULATED_KAGGLE_KEY",
        username: str = "dreamcobots",
    ) -> None:
        """
        Initialise the Kaggle connector.

        Args:
            api_key: Kaggle API key (simulated).
            username: Kaggle username.
        """
        super().__init__(
            name="kaggle",
            api_key=api_key,
            base_url="https://www.kaggle.com/api/v1",
        )
        self.username = username
        self._rate_limit = 60

    def connect(self) -> bool:
        """Simulate connecting to the Kaggle API."""
        self._connected = True
        self.logger.info("Kaggle connector connected (simulated)")
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from the Kaggle API."""
        self._connected = False
        self.logger.info("Kaggle connector disconnected")

    def call(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, Any]:
        """
        Simulate a Kaggle API call.

        Args:
            method: HTTP method.
            endpoint: API endpoint path.
            data: Optional request payload.

        Returns:
            A simulated response dict.
        """
        data = data or {}
        self._record_call()
        self.logger.debug("Kaggle call: %s %s", method, endpoint)

        if endpoint == "/health":
            return {"status": "ok"}

        if "datasets/create" in endpoint:
            title = data.get("title", "unnamed")
            return {
                "ref": f"{self.username}/{title.lower().replace(' ', '-')}",
                "url": f"https://www.kaggle.com/datasets/{self.username}/{title}",
                "datasetId": uuid.uuid4().int % 1_000_000,
                "status": "datasetCreated",
            }

        if "datasets" in endpoint and method.upper() == "GET":
            return {
                "datasets": [
                    {
                        "ref": f"{self.username}/dataset-{i}",
                        "title": f"Dataset {i}",
                        "totalBytes": i * 1024 * 1024,
                        "downloadCount": i * 50,
                    }
                    for i in range(1, 6)
                ]
            }

        return {"status": "ok", "endpoint": endpoint, "simulated": True}
