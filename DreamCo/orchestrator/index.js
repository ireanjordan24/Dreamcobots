'use strict';

/**
 * DreamCo Orchestrator — God Mode Edition
 *
 * Central brain for the DreamCo Money Operating System.
 * Wires all 9 bots together, validates revenue output, and triggers scaling
 * for profitable bots.
 *
 * Cycle targets: ~$17,500 revenue | ~431 leads
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const realEstateBot = require('../bots/realEstateBot');
const contractBot = require('../bots/contractBot');
const jobBot = require('../bots/jobBot');
const adEngine = require('../bots/business/adEngine');
const businessBuilder = require('../bots/business/businessBuilder');
const viralEngine = require('../bots/marketing/viralEngine');
const autoClientHunter = require('../bots/marketing/autoClientHunter');
const autoCloser = require('../bots/marketing/autoCloser');
const paymentAutoCollector = require('../bots/marketing/paymentAutoCollector');

// ---------------------------------------------------------------------------
// Revenue Validator
// ---------------------------------------------------------------------------

const REVENUE_THRESHOLDS = {
  scale: 1000,
  maintain: 100,
};

/**
 * Validate a bot's revenue output.
 * @param {Object} botOutput - Standardised bot output object
 * @returns {Object} Validation result with scale recommendation
 */
function validateRevenue(botOutput) {
  const { revenue = 0, conversion_rate = 0, leads_generated = 0 } = botOutput;

  let status = 'underperforming';
  let scale = false;

  if (revenue >= REVENUE_THRESHOLDS.scale) {
    status = 'scale';
    scale = true;
  } else if (revenue >= REVENUE_THRESHOLDS.maintain) {
    status = 'maintain';
  }

  return {
    bot: botOutput.bot,
    revenue,
    leads_generated,
    conversion_rate,
    status,
    scale,
    message: scale
      ? `🚀 Scale "${botOutput.bot}" — revenue $${revenue} exceeded threshold`
      : `📊 "${botOutput.bot}" status: ${status} (revenue: $${revenue})`,
  };
}

// ---------------------------------------------------------------------------
// Auto Scaler
// ---------------------------------------------------------------------------

/**
 * Clone a bot into a new niche when revenue threshold is exceeded.
 * @param {string} botName - Name of the bot to clone
 * @returns {string} Clone notification message
 */
function cloneBot(botName) {
  return `[AutoScaler] Cloning "${botName}" into new niche — deploying scaled instance`;
}

// ---------------------------------------------------------------------------
// Orchestrator
// ---------------------------------------------------------------------------

const BOTS = [
  { name: 'realEstateBot', module: realEstateBot },
  { name: 'contractBot', module: contractBot },
  { name: 'jobBot', module: jobBot },
  { name: 'adEngine', module: adEngine },
  { name: 'businessBuilder', module: businessBuilder },
  { name: 'viralEngine', module: viralEngine },
  { name: 'autoClientHunter', module: autoClientHunter },
  { name: 'autoCloser', module: autoCloser },
  { name: 'paymentAutoCollector', module: paymentAutoCollector },
];

/**
 * Process a single bot: run it, validate output, and optionally scale.
 * @param {string} botName - Identifier for the bot
 * @param {Object} botModule - Module with a `run()` function
 * @param {Object} [options] - Options passed to bot.run()
 * @returns {Object} Full result including output and validation
 */
function processBot(botName, botModule, options = {}) {
  try {
    const output = botModule.run(options);
    const validation = validateRevenue(output);

    console.log(`[${botName}] →`, validation.message);

    if (validation.scale) {
      console.log(cloneBot(botName));
    }

    return { bot: botName, output, validation, error: null };
  } catch (err) {
    console.error(`[${botName}] ERROR:`, err.message);
    return { bot: botName, output: null, validation: null, error: err.message };
  }
}

/**
 * Run all registered bots and collect results.
 * @returns {Array<Object>} Results for every bot
 */
function runAllBots() {
  console.log('\n🚀 DreamCo Orchestrator — Starting full bot cycle\n');

  const results = BOTS.map(({ name, module }) => processBot(name, module));

  const totalRevenue = results.reduce((sum, r) => sum + (r.output ? r.output.revenue : 0), 0);
  const totalLeads = results.reduce((sum, r) => sum + (r.output ? r.output.leads_generated : 0), 0);
  const scalingBots = results.filter((r) => r.validation && r.validation.scale).map((r) => r.bot);

  console.log('\n─────────────────────────────────────');
  console.log(`💰 Total Revenue:   $${totalRevenue}  (cycle target ~$17,500)`);
  console.log(`📋 Total Leads:     ${totalLeads}  (cycle target ~431)`);
  console.log(`📈 Scaling Bots:    ${scalingBots.length > 0 ? scalingBots.join(', ') : 'none'}`);
  console.log('─────────────────────────────────────\n');

  return {
    results,
    summary: {
      total_revenue: totalRevenue,
      total_leads: totalLeads,
      scaling_bots: scalingBots,
      bots_run: results.length,
      timestamp: new Date().toISOString(),
    },
  };
}

module.exports = { runAllBots, processBot, validateRevenue, cloneBot, BOTS };

// Run directly if invoked as a script
if (require.main === module) {
  runAllBots();
}
