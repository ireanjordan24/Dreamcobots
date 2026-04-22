/**
 * DreamCo Control Tower — Express.js API Server
 *
 * Endpoints:
 *   POST /api/bot-heartbeat        — update bot status via heartbeat
 *   POST /api/github-webhook       — receive GitHub repository events
 *   GET  /api/bots                 — list all registered bots and their status
 *   GET  /api/get-bots             — list bots with metadata envelope
 *   GET  /api/status               — overall system health
 */

import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BOTS_FILE = path.join(__dirname, '../config/bots.json');

const app = express();
app.use(express.json());

// ---------------------------------------------------------------------------
// Simple in-process rate limiter (sliding window)
// Protects file-system endpoints from excessive reads.
// ---------------------------------------------------------------------------

const RATE_LIMIT_WINDOW_MS = 60_000; // 1 minute
const RATE_LIMIT_MAX = 60; // max requests per window per IP

const _rateLimitStore = new Map();

function rateLimiter(req, res, next) {
  const ip = req.ip || req.connection.remoteAddress || 'unknown';
  const now = Date.now();
  const entry = _rateLimitStore.get(ip) ?? { count: 0, resetAt: now + RATE_LIMIT_WINDOW_MS };

  if (now > entry.resetAt) {
    entry.count = 0;
    entry.resetAt = now + RATE_LIMIT_WINDOW_MS;
  }

  entry.count += 1;
  _rateLimitStore.set(ip, entry);

  if (entry.count > RATE_LIMIT_MAX) {
    return res.status(429).json({ error: 'Too many requests — please slow down.' });
  }

  return next();
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function readBots() {
  return JSON.parse(fs.readFileSync(BOTS_FILE, 'utf8'));
}

function writeBots(bots) {
  fs.writeFileSync(BOTS_FILE, JSON.stringify(bots, null, 2));
}

// ---------------------------------------------------------------------------
// Heartbeat endpoint
// Bots POST here to signal they are online and operational.
// ---------------------------------------------------------------------------
app.post('/api/bot-heartbeat', (req, res) => {
  const { botName, status = 'active' } = req.body;

  if (!botName) {
    return res.status(400).json({ error: 'botName is required' });
  }

  const bots = readBots();
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
        // Future: trigger auto-upgrade for dependent bots
      }
      break;
    }

    case 'issues': {
      const issue = payload.issue;
      const label = payload.label?.name;
      if (payload.action === 'labeled' && label === 'bug') {
        console.log(`  🐛 Issue #${issue?.number} labeled 'bug' — scheduling auto-fix`);
        // Future: trigger auto-heal script
      }
      break;
    }

    case 'workflow_run': {
      const wf = payload.workflow_run;
      if (wf?.conclusion === 'failure') {
        console.log(`  ❌ Workflow '${wf?.name}' failed — triggering self-heal`);
        // Future: trigger self-healing automation
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
// GET /api/bots — list all bots with current status
// ---------------------------------------------------------------------------
app.get('/api/bots', rateLimiter, (_req, res) => {
  const bots = readBots();
  return res.json(bots);
});

// ---------------------------------------------------------------------------
// GET /api/get-bots — list bots with enriched metadata envelope
// ---------------------------------------------------------------------------
app.get('/api/get-bots', rateLimiter, (_req, res) => {
  if (!fs.existsSync(BOTS_FILE)) {
    return res.status(503).json({ success: false, error: 'bots.json not found' });
  }
  let bots;
  try {
    bots = JSON.parse(fs.readFileSync(BOTS_FILE, 'utf8'));
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
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
app.get('/api/status', rateLimiter, (_req, res) => {
  const bots = readBots();
  const total = bots.length;
  const active = bots.filter((b) => b.status === 'active').length;
  const stale = bots.filter((b) => {
    if (!b.lastHeartbeat) {
      return false;
    }
    const age = Date.now() - new Date(b.lastHeartbeat).getTime();
    return age > 5 * 60 * 1000; // older than 5 minutes
  }).length;

  return res.json({
    dashboard: 'DreamCo Control Tower',
    timestamp: new Date().toISOString(),
    bots: { total, active, stale },
    health: stale > 0 ? 'degraded' : 'healthy',
  });
});

// ---------------------------------------------------------------------------
// Start server (only when not in test mode)
// ---------------------------------------------------------------------------
const PORT = process.env.PORT || 4000;
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`🚀 Control Tower API running on port ${PORT}`);
  });
}

export { app };
export default app;
