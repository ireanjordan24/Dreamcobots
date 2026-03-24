"""
Tests for bots/stripe_integration/

Covers StripeClient (mock mode) and StripeWebhookHandler.
"""

import json
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.stripe_integration.stripe_client import StripeClient, StripeClientError
from bots.stripe_integration.webhook_handler import (
    StripeWebhookHandler,
    WebhookEvent,
)


# ===========================================================================
# StripeClient — constructor
# ===========================================================================

class TestStripeClientInit:
    def test_default_client_is_mock(self):
        client = StripeClient()
        assert client.mock_mode is True

    def test_publishable_key_present(self):
        client = StripeClient()
        assert client.publishable_key

    def test_placeholder_key_detected(self):
        client = StripeClient(secret_key="sk_test_placeholder_dreamcobots_secret_key")
        assert client.mock_mode is True


# ===========================================================================
# StripeClient — checkout sessions
# ===========================================================================

class TestCreateCheckoutSession:
    def setup_method(self):
        self.client = StripeClient()

    def test_returns_dict(self):
        result = self.client.create_checkout_session(
            amount_cents=2500,
            currency="usd",
            product_name="Test Product",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )
        assert isinstance(result, dict)

    def test_has_id(self):
        result = self.client.create_checkout_session(
            amount_cents=2500, currency="usd", product_name="X",
            success_url="https://s.co", cancel_url="https://c.co",
        )
        assert result["id"].startswith("cs_")

    def test_has_url(self):
        result = self.client.create_checkout_session(
            amount_cents=2500, currency="usd", product_name="X",
            success_url="https://s.co", cancel_url="https://c.co",
        )
        assert "checkout.stripe.com" in result["url"]

    def test_amount_preserved(self):
        result = self.client.create_checkout_session(
            amount_cents=4999, currency="usd", product_name="X",
            success_url="https://s.co", cancel_url="https://c.co",
        )
        assert result["amount_total"] == 4999

    def test_currency_lowercase(self):
        result = self.client.create_checkout_session(
            amount_cents=100, currency="USD", product_name="X",
            success_url="https://s.co", cancel_url="https://c.co",
        )
        assert result["currency"] == "usd"

    def test_customer_email_stored(self):
        result = self.client.create_checkout_session(
            amount_cents=100, currency="usd", product_name="X",
            success_url="https://s.co", cancel_url="https://c.co",
            customer_email="test@example.com",
        )
        assert result["customer_email"] == "test@example.com"

    def test_metadata_stored(self):
        result = self.client.create_checkout_session(
            amount_cents=100, currency="usd", product_name="X",
            success_url="https://s.co", cancel_url="https://c.co",
            metadata={"bot": "test_bot"},
        )
        assert result["metadata"]["bot"] == "test_bot"

    def test_status_open(self):
        result = self.client.create_checkout_session(
            amount_cents=100, currency="usd", product_name="X",
            success_url="https://s.co", cancel_url="https://c.co",
        )
        assert result["status"] == "open"


# ===========================================================================
# StripeClient — payment intents
# ===========================================================================

class TestCreatePaymentIntent:
    def setup_method(self):
        self.client = StripeClient()

    def test_returns_dict(self):
        result = self.client.create_payment_intent(1000, "usd")
        assert isinstance(result, dict)

    def test_has_id(self):
        result = self.client.create_payment_intent(1000, "usd")
        assert result["id"].startswith("pi_")

    def test_has_client_secret(self):
        result = self.client.create_payment_intent(1000, "usd")
        assert "client_secret" in result
        assert result["client_secret"]

    def test_amount_preserved(self):
        result = self.client.create_payment_intent(5000, "usd")
        assert result["amount"] == 5000

    def test_currency_lowercase(self):
        result = self.client.create_payment_intent(100, "EUR")
        assert result["currency"] == "eur"

    def test_with_customer_id(self):
        result = self.client.create_payment_intent(
            100, "usd", customer_id="cus_abc123"
        )
        assert result["customer_id"] == "cus_abc123"


# ===========================================================================
# StripeClient — subscriptions
# ===========================================================================

class TestSubscriptions:
    def setup_method(self):
        self.client = StripeClient()

    def test_create_subscription_returns_dict(self):
        result = self.client.create_subscription("cus_123", "price_abc")
        assert isinstance(result, dict)

    def test_subscription_has_id(self):
        result = self.client.create_subscription("cus_123", "price_abc")
        assert result["id"].startswith("sub_")

    def test_subscription_active_no_trial(self):
        result = self.client.create_subscription("cus_123", "price_abc")
        assert result["status"] == "active"

    def test_subscription_trialing_with_trial(self):
        result = self.client.create_subscription("cus_123", "price_abc", trial_days=7)
        assert result["status"] == "trialing"

    def test_subscription_has_period_end(self):
        result = self.client.create_subscription("cus_123", "price_abc")
        assert result["current_period_end"] > 0

    def test_cancel_subscription(self):
        result = self.client.cancel_subscription("sub_abc123")
        assert result["status"] == "canceled"
        assert result["id"] == "sub_abc123"

    def test_retrieve_subscription(self):
        result = self.client.retrieve_subscription("sub_abc123")
        assert result["id"] == "sub_abc123"
        assert result["status"] == "active"


# ===========================================================================
# StripeClient — customers
# ===========================================================================

class TestCustomers:
    def setup_method(self):
        self.client = StripeClient()

    def test_create_customer_returns_dict(self):
        result = self.client.create_customer("test@example.com")
        assert isinstance(result, dict)

    def test_create_customer_has_id(self):
        result = self.client.create_customer("test@example.com")
        assert result["id"].startswith("cus_")

    def test_create_customer_stores_email(self):
        result = self.client.create_customer("test@example.com")
        assert result["email"] == "test@example.com"

    def test_create_customer_stores_name(self):
        result = self.client.create_customer("test@example.com", name="Jane Doe")
        assert result["name"] == "Jane Doe"


# ===========================================================================
# StripeClient — payment links
# ===========================================================================

class TestPaymentLinks:
    def setup_method(self):
        self.client = StripeClient()

    def test_create_payment_link_returns_dict(self):
        result = self.client.create_payment_link(2500, "usd", "Test Product")
        assert isinstance(result, dict)

    def test_payment_link_has_id(self):
        result = self.client.create_payment_link(2500, "usd", "Test Product")
        assert result["id"].startswith("plink_")

    def test_payment_link_has_url(self):
        result = self.client.create_payment_link(2500, "usd", "Test Product")
        assert "stripe.com" in result["url"]

    def test_payment_link_active(self):
        result = self.client.create_payment_link(2500, "usd", "Test Product")
        assert result["active"] is True


# ===========================================================================
# StripeClient — refunds
# ===========================================================================

class TestRefunds:
    def setup_method(self):
        self.client = StripeClient()

    def test_refund_returns_dict(self):
        result = self.client.refund_payment("pi_abc123")
        assert isinstance(result, dict)

    def test_refund_has_id(self):
        result = self.client.refund_payment("pi_abc123")
        assert result["id"].startswith("re_")

    def test_refund_succeeded(self):
        result = self.client.refund_payment("pi_abc123")
        assert result["status"] == "succeeded"

    def test_partial_refund_amount(self):
        result = self.client.refund_payment("pi_abc123", amount_cents=500)
        assert result["amount"] == 500


# ===========================================================================
# StripeClient — balance & payouts
# ===========================================================================

class TestBalancePayouts:
    def setup_method(self):
        self.client = StripeClient()

    def test_get_balance_returns_dict(self):
        result = self.client.get_balance()
        assert "available" in result
        assert "pending" in result

    def test_balance_available_is_list(self):
        result = self.client.get_balance()
        assert isinstance(result["available"], list)

    def test_list_payouts_returns_list(self):
        result = self.client.list_payouts()
        assert isinstance(result, list)


# ===========================================================================
# StripeClient — webhook signature
# ===========================================================================

class TestWebhookSignature:
    def test_mock_mode_always_valid(self):
        client = StripeClient()
        assert client.verify_webhook_signature(b"payload", "sig_header") is True


# ===========================================================================
# StripeWebhookHandler
# ===========================================================================

class TestWebhookHandler:
    def setup_method(self):
        self.handler = StripeWebhookHandler(verify_signatures=False)

    def test_dispatch_valid_event(self):
        payload = StripeWebhookHandler.build_event_payload(
            "payment_intent.succeeded",
            {"id": "pi_123", "amount": 2500},
        )
        event = self.handler.dispatch(payload, skip_verify=True)
        assert event is not None
        assert event.event_type == "payment_intent.succeeded"

    def test_dispatch_returns_webhook_event(self):
        payload = StripeWebhookHandler.build_event_payload(
            "checkout.session.completed", {}
        )
        event = self.handler.dispatch(payload, skip_verify=True)
        assert isinstance(event, WebhookEvent)

    def test_dispatch_invalid_json_returns_none(self):
        event = self.handler.dispatch(b"not-json", skip_verify=True)
        assert event is None

    def test_on_decorator_registers_listener(self):
        received = []

        @self.handler.on("charge.succeeded")
        def handle(e: WebhookEvent):
            received.append(e)

        payload = StripeWebhookHandler.build_event_payload(
            "charge.succeeded", {"id": "ch_abc"}
        )
        self.handler.dispatch(payload, skip_verify=True)
        assert len(received) == 1

    def test_register_callback(self):
        received = []

        def handle(e: WebhookEvent):
            received.append(e.event_type)

        self.handler.register("invoice.payment_succeeded", handle)
        payload = StripeWebhookHandler.build_event_payload(
            "invoice.payment_succeeded", {}
        )
        self.handler.dispatch(payload, skip_verify=True)
        assert received == ["invoice.payment_succeeded"]

    def test_multiple_listeners_same_event(self):
        calls = []

        @self.handler.on("charge.failed")
        def first(e):
            calls.append("first")

        @self.handler.on("charge.failed")
        def second(e):
            calls.append("second")

        payload = StripeWebhookHandler.build_event_payload("charge.failed", {})
        self.handler.dispatch(payload, skip_verify=True)
        assert calls == ["first", "second"]

    def test_event_id_preserved(self):
        payload = StripeWebhookHandler.build_event_payload(
            "payment_intent.succeeded", {}, event_id="evt_test_123"
        )
        event = self.handler.dispatch(payload, skip_verify=True)
        assert event.event_id == "evt_test_123"

    def test_event_data_object_extracted(self):
        payload = StripeWebhookHandler.build_event_payload(
            "payment_intent.succeeded", {"amount": 9999}
        )
        event = self.handler.dispatch(payload, skip_verify=True)
        assert event.data["amount"] == 9999

    def test_build_event_payload_is_valid_json(self):
        payload = StripeWebhookHandler.build_event_payload("test.event", {})
        data = json.loads(payload)
        assert data["type"] == "test.event"

    def test_supported_events_contains_key_types(self):
        for evt in (
            "payment_intent.succeeded",
            "customer.subscription.created",
            "customer.subscription.deleted",
            "invoice.payment_succeeded",
            "checkout.session.completed",
        ):
            assert evt in StripeWebhookHandler.SUPPORTED_EVENTS

    def test_unhandled_event_still_dispatched(self):
        payload = StripeWebhookHandler.build_event_payload(
            "some.unknown.event", {"foo": "bar"}
        )
        event = self.handler.dispatch(payload, skip_verify=True)
        assert event is not None
        assert event.event_type == "some.unknown.event"
