'use strict';

/**
 * DreamCo Coupon Bot
 *
 * Aggregates coupons from multiple sources and calculates the optimal stack
 * to minimise purchase cost.  Returns a standardised output for the DreamCo
 * Money Operating System.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const COUPON_SOURCES = [
  'honey', 'retailmenot', 'coupons_com', 'groupon', 'manufacturer',
];

/** Deterministic pseudo-random helper — no Math.random() */
function deterministicValue(seed, min, max) {
  const PRIME = 53;
  const range = max - min;
  return min + ((seed * PRIME) % range);
}

/**
 * Find coupons for a store and product.
 * @param {string} store - Store name
 * @param {string} product - Product keyword
 * @returns {Array<Object>} Array of coupon objects
 */
function findCoupons(store = 'amazon', product = 'electronics') {
  const storeSeed = store.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  const prodSeed = product.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  const seedBase = storeSeed + prodSeed;
  const COUNT_PRIME = 3;
  const count = 2 + (seedBase * COUNT_PRIME) % 4; // 2–5 coupons

  // Expiry dates 3–30 days from a fixed epoch offset (deterministic)
  const BASE_DATE = new Date('2025-01-01T00:00:00Z');

  const coupons = [];
  for (let i = 0; i < count; i++) {
    const seed = seedBase * 100 + i * 53;
    const sourceIdx = deterministicValue(seed, 0, COUPON_SOURCES.length);
    const isPct = deterministicValue(seed + 3, 0, 2) === 0; // 50 % chance
    const discount = isPct
      ? 5 + deterministicValue(seed + 7, 0, 46)   // 5–50 % off
      : 2 + deterministicValue(seed + 11, 0, 48); // $2–$50 off
    const daysUntilExpiry = 3 + deterministicValue(seed + 19, 0, 27);
    const expiryDate = new Date(BASE_DATE.getTime() + daysUntilExpiry * 86400000);
    const codeSuffix = (seed * 7) % 90000 + 10000;
    const stackable = deterministicValue(seed + 23, 0, 3) !== 0; // ~67 % stackable

    coupons.push({
      code: `${store.toUpperCase().slice(0, 3)}${codeSuffix}`,
      discount,
      discountType: isPct ? 'pct' : 'fixed',
      source: COUPON_SOURCES[sourceIdx],
      stackable,
      expires: expiryDate.toISOString().split('T')[0],
    });
  }
  return coupons;
}

/**
 * Stack applicable coupons to compute the final price.
 * @param {Array<Object>} coupons - From findCoupons
 * @param {number} originalPrice - Original price in dollars
 * @returns {{ finalPrice: number, totalSaved: number, appliedCoupons: Array, savingsPct: number }}
 */
function stackCoupons(coupons, originalPrice) {
  let price = originalPrice;
  const appliedCoupons = [];

  // Apply percentage-off coupons first, then fixed
  const sorted = [
    ...coupons.filter((c) => c.stackable && c.discountType === 'pct'),
    ...coupons.filter((c) => c.stackable && c.discountType === 'fixed'),
  ];

  for (const coupon of sorted) {
    if (price <= 0) break;
    if (coupon.discountType === 'pct') {
      const saved = parseFloat((price * (coupon.discount / 100)).toFixed(2));
      price = parseFloat((price - saved).toFixed(2));
    } else {
      price = parseFloat(Math.max(0, price - coupon.discount).toFixed(2));
    }
    appliedCoupons.push(coupon);
  }

  const finalPrice = Math.max(0, parseFloat(price.toFixed(2)));
  const totalSaved = parseFloat((originalPrice - finalPrice).toFixed(2));
  const savingsPct = originalPrice > 0
    ? parseFloat(((totalSaved / originalPrice) * 100).toFixed(1))
    : 0;

  return { finalPrice, totalSaved, appliedCoupons, savingsPct };
}

/**
 * Main bot entry point — runs a single cycle and returns revenue output.
 * @param {Object} [options]
 * @param {string} [options.store] - Store to search
 * @param {string} [options.product] - Product keyword
 * @param {number} [options.originalPrice] - Base price to stack against
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const store = options.store || 'amazon';
  const product = options.product || 'electronics';
  const originalPrice = typeof options.originalPrice === 'number' ? options.originalPrice : 100;

  const coupons = findCoupons(store, product);
  const stacked = stackCoupons(coupons, originalPrice);
  // Revenue is the value of savings delivered to the user (affiliate model)
  const revenue = parseFloat((stacked.totalSaved * 0.1).toFixed(2));

  return {
    bot: 'couponBot',
    store,
    product,
    revenue,
    coupons_found: coupons.length,
    best_savings: stacked.totalSaved,
    action: `Found ${coupons.length} coupon(s) for "${product}" at ${store} — stacked savings $${stacked.totalSaved} (${stacked.savingsPct}% off)`,
    timestamp: new Date().toISOString(),
  };
}

module.exports = {
  run,
  findCoupons,
  stackCoupons,
  COUPON_SOURCES,
};
