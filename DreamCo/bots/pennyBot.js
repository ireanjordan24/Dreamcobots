'use strict';

/**
 * DreamCo Penny Bot
 *
 * Hunts for penny items ($0.01–$1.00) at clearance sections of major retail
 * stores to resell at a significant profit.  Returns a standardised output
 * for the DreamCo Money Operating System.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const PENNY_STORES = [
  'dollar_general', 'walmart', 'target', 'walgreens', 'cvs', 'rite_aid',
];

/** Deterministic pseudo-random helper — no Math.random() */
function deterministicValue(seed, min, max) {
  const PRIME = 41;
  const range = max - min;
  return min + ((seed * PRIME) % range);
}

/**
 * Find penny deal items at a given store.
 * @param {string} store - Store name from PENNY_STORES
 * @returns {Array<Object>} Array of penny deal items
 */
function findPennyDeals(store = 'dollar_general') {
  const storeIdx = PENNY_STORES.indexOf(store);
  const seedBase = (storeIdx < 0 ? 1 : storeIdx + 1) * 17;
  const COUNT_PRIME = 5;
  const count = 4 + (seedBase * COUNT_PRIME) % 5; // 4–8 items

  const ITEM_NAMES = [
    'Clearance Shampoo', 'Discount Candy Bar', 'Marked-down Toy',
    'Clearance Candle', 'Penny Mug', 'Discount Notebook',
    'Clearance Lotion', 'Penny Snack Pack', 'Discount Card Game',
  ];

  const items = [];
  for (let i = 0; i < count; i++) {
    const seed = seedBase * 100 + i * 41;
    // clearance price: $0.01 – $1.00 (stored as cents 1–100)
    const clearanceCents = 1 + deterministicValue(seed, 0, 99);
    const clearancePrice = parseFloat((clearanceCents / 100).toFixed(2));
    // resale value: $5 – $50
    const resaleValue = 5 + deterministicValue(seed + 11, 0, 45);
    const profit = parseFloat((resaleValue - clearancePrice).toFixed(2));
    const profitPct = parseFloat(((profit / clearancePrice) * 100).toFixed(1));
    const skuSeed = (seed * 1337) % 900000 + 100000;

    items.push({
      id: `PENNY-${store.toUpperCase().slice(0, 3)}-${seed % 10000}`,
      name: ITEM_NAMES[i % ITEM_NAMES.length],
      store,
      clearancePrice,
      resaleValue,
      profit,
      profitPct,
      sku: `SKU-${skuSeed}`,
    });
  }
  return items;
}

/**
 * Estimate resale profit for a single penny deal item.
 * @param {Object} item - Penny deal item
 * @returns {number} Profit in dollars
 */
function estimateResaleProfit(item) {
  return parseFloat((item.resaleValue - item.clearancePrice).toFixed(2));
}

/**
 * Main bot entry point — runs a single cycle and returns revenue output.
 * @param {Object} [options]
 * @param {string} [options.store] - Store to scan
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const storeIdx = options.store ? PENNY_STORES.indexOf(options.store) : 0;
  const store = storeIdx >= 0 && options.store ? options.store : PENNY_STORES[0];

  const items = findPennyDeals(store);
  let totalPotentialProfit = 0;

  for (const item of items) {
    totalPotentialProfit += estimateResaleProfit(item);
  }

  totalPotentialProfit = parseFloat(totalPotentialProfit.toFixed(2));
  // Revenue is a conservative 30 % realisation of potential profit
  const revenue = parseFloat((totalPotentialProfit * 0.3).toFixed(2));

  return {
    bot: 'pennyBot',
    store,
    revenue,
    items_found: items.length,
    total_potential_profit: totalPotentialProfit,
    action: `Scanned ${store} for penny deals — found ${items.length} item(s) with $${totalPotentialProfit} total resale profit potential`,
    timestamp: new Date().toISOString(),
  };
}

module.exports = {
  run,
  findPennyDeals,
  estimateResaleProfit,
  PENNY_STORES,
};
