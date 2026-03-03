"""
bots/dataforge/apis/connectors/salesforce_connector.py

SalesforceConnector – simulated connector for the Salesforce REST API.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from bots.dataforge.apis.connectors.base_connector import BaseAPIConnector


class SalesforceConnector(BaseAPIConnector):
    """Simulated connector for the Salesforce REST API (SOQL queries, objects)."""

    def __init__(
        self,
        api_key: str = "SIMULATED_SF_ACCESS_TOKEN",
        instance_url: str = "https://dreamcobots.my.salesforce.com",
        api_version: str = "v59.0",
    ) -> None:
        """
        Initialise the Salesforce connector.

        Args:
            api_key: Salesforce OAuth access token (simulated).
            instance_url: Salesforce instance URL.
            api_version: Salesforce API version.
        """
        super().__init__(
            name="salesforce",
            api_key=api_key,
            base_url=f"{instance_url}/services/data/{api_version}",
        )
        self.instance_url = instance_url
        self.api_version = api_version
        self._rate_limit = 100

    def connect(self) -> bool:
        """Simulate connecting to the Salesforce API."""
        self._connected = True
        self.logger.info(
            "Salesforce connector connected (simulated, instance=%s)", self.instance_url
        )
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from the Salesforce API."""
        self._connected = False
        self.logger.info("Salesforce connector disconnected")

    def call(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, Any]:
        """
        Simulate a Salesforce REST API call.

        Args:
            method: HTTP method.
            endpoint: API endpoint path.
            data: Optional request payload.

        Returns:
            A simulated response dict.
        """
        data = data or {}
        self._record_call()
        self.logger.debug("Salesforce call: %s %s", method, endpoint)

        if endpoint == "/health":
            return {"status": "ok"}

        if "query" in endpoint:
            soql = data.get("q", "SELECT Id FROM Account")
            return {
                "totalSize": 3,
                "done": True,
                "records": [
                    {
                        "Id": f"001{uuid.uuid4().hex[:15].upper()}",
                        "attributes": {"type": "Account"},
                        "Name": f"Simulated Account {i}",
                    }
                    for i in range(1, 4)
                ],
                "query": soql,
            }

        if "sobjects" in endpoint and method.upper() == "POST":
            object_type = endpoint.split("/sobjects/")[-1].split("/")[0]
            return {
                "id": f"001{uuid.uuid4().hex[:15].upper()}",
                "success": True,
                "errors": [],
                "object_type": object_type,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

        return {"status": "ok", "endpoint": endpoint, "simulated": True}
