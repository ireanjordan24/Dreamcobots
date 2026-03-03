"""
bots/dataforge/apis/connectors/sendgrid_connector.py

SendGridConnector – simulated connector for the SendGrid Email API.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from bots.dataforge.apis.connectors.base_connector import BaseAPIConnector


class SendGridConnector(BaseAPIConnector):
    """Simulated connector for the SendGrid v3 Email API."""

    def __init__(
        self,
        api_key: str = "SIMULATED_SENDGRID_KEY",
        from_email: str = "noreply@dreamcobots.ai",
    ) -> None:
        """
        Initialise the SendGrid connector.

        Args:
            api_key: SendGrid API key (simulated).
            from_email: Default sender email address.
        """
        super().__init__(
            name="sendgrid",
            api_key=api_key,
            base_url="https://api.sendgrid.com/v3",
        )
        self.from_email = from_email
        self._rate_limit = 200

    def connect(self) -> bool:
        """Simulate connecting to the SendGrid API."""
        self._connected = True
        self.logger.info("SendGrid connector connected (simulated)")
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from the SendGrid API."""
        self._connected = False
        self.logger.info("SendGrid connector disconnected")

    def call(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, Any]:
        """
        Simulate a SendGrid API call.

        Args:
            method: HTTP method.
            endpoint: API endpoint path.
            data: Optional request payload.

        Returns:
            A simulated response dict.
        """
        data = data or {}
        self._record_call()
        self.logger.debug("SendGrid call: %s %s", method, endpoint)

        if endpoint == "/health":
            return {"status": "ok"}

        if "mail/send" in endpoint and method.upper() == "POST":
            personalizations = data.get("personalizations", [{}])
            to_list = personalizations[0].get("to", [{"email": "unknown@example.com"}])
            return {
                "message_id": f"{uuid.uuid4().hex}@sendgrid.net",
                "to": [r["email"] for r in to_list],
                "subject": data.get("subject", "(no subject)"),
                "status": "queued",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        if "templates" in endpoint and method.upper() == "GET":
            return {
                "templates": [
                    {"id": f"d-{uuid.uuid4().hex[:32]}", "name": f"Template {i}"}
                    for i in range(1, 4)
                ]
            }

        return {"status": "ok", "endpoint": endpoint, "simulated": True}
