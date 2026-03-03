"""
bots/dataforge/apis/connectors/stripe_connector.py

StripeConnector – simulated connector for the Stripe Payments API.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from bots.dataforge.apis.connectors.base_connector import BaseAPIConnector


class StripeConnector(BaseAPIConnector):
    """Simulated connector for the Stripe REST API."""

    def __init__(
        self,
        api_key: str = "SIMULATED_STRIPE_SK",
    ) -> None:
        """
        Initialise the Stripe connector.

        Args:
            api_key: Stripe secret key (simulated).
        """
        super().__init__(
            name="stripe",
            api_key=api_key,
            base_url="https://api.stripe.com/v1",
        )
        self._rate_limit = 100

    def connect(self) -> bool:
        """Simulate connecting to the Stripe API."""
        self._connected = True
        self.logger.info("Stripe connector connected (simulated)")
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from the Stripe API."""
        self._connected = False
        self.logger.info("Stripe connector disconnected")

    def call(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, Any]:
        """
        Simulate a Stripe API call.

        Args:
            method: HTTP method.
            endpoint: API endpoint path.
            data: Optional request payload.

        Returns:
            A simulated response dict.
        """
        data = data or {}
        self._record_call()
        self.logger.debug("Stripe call: %s %s", method, endpoint)

        if endpoint == "/health":
            return {"status": "ok"}

        if "payment_intents" in endpoint and method.upper() == "POST":
            amount = data.get("amount", 1000)
            currency = data.get("currency", "usd")
            return {
                "id": f"pi_{uuid.uuid4().hex[:24]}",
                "object": "payment_intent",
                "amount": amount,
                "currency": currency,
                "status": "succeeded",
                "created": int(datetime.now(timezone.utc).timestamp()),
                "client_secret": f"pi_{uuid.uuid4().hex[:24]}_secret_{uuid.uuid4().hex[:8]}",
            }

        if "transfers" in endpoint and method.upper() == "POST":
            return {
                "id": f"tr_{uuid.uuid4().hex[:24]}",
                "object": "transfer",
                "amount": data.get("amount", 0),
                "currency": data.get("currency", "usd"),
                "destination": data.get("destination", "acct_simulated"),
                "status": "paid",
            }

        return {"status": "ok", "endpoint": endpoint, "simulated": True}
