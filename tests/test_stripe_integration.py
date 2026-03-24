"""
Tests for bots/stripe_integration/

Covers StripeBot, WebhookHandler, and PaymentLinks in simulation mode
(no real Stripe credentials required).
"""

import json
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.stripe_integration.stripe_bot import StripeBot, StripeBotError
from bots.stripe_integration.webhook_handler import WebhookHandler, WebhookVerificationError
from bots.stripe_integration.payment_links import PaymentLinks, PaymentLinksError
from bots.stripe_integration import StripeBot as StripeBotPublic


# ===========================================================================
# StripeBot tests
# ===========================================================================

class TestStripeBotInit:
    """StripeBot initialisation."""

    def test_simulation_mode_when_no_key(self):
        bot = StripeBot(secret_key="", simulation_mode=True)
        assert bot.simulation_mode is True

    def test_explicit_simulation_mode(self):
        bot = StripeBot(simulation_mode=True)
        assert bot.simulation_mode is True

    def test_publishable_key_stored(self):
        bot = StripeBot(publishable_key="pk_test_abc", simulation_mode=True)
        assert bot.publishable_key == "pk_test_abc"

    def test_package_export(self):
        """StripeBot is exported from bots.stripe_integration."""
        assert StripeBotPublic is StripeBot


class TestStripeBotCustomers:
    """Customer management in simulation mode."""

    def setup_method(self):
        self.bot = StripeBot(simulation_mode=True)

    def test_create_customer_returns_dict(self):
        result = self.bot.create_customer("test@example.com", "Test User")
        assert "id" in result
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert result["live"] is False

    def test_create_customer_id_prefixed(self):
        result = self.bot.create_customer("a@b.com")
        assert result["id"].startswith("cus_")

    def test_create_customer_stored_internally(self):
        result = self.bot.create_customer("stored@example.com")
        retrieved = self.bot.get_customer(result["id"])
        assert retrieved["email"] == "stored@example.com"

    def test_get_customer_missing_raises(self):
        with pytest.raises(StripeBotError):
            self.bot.get_customer("cus_nonexistent")


class TestStripeBotCheckout:
    """Checkout session creation in simulation mode."""

    def setup_method(self):
        self.bot = StripeBot(simulation_mode=True)

    def test_create_checkout_session_returns_url(self):
        result = self.bot.create_checkout_session(
            amount_cents=4999,
            currency="usd",
            customer_email="buyer@example.com",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )
        assert "checkout_url" in result
        assert "session_id" in result
        assert result["amount_cents"] == 4999
        assert result["currency"] == "usd"
        assert result["live"] is False

    def test_session_id_prefix(self):
        result = self.bot.create_checkout_session(
            amount_cents=100,
            currency="usd",
            customer_email="x@y.com",
            success_url="https://ok.com",
            cancel_url="https://no.com",
        )
        assert result["session_id"].startswith("cs_")

    def test_checkout_url_contains_session_id(self):
        result = self.bot.create_checkout_session(
            amount_cents=100,
            currency="usd",
            customer_email="x@y.com",
            success_url="https://ok.com",
            cancel_url="https://no.com",
        )
        assert result["session_id"] in result["checkout_url"]

    def test_subscription_mode(self):
        result = self.bot.create_checkout_session(
            amount_cents=999,
            currency="usd",
            customer_email="sub@example.com",
            success_url="https://ok.com",
            cancel_url="https://no.com",
            mode="subscription",
        )
        assert result["mode"] == "subscription"


class TestStripeBotPaymentIntents:
    """PaymentIntent creation in simulation mode."""

    def setup_method(self):
        self.bot = StripeBot(simulation_mode=True)

    def test_create_payment_intent_returns_dict(self):
        result = self.bot.create_payment_intent(2500, "usd")
        assert result["id"].startswith("pi_")
        assert "client_secret" in result
        assert result["amount_cents"] == 2500
        assert result["currency"] == "usd"
        assert result["live"] is False

    def test_payment_intent_status(self):
        result = self.bot.create_payment_intent(100, "eur")
        assert result["status"] == "requires_payment_method"


class TestStripeBotSubscriptions:
    """Subscription management in simulation mode."""

    def setup_method(self):
        self.bot = StripeBot(simulation_mode=True)

    def test_create_subscription_returns_active(self):
        result = self.bot.create_subscription("cus_123", "price_starter")
        assert result["id"].startswith("sub_")
        assert result["status"] == "active"
        assert result["customer_id"] == "cus_123"
        assert result["price_id"] == "price_starter"

    def test_cancel_subscription(self):
        sub = self.bot.create_subscription("cus_456", "price_growth")
        result = self.bot.cancel_subscription(sub["id"])
        assert result["status"] == "canceled"

    def test_cancel_nonexistent_subscription_raises(self):
        with pytest.raises(StripeBotError):
            self.bot.cancel_subscription("sub_nonexistent")


class TestStripeBotRefunds:
    """Refund creation in simulation mode."""

    def setup_method(self):
        self.bot = StripeBot(simulation_mode=True)

    def test_full_refund(self):
        result = self.bot.create_refund("pi_test_abc")
        assert result["id"].startswith("re_")
        assert result["status"] == "succeeded"
        assert result["live"] is False

    def test_partial_refund(self):
        result = self.bot.create_refund("pi_test_abc", amount_cents=1000)
        assert result["amount_cents"] == 1000


class TestStripeBotPayouts:
    """Payout creation in simulation mode."""

    def setup_method(self):
        self.bot = StripeBot(simulation_mode=True)

    def test_create_payout_returns_pending(self):
        result = self.bot.create_payout(10000, "usd")
        assert result["id"].startswith("po_")
        assert result["status"] == "pending"
        assert result["amount_cents"] == 10000

    def test_payout_currency_normalised(self):
        result = self.bot.create_payout(5000, "USD")
        assert result["currency"] == "usd"


class TestStripeBotBalance:
    """Balance retrieval in simulation mode."""

    def setup_method(self):
        self.bot = StripeBot(simulation_mode=True)

    def test_get_balance_returns_dict(self):
        result = self.bot.get_balance()
        assert "available" in result
        assert "pending" in result
        assert result["live"] is False

    def test_balance_has_currency(self):
        result = self.bot.get_balance()
        assert result["available"][0]["currency"] == "usd"


class TestStripeBotChat:
    """BuddyAI-compatible chat interface."""

    def setup_method(self):
        self.bot = StripeBot(simulation_mode=True)

    def test_chat_returns_dict(self):
        result = self.bot.chat("hello")
        assert "response" in result
        assert result["bot_name"] == "stripe_integration"

    def test_chat_mode_simulation(self):
        result = self.bot.chat("what mode am I in?")
        assert result["mode"] == "simulation"

    def test_chat_balance_keyword(self):
        result = self.bot.chat("what is my balance?")
        assert "balance" in result["response"].lower() or "available" in result["response"].lower()

    def test_chat_checkout_keyword(self):
        result = self.bot.chat("how do I create a checkout session?")
        assert "checkout" in result["response"].lower() or "session" in result["response"].lower()

    def test_chat_subscription_keyword(self):
        result = self.bot.chat("how do I create a subscription?")
        assert "subscription" in result["response"].lower()

    def test_chat_refund_keyword(self):
        result = self.bot.chat("how do I refund a payment?")
        assert "refund" in result["response"].lower()

    def test_chat_payout_keyword(self):
        result = self.bot.chat("how do I get a payout?")
        assert "payout" in result["response"].lower()

    def test_chat_webhook_keyword(self):
        result = self.bot.chat("how do I handle webhooks?")
        assert "webhook" in result["response"].lower()

    def test_chat_payment_link_keyword(self):
        result = self.bot.chat("how do I create a payment link?")
        assert "payment" in result["response"].lower()

    def test_register_with_buddy(self):
        """register_with_buddy calls register_bot on the provided instance."""
        class FakeBuddy:
            def __init__(self):
                self.registered = {}
            def register_bot(self, name, bot):
                self.registered[name] = bot

        buddy = FakeBuddy()
        self.bot.register_with_buddy(buddy)
        assert "stripe_integration" in buddy.registered
        assert buddy.registered["stripe_integration"] is self.bot


# ===========================================================================
# WebhookHandler tests
# ===========================================================================

class TestWebhookHandlerInit:
    """WebhookHandler initialisation."""

    def test_init_no_secret(self):
        handler = WebhookHandler(webhook_secret="")
        assert handler.webhook_secret == ""

    def test_init_with_secret(self):
        handler = WebhookHandler(webhook_secret="whsec_test")
        assert handler.webhook_secret == "whsec_test"

    def test_supported_events_list(self):
        assert "payment_intent.succeeded" in WebhookHandler.SUPPORTED_EVENTS
        assert "checkout.session.completed" in WebhookHandler.SUPPORTED_EVENTS


class TestWebhookHandlerRegistration:
    """Handler registration via decorator and programmatic API."""

    def setup_method(self):
        self.handler = WebhookHandler(webhook_secret="whsec_test")

    def test_register_via_decorator(self):
        @self.handler.on("payment_intent.succeeded")
        def my_handler(event):
            pass

        assert "payment_intent.succeeded" in self.handler._handlers
        assert my_handler in self.handler._handlers["payment_intent.succeeded"]

    def test_register_programmatically(self):
        called = []
        def fn(event):
            called.append(event)
        self.handler.register_handler("charge.succeeded", fn)
        assert fn in self.handler._handlers["charge.succeeded"]

    def test_multiple_handlers_same_event(self):
        results = []
        self.handler.register_handler("invoice.paid", lambda e: results.append("h1"))
        self.handler.register_handler("invoice.paid", lambda e: results.append("h2"))
        payload = json.dumps({"type": "invoice.paid", "id": "evt_1"}).encode()
        result = self.handler.handle_event(payload, "", skip_verification=True)
        assert result["dispatched"] == 2
        assert results == ["h1", "h2"]


class TestWebhookHandlerEventProcessing:
    """Event dispatching and logging."""

    def setup_method(self):
        self.handler = WebhookHandler(webhook_secret="")

    def _make_payload(self, event_type: str, event_id: str = "evt_123") -> bytes:
        return json.dumps({"type": event_type, "id": event_id, "data": {"object": {}}}).encode()

    def test_handle_event_returns_received(self):
        payload = self._make_payload("payment_intent.succeeded")
        result = self.handler.handle_event(payload, "", skip_verification=True)
        assert result["received"] is True

    def test_handle_event_returns_event_type(self):
        payload = self._make_payload("checkout.session.completed", "evt_abc")
        result = self.handler.handle_event(payload, "", skip_verification=True)
        assert result["event_type"] == "checkout.session.completed"
        assert result["event_id"] == "evt_abc"

    def test_dispatched_count_zero_when_no_handler(self):
        payload = self._make_payload("payout.created")
        result = self.handler.handle_event(payload, "", skip_verification=True)
        assert result["dispatched"] == 0

    def test_dispatched_count_one_when_handler_registered(self):
        received = []
        self.handler.register_handler("payout.paid", lambda e: received.append(e))
        payload = self._make_payload("payout.paid")
        result = self.handler.handle_event(payload, "", skip_verification=True)
        assert result["dispatched"] == 1
        assert len(received) == 1

    def test_event_logged(self):
        payload = self._make_payload("invoice.paid", "evt_log1")
        self.handler.handle_event(payload, "", skip_verification=True)
        log = self.handler.get_event_log()
        assert any(e["event_id"] == "evt_log1" for e in log)

    def test_event_log_grows(self):
        for i in range(5):
            payload = self._make_payload("charge.succeeded", f"evt_{i}")
            self.handler.handle_event(payload, "", skip_verification=True)
        assert len(self.handler.get_event_log()) == 5

    def test_clear_event_log(self):
        payload = self._make_payload("charge.failed", "evt_clear")
        self.handler.handle_event(payload, "", skip_verification=True)
        self.handler.clear_event_log()
        assert self.handler.get_event_log() == []

    def test_get_event_log_returns_copy(self):
        payload = self._make_payload("charge.refunded", "evt_copy")
        self.handler.handle_event(payload, "", skip_verification=True)
        log1 = self.handler.get_event_log()
        log1.append({"fake": "entry"})
        log2 = self.handler.get_event_log()
        assert len(log2) == 1  # original unchanged


class TestWebhookHandlerVerification:
    """Signature verification."""

    def test_invalid_sig_raises_when_no_skip(self):
        handler = WebhookHandler(webhook_secret="whsec_test_secret")
        payload = json.dumps({"type": "invoice.paid", "id": "evt_1"}).encode()
        with pytest.raises(WebhookVerificationError):
            handler.handle_event(payload, "t=bad,v1=badsig")

    def test_skip_verification_bypasses_check(self):
        handler = WebhookHandler(webhook_secret="whsec_test_secret")
        payload = json.dumps({"type": "invoice.paid", "id": "evt_2"}).encode()
        result = handler.handle_event(payload, "t=bad,v1=badsig", skip_verification=True)
        assert result["received"] is True


# ===========================================================================
# PaymentLinks tests
# ===========================================================================

class TestPaymentLinksInit:
    """PaymentLinks initialisation."""

    def test_simulation_mode_when_no_key(self):
        pl = PaymentLinks(secret_key="")
        assert pl.simulation_mode is True

    def test_explicit_no_key_is_simulation(self):
        pl = PaymentLinks()
        # Without env var, should default to simulation
        assert isinstance(pl.simulation_mode, bool)


class TestPaymentLinksCreate:
    """Payment link creation in simulation mode."""

    def setup_method(self):
        self.pl = PaymentLinks(secret_key="")

    def test_create_link_returns_dict(self):
        result = self.pl.create_link(4999, "usd", "Starter Plan")
        assert "id" in result
        assert "url" in result
        assert result["product_name"] == "Starter Plan"
        assert result["amount_cents"] == 4999
        assert result["currency"] == "usd"
        assert result["active"] is True

    def test_link_id_prefix(self):
        result = self.pl.create_link(100, "usd", "Test")
        assert result["id"].startswith("plink_")

    def test_link_url_contains_id(self):
        result = self.pl.create_link(100, "usd", "Test")
        assert result["id"] in result["url"]

    def test_currency_normalised(self):
        result = self.pl.create_link(100, "USD", "Test")
        assert result["currency"] == "usd"

    def test_link_stored_internally(self):
        result = self.pl.create_link(100, "usd", "Stored")
        links = self.pl.list_links()
        assert any(l["id"] == result["id"] for l in links)


class TestPaymentLinksDeactivate:
    """Deactivating payment links."""

    def setup_method(self):
        self.pl = PaymentLinks(secret_key="")

    def test_deactivate_link(self):
        link = self.pl.create_link(1000, "usd", "Deactivate Test")
        result = self.pl.deactivate_link(link["id"])
        assert result["active"] is False

    def test_deactivate_nonexistent_raises(self):
        with pytest.raises(PaymentLinksError):
            self.pl.deactivate_link("plink_nonexistent")

    def test_list_links_empty_initially(self):
        pl = PaymentLinks(secret_key="")
        assert pl.list_links() == []

    def test_list_links_returns_all(self):
        pl = PaymentLinks(secret_key="")
        pl.create_link(100, "usd", "A")
        pl.create_link(200, "usd", "B")
        assert len(pl.list_links()) == 2


# ===========================================================================
# Integration: StripeBot + WebhookHandler + PaymentLinks
# ===========================================================================

class TestIntegration:
    """High-level integration across all three components."""

    def setup_method(self):
        self.bot = StripeBot(simulation_mode=True)
        self.handler = WebhookHandler(webhook_secret="")
        self.pl = PaymentLinks(secret_key="")

    def test_end_to_end_payment_flow(self):
        # 1. Create customer
        customer = self.bot.create_customer("e2e@example.com", "E2E User")
        assert customer["id"].startswith("cus_")

        # 2. Create checkout session
        session = self.bot.create_checkout_session(
            amount_cents=9900,
            currency="usd",
            customer_email="e2e@example.com",
            success_url="https://ok.com",
            cancel_url="https://no.com",
        )
        assert session["checkout_url"].startswith("https://")

        # 3. Simulate payment_intent.succeeded webhook
        received = []
        self.handler.register_handler(
            "payment_intent.succeeded", lambda e: received.append(e)
        )
        payload = json.dumps({
            "type": "payment_intent.succeeded",
            "id": "evt_e2e",
            "data": {"object": {"id": "pi_e2e", "amount": 9900, "currency": "usd"}},
        }).encode()
        result = self.handler.handle_event(payload, "", skip_verification=True)
        assert result["dispatched"] == 1
        assert len(received) == 1

    def test_subscription_with_payment_link(self):
        # Create subscription
        sub = self.bot.create_subscription("cus_sub_test", "price_monthly")
        assert sub["status"] == "active"

        # Create payment link for ongoing use
        link = self.pl.create_link(2999, "usd", "Monthly Plan")
        assert link["active"] is True

        # Cancel subscription
        cancelled = self.bot.cancel_subscription(sub["id"])
        assert cancelled["status"] == "canceled"
