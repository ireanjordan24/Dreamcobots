"""
bots/dataforge/apis/connectors/twilio_connector.py

TwilioConnector – simulated connector for the Twilio Communications API.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from bots.dataforge.apis.connectors.base_connector import BaseAPIConnector


class TwilioConnector(BaseAPIConnector):
    """Simulated connector for the Twilio REST API (SMS, Voice, Verify)."""

    def __init__(
        self,
        api_key: str = "SIMULATED_TWILIO_AUTH_TOKEN",
        account_sid: str = "SIMULATED_ACCOUNT_SID",
    ) -> None:
        """
        Initialise the Twilio connector.

        Args:
            api_key: Twilio Auth Token (simulated).
            account_sid: Twilio Account SID (simulated).
        """
        super().__init__(
            name="twilio",
            api_key=api_key,
            base_url="https://api.twilio.com/2010-04-01",
        )
        self.account_sid = account_sid
        self._rate_limit = 100

    def connect(self) -> bool:
        """Simulate connecting to the Twilio API."""
        self._connected = True
        self.logger.info("Twilio connector connected (simulated)")
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from the Twilio API."""
        self._connected = False
        self.logger.info("Twilio connector disconnected")

    def call(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, Any]:
        """
        Simulate a Twilio API call.

        Args:
            method: HTTP method.
            endpoint: API endpoint path.
            data: Optional request payload.

        Returns:
            A simulated response dict.
        """
        data = data or {}
        self._record_call()
        self.logger.debug("Twilio call: %s %s", method, endpoint)

        if endpoint == "/health":
            return {"status": "ok"}

        if "Messages" in endpoint and method.upper() == "POST":
            return {
                "sid": f"SM{uuid.uuid4().hex[:32]}",
                "account_sid": self.account_sid,
                "to": data.get("To", "+10000000000"),
                "from_": data.get("From", "+19999999999"),
                "body": data.get("Body", "[SIMULATED MESSAGE]"),
                "status": "sent",
                "date_created": datetime.now(timezone.utc).isoformat(),
            }

        if "Calls" in endpoint and method.upper() == "POST":
            return {
                "sid": f"CA{uuid.uuid4().hex[:32]}",
                "account_sid": self.account_sid,
                "to": data.get("To", "+10000000000"),
                "from_": data.get("From", "+19999999999"),
                "status": "queued",
                "direction": "outbound-api",
            }

        return {"status": "ok", "endpoint": endpoint, "simulated": True}
