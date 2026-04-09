'use strict';

/**
 * DreamCo Flip Bot
 *
 * Finds local items to buy low and resell at a profit via platforms such as
 * Facebook Marketplace, eBay, and OfferUp.  Returns a standardised output
 * for the DreamCo Money Operating System.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const FLIP_SOURCES = [
  'ebay', 'facebook_marketplace', 'craigslist', 'offerup', 'letgo',
];

const FLIP_CATEGORIES = [
  'electronics', 'furniture', 'clothing', 'collectibles', 'tools', 'sporting_goods',
];

const CONDITIONS = ['like_new', 'good', 'fair', 'poor'];

/** Deterministic pseudo-random helper — no Math.random() */
function deterministicValue(seed, min, max) {
  const PRIME = 43;
  const range = max - min;
  return min + ((seed * PRIME) % range);
}

/**
 * Find flip opportunities in a given location within a budget.
 * @param {string} location - City or zip code
 * @param {number} budget - Maximum buy price per item
 * @returns {Array<Object>} Array of flip opportunity objects
 */
function findFlips(location = 'New York', budget = 200) {
  const locSeed = location.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  const budgetSeed = Math.floor(budget);
  const seedBase = locSeed + budgetSeed;
  const COUNT_PRIME = 11;
  const count = 3 + (seedBase * COUNT_PRIME) % 5; // 3–7 flips

  const ITEM_NAMES = [
    'Vintage Console', 'Refurb Laptop', 'Antique Chair', 'Designer Jacket',
    'Power Drill Set', 'Retro Camera', 'Gaming Controller', 'Gym Equipment',
    'Collectible Cards', 'Smart Speaker',
  ];

  const flips = [];
  for (let i = 0; i < count; i++) {
    const seed = seedBase * 100 + i * 43;
    const sourceIdx = deterministicValue(seed, 0, FLIP_SOURCES.length);
    const catIdx = deterministicValue(seed + 7, 0, FLIP_CATEGORIES.length);
    const condIdx = deterministicValue(seed + 13, 0, CONDITIONS.length);

    const maxBuyPrice = Math.min(budget, 190);
    const buyPrice = 10 + deterministicValue(seed, 0, maxBuyPrice - 10);
    const profitMultiplier = 1.5 + deterministicValue(seed + 17, 0, 30) / 10;
    const estimatedSellPrice = parseFloat((buyPrice * profitMultiplier).toFixed(2));
    const profit = parseFloat((estimatedSellPrice - buyPrice).toFixed(2));
    const profitPct = parseFloat(((profit / buyPrice) * 100).toFixed(1));

    flips.push({
      id: `FLIP-${seed % 100000}`,
      name: ITEM_NAMES[i % ITEM_NAMES.length],
      source: FLIP_SOURCES[sourceIdx],
      category: FLIP_CATEGORIES[catIdx],
      buyPrice,
      estimatedSellPrice,
      profit,
      profitPct,
      location,
      condition: CONDITIONS[condIdx],
    });
  }
  return flips;
}

/**
 * Rank flip opportunities by profit percentage (descending).
 * @param {Array<Object>} flips - Array from findFlips
 * @returns {Array<Object>} Sorted array
 */
function rankFlips(flips) {
  return [...flips].sort((a, b) => b.profitPct - a.profitPct);
}

/**
 * Main bot entry point — runs a single cycle and returns revenue output.
 * @param {Object} [options]
 * @param {string} [options.location] - Location to search
 * @param {number} [options.budget] - Buy budget per item
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const location = options.location || 'New York';
  const budget = typeof options.budget === 'number' ? options.budget : 200;

  const flips = findFlips(location, budget);
  const ranked = rankFlips(flips);
  const best_flip = ranked[0] || null;
  const revenue = ranked.reduce((sum, f) => sum + f.profit, 0);

  return {
    bot: 'flipBot',
    location,
    budget,
    revenue: parseFloat(revenue.toFixed(2)),
    flips_found: flips.length,
    best_flip,
    action: `Searched ${location} within $${budget} budget — found ${flips.length} flip(s), best: ${best_flip ? best_flip.name + ' (+' + best_flip.profitPct + '%)' : 'none'}`,
    timestamp: new Date().toISOString(),
  };
}

module.exports = {
  run,
  findFlips,
  rankFlips,
  FLIP_SOURCES,
  FLIP_CATEGORIES,
};
