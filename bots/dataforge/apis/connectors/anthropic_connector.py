"""
bots/dataforge/apis/connectors/anthropic_connector.py

AnthropicConnector – simulated connector for the Anthropic Claude API.
"""

import uuid
from typing import Any

from bots.dataforge.apis.connectors.base_connector import BaseAPIConnector


class AnthropicConnector(BaseAPIConnector):
    """Simulated connector for the Anthropic Claude API."""

    def __init__(
        self,
        api_key: str = "SIMULATED_ANTHROPIC_KEY",
        model: str = "claude-3-5-sonnet-20241022",
    ) -> None:
        """
        Initialise the Anthropic connector.

        Args:
            api_key: Anthropic API key (simulated).
            model: Default Claude model to use.
        """
        super().__init__(
            name="anthropic",
            api_key=api_key,
            base_url="https://api.anthropic.com/v1",
        )
        self.model = model
        self._rate_limit = 300

    def connect(self) -> bool:
        """Simulate connecting to the Anthropic API."""
        self._connected = True
        self.logger.info("Anthropic connector connected (simulated)")
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from the Anthropic API."""
        self._connected = False
        self.logger.info("Anthropic connector disconnected")

    def call(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, Any]:
        """
        Simulate an Anthropic API call.

        Args:
            method: HTTP method.
            endpoint: API endpoint path.
            data: Optional request payload.

        Returns:
            A simulated response dict.
        """
        data = data or {}
        self._record_call()
        self.logger.debug("Anthropic call: %s %s", method, endpoint)

        if endpoint == "/health":
            return {"status": "ok"}

        if "messages" in endpoint:
            user_msg = data.get("messages", [{}])[-1].get("content", "")
            return {
                "id": f"msg_{uuid.uuid4().hex[:20]}",
                "type": "message",
                "role": "assistant",
                "model": self.model,
                "content": [
                    {
                        "type": "text",
                        "text": f"[SIMULATED Claude] Responding to: {user_msg[:50]}",
                    }
                ],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 15, "output_tokens": 25},
            }

        return {"status": "ok", "endpoint": endpoint, "simulated": True}
