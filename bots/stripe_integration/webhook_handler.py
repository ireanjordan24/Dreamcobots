"""
Stripe Webhook Handler for Dreamcobots.

Validates inbound Stripe webhook payloads using the webhook signing secret
and dispatches events to registered handlers.

Configure via environment variable:
  STRIPE_WEBHOOK_SECRET — whsec_... (from your Stripe webhook endpoint)

Usage
-----
    from bots.stripe_integration import WebhookHandler

    handler = WebhookHandler()

    # Register custom callbacks
    @handler.on("payment_intent.succeeded")
    def handle_payment(event):
        print("Payment succeeded:", event["data"]["object"]["id"])

    # In your server route (raw bytes + signature header):
    result = handler.handle_event(request.body, request.headers["stripe-signature"])
"""

import os
import json
import hashlib
import hmac
import datetime
from typing import Callable, Dict, List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class WebhookVerificationError(Exception):
    """Raised when a webhook signature cannot be verified."""


class WebhookHandler:
    """
    Stripe webhook event dispatcher for Dreamcobots bots.

    Parameters
    ----------
    webhook_secret : str, optional
        Stripe webhook signing secret (``whsec_...``).  Defaults to the
        ``STRIPE_WEBHOOK_SECRET`` environment variable.
    """

    # Stripe-supported event types relevant to bots
    SUPPORTED_EVENTS: List[str] = [
        "payment_intent.succeeded",
        "payment_intent.payment_failed",
        "payment_intent.created",
        "payment_intent.canceled",
        "checkout.session.completed",
        "checkout.session.expired",
        "customer.created",
        "customer.updated",
        "customer.deleted",
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
        "invoice.paid",
        "invoice.payment_failed",
        "invoice.finalized",
        "charge.succeeded",
        "charge.failed",
        "charge.refunded",
        "payout.created",
        "payout.paid",
        "payout.failed",
        "product.created",
        "price.created",
        "payment_link.created",
        "radar.early_fraud_warning.created",
    ]

    def __init__(self, webhook_secret: Optional[str] = None) -> None:
        self.webhook_secret = webhook_secret or os.environ.get(
            "STRIPE_WEBHOOK_SECRET", ""
        )
        self._handlers: Dict[str, List[Callable]] = {}
        self._event_log: List[dict] = []

    # ------------------------------------------------------------------
    # Handler registration
    # ------------------------------------------------------------------

    def on(self, event_type: str) -> Callable:
        """
        Decorator / function to register a callback for a Stripe event type.

        Parameters
        ----------
        event_type : str
            Stripe event type string, e.g. ``"payment_intent.succeeded"``.

        Returns
        -------
        Callable
            Decorator that registers the wrapped function.
        """
        def decorator(func: Callable) -> Callable:
            self._handlers.setdefault(event_type, []).append(func)
            return func
        return decorator

    def register_handler(self, event_type: str, func: Callable) -> None:
        """Programmatically register a handler without using the decorator."""
        self._handlers.setdefault(event_type, []).append(func)

    # ------------------------------------------------------------------
    # Event processing
    # ------------------------------------------------------------------

    def handle_event(
        self,
        payload: bytes,
        sig_header: str,
        skip_verification: bool = False,
    ) -> dict:
        """
        Validate a Stripe webhook payload and dispatch to handlers.

        Parameters
        ----------
        payload : bytes
            Raw request body as received from Stripe.
        sig_header : str
            Value of the ``Stripe-Signature`` HTTP header.
        skip_verification : bool
            When ``True``, skip signature verification (for testing only).

        Returns
        -------
        dict
            Processing result with ``event_type``, ``event_id``, ``dispatched``.

        Raises
        ------
        WebhookVerificationError
            If signature verification fails and ``skip_verification`` is False.
        """
        # Attempt live Stripe verification first
        stripe_lib = self._load_stripe()
        if stripe_lib and self.webhook_secret and not skip_verification:
            try:
                event = stripe_lib.Webhook.construct_event(
                    payload, sig_header, self.webhook_secret
                )
                event_dict = dict(event)
            except stripe_lib.error.SignatureVerificationError as exc:
                raise WebhookVerificationError(str(exc)) from exc
        else:
            if not skip_verification and self.webhook_secret:
                self._verify_signature(payload, sig_header)
            event_dict = json.loads(payload) if isinstance(payload, bytes) else payload

        event_type = event_dict.get("type", "")
        event_id = event_dict.get("id", "")

        # Log the event
        self._event_log.append({
            "event_id": event_id,
            "event_type": event_type,
            "received_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })

        # Dispatch to registered handlers
        dispatched = self._dispatch(event_type, event_dict)

        return {
            "event_id": event_id,
            "event_type": event_type,
            "dispatched": dispatched,
            "received": True,
        }

    def _dispatch(self, event_type: str, event_dict: dict) -> int:
        """Call all registered handlers for event_type; return call count."""
        handlers = self._handlers.get(event_type, [])
        for func in handlers:
            func(event_dict)
        return len(handlers)

    def _verify_signature(self, payload: bytes, sig_header: str) -> None:
        """Manually verify a Stripe webhook signature (fallback for no stripe lib)."""
        if not self.webhook_secret:
            return

        # Parse the Stripe-Signature header
        parts: dict = {}
        for item in sig_header.split(","):
            if "=" in item:
                k, v = item.split("=", 1)
                parts[k.strip()] = v.strip()

        timestamp = parts.get("t", "")
        v1_sigs = parts.get("v1", "").split()

        if not timestamp or not v1_sigs:
            raise WebhookVerificationError("Invalid Stripe-Signature header format.")

        signed_payload = f"{timestamp}.".encode() + payload
        expected = hmac.new(
            self.webhook_secret.encode(),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        if not any(hmac.compare_digest(expected, sig) for sig in v1_sigs):
            raise WebhookVerificationError("Webhook signature verification failed.")

    @staticmethod
    def _load_stripe():
        """Try to import the stripe library without raising."""
        try:
            import stripe  # noqa: PLC0415
            return stripe
        except ImportError:
            return None

    # ------------------------------------------------------------------
    # Event log
    # ------------------------------------------------------------------

    def get_event_log(self) -> List[dict]:
        """Return a copy of the processed-event log."""
        return list(self._event_log)

    def clear_event_log(self) -> None:
        """Clear the in-memory event log."""
        self._event_log.clear()
