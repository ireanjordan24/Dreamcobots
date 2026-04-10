'use strict';

/**
 * DreamCo Payment Auto Collector — God Mode Feature
 *
 * Streamlined Stripe-compatible payment processing with subscription billing,
 * invoice automation, and payment collection workflows.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const SUBSCRIPTION_PLANS = {
  starter:    { name: 'Starter',    price_monthly: 49,   price_yearly: 470,   features: ['5 bots', 'basic analytics', 'email support'] },
  growth:     { name: 'Growth',     price_monthly: 149,  price_yearly: 1430,  features: ['20 bots', 'advanced analytics', 'priority support', 'API access'] },
  pro:        { name: 'Pro',        price_monthly: 299,  price_yearly: 2870,  features: ['unlimited bots', 'white-label', 'dedicated manager', 'custom integrations'] },
  enterprise: { name: 'Enterprise', price_monthly: 999,  price_yearly: 9590,  features: ['everything in Pro', 'SLA guarantee', 'on-prem option', 'custom AI training'] },
};

const PAYMENT_STATUSES = ['pending', 'processing', 'succeeded', 'failed', 'refunded', 'disputed'];

const INVOICE_TERMS = {
  net_7:  { days: 7,  label: 'Net 7'  },
  net_14: { days: 14, label: 'Net 14' },
  net_30: { days: 30, label: 'Net 30' },
  due_on_receipt: { days: 0, label: 'Due on Receipt' },
};

// In-memory stores (production: replace with database)
const _subscriptions = [];
const _invoices = [];
const _payments = [];

// ---------------------------------------------------------------------------
// Subscription Engine
// ---------------------------------------------------------------------------

/**
 * Create a new subscription for a customer.
 * @param {string} customerName
 * @param {string} plan - 'starter' | 'growth' | 'pro' | 'enterprise'
 * @param {string} [billingCycle='monthly'] - 'monthly' | 'yearly'
 * @returns {Object} Subscription record
 */
function createSubscription(customerName, plan, billingCycle = 'monthly') {
  const planConfig = SUBSCRIPTION_PLANS[plan];
  if (!planConfig) {
    throw new Error(`Unknown plan: "${plan}". Valid plans: ${Object.keys(SUBSCRIPTION_PLANS).join(', ')}`);
  }

  const amount = billingCycle === 'yearly' ? planConfig.price_yearly : planConfig.price_monthly;
  const subscriptionId = `SUB-${Date.now()}`;
  const now = new Date();
  const nextBilling = new Date(now);
  nextBilling.setMonth(nextBilling.getMonth() + (billingCycle === 'yearly' ? 12 : 1));

  const subscription = {
    subscription_id: subscriptionId,
    customer_name: customerName,
    customer_id: `CUS-${Math.abs(hashStr(customerName)) % 100000}`,
    plan,
    plan_name: planConfig.name,
    billing_cycle: billingCycle,
    amount_usd: amount,
    features: planConfig.features,
    status: 'active',
    created_at: now.toISOString(),
    next_billing_at: nextBilling.toISOString(),
    auto_renew: true,
    payment_method: 'card_****4242',
  };

  _subscriptions.push(subscription);
  return subscription;
}

/**
 * List all active subscriptions.
 * @returns {Object[]}
 */
function listSubscriptions() {
  return [..._subscriptions];
}

/**
 * Cancel a subscription.
 * @param {string} subscriptionId
 * @returns {Object} Updated subscription
 */
function cancelSubscription(subscriptionId) {
  const sub = _subscriptions.find((s) => s.subscription_id === subscriptionId);
  if (!sub) throw new Error(`Subscription not found: ${subscriptionId}`);
  sub.status = 'cancelled';
  sub.cancelled_at = new Date().toISOString();
  sub.auto_renew = false;
  return { ...sub };
}

// ---------------------------------------------------------------------------
// Invoice Engine
// ---------------------------------------------------------------------------

/**
 * Generate an invoice for a customer.
 * @param {string} customerName
 * @param {number} amount
 * @param {string} description
 * @param {string} [terms='net_30']
 * @returns {Object} Invoice record
 */
function generateInvoice(customerName, amount, description, terms = 'net_30') {
  const termConfig = INVOICE_TERMS[terms] || INVOICE_TERMS.net_30;
  const dueDate = new Date(Date.now() + termConfig.days * 86400000);
  const invoiceId = `INV-${Date.now()}`;

  const invoice = {
    invoice_id: invoiceId,
    invoice_number: `DC-${String(_invoices.length + 1001).padStart(5, '0')}`,
    customer_name: customerName,
    customer_id: `CUS-${Math.abs(hashStr(customerName)) % 100000}`,
    description,
    amount_usd: amount,
    tax_usd: Math.round(amount * 0.0875 * 100) / 100,
    total_usd: Math.round(amount * 1.0875 * 100) / 100,
    terms: termConfig.label,
    due_date: dueDate.toISOString(),
    status: 'pending',
    created_at: new Date().toISOString(),
    paid_at: null,
    payment_link: `https://pay.dreamco.ai/i/${invoiceId}`,
  };

  _invoices.push(invoice);
  return invoice;
}

/**
 * List all invoices.
 * @param {string} [status] - Filter by status
 * @returns {Object[]}
 */
function listInvoices(status) {
  return status ? _invoices.filter((i) => i.status === status) : [..._invoices];
}

/**
 * Mark an invoice as paid and process the payment.
 * @param {string} invoiceId
 * @returns {Object} Payment confirmation
 */
function collectPayment(invoiceId) {
  const invoice = _invoices.find((i) => i.invoice_id === invoiceId);
  if (!invoice) throw new Error(`Invoice not found: ${invoiceId}`);
  if (invoice.status === 'paid') throw new Error(`Invoice ${invoiceId} is already paid`);

  invoice.status = 'paid';
  invoice.paid_at = new Date().toISOString();

  const payment = {
    payment_id: `PAY-${Date.now()}`,
    invoice_id: invoiceId,
    invoice_number: invoice.invoice_number,
    customer_name: invoice.customer_name,
    amount_usd: invoice.total_usd,
    status: 'succeeded',
    provider: 'stripe',
    charge_id: `ch_${Math.abs(hashStr(invoiceId)).toString(36).slice(0, 16)}`,
    receipt_url: `https://receipts.dreamco.ai/${invoiceId}`,
    processed_at: new Date().toISOString(),
  };

  _payments.push(payment);
  return payment;
}

// ---------------------------------------------------------------------------
// Payment Analytics
// ---------------------------------------------------------------------------

/**
 * Get revenue summary across all payment records.
 * @returns {Object}
 */
function revenueSummary() {
  const totalRevenue = _payments
    .filter((p) => p.status === 'succeeded')
    .reduce((sum, p) => sum + p.amount_usd, 0);

  const mrr = _subscriptions
    .filter((s) => s.status === 'active' && s.billing_cycle === 'monthly')
    .reduce((sum, s) => sum + s.amount_usd, 0);

  const arr = mrr * 12 + _subscriptions
    .filter((s) => s.status === 'active' && s.billing_cycle === 'yearly')
    .reduce((sum, s) => sum + s.amount_usd, 0);

  return {
    total_revenue_usd: Math.round(totalRevenue * 100) / 100,
    mrr_usd: Math.round(mrr * 100) / 100,
    arr_usd: Math.round(arr * 100) / 100,
    active_subscriptions: _subscriptions.filter((s) => s.status === 'active').length,
    pending_invoices: _invoices.filter((i) => i.status === 'pending').length,
    total_payments: _payments.length,
    summary_at: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function hashStr(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

// ---------------------------------------------------------------------------
// Module-level run()
// ---------------------------------------------------------------------------

/**
 * Run the Payment Auto Collector with sample data.
 * @returns {Object} Standardised revenue output
 */
function run(options = {}) {
  // Create a sample subscription
  const sub = createSubscription('Demo Customer', 'pro');

  // Create and collect a sample invoice
  const invoice = generateInvoice('Demo Customer', 299, 'AI Automation — Monthly Pro Package', 'due_on_receipt');
  const payment = collectPayment(invoice.invoice_id);

  const summary = revenueSummary();

  return {
    bot: 'paymentAutoCollector',
    revenue: payment.amount_usd,
    leads_generated: 1,
    conversion_rate: 1.0,
    subscription_id: sub.subscription_id,
    invoice_id: invoice.invoice_id,
    payment_id: payment.payment_id,
    mrr_usd: summary.mrr_usd,
  };
}

module.exports = {
  createSubscription,
  listSubscriptions,
  cancelSubscription,
  generateInvoice,
  listInvoices,
  collectPayment,
  revenueSummary,
  run,
  SUBSCRIPTION_PLANS,
  INVOICE_TERMS,
};
