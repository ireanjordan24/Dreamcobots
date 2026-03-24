/**
 * Dreamcobots Stripe Integration — Node.js
 *
 * Install: npm install
 * Configure .env (see ../../.env.example)
 *
 * Usage:
 *   node index.js
 */

require("dotenv").config();
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);

/**
 * Create a Stripe Checkout session for a one-time payment.
 */
async function createCheckoutSession({
  amountCents,
  currency = "usd",
  customerEmail,
  successUrl,
  cancelUrl,
  mode = "payment",
}) {
  const session = await stripe.checkout.sessions.create({
    payment_method_types: ["card"],
    line_items: [
      {
        price_data: {
          currency: currency.toLowerCase(),
          product_data: { name: "Dreamcobots Service" },
          unit_amount: amountCents,
        },
        quantity: 1,
      },
    ],
    mode,
    customer_email: customerEmail,
    success_url: successUrl,
    cancel_url: cancelUrl,
  });
  return { sessionId: session.id, checkoutUrl: session.url };
}

/**
 * Create a shareable Stripe Payment Link.
 */
async function createPaymentLink({ amountCents, currency = "usd", productName }) {
  const price = await stripe.prices.create({
    unit_amount: amountCents,
    currency: currency.toLowerCase(),
    product_data: { name: productName },
  });
  const link = await stripe.paymentLinks.create({
    line_items: [{ price: price.id, quantity: 1 }],
  });
  return { id: link.id, url: link.url };
}

/**
 * Create a Stripe Subscription for a customer.
 */
async function createSubscription({ customerId, priceId }) {
  const subscription = await stripe.subscriptions.create({
    customer: customerId,
    items: [{ price: priceId }],
  });
  return { id: subscription.id, status: subscription.status };
}

/**
 * Issue a refund for a PaymentIntent.
 */
async function createRefund({ paymentIntentId, amountCents }) {
  const params = { payment_intent: paymentIntentId };
  if (amountCents) params.amount = amountCents;
  const refund = await stripe.refunds.create(params);
  return { id: refund.id, status: refund.status };
}

module.exports = {
  createCheckoutSession,
  createPaymentLink,
  createSubscription,
  createRefund,
};

if (require.main === module) {
  const mode = process.env.STRIPE_SECRET_KEY ? "live" : "simulation";
  console.log(`Dreamcobots Stripe Node.js client initialised in ${mode} mode.`);
}
