'use strict';

/**
 * DreamCo Ranking AI — Ranks opportunities by profit, ease, payout speed
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

/** Store-level trust/ease scores (0–10) */
const STORE_SCORES = {
  amazon: 9, walmart: 8, target: 8, ebay: 7,
  best_buy: 7, home_depot: 6, walgreens: 6,
  dollar_general: 5, default: 5,
};

/** Source-level ease scores for flips (0–10) */
const SOURCE_EASE_SCORES = {
  facebook_marketplace: 9, craigslist: 7, offerup: 8,
  letgo: 7, ebay: 6, default: 5,
};

/**
 * Score a deal opportunity 0–100.
 * Formula: savingsPct * 0.4 + (cashbackPct * 10) * 0.3 + store_score * 10 * 0.3
 * @param {Object} deal - Deal object with savingsPct, cashbackPct, store
 * @returns {number} Score 0–100
 */
function scoreDeal(deal) {
  const savingsPct = deal.savingsPct || 0;
  const cashbackPct = deal.cashbackPct || 0;
  const storeScore = STORE_SCORES[deal.store] || STORE_SCORES.default;

  const raw =
    savingsPct * 0.4 +
    cashbackPct * 10 * 0.3 +
    storeScore * 10 * 0.3;

  return Math.min(100, Math.max(0, parseFloat(raw.toFixed(2))));
}

/**
 * Score a flip opportunity 0–100.
 * Formula: profitPct * 0.5 + ease_score * 10 * 0.5
 * @param {Object} flip - Flip object with profitPct, source
 * @returns {number} Score 0–100
 */
function scoreFlip(flip) {
  const profitPct = flip.profitPct || 0;
  const easeScore = SOURCE_EASE_SCORES[flip.source] || SOURCE_EASE_SCORES.default;

  const raw = profitPct * 0.5 + easeScore * 10 * 0.5;

  return Math.min(100, Math.max(0, parseFloat(raw.toFixed(2))));
}

/**
 * Rank an array of opportunities by score (descending).
 * @param {Array<Object>} items - Deals or flips
 * @param {'deal'|'flip'} type - Scoring type
 * @returns {Array<Object>} Items with `score` attached, sorted descending
 */
function rankOpportunities(items, type) {
  const scored = items.map((item) => {
    const score = type === 'flip' ? scoreFlip(item) : scoreDeal(item);
    return { ...item, score };
  });
  return scored.sort((a, b) => b.score - a.score);
}

/**
 * Return the top N ranked opportunities.
 * @param {Array<Object>} items - Pre-ranked or unranked items
 * @param {number} n - How many to return
 * @returns {Array<Object>} Top N items
 */
function getTopN(items, n) {
  const sorted = [...items].sort((a, b) => (b.score || 0) - (a.score || 0));
  return sorted.slice(0, n);
}

module.exports = {
  scoreDeal,
  scoreFlip,
  rankOpportunities,
  getTopN,
  STORE_SCORES,
  SOURCE_EASE_SCORES,
};
