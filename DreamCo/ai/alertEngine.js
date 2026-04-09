'use strict';

/**
 * DreamCo Alert Engine — Alerts users for best deals/jobs/flips
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

/**
 * Determine whether an opportunity should trigger an alert.
 * @param {Object} opportunity - Any opportunity with a profit/savings/revenue field
 * @param {number} minProfit - Minimum profit threshold
 * @returns {boolean}
 */
function shouldAlert(opportunity, minProfit = 10) {
  const value =
    opportunity.netProfit ??
    opportunity.profit ??
    opportunity.savings ??
    opportunity.revenue ??
    0;
  return value >= minProfit;
}

/**
 * Assign urgency level based on profit magnitude.
 * @param {Object} opportunity
 * @returns {'HIGH'|'MEDIUM'|'LOW'}
 */
function _urgency(opportunity) {
  const value =
    opportunity.netProfit ??
    opportunity.profit ??
    opportunity.savings ??
    opportunity.revenue ??
    0;
  if (value >= 100) return 'HIGH';
  if (value >= 30) return 'MEDIUM';
  return 'LOW';
}

/**
 * Filter opportunities that exceed the profit threshold and attach urgency.
 * @param {Array<Object>} opportunities
 * @param {number} [minProfit=10]
 * @returns {Array<Object>} Filtered opportunities with `urgency` attached
 */
function getAlerts(opportunities, minProfit = 10) {
  return opportunities
    .filter((o) => shouldAlert(o, minProfit))
    .map((o) => ({ ...o, urgency: _urgency(o) }));
}

/**
 * Format an opportunity as a human-readable notification string.
 * @param {Object} opportunity - Opportunity with type, name/title, store, and profit fields
 * @returns {string}
 */
function formatAlert(opportunity) {
  const name = opportunity.title || opportunity.name || 'Opportunity';
  const store = opportunity.store || opportunity.source || 'N/A';
  const profit =
    opportunity.netProfit ??
    opportunity.profit ??
    opportunity.savings ??
    opportunity.revenue ??
    0;
  const urgency = _urgency(opportunity);
  return `[${urgency}] 🔔 ${name} @ ${store} — Profit/Savings: $${parseFloat(profit).toFixed(2)}`;
}

/**
 * Get alerts filtered by type and profit threshold.
 * @param {Array<Object>} opportunities - Mixed array of opportunities
 * @param {string} type - 'deal', 'flip', 'penny', 'coupon', etc.
 * @param {number} [minProfit=10]
 * @returns {Array<Object>}
 */
function getAlertsByType(opportunities, type, minProfit = 10) {
  const filtered = opportunities.filter(
    (o) => (o.type || o.bot || '').toLowerCase().includes(type.toLowerCase()),
  );
  return getAlerts(filtered, minProfit);
}

module.exports = {
  shouldAlert,
  getAlerts,
  formatAlert,
  getAlertsByType,
};
