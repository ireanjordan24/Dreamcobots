/**
 * DreamCobots — Autonomous Money Operating System
 *
 * Entry point for the Node.js/Express API layer.
 * Python bots are managed via the bots/ directory.
 */

'use strict';

const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Health check
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', service: 'dreamcobots', version: '1.0.0' });
});

// Bot catalog endpoint
app.get('/bots', (_req, res) => {
  const bots = [
    { id: 'multi_source_lead_scraper', name: 'Multi-Source Lead Scraper', category: 'revenue', status: 'active' },
    { id: 'real_estate_bot', name: 'Real Estate Bot', category: 'revenue', status: 'active' },
    { id: 'crypto_bot', name: 'Crypto Bot', category: 'revenue', status: 'active' },
    { id: 'fiverr_bot', name: 'Fiverr Bot', category: 'revenue', status: 'active' },
    { id: 'deal_finder_bot', name: 'Deal Finder Bot', category: 'revenue', status: 'active' },
    { id: 'money_finder_bot', name: 'Money Finder Bot', category: 'revenue', status: 'active' },
    { id: 'affiliate_bot', name: 'Affiliate Bot', category: 'revenue', status: 'active' },
    { id: 'car_flipping_bot', name: 'Car Flipping Bot', category: 'revenue', status: 'active' },
    { id: 'software_bot', name: 'Software Bot', category: 'automation', status: 'active' },
    { id: 'job_titles_bot', name: 'Job Titles Bot', category: 'automation', status: 'active' },
    { id: 'ai_chatbot', name: 'AI Chatbot', category: 'ai', status: 'active' },
    { id: 'ai_level_up_bot', name: 'AI Level Up Bot', category: 'ai', status: 'active' },
    { id: 'bot_generator', name: 'Bot Generator', category: 'factory', status: 'active' },
    { id: 'dreamco_empire_os', name: 'DreamCo Empire OS', category: 'platform', status: 'active' },
    { id: 'government_contract_grant_bot', name: 'Government Contract & Grant Bot', category: 'revenue', status: 'active' },
  ];
  res.json({ bots, total: bots.length });
});

// Start server only when not in test mode
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`DreamCobots API running on port ${PORT}`);
  });
}

module.exports = app;
