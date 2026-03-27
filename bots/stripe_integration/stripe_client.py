"""
Dreamcobots Stripe Client

Wraps all Stripe API interactions behind a single class that reads
credentials exclusively from environment variables — no keys are ever
hard-coded.  When the ``stripe`` SDK is not installed (e.g. during
unit tests) the client falls back to deterministic mock responses so
the rest of the codebase can be exercised without a live Stripe account.

Required environment variables
-------------------------------
STRIPE_SECRET_KEY      Live or test secret key (sk_live_... / sk_test_...).
STRIPE_PUBLISHABLE_KEY Live or test publishable key (pk_live_... / pk_test_...).
STRIPE_WEBHOOK_SECRET  Webhook endpoint signing secret (whsec_...).

All variables default to safe placeholder values when absent so tests run
offline without any network calls.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
import uuid
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401

# ---------------------------------------------------------------------------
# Credentials — loaded from environment, never hard-coded
# ---------------------------------------------------------------------------

_SECRET_KEY: str = os.environ.get(
    "STRIPE_SECRET_KEY",
    "sk_test_placeholder_dreamcobots_secret_key",
)
_PUBLISHABLE_KEY: str = os.environ.get(
    "STRIPE_PUBLISHABLE_KEY",
    "pk_test_placeholder_dreamcobots_publishable_key",
)
_WEBHOOK_SECRET: str = os.environ.get(
    "STRIPE_WEBHOOK_SECRET",
    "whsec_placeholder_dreamcobots_webhook_secret",
)

# ---------------------------------------------------------------------------
# Optional Stripe SDK import — graceful degradation
# ---------------------------------------------------------------------------

try:
    import stripe as _stripe_sdk  # type: ignore

    _stripe_sdk.api_key = _SECRET_KEY
    _SDK_AVAILABLE = True
except ImportError:
    _stripe_sdk = None  # type: ignore
    _SDK_AVAILABLE = False


class StripeClientError(Exception):
    """Raised when a Stripe API call fails."""


class StripeClient:
    """
    Unified Stripe client for all Dreamcobots bots.

    When the Stripe SDK is available and a real key is configured, API calls
    are forwarded to Stripe.  Otherwise, deterministic mock responses are
    returned so the bots remain fully testable offline.

    Parameters
    ----------
    secret_key : str | None
        Override the secret key.  Defaults to the ``STRIPE_SECRET_KEY``
        environment variable.
    """

    def __init__(self, secret_key: Optional[str] = None) -> None:
        self._secret_key = secret_key or _SECRET_KEY
        self._publishable_key = _PUBLISHABLE_KEY
        self._webhook_secret = _WEBHOOK_SECRET
        self._mock_mode = not _SDK_AVAILABLE or self._secret_key.startswith(
            "sk_test_placeholder"
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _new_id(prefix: str = "pi") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:20]}"

    @staticmethod
    def _now_ts() -> int:
        return int(time.time())

    # ------------------------------------------------------------------
    # Checkout / Payment Intents
    # ------------------------------------------------------------------

    def create_checkout_session(
        self,
        amount_cents: int,
        currency: str,
        product_name: str,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a Stripe Checkout Session for a one-time payment.

        Parameters
        ----------
        amount_cents : int
            Amount in the smallest currency unit (e.g. cents for USD).
        currency : str
            ISO 4217 currency code (e.g. ``"usd"``).
        product_name : str
            Human-readable product / service name shown on the checkout page.
        success_url : str
            URL Stripe redirects to after a successful payment.
        cancel_url : str
            URL Stripe redirects to when the customer cancels.
        customer_email : str | None
            Pre-fill the customer's email address.
        metadata : dict | None
            Arbitrary key/value pairs attached to the session.

        Returns
        -------
        dict
            ``id``, ``url``, ``status``, ``amount_total``, ``currency``.
        """
        if not self._mock_mode and _stripe_sdk is not None:
            try:
                params: dict = {
                    "payment_method_types": ["card"],
                    "line_items": [
                        {
                            "price_data": {
                                "currency": currency.lower(),
                                "product_data": {"name": product_name},
                                "unit_amount": amount_cents,
                            },
                            "quantity": 1,
                        }
                    ],
                    "mode": "payment",
                    "success_url": success_url,
                    "cancel_url": cancel_url,
                }
                if customer_email:
                    params["customer_email"] = customer_email
                if metadata:
                    params["metadata"] = metadata
                session = _stripe_sdk.checkout.Session.create(**params)
                return {
                    "id": session.id,
                    "url": session.url,
                    "status": session.status,
                    "amount_total": session.amount_total,
                    "currency": session.currency,
                }
            except Exception as exc:
                raise StripeClientError(str(exc)) from exc

        # Mock response
        session_id = self._new_id("cs")
        return {
            "id": session_id,
            "url": f"https://checkout.stripe.com/pay/{session_id}",
            "status": "open",
            "amount_total": amount_cents,
            "currency": currency.lower(),
            "product_name": product_name,
            "customer_email": customer_email,
            "metadata": metadata or {},
        }

    def create_payment_intent(
        self,
        amount_cents: int,
        currency: str,
        customer_id: Optional[str] = None,
        payment_method: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a Stripe PaymentIntent for server-side payment confirmation.

        Returns
        -------
        dict
            ``id``, ``status``, ``amount``, ``currency``, ``client_secret``.
        """
        if not self._mock_mode and _stripe_sdk is not None:
            try:
                params: dict = {"amount": amount_cents, "currency": currency.lower()}
                if customer_id:
                    params["customer"] = customer_id
                if payment_method:
                    params["payment_method"] = payment_method
                if metadata:
                    params["metadata"] = metadata
                intent = _stripe_sdk.PaymentIntent.create(**params)
                return {
                    "id": intent.id,
                    "status": intent.status,
                    "amount": intent.amount,
                    "currency": intent.currency,
                    "client_secret": intent.client_secret,
                }
            except Exception as exc:
                raise StripeClientError(str(exc)) from exc

        pi_id = self._new_id("pi")
        return {
            "id": pi_id,
            "status": "requires_payment_method",
            "amount": amount_cents,
            "currency": currency.lower(),
            "client_secret": f"{pi_id}_secret_{uuid.uuid4().hex[:8]}",
            "customer_id": customer_id,
            "metadata": metadata or {},
        }

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 0,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a Stripe Subscription.

        Parameters
        ----------
        customer_id : str
            Stripe customer ID (``cus_...``).
        price_id : str
            Stripe Price ID for the recurring plan (``price_...``).
        trial_days : int
            Number of free trial days before billing starts.
        metadata : dict | None
            Arbitrary key/value metadata attached to the subscription.

        Returns
        -------
        dict
            ``id``, ``status``, ``current_period_end``, ``customer``.
        """
        if not self._mock_mode and _stripe_sdk is not None:
            try:
                params: dict = {
                    "customer": customer_id,
                    "items": [{"price": price_id}],
                }
                if trial_days:
                    params["trial_period_days"] = trial_days
                if metadata:
                    params["metadata"] = metadata
                sub = _stripe_sdk.Subscription.create(**params)
                return {
                    "id": sub.id,
                    "status": sub.status,
                    "current_period_end": sub.current_period_end,
                    "customer": sub.customer,
                }
            except Exception as exc:
                raise StripeClientError(str(exc)) from exc

        sub_id = self._new_id("sub")
        return {
            "id": sub_id,
            "status": "trialing" if trial_days else "active",
            "current_period_end": self._now_ts() + 30 * 24 * 3600,
            "customer": customer_id,
            "price_id": price_id,
            "trial_days": trial_days,
            "metadata": metadata or {},
        }

    def cancel_subscription(self, subscription_id: str) -> dict:
        """
        Cancel a Stripe Subscription immediately.

        Returns
        -------
        dict
            ``id``, ``status``.
        """
        if not self._mock_mode and _stripe_sdk is not None:
            try:
                sub = _stripe_sdk.Subscription.delete(subscription_id)
                return {"id": sub.id, "status": sub.status}
            except Exception as exc:
                raise StripeClientError(str(exc)) from exc

        return {"id": subscription_id, "status": "canceled"}

    def retrieve_subscription(self, subscription_id: str) -> dict:
        """
        Retrieve the current status of a subscription.

        Returns
        -------
        dict
            ``id``, ``status``, ``current_period_end``.
        """
        if not self._mock_mode and _stripe_sdk is not None:
            try:
                sub = _stripe_sdk.Subscription.retrieve(subscription_id)
                return {
                    "id": sub.id,
                    "status": sub.status,
                    "current_period_end": sub.current_period_end,
                }
            except Exception as exc:
                raise StripeClientError(str(exc)) from exc

        return {
            "id": subscription_id,
            "status": "active",
            "current_period_end": self._now_ts() + 30 * 24 * 3600,
        }

    # ------------------------------------------------------------------
    # Customers
    # ------------------------------------------------------------------

    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a Stripe Customer record.

        Returns
        -------
        dict
            ``id``, ``email``, ``name``.
        """
        if not self._mock_mode and _stripe_sdk is not None:
            try:
                params: dict = {"email": email}
                if name:
                    params["name"] = name
                if metadata:
                    params["metadata"] = metadata
                customer = _stripe_sdk.Customer.create(**params)
                return {"id": customer.id, "email": customer.email, "name": customer.name}
            except Exception as exc:
                raise StripeClientError(str(exc)) from exc

        cust_id = self._new_id("cus")
        return {"id": cust_id, "email": email, "name": name, "metadata": metadata or {}}

    # ------------------------------------------------------------------
    # Payment Links
    # ------------------------------------------------------------------

    def create_payment_link(
        self,
        amount_cents: int,
        currency: str,
        product_name: str,
        quantity: int = 1,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a shareable Stripe Payment Link.

        Returns
        -------
        dict
            ``id``, ``url``, ``active``.
        """
        if not self._mock_mode and _stripe_sdk is not None:
            try:
                price = _stripe_sdk.Price.create(
                    unit_amount=amount_cents,
                    currency=currency.lower(),
                    product_data={"name": product_name},
                )
                link = _stripe_sdk.PaymentLink.create(
                    line_items=[{"price": price.id, "quantity": quantity}]
                )
                return {"id": link.id, "url": link.url, "active": link.active}
            except Exception as exc:
                raise StripeClientError(str(exc)) from exc

        link_id = self._new_id("plink")
        return {
            "id": link_id,
            "url": f"https://buy.stripe.com/{link_id}",
            "active": True,
            "amount_cents": amount_cents,
            "currency": currency.lower(),
            "product_name": product_name,
            "metadata": metadata or {},
        }

    # ------------------------------------------------------------------
    # Refunds
    # ------------------------------------------------------------------

    def refund_payment(
        self,
        payment_intent_id: str,
        amount_cents: Optional[int] = None,
        reason: str = "requested_by_customer",
    ) -> dict:
        """
        Refund a payment (full or partial).

        Returns
        -------
        dict
            ``id``, ``status``, ``amount``.
        """
        if not self._mock_mode and _stripe_sdk is not None:
            try:
                params: dict = {"payment_intent": payment_intent_id, "reason": reason}
                if amount_cents is not None:
                    params["amount"] = amount_cents
                refund = _stripe_sdk.Refund.create(**params)
                return {"id": refund.id, "status": refund.status, "amount": refund.amount}
            except Exception as exc:
                raise StripeClientError(str(exc)) from exc

        return {
            "id": self._new_id("re"),
            "status": "succeeded",
            "amount": amount_cents,
            "payment_intent": payment_intent_id,
            "reason": reason,
        }

    # ------------------------------------------------------------------
    # Payouts / Balance
    # ------------------------------------------------------------------

    def get_balance(self) -> dict:
        """
        Retrieve the current Stripe account balance.

        Returns
        -------
        dict
            ``available`` and ``pending`` lists of ``{amount, currency}`` dicts.
        """
        if not self._mock_mode and _stripe_sdk is not None:
            try:
                balance = _stripe_sdk.Balance.retrieve()
                return {
                    "available": [
                        {"amount": b.amount, "currency": b.currency}
                        for b in balance.available
                    ],
                    "pending": [
                        {"amount": b.amount, "currency": b.currency}
                        for b in balance.pending
                    ],
                }
            except Exception as exc:
                raise StripeClientError(str(exc)) from exc

        return {
            "available": [{"amount": 0, "currency": "usd"}],
            "pending": [{"amount": 0, "currency": "usd"}],
        }

    def list_payouts(self, limit: int = 10) -> list:
        """
        List recent Stripe payouts.

        Returns
        -------
        list[dict]
            Each dict contains ``id``, ``amount``, ``currency``, ``status``.
        """
        if not self._mock_mode and _stripe_sdk is not None:
            try:
                payouts = _stripe_sdk.Payout.list(limit=limit)
                return [
                    {
                        "id": p.id,
                        "amount": p.amount,
                        "currency": p.currency,
                        "status": p.status,
                        "arrival_date": p.arrival_date,
                    }
                    for p in payouts.data
                ]
            except Exception as exc:
                raise StripeClientError(str(exc)) from exc

        return []

    # ------------------------------------------------------------------
    # Webhook signature verification
    # ------------------------------------------------------------------

    def verify_webhook_signature(self, payload: bytes, sig_header: str) -> bool:
        """
        Verify that a webhook payload was signed by Stripe.

        Parameters
        ----------
        payload : bytes
            Raw request body.
        sig_header : str
            ``Stripe-Signature`` header value.

        Returns
        -------
        bool
            ``True`` if signature is valid, ``False`` otherwise.
        """
        if not self._mock_mode and _stripe_sdk is not None:
            try:
                _stripe_sdk.Webhook.construct_event(
                    payload, sig_header, self._webhook_secret
                )
                return True
            except Exception:
                return False

        # Mock mode: accept any payload
        return True

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def publishable_key(self) -> str:
        """Return the publishable key for use in frontend integrations."""
        return self._publishable_key

    @property
    def mock_mode(self) -> bool:
        """Return True when running without a live Stripe connection."""
        return self._mock_mode
