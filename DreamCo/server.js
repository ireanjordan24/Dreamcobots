'use strict';

const express = require('express');
const dealBot = require('./bots/dealBot');
const pennyBot = require('./bots/pennyBot');
const receiptBot = require('./bots/receiptBot');
const flipBot = require('./bots/flipBot');
const couponBot = require('./bots/couponBot');
const profitEngine = require('./ai/profitEngine');
const rankingAI = require('./ai/rankingAI');
const alertEngine = require('./ai/alertEngine');
const SCHEMAS = require('./firebase/schemas');

const app = express();
app.use(express.json());

// 1. GET /deals
app.get('/deals', (req, res) => {
  const { minProfit = 10, limit = 10 } = req.query;
  res.json(dealBot.run({ minProfit: parseFloat(minProfit), limit: parseInt(limit, 10) }));
});

// 2. GET /flips
app.get('/flips', (req, res) => {
  const { minProfit = 20, city = 'Local' } = req.query;
  res.json(flipBot.run({ minProfit: parseFloat(minProfit), city }));
});

// 3. GET /penny-deals
app.get('/penny-deals', (req, res) => {
  const { threshold = 1.00 } = req.query;
  res.json(pennyBot.run({ threshold: parseFloat(threshold) }));
});

// 4. GET /cashback
app.get('/cashback', (req, res) => {
  const { items } = req.query;
  const itemList = items ? items.split(',') : [];
  res.json(receiptBot.run({ items: itemList }));
});

// 5. GET /coupons
app.get('/coupons', (req, res) => {
  const { sources } = req.query;
  const sourceList = sources ? sources.split(',') : ['Honey', 'Rakuten', 'Ibotta'];
  res.json(couponBot.run({ sources: sourceList }));
});

// 6. GET /alerts
app.get('/alerts', (req, res) => {
  const { minUrgency = 'LOW' } = req.query;
  const deals = dealBot.run({ minProfit: 5, limit: 20 }).deals;
  const alerts = alertEngine.filterAlerts(deals, minUrgency);
  res.json({ alerts, count: alerts.length, timestamp: new Date().toISOString() });
});

// 7. GET /rank
app.get('/rank', (req, res) => {
  const { n = 10 } = req.query;
  const deals = dealBot.run({ minProfit: 0, limit: 50 }).deals;
  res.json({ ranked: rankingAI.topN(deals, parseInt(n, 10)), timestamp: new Date().toISOString() });
});

// 8. GET /schemas
app.get('/schemas', (req, res) => {
  res.json(SCHEMAS);
});

// 9. POST /profit
app.post('/profit', (req, res) => {
  const deal = req.body;
  res.json(profitEngine.calculateDeal(deal));
});

// 10. POST /profit/flip
app.post('/profit/flip', (req, res) => {
  const { buyPrice, sellPrice, feesPct } = req.body;
  res.json(profitEngine.calculateFlip(parseFloat(buyPrice), parseFloat(sellPrice), feesPct ? parseFloat(feesPct) : undefined));
});

// 11. GET /health
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'DreamCo Money OS', timestamp: new Date().toISOString() });
});

// 12. GET /stack
app.get('/stack', (req, res) => {
  const { minProfit = 10 } = req.query;
  const mp = parseFloat(minProfit);
  const deals = dealBot.run({ minProfit: mp, limit: 20 }).deals;
  const pennies = pennyBot.run({}).pennyDeals;
  const coupons = couponBot.run({}).coupons;
  const ranked = rankingAI.topN([...deals, ...pennies], 10);
  const alerts = alertEngine.filterAlerts(ranked);
  const totalRevenue = ranked.reduce((s, d) => s + parseFloat(d.profit || d.revenue || 0), 0);
  res.json({
    deals,
    penny_deals: pennies,
    coupons,
    ranked,
    alerts,
    estimated_daily_profit: Math.round(totalRevenue * 100) / 100,
    timestamp: new Date().toISOString(),
  });
});

// 13. GET /bots
app.get('/bots', (req, res) => {
  res.json({
    bots: ['dealBot', 'pennyBot', 'receiptBot', 'flipBot', 'couponBot'],
    ai: ['profitEngine', 'rankingAI', 'alertEngine'],
    version: '1.0.0',
  });
});

const PORT = process.env.PORT || 3001;

if (require.main === module) {
  app.listen(PORT, () => console.log(`DreamCo Money OS API running on port ${PORT}`));
}

module.exports = app;
