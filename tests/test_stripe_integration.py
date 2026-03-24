"""
Tests for the DreamCobots Stripe library integration.

Validates the Python integration module in stripe/python/app.py without
making real API calls — all Stripe SDK calls are mocked.
"""

import sys
import os
import json
import types
import importlib
import importlib.util
import unittest
from unittest.mock import patch

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

# ---------------------------------------------------------------------------
# Load stripe/python/app.py by file path to avoid conflict with the
# `stripe` pip package (which is also named `stripe`).
# ---------------------------------------------------------------------------

_STRIPE_APP_PATH = os.path.join(REPO_ROOT, "stripe", "python", "app.py")


def _load_stripe_app():
    """Import stripe/python/app.py under the alias 'dreamcobots_stripe_app'."""
    spec = importlib.util.spec_from_file_location("dreamcobots_stripe_app", _STRIPE_APP_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Helpers — build lightweight mock Stripe objects
# ---------------------------------------------------------------------------

def _make_stripe_obj(**kwargs):
    """Return a dict-like object that also supports attribute access, mimicking a Stripe SDK object."""

    class _StripeObj(dict):
        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError:
                raise AttributeError(name)

    return _StripeObj(kwargs)


def _make_pi(pi_id="pi_test123", client_secret="pi_test123_secret_test"):
    return _make_stripe_obj(
        id=pi_id,
        client_secret=client_secret,
        amount=2500,
        currency="usd",
        status="requires_payment_method",
    )


def _make_customer(cust_id="cus_test123", email="test@example.com"):
    return _make_stripe_obj(id=cust_id, email=email)


def _make_subscription(sub_id="sub_test123", status="active"):
    return _make_stripe_obj(id=sub_id, status=status)


def _make_session(session_id="cs_test123", url="https://checkout.stripe.com/pay/cs_test123"):
    return _make_stripe_obj(id=session_id, url=url)


def _make_payout(payout_id="po_test123", amount=10000, currency="usd"):
    return _make_stripe_obj(id=payout_id, amount=amount, currency=currency)


# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

class TestStripeIntegration(unittest.TestCase):
    """Unit tests for stripe/python/app.py helper functions."""

    # ------------------------------------------------------------------
    # Payment Intent
    # ------------------------------------------------------------------

    @patch("stripe.PaymentIntent.create")
    def test_create_payment_intent_returns_dict(self, mock_create):
        """create_payment_intent should return a dict with the PaymentIntent id."""
        mock_create.return_value = _make_pi()
        stripe_app = _load_stripe_app()

        result = stripe_app.create_payment_intent(2500, "usd")
        mock_create.assert_called_once_with(
            amount=2500,
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )
        self.assertIsInstance(result, dict)

    @patch("stripe.PaymentIntent.create")
    def test_create_payment_intent_called_with_correct_args(self, mock_create):
        """create_payment_intent passes amount and currency to the Stripe SDK."""
        mock_create.return_value = _make_pi(pi_id="pi_abc", client_secret="pi_abc_secret")
        stripe_app = _load_stripe_app()

        stripe_app.create_payment_intent(5000, "eur")
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs["amount"], 5000)
        self.assertEqual(call_kwargs["currency"], "eur")

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------

    @patch("stripe.Subscription.create")
    @patch("stripe.Customer.create")
    def test_create_subscription_creates_customer_first(self, mock_customer, mock_sub):
        """create_subscription should create a Customer then a Subscription."""
        mock_customer.return_value = _make_customer()
        mock_sub.return_value = _make_subscription()
        stripe_app = _load_stripe_app()

        result = stripe_app.create_subscription("user@example.com", "price_test123")
        mock_customer.assert_called_once_with(email="user@example.com")
        mock_sub.assert_called_once()
        self.assertIsInstance(result, dict)

    @patch("stripe.Subscription.delete")
    def test_cancel_subscription(self, mock_delete):
        """cancel_subscription should call stripe.Subscription.delete."""
        mock_delete.return_value = _make_subscription(status="canceled")
        stripe_app = _load_stripe_app()

        result = stripe_app.cancel_subscription("sub_test123")
        mock_delete.assert_called_once_with("sub_test123")
        self.assertIsInstance(result, dict)

    # ------------------------------------------------------------------
    # Checkout Session
    # ------------------------------------------------------------------

    @patch("stripe.checkout.Session.create")
    def test_create_checkout_session_subscription_mode(self, mock_create):
        """create_checkout_session in subscription mode passes correct params."""
        mock_create.return_value = _make_session()
        stripe_app = _load_stripe_app()

        result = stripe_app.create_checkout_session(
            price_id="price_test123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            mode="subscription",
        )
        mock_create.assert_called_once()
        kwargs = mock_create.call_args[1]
        self.assertEqual(kwargs["mode"], "subscription")
        self.assertEqual(kwargs["success_url"], "https://example.com/success")
        self.assertIsInstance(result, dict)

    @patch("stripe.checkout.Session.create")
    def test_create_checkout_session_payment_mode(self, mock_create):
        """create_checkout_session in payment mode passes correct params."""
        mock_create.return_value = _make_session()
        stripe_app = _load_stripe_app()

        stripe_app.create_checkout_session(
            price_id="price_test123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            mode="payment",
        )
        kwargs = mock_create.call_args[1]
        self.assertEqual(kwargs["mode"], "payment")

    @patch("stripe.checkout.Session.create")
    def test_create_checkout_session_with_customer_email(self, mock_create):
        """create_checkout_session includes customer_email when supplied."""
        mock_create.return_value = _make_session()
        stripe_app = _load_stripe_app()

        stripe_app.create_checkout_session(
            price_id="price_test123",
            success_url="https://example.com/s",
            cancel_url="https://example.com/c",
            customer_email="customer@example.com",
        )
        kwargs = mock_create.call_args[1]
        self.assertEqual(kwargs["customer_email"], "customer@example.com")

    # ------------------------------------------------------------------
    # Payout Tracking
    # ------------------------------------------------------------------

    @patch("stripe.Payout.list")
    def test_list_payouts_returns_list(self, mock_list):
        """list_payouts should return a list of payout dicts."""
        mock_list.return_value = _make_stripe_obj(
            data=[_make_payout("po_1"), _make_payout("po_2")]
        )
        stripe_app = _load_stripe_app()

        result = stripe_app.list_payouts(limit=2)
        mock_list.assert_called_once_with(limit=2)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    @patch("stripe.Payout.list")
    def test_list_payouts_default_limit(self, mock_list):
        """list_payouts defaults to limit=10."""
        mock_list.return_value = _make_stripe_obj(data=[])
        stripe_app = _load_stripe_app()

        stripe_app.list_payouts()
        mock_list.assert_called_once_with(limit=10)

    # ------------------------------------------------------------------
    # Webhook Handler
    # ------------------------------------------------------------------

    def test_webhook_endpoint_exists(self):
        """The Flask app should have a /webhook POST route."""
        stripe_app = _load_stripe_app()
        client = stripe_app.app.test_client()
        payload = json.dumps({"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_test"}}})
        response = client.post("/webhook", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_webhook_returns_received_true(self):
        """Webhook handler should return {"received": true}."""
        stripe_app = _load_stripe_app()
        client = stripe_app.app.test_client()
        payload = json.dumps({"type": "checkout.session.completed", "data": {"object": {"id": "cs_test"}}})
        response = client.post("/webhook", data=payload, content_type="application/json")
        data = json.loads(response.data)
        self.assertTrue(data.get("received"))

    def test_webhook_unhandled_event_type(self):
        """Webhook handler should still return 200 for unknown event types."""
        stripe_app = _load_stripe_app()
        client = stripe_app.app.test_client()
        payload = json.dumps({"type": "some.unknown.event", "data": {"object": {}}})
        response = client.post("/webhook", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_webhook_subscription_created(self):
        """Webhook handler should handle customer.subscription.created."""
        stripe_app = _load_stripe_app()
        client = stripe_app.app.test_client()
        payload = json.dumps({"type": "customer.subscription.created", "data": {"object": {"id": "sub_test"}}})
        response = client.post("/webhook", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_webhook_subscription_deleted(self):
        """Webhook handler should handle customer.subscription.deleted."""
        stripe_app = _load_stripe_app()
        client = stripe_app.app.test_client()
        payload = json.dumps({"type": "customer.subscription.deleted", "data": {"object": {"id": "sub_test"}}})
        response = client.post("/webhook", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)


# ---------------------------------------------------------------------------
# Environment configuration tests
# ---------------------------------------------------------------------------

class TestStripeEnvironmentConfig(unittest.TestCase):
    """Verify the .env.example template has the required Stripe variables."""

    ENV_EXAMPLE_PATH = os.path.join(REPO_ROOT, ".env.example")

    def _read_env_example(self) -> str:
        with open(self.ENV_EXAMPLE_PATH, "r", encoding="utf-8") as fh:
            return fh.read()

    def test_env_example_has_stripe_secret_key(self):
        content = self._read_env_example()
        self.assertIn("STRIPE_SECRET_KEY", content)

    def test_env_example_has_stripe_publishable_key(self):
        content = self._read_env_example()
        self.assertIn("STRIPE_PUBLISHABLE_KEY", content)

    def test_env_example_has_stripe_webhook_secret(self):
        content = self._read_env_example()
        self.assertIn("STRIPE_WEBHOOK_SECRET", content)

    def test_env_example_no_real_secret_keys(self):
        """The .env.example must not contain real Stripe live keys."""
        content = self._read_env_example()
        # Real live secret keys start with sk_live_ followed by actual characters
        import re
        real_key_pattern = re.compile(r"sk_live_[A-Za-z0-9]{20,}")
        self.assertIsNone(
            real_key_pattern.search(content),
            "Real Stripe secret key found in .env.example — remove it immediately!",
        )

    def test_gitignore_excludes_env(self):
        """The .gitignore should prevent .env from being committed."""
        gitignore_path = os.path.join(REPO_ROOT, ".gitignore")
        with open(gitignore_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn(".env", content)


# ---------------------------------------------------------------------------
# Integration directory structure tests
# ---------------------------------------------------------------------------

class TestStripeDirectoryStructure(unittest.TestCase):
    """Verify that all required Stripe integration files exist."""

    STRIPE_ROOT = os.path.join(REPO_ROOT, "stripe")

    def _path(self, *parts) -> str:
        return os.path.join(self.STRIPE_ROOT, *parts)

    def test_node_index_exists(self):
        self.assertTrue(os.path.isfile(self._path("node", "index.js")))

    def test_node_package_json_exists(self):
        self.assertTrue(os.path.isfile(self._path("node", "package.json")))

    def test_python_app_exists(self):
        self.assertTrue(os.path.isfile(self._path("python", "app.py")))

    def test_python_requirements_exists(self):
        self.assertTrue(os.path.isfile(self._path("python", "requirements.txt")))

    def test_ruby_app_exists(self):
        self.assertTrue(os.path.isfile(self._path("ruby", "app.rb")))

    def test_ruby_gemfile_exists(self):
        self.assertTrue(os.path.isfile(self._path("ruby", "Gemfile")))

    def test_php_index_exists(self):
        self.assertTrue(os.path.isfile(self._path("php", "index.php")))

    def test_php_composer_json_exists(self):
        self.assertTrue(os.path.isfile(self._path("php", "composer.json")))

    def test_go_main_exists(self):
        self.assertTrue(os.path.isfile(self._path("go", "main.go")))

    def test_go_mod_exists(self):
        self.assertTrue(os.path.isfile(self._path("go", "go.mod")))

    def test_java_integration_exists(self):
        self.assertTrue(os.path.isfile(self._path("java", "StripeIntegration.java")))

    def test_java_pom_exists(self):
        self.assertTrue(os.path.isfile(self._path("java", "pom.xml")))

    def test_dotnet_cs_exists(self):
        self.assertTrue(os.path.isfile(self._path("dotnet", "StripeIntegration.cs")))

    def test_dotnet_csproj_exists(self):
        self.assertTrue(os.path.isfile(self._path("dotnet", "DreamCobotsStripe.csproj")))

    def test_ios_swift_exists(self):
        self.assertTrue(os.path.isfile(self._path("ios", "StripeIntegration.swift")))

    def test_ios_podfile_exists(self):
        self.assertTrue(os.path.isfile(self._path("ios", "Podfile")))

    def test_android_kotlin_exists(self):
        self.assertTrue(os.path.isfile(self._path("android", "StripeIntegration.kt")))

    def test_stripe_readme_exists(self):
        self.assertTrue(os.path.isfile(self._path("README.md")))

    def test_env_example_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, ".env.example")))

    def test_stripe_in_requirements(self):
        req_path = os.path.join(REPO_ROOT, "requirements.txt")
        with open(req_path) as fh:
            content = fh.read()
        self.assertIn("stripe", content)


# ---------------------------------------------------------------------------
# Node.js package.json content tests
# ---------------------------------------------------------------------------

class TestNodePackageJson(unittest.TestCase):
    """Verify stripe/node/package.json lists stripe as a dependency."""

    def test_stripe_dependency_listed(self):
        pkg_path = os.path.join(REPO_ROOT, "stripe", "node", "package.json")
        with open(pkg_path) as fh:
            pkg = json.load(fh)
        self.assertIn("stripe", pkg.get("dependencies", {}))

    def test_express_dependency_listed(self):
        pkg_path = os.path.join(REPO_ROOT, "stripe", "node", "package.json")
        with open(pkg_path) as fh:
            pkg = json.load(fh)
        self.assertIn("express", pkg.get("dependencies", {}))


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
