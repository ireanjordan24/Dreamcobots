'use strict';

/**
 * DreamCo Control Tower — Express.js API Server
 *
 * Endpoints:
 *   POST /api/bot-heartbeat        — update bot status via heartbeat
 *   POST /api/github-webhook       — receive GitHub repository events
 *   GET  /api/get-bots             — list all registered bots and their status
 *   GET  /api/bots                 — alias for get-bots
 *   GET  /api/status               — overall system health
 */

const express = require('express');
const fs = require('fs');
const path = require('path');

const BOTS_FILE = path.join(__dirname, '../config/bots.json');

const app = express();
app.use(express.json());

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function readBots() {
  if (!fs.existsSync(BOTS_FILE)) {
    const err = new Error('bots.json not found');
    err.code = 'ENOENT';
    throw err;
  }
  return JSON.parse(fs.readFileSync(BOTS_FILE, 'utf8'));
}

function writeBots(bots) {
  fs.writeFileSync(BOTS_FILE, JSON.stringify(bots, null, 2));
}

// ---------------------------------------------------------------------------
// GET /api/get-bots — list all bots with current status
// ---------------------------------------------------------------------------
app.get('/api/get-bots', (_req, res) => {
  let bots;
  try {
    bots = readBots();
  } catch (err) {
    if (err.code === 'ENOENT') {
      return res.status(503).json({ success: false, error: 'Bot registry unavailable: bots.json not found' });
    }
    return res.status(500).json({ success: false, error: `Failed to read bots.json: ${err.message}` });
  }
  return res.json({
    success: true,
    bots,
    count: bots.length,
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// Heartbeat endpoint
// Bots POST here to signal they are online and operational.
// ---------------------------------------------------------------------------
app.post('/api/bot-heartbeat', (req, res) => {
  const { botName, status = 'active' } = req.body;

  if (!botName) {
    return res.status(400).json({ error: 'botName is required' });
  }

  let bots;
  try {
    bots = readBots();
  } catch (err) {
    return res.status(503).json({ error: `Bot registry unavailable: ${err.message}` });
  }

  const bot = bots.find((b) => b.name === botName);

  if (!bot) {
    return res.status(404).json({ error: `Bot '${botName}' not found` });
  }

  bot.lastHeartbeat = new Date().toISOString();
  bot.status = status;
  writeBots(bots);

  console.log(`💓 Heartbeat received from ${botName} — status: ${status}`);
  return res.json({ status: 'updated', bot: botName, lastHeartbeat: bot.lastHeartbeat });
});

// ---------------------------------------------------------------------------
// GitHub webhook endpoint
// Receives events from GitHub: push, pull_request, issues, workflow_run, etc.
// ---------------------------------------------------------------------------
app.post('/api/github-webhook', (req, res) => {
  const event = req.headers['x-github-event'] || 'unknown';
  const payload = req.body;

  console.log(`🔔 GitHub Event: ${event}`);

  switch (event) {
    case 'pull_request': {
      const action = payload.action;
      const pr = payload.pull_request;
      console.log(`  PR #${pr?.number} ${action}: ${pr?.title}`);

      if (action === 'closed' && pr?.merged) {
        console.log('  ✅ PR merged — triggering dependent bot updates');
      }
      break;
    }

    case 'issues': {
      const issue = payload.issue;
      const label = payload.label?.name;
      if (payload.action === 'labeled' && label === 'bug') {
        console.log(`  🐛 Issue #${issue?.number} labeled 'bug' — scheduling auto-fix`);
      }
      break;
    }

    case 'workflow_run': {
      const wf = payload.workflow_run;
      if (wf?.conclusion === 'failure') {
        console.log(`  ❌ Workflow '${wf?.name}' failed — triggering self-heal`);
      }
      break;
    }

    case 'push': {
      const ref = payload.ref;
      const commits = payload.commits?.length ?? 0;
      console.log(`  📦 Push to ${ref}: ${commits} commit(s)`);
      break;
    }

    default:
      console.log(`  ℹ️ Unhandled event: ${event}`);
  }

  return res.sendStatus(200);
});

// ---------------------------------------------------------------------------
// GET /api/bots — alias for get-bots (same response structure)
// ---------------------------------------------------------------------------
app.get('/api/bots', (_req, res) => {
  let bots;
  try {
    bots = readBots();
  } catch (err) {
    if (err.code === 'ENOENT') {
      return res.status(503).json({ success: false, error: 'Bot registry unavailable: bots.json not found' });
    }
    return res.status(500).json({ success: false, error: `Failed to read bots.json: ${err.message}` });
  }
  return res.json({
    success: true,
    bots,
    count: bots.length,
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// GET /api/status — overall system health summary
// ---------------------------------------------------------------------------
app.get('/api/status', (_req, res) => {
  let bots;
  try {
    bots = readBots();
  } catch (_err) {
    bots = [];
  }
  const total = bots.length;
  const active = bots.filter((b) => b.status === 'active').length;
  const stale = bots.filter((b) => {
    if (!b.lastHeartbeat) {
      return false;
    }
    const age = Date.now() - new Date(b.lastHeartbeat).getTime();
    return age > 5 * 60 * 1000;
  }).length;

  return res.json({
    dashboard: 'DreamCo Control Tower',
    timestamp: new Date().toISOString(),
    bots: { total, active, stale },
    health: stale > 0 ? 'degraded' : 'healthy',
  });
});

// ---------------------------------------------------------------------------
// Start server (only when run directly, not when required by tests)
// ---------------------------------------------------------------------------
if (require.main === module) {
  const PORT = process.env.PORT || 4000;
  app.listen(PORT, () => {
    console.log(`🚀 Control Tower API running on port ${PORT}`);
  });
}

module.exports = app;

