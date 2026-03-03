"""
bots/dataforge/apis/connectors/openai_connector.py

OpenAIConnector – simulated connector for the OpenAI API.
"""

import uuid
from typing import Any

from bots.dataforge.apis.connectors.base_connector import BaseAPIConnector


class OpenAIConnector(BaseAPIConnector):
    """
    Simulated connector for the OpenAI REST API.

    Supports chat completions, embeddings, and model listings without
    making real network calls.
    """

    def __init__(
        self,
        api_key: str = "SIMULATED_OPENAI_KEY",
        model: str = "gpt-4o",
    ) -> None:
        """
        Initialise the OpenAI connector.

        Args:
            api_key: OpenAI API key (simulated).
            model: Default model to use for completions.
        """
        super().__init__(
            name="openai",
            api_key=api_key,
            base_url="https://api.openai.com/v1",
        )
        self.model = model
        self._rate_limit = 500

    def connect(self) -> bool:
        """Simulate connecting to the OpenAI API."""
        self._connected = True
        self.logger.info("OpenAI connector connected (simulated)")
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting from the OpenAI API."""
        self._connected = False
        self.logger.info("OpenAI connector disconnected")

    def call(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, Any]:
        """
        Simulate an OpenAI API call.

        Args:
            method: HTTP method.
            endpoint: API endpoint path.
            data: Optional request payload.

        Returns:
            A simulated response dict.
        """
        data = data or {}
        self._record_call()
        self.logger.debug("OpenAI call: %s %s", method, endpoint)

        if endpoint == "/health":
            return {"status": "ok"}

        if "chat/completions" in endpoint:
            prompt = data.get("messages", [{}])[-1].get("content", "")
            return {
                "id": f"chatcmpl-{uuid.uuid4().hex[:10]}",
                "object": "chat.completion",
                "model": self.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": f"[SIMULATED] Response to: {prompt[:50]}",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            }

        if "embeddings" in endpoint:
            return {
                "object": "list",
                "data": [{"object": "embedding", "embedding": [0.1] * 1536, "index": 0}],
                "model": "text-embedding-3-small",
                "usage": {"prompt_tokens": 8, "total_tokens": 8},
            }

        return {"status": "ok", "endpoint": endpoint, "simulated": True}
