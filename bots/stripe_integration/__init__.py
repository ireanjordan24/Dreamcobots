"""Stripe Integration package for Dreamcobots.

Provides StripeBot, WebhookHandler, and PaymentLinks for full Stripe support.
Configure the bot by setting environment variables:
  STRIPE_SECRET_KEY      — your Stripe secret key (sk_live_... or sk_test_...)
  STRIPE_PUBLISHABLE_KEY — your Stripe publishable key (pk_live_... or pk_test_...)
  STRIPE_WEBHOOK_SECRET  — your Stripe webhook signing secret (whsec_...)
"""

from bots.stripe_integration.stripe_bot import StripeBot
from bots.stripe_integration.webhook_handler import WebhookHandler
from bots.stripe_integration.payment_links import PaymentLinks

__all__ = ["StripeBot", "WebhookHandler", "PaymentLinks"]
