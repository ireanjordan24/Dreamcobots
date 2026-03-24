"""
Dreamcobots Stripe Webhook Handler

Processes incoming Stripe webhook events and dispatches them to registered
listeners.  Supports all standard Stripe event types relevant to the
Dreamcobots bots (payments, subscriptions, invoices, etc.).

Webhook events are verified using the ``StripeClient.verify_webhook_signature``
method before dispatching, ensuring only genuine Stripe payloads are processed.

Usage::

    from bots.stripe_integration import StripeWebhookHandler, WebhookEvent

    handler = StripeWebhookHandler()

    @handler.on("payment_intent.succeeded")
    def handle_payment(event):
        print("Payment received:", event.data)

    # In your HTTP endpoint:
    handler.dispatch(raw_body, stripe_signature_header)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from bots.stripe_integration.stripe_client import StripeClient
from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class WebhookEvent:
    """Represents a parsed Stripe webhook event."""

    event_type: str
    event_id: str
    data: dict
    api_version: str = ""
    created: int = 0
    livemode: bool = False
    raw: dict = field(default_factory=dict)


class StripeWebhookHandler:
    """
    Dispatches Stripe webhook events to registered listeners.

    Parameters
    ----------
    client : StripeClient | None
        Optional shared StripeClient.  A new one is created if not provided.
    verify_signatures : bool
        Whether to verify Stripe-Signature headers.  Set to False in tests.
    """

    # Standard Stripe event types relevant to Dreamcobots bots
    SUPPORTED_EVENTS: frozenset = frozenset(
        {
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
            "checkout.session.completed",
            "checkout.session.expired",
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "customer.subscription.trial_will_end",
            "invoice.payment_succeeded",
            "invoice.payment_failed",
            "invoice.upcoming",
            "charge.succeeded",
            "charge.failed",
            "charge.refunded",
        }
    )

    def __init__(
        self,
        client: Optional[StripeClient] = None,
        verify_signatures: bool = True,
    ) -> None:
        self._client = client or StripeClient()
        self._verify = verify_signatures
        self._listeners: dict[str, list[Callable]] = {}

    # ------------------------------------------------------------------
    # Listener registration
    # ------------------------------------------------------------------

    def on(self, event_type: str) -> Callable:
        """
        Decorator to register a listener for a specific event type.

        Usage::

            @handler.on("payment_intent.succeeded")
            def handle(event: WebhookEvent) -> None:
                ...
        """

        def decorator(fn: Callable) -> Callable:
            self._listeners.setdefault(event_type, []).append(fn)
            return fn

        return decorator

    def register(self, event_type: str, callback: Callable) -> None:
        """Register *callback* for *event_type* without using the decorator."""
        self._listeners.setdefault(event_type, []).append(callback)

    # ------------------------------------------------------------------
    # Dispatching
    # ------------------------------------------------------------------

    def dispatch(
        self,
        payload: bytes,
        sig_header: str = "",
        *,
        skip_verify: bool = False,
    ) -> Optional[WebhookEvent]:
        """
        Verify and dispatch a raw Stripe webhook payload.

        Parameters
        ----------
        payload : bytes
            Raw HTTP request body.
        sig_header : str
            ``Stripe-Signature`` header.
        skip_verify : bool
            Skip signature verification (useful in tests).

        Returns
        -------
        WebhookEvent | None
            The parsed event, or None if verification failed.
        """
        if self._verify and not skip_verify:
            if not self._client.verify_webhook_signature(payload, sig_header):
                return None

        try:
            raw = json.loads(payload)
        except (json.JSONDecodeError, ValueError):
            return None

        event = WebhookEvent(
            event_type=raw.get("type", "unknown"),
            event_id=raw.get("id", ""),
            data=raw.get("data", {}).get("object", {}),
            api_version=raw.get("api_version", ""),
            created=raw.get("created", 0),
            livemode=raw.get("livemode", False),
            raw=raw,
        )

        for callback in self._listeners.get(event.event_type, []):
            callback(event)

        return event

    # ------------------------------------------------------------------
    # Convenience: build a test event payload
    # ------------------------------------------------------------------

    @staticmethod
    def build_event_payload(
        event_type: str,
        object_data: dict,
        event_id: Optional[str] = None,
        livemode: bool = False,
    ) -> bytes:
        """
        Build a JSON bytes payload suitable for testing ``dispatch``.

        Parameters
        ----------
        event_type : str
            Stripe event type string.
        object_data : dict
            The ``data.object`` contents.
        event_id : str | None
            Optional event ID.  Auto-generated when None.
        livemode : bool
            Whether to mark the event as live mode.

        Returns
        -------
        bytes
            UTF-8 encoded JSON payload.
        """
        import time
        import uuid

        payload = {
            "id": event_id or f"evt_{uuid.uuid4().hex[:20]}",
            "type": event_type,
            "api_version": "2023-10-16",
            "created": int(time.time()),
            "livemode": livemode,
            "data": {"object": object_data},
        }
        return json.dumps(payload).encode("utf-8")
