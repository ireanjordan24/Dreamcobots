/**
 * DreamCobots — Stripe Node.js Integration
 *
 * Provides Payment Intent creation and webhook handling.
 *
 * Setup:
 *   npm install stripe express body-parser
 *   export STRIPE_SECRET_KEY=sk_...
 *   node index.js
 */

"use strict";

const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);
const express = require("express");
const bodyParser = require("body-parser");

const app = express();

// ── Payment Intent ────────────────────────────────────────────────────────────

/**
 * Create a Payment Intent for a one-time charge.
 * @param {number} amountInCents  Amount in the smallest currency unit (e.g. cents).
 * @param {string} currency       ISO 4217 currency code (e.g. "usd").
 * @returns {Promise<object>}     Stripe PaymentIntent object.
 */
async function createPaymentIntent(amountInCents, currency) {
  const paymentIntent = await stripe.paymentIntents.create({
    amount: amountInCents,
    currency: currency,
    automatic_payment_methods: { enabled: true },
  });
  return paymentIntent;
}

// ── Subscription ──────────────────────────────────────────────────────────────

/**
 * Create a customer and subscribe them to a price/plan.
 * @param {string} email    Customer e-mail address.
 * @param {string} priceId  Stripe Price ID (e.g. "price_xxx").
 * @returns {Promise<object>} Stripe Subscription object.
 */
async function createSubscription(email, priceId) {
  const customer = await stripe.customers.create({ email });
  const subscription = await stripe.subscriptions.create({
    customer: customer.id,
    items: [{ price: priceId }],
    payment_behavior: "default_incomplete",
    expand: ["latest_invoice.payment_intent"],
  });
  return subscription;
}

// ── Payout Tracking ───────────────────────────────────────────────────────────

/**
 * List recent payouts from your Stripe account.
 * @param {number} limit  Maximum number of payouts to return (default 10).
 * @returns {Promise<object[]>} Array of Stripe Payout objects.
 */
async function listPayouts(limit = 10) {
  const payouts = await stripe.payouts.list({ limit });
  return payouts.data;
}

// ── Webhook Handler ───────────────────────────────────────────────────────────

app.use("/webhook", bodyParser.raw({ type: "application/json" }));

app.post("/webhook", (req, res) => {
  const sig = req.headers["stripe-signature"];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  let event;
  try {
    event = webhookSecret
      ? stripe.webhooks.constructEvent(req.body, sig, webhookSecret)
      : JSON.parse(req.body);
  } catch (err) {
    console.error("Webhook signature verification failed:", err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  console.log("Webhook event received:", event.type);

  switch (event.type) {
    case "payment_intent.succeeded":
      console.log("Payment succeeded:", event.data.object.id);
      break;
    case "checkout.session.completed":
      console.log("Checkout session completed:", event.data.object.id);
      break;
    case "customer.subscription.created":
      console.log("Subscription created:", event.data.object.id);
      break;
    case "customer.subscription.deleted":
      console.log("Subscription canceled:", event.data.object.id);
      break;
    default:
      console.log("Unhandled event type:", event.type);
  }

  res.status(200).json({ received: true });
});

app.use(bodyParser.json());

// ── Start Server ──────────────────────────────────────────────────────────────

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`DreamCobots Stripe webhook listener running on port ${PORT}`);
  console.log("Test locally: stripe listen --forward-to localhost:" + PORT + "/webhook");
});

// ── Quick smoke-test (run directly) ──────────────────────────────────────────

if (require.main === module && process.env.STRIPE_SECRET_KEY) {
  createPaymentIntent(2500, "usd")
    .then((pi) => console.log("PaymentIntent created:", pi.id))
    .catch(console.error);
}

module.exports = { createPaymentIntent, createSubscription, listPayouts };
