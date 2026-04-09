'use strict';

/**
 * DreamCo Receipt Bot
 *
 * Processes store receipts across multiple cashback apps to stack cashback
 * rewards and maximise returns.  Returns a standardised output for the
 * DreamCo Money Operating System.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const CASHBACK_APPS = {
  coinout: 0.05,
  ibotta: 0.08,
  fetch_rewards: 0.03,
  checkout51: 0.06,
  rakuten: 0.10,
};

/**
 * Process cashback opportunities for a purchase.
 * @param {string} store - Store where the purchase was made
 * @param {number} amount - Purchase amount in dollars
 * @returns {Array<Object>} Cashback opportunity objects per app
 */
function processCashback(store = 'walmart', amount = 50) {
  const safePurchase = Math.max(0, amount);
  return Object.entries(CASHBACK_APPS).map(([app, pct]) => ({
    app,
    cashback_amount: parseFloat((safePurchase * pct).toFixed(2)),
    cashback_pct: pct * 100,
    status: 'pending',
  }));
}

/**
 * Stack all cashback apps for a single purchase to get maximum return.
 * @param {string} store - Store of purchase
 * @param {number} amount - Purchase amount in dollars
 * @returns {{ total_cashback: number, breakdown: Array<Object>, original_amount: number }}
 */
function stackCashback(store = 'walmart', amount = 50) {
  const opportunities = processCashback(store, amount);
  const total_cashback = parseFloat(
    opportunities.reduce((sum, o) => sum + o.cashback_amount, 0).toFixed(2),
  );
  return {
    total_cashback,
    breakdown: opportunities,
    original_amount: amount,
  };
}

/**
 * Main bot entry point — runs a single cycle and returns revenue output.
 * @param {Object} [options]
 * @param {string} [options.store] - Store of the receipt
 * @param {number} [options.amount] - Receipt total in dollars
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const store = options.store || 'walmart';
  const amount = typeof options.amount === 'number' ? options.amount : 75;

  const stacked = stackCashback(store, amount);
  const revenue = stacked.total_cashback;

  return {
    bot: 'receiptBot',
    store,
    amount,
    revenue,
    cashback_opportunities: stacked.breakdown.length,
    action: `Processed $${amount} receipt from ${store} — stacked ${stacked.breakdown.length} cashback app(s) for $${revenue} total cashback`,
    timestamp: new Date().toISOString(),
  };
}

module.exports = {
  run,
  processCashback,
  stackCashback,
  CASHBACK_APPS,
};
