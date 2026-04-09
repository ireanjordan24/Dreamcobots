'use strict';

/**
 * DreamCo Money OS — Main Server
 * Runs all bots automatically and exposes REST endpoints.
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const express = require('express');

const dealBot = require('./bots/dealBot');
const pennyBot = require('./bots/pennyBot');
const receiptBot = require('./bots/receiptBot');
const flipBot = require('./bots/flipBot');
const couponBot = require('./bots/couponBot');
const profitEngine = require('./ai/profitEngine');
const rankingAI = require('./ai/rankingAI');
const alertEngine = require('./ai/alertEngine');
const { ALL_SCHEMAS } = require('./firebase/schemas');

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

const REGISTERED_BOTS = [
  { name: 'dealBot', module: dealBot },
  { name: 'pennyBot', module: pennyBot },
  { name: 'receiptBot', module: receiptBot },
  { name: 'flipBot', module: flipBot },
  { name: 'couponBot', module: couponBot },
];

// ---------------------------------------------------------------------------
// Root
// ---------------------------------------------------------------------------
app.get('/', (req, res) => {
  res.json({
    name: 'DreamCo Money OS',
    version: '1.0.0',
    status: 'running',
    bots: REGISTERED_BOTS.map((b) => b.name),
  });
});

// ---------------------------------------------------------------------------
// Bots
// ---------------------------------------------------------------------------
app.get('/bots', (req, res) => {
  res.json(REGISTERED_BOTS.map((b) => ({ name: b.name })));
});

app.post('/bots/run/:botName', (req, res) => {
  try {
    const { botName } = req.params;
    const bot = REGISTERED_BOTS.find((b) => b.name === botName);
    if (!bot) {
      return res.status(404).json({ error: `Bot "${botName}" not found` });
    }
    const result = bot.module.run(req.body || {});
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ---------------------------------------------------------------------------
// Deal routes
// ---------------------------------------------------------------------------
app.get('/deals', (req, res) => {
  try {
    const store = req.query.store || 'amazon';
    const category = req.query.category || 'electronics';
    const deals = dealBot.findDeals(store, category);
    const result = dealBot.run({ store, category });
    res.json({ ...result, deals });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ---------------------------------------------------------------------------
// Flip routes
// ---------------------------------------------------------------------------
app.get('/flips', (req, res) => {
  try {
    const location = req.query.location || 'New York';
    const budget = parseFloat(req.query.budget) || 200;
    const flips = flipBot.findFlips(location, budget);
    const result = flipBot.run({ location, budget });
    res.json({ ...result, flips });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ---------------------------------------------------------------------------
// Penny deals
// ---------------------------------------------------------------------------
app.get('/penny-deals', (req, res) => {
  try {
    const store = req.query.store || 'dollar_general';
    const items = pennyBot.findPennyDeals(store);
    const result = pennyBot.run({ store });
    res.json({ ...result, items });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ---------------------------------------------------------------------------
// Cashback
// ---------------------------------------------------------------------------
app.get('/cashback', (req, res) => {
  try {
    const store = req.query.store || 'walmart';
    const amount = parseFloat(req.query.amount) || 75;
    const stacked = receiptBot.stackCashback(store, amount);
    const result = receiptBot.run({ store, amount });
    res.json({ ...result, stacked });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ---------------------------------------------------------------------------
// Coupons
// ---------------------------------------------------------------------------
app.get('/coupons', (req, res) => {
  try {
    const store = req.query.store || 'amazon';
    const product = req.query.product || 'electronics';
    const originalPrice = parseFloat(req.query.price) || 100;
    const coupons = couponBot.findCoupons(store, product);
    const stacked = couponBot.stackCoupons(coupons, originalPrice);
    const result = couponBot.run({ store, product, originalPrice });
    res.json({ ...result, coupons, stacked });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ---------------------------------------------------------------------------
// Profit calculator
// ---------------------------------------------------------------------------
app.get('/profit/:type', (req, res) => {
  try {
    const { type } = req.params;
    const query = req.query;

    let result;
    if (type === 'deal') {
      result = profitEngine.calculateDealProfit({
        originalPrice: parseFloat(query.originalPrice) || 100,
        salePrice: parseFloat(query.salePrice) || 60,
        cashbackPct: parseFloat(query.cashbackPct) || 5,
        fees: parseFloat(query.fees) || 0,
      });
    } else if (type === 'flip') {
      result = profitEngine.calculateFlipProfit(
        parseFloat(query.buyPrice) || 50,
        parseFloat(query.sellPrice) || 120,
        parseFloat(query.fees) || 10,
      );
    } else if (type === 'job') {
      result = profitEngine.calculateJobProfit(
        parseFloat(query.hourlyRate) || 25,
        parseFloat(query.hoursWorked) || 8,
        parseFloat(query.expenses) || 0,
      );
    } else if (type === 'grant') {
      result = profitEngine.calculateGrantProfit(
        parseFloat(query.grantAmount) || 5000,
        parseFloat(query.applicationCost) || 50,
      );
    } else {
      return res.status(400).json({ error: `Unknown profit type: ${type}` });
    }

    res.json({ type, ...result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ---------------------------------------------------------------------------
// Alerts
// ---------------------------------------------------------------------------
app.get('/alerts', (req, res) => {
  try {
    const minProfit = parseFloat(req.query.minProfit) || 10;
    const dealResult = dealBot.run({ store: 'amazon', category: 'electronics' });
    const flipResult = flipBot.run({ location: 'New York', budget: 200 });

    const sampleDeals = dealBot.findDeals('amazon', 'electronics').map((d) => ({
      ...d,
      type: 'deal',
      revenue: d.savings,
    }));
    const sampleFlips = flipBot.findFlips('New York', 200).map((f) => ({
      ...f,
      type: 'flip',
    }));

    const all = [...sampleDeals, ...sampleFlips];
    const alerts = alertEngine.getAlerts(all, minProfit);
    const formatted = alerts.map((a) => alertEngine.formatAlert(a));

    res.json({
      alerts_count: alerts.length,
      min_profit: minProfit,
      alerts,
      formatted,
      summary: { dealBot: dealResult, flipBot: flipResult },
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ---------------------------------------------------------------------------
// Rank
// ---------------------------------------------------------------------------
app.get('/rank', (req, res) => {
  try {
    const type = req.query.type || 'deal';
    const n = parseInt(req.query.n, 10) || 5;

    let items;
    if (type === 'flip') {
      items = flipBot.findFlips('New York', 200);
    } else {
      items = dealBot.findDeals('amazon', 'electronics');
    }

    const ranked = rankingAI.rankOpportunities(items, type);
    const top = rankingAI.getTopN(ranked, n);

    res.json({ type, total: ranked.length, top_n: n, ranked, top });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------
app.get('/schemas', (req, res) => {
  res.json(ALL_SCHEMAS);
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`🚀 DreamCo Money OS running on port ${PORT}`);
  });
}

module.exports = app;
