"""
Dreamcobots Stripe Integration Package.

Provides a unified, environment-variable-driven Stripe client used by all
Dreamcobots bots (Lead Gen, SaaS, Real Estate, Car Flipping, etc.).

Usage::

    from bots.stripe_integration import StripeClient, StripeWebhookHandler

    client = StripeClient()
    result = client.create_checkout_session(
        amount_cents=2500,
        currency="usd",
        product_name="Premium Lead Package",
        success_url="https://dreamcobots.com/success",
        cancel_url="https://dreamcobots.com/cancel",
    )
"""

from bots.stripe_integration.stripe_client import StripeClient, StripeClientError
from bots.stripe_integration.webhook_handler import StripeWebhookHandler, WebhookEvent

__all__ = [
    "StripeClient",
    "StripeClientError",
    "StripeWebhookHandler",
    "WebhookEvent",
]
