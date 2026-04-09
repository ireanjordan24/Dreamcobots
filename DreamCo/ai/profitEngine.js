'use strict';

/**
 * DreamCo Profit Engine — Calculates profits for deals, flips, jobs, grants
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

/**
 * Calculate net profit for a deal including cashback.
 * @param {Object} deal - Deal object with salePrice, originalPrice, cashbackPct, (optional) fees
 * @returns {{ finalCost: number, savings: number, savingsPct: number, cashback: number, netProfit: number, roiPct: number }}
 */
function calculateDealProfit(deal) {
  const originalPrice = deal.originalPrice || 0;
  const salePrice = deal.salePrice || 0;
  const cashbackPct = deal.cashbackPct || 0;
  const fees = deal.fees || 0;

  const savings = parseFloat((originalPrice - salePrice).toFixed(2));
  const savingsPct = originalPrice > 0
    ? parseFloat(((savings / originalPrice) * 100).toFixed(2))
    : 0;
  const cashback = parseFloat((salePrice * (cashbackPct / 100)).toFixed(2));
  const finalCost = parseFloat((salePrice - cashback + fees).toFixed(2));
  const netProfit = parseFloat((savings + cashback - fees).toFixed(2));
  const roiPct = finalCost > 0
    ? parseFloat(((netProfit / finalCost) * 100).toFixed(2))
    : 0;

  return { finalCost, savings, savingsPct, cashback, netProfit, roiPct };
}

/**
 * Calculate profit from a buy-low sell-high flip.
 * @param {number} buyPrice - Purchase price
 * @param {number} sellPrice - Expected sell price
 * @param {number} [fees=0] - Platform fees and shipping
 * @returns {{ profit: number, profitPct: number, roi: number }}
 */
function calculateFlipProfit(buyPrice, sellPrice, fees = 0) {
  const profit = parseFloat((sellPrice - buyPrice - fees).toFixed(2));
  const profitPct = buyPrice > 0
    ? parseFloat(((profit / buyPrice) * 100).toFixed(2))
    : 0;
  const totalCost = buyPrice + fees;
  const roi = totalCost > 0
    ? parseFloat(((profit / totalCost) * 100).toFixed(2))
    : 0;

  return { profit, profitPct, roi };
}

/**
 * Calculate take-home pay from a job or gig.
 * @param {number} hourlyRate - Hourly rate in dollars
 * @param {number} hoursWorked - Hours worked
 * @param {number} [expenses=0] - Work-related expenses
 * @returns {{ grossPay: number, netPay: number, roi: number }}
 */
function calculateJobProfit(hourlyRate, hoursWorked, expenses = 0) {
  const grossPay = parseFloat((hourlyRate * hoursWorked).toFixed(2));
  const netPay = parseFloat((grossPay - expenses).toFixed(2));
  const roi = expenses > 0
    ? parseFloat(((netPay / expenses) * 100).toFixed(2))
    : null;

  return { grossPay, netPay, roi };
}

/**
 * Calculate net benefit from a grant or legal payout.
 * @param {number} grantAmount - Total grant / payout amount
 * @param {number} [applicationCost=0] - Cost to apply or legal fees
 * @returns {{ netProfit: number, roi: number }}
 */
function calculateGrantProfit(grantAmount, applicationCost = 0) {
  const netProfit = parseFloat((grantAmount - applicationCost).toFixed(2));
  const roi = applicationCost > 0
    ? parseFloat(((netProfit / applicationCost) * 100).toFixed(2))
    : null;

  return { netProfit, roi };
}

/**
 * Run profit calculations for an array of items of a given type.
 * @param {Array<Object>} items - Array of deal / flip / job / grant objects
 * @param {'deal'|'flip'|'job'|'grant'} type - Calculation type
 * @returns {Array<Object>} Array of profit calculation results
 */
function batchCalculate(items, type) {
  return items.map((item) => {
    switch (type) {
      case 'deal':
        return { item, profit: calculateDealProfit(item) };
      case 'flip':
        return {
          item,
          profit: calculateFlipProfit(item.buyPrice, item.estimatedSellPrice || item.sellPrice, item.fees),
        };
      case 'job':
        return {
          item,
          profit: calculateJobProfit(item.hourlyRate, item.hoursWorked, item.expenses),
        };
      case 'grant':
        return {
          item,
          profit: calculateGrantProfit(item.grantAmount, item.applicationCost),
        };
      default:
        return { item, profit: null, error: `Unknown type: ${type}` };
    }
  });
}

module.exports = {
  calculateDealProfit,
  calculateFlipProfit,
  calculateJobProfit,
  calculateGrantProfit,
  batchCalculate,
};
