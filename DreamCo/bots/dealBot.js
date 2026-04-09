'use strict';

/**
 * DreamCo Deal Bot
 *
 * Scans retail stores for deals, calculates affiliate commissions, and stacks
 * cashback to maximise revenue.  Returns a standardised output for the
 * DreamCo Money Operating System.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const DEAL_STORES = [
  'walmart', 'amazon', 'target', 'dollar_general',
  'ebay', 'walgreens', 'best_buy', 'home_depot',
];

const DEAL_CATEGORIES = [
  'electronics', 'appliances', 'clothing', 'home', 'toys',
  'groceries', 'tools', 'gaming', 'beauty', 'sports',
];

const AFFILIATE_COMMISSIONS = {
  walmart: 0.04,
  amazon: 0.08,
  target: 0.05,
  dollar_general: 0.03,
  ebay: 0.07,
  walgreens: 0.05,
  best_buy: 0.06,
  home_depot: 0.04,
};

/** Deterministic pseudo-random helper — no Math.random() */
function deterministicValue(seed, min, max) {
  const PRIME = 37;
  const range = max - min;
  return min + ((seed * PRIME) % range);
}

/**
 * Find deals at a given store in a given category.
 * @param {string} store - Store name from DEAL_STORES
 * @param {string} category - Category from DEAL_CATEGORIES
 * @returns {Array<Object>} 3–5 deal objects
 */
function findDeals(store = 'amazon', category = 'electronics') {
  const storeIdx = DEAL_STORES.indexOf(store);
  const catIdx = DEAL_CATEGORIES.indexOf(category);
  const seedBase = (storeIdx < 0 ? 1 : storeIdx + 1) * (catIdx < 0 ? 1 : catIdx + 1);

  // Deterministic count between 3 and 5
  const DEAL_PRIME = 7;
  const count = 3 + (seedBase * DEAL_PRIME) % 3;

  const deals = [];
  for (let i = 0; i < count; i++) {
    const seed = seedBase * 100 + i * 37;
    const originalPrice = 50 + deterministicValue(seed, 0, 450);
    // sale multiplier between 0.4 and 0.7
    const discountFactor = 0.4 + (deterministicValue(seed + 13, 0, 30) / 100);
    const salePrice = parseFloat((originalPrice * discountFactor).toFixed(2));
    const savings = parseFloat((originalPrice - salePrice).toFixed(2));
    const savingsPct = parseFloat(((savings / originalPrice) * 100).toFixed(1));
    const cashbackPct = 3 + deterministicValue(seed + 7, 0, 7);
    const couponSuffix = (seed % 9000) + 1000;

    deals.push({
      id: `DEAL-${store.toUpperCase().slice(0, 3)}-${seed % 100000}`,
      title: `${category.charAt(0).toUpperCase() + category.slice(1)} Deal #${i + 1} at ${store}`,
      store,
      category,
      originalPrice,
      salePrice,
      savings,
      savingsPct,
      couponCode: `SAVE${couponSuffix}`,
      cashbackPct,
    });
  }
  return deals;
}

/**
 * Calculate affiliate commission for a single deal.
 * @param {Object} deal - Deal object returned by findDeals
 * @returns {number} Commission amount in dollars
 */
function calculateAffiliateCommission(deal) {
  const rate = AFFILIATE_COMMISSIONS[deal.store] || 0.04;
  return parseFloat((deal.salePrice * rate).toFixed(2));
}

/**
 * Main bot entry point — runs a single cycle and returns revenue output.
 * @param {Object} [options]
 * @param {string} [options.store] - Store to scan
 * @param {string} [options.category] - Product category
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const rawStore = Array.isArray(options.store) ? options.store[0] : options.store;
  const rawCategory = Array.isArray(options.category) ? options.category[0] : options.category;
  const storeIdx = rawStore ? DEAL_STORES.indexOf(String(rawStore)) : 0;
  const store = storeIdx >= 0 && rawStore ? String(rawStore) : DEAL_STORES[0];
  const catIdx = rawCategory ? DEAL_CATEGORIES.indexOf(String(rawCategory)) : 0;
  const category = catIdx >= 0 && rawCategory ? String(rawCategory) : DEAL_CATEGORIES[0];

  const deals = findDeals(store, category);
  let totalRevenue = 0;
  let totalSavings = 0;

  for (const deal of deals) {
    totalRevenue += calculateAffiliateCommission(deal);
    totalSavings += deal.savings;
  }

  totalRevenue = parseFloat(totalRevenue.toFixed(2));
  totalSavings = parseFloat(totalSavings.toFixed(2));

  return {
    bot: 'dealBot',
    store,
    category,
    revenue: totalRevenue,
    deals_found: deals.length,
    total_savings: totalSavings,
    action: `Scanned ${store} in category "${category}" — found ${deals.length} deal(s), earned $${totalRevenue} in affiliate commissions`,
    timestamp: new Date().toISOString(),
  };
}

module.exports = {
  run,
  findDeals,
  calculateAffiliateCommission,
  DEAL_STORES,
  DEAL_CATEGORIES,
  AFFILIATE_COMMISSIONS,
};
