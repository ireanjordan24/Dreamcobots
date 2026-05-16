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
  // Skip rate limiting in test environment
  if (process.env.NODE_ENV === 'test') return next();

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
// GET /api/actions — live GitHub Actions workflow runs (read-only)
//
// Fetches the most recent workflow runs from the GitHub REST API.
// Requires the GITHUB_TOKEN env variable for authenticated requests.
// Gracefully degrades when the token is absent or the API is unreachable.
// ---------------------------------------------------------------------------

const GITHUB_API_BASE = 'https://api.github.com';
const DEFAULT_REPO = process.env.GITHUB_REPO || 'DreamCo-Technologies/Dreamcobots';
const ACTIONS_PER_PAGE = 10;

async function fetchGitHubWorkflowRuns(repo, token) {
  const { default: https } = await import('https');
  return new Promise((resolve) => {
    const headers = {
      'User-Agent': 'dreamco-control-tower',
      Accept: 'application/vnd.github+json',
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const url = new URL(
      `/repos/${repo}/actions/runs?per_page=${ACTIONS_PER_PAGE}`,
      GITHUB_API_BASE,
    );
    const req = https.get(
      { hostname: url.hostname, path: url.pathname + url.search, headers },
      (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          try {
            const json = JSON.parse(body);
            const runs = (json.workflow_runs ?? []).map((r) => ({
              id: r.id,
              name: r.name,
              status: r.status,
              conclusion: r.conclusion,
              branch: r.head_branch,
              event: r.event,
              run_started_at: r.run_started_at,
              url: r.html_url,
            }));
            resolve({ runs, source: 'github_api' });
          } catch {
            resolve({ runs: [], source: 'parse_error' });
          }
        });
      },
    );
    req.on('error', () => resolve({ runs: [], source: 'unavailable' }));
    req.setTimeout(5000, () => {
      req.destroy();
      resolve({ runs: [], source: 'timeout' });
    });
  });
}

app.get('/api/actions', rateLimiter, async (req, res) => {
  const token = process.env.GITHUB_TOKEN || '';
  const result = await fetchGitHubWorkflowRuns(DEFAULT_REPO, token);
  return res.json({
    repo: DEFAULT_REPO,
    ...result,
    fetched_at: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// GET /api/catalog — bot catalog for the marketplace UI
//
// Returns the list of bots from bots.json enriched with metadata useful for
// the build-a-bot marketplace (tier, pricing, features).
// ---------------------------------------------------------------------------

app.get('/api/catalog', rateLimiter, (_req, res) => {
  const bots = readBots();
  const catalog = bots.map((b) => ({
    bot_id: b.name.replace(/-/g, '_'),
    display_name: b.name
      .split('-')
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' '),
    category: b.category || 'General',
    tier: b.tier || 'FREE',
    description: b.description || '',
    price_usd: b.price_usd ?? 0,
    features: b.features || [],
    is_live: b.status === 'active',
  }));
  return res.json(catalog);
});

// ---------------------------------------------------------------------------
// GET /api/orchestrator — BuddyOrchestrator health snapshot
//
// Returns a lightweight status payload showing scraping deadline, catalog
// size, and system health.  Does not expose sensitive data.
// ---------------------------------------------------------------------------

app.get('/api/orchestrator', rateLimiter, (_req, res) => {
  const bots = readBots();
  const deadline = '2026-06-22';
  const today = new Date();
  const deadlineDate = new Date(deadline);
  const daysRemaining = Math.max(
    0,
    Math.ceil((deadlineDate - today) / (1000 * 60 * 60 * 24)),
  );
  const scrapingActive = today <= deadlineDate;

  return res.json({
    orchestrator: 'BuddyOrchestrator',
    github_repo: DEFAULT_REPO,
    catalog_size: bots.length,
    scraping_active: scrapingActive,
    scrape_deadline: deadline,
    days_until_deadline: daysRemaining,
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// GET /api/learning — AI learning progress snapshot
//
// Returns per-category learning progress toward the June 22 2026 deadline,
// derived from the bot catalog (each bot contributes learning activity to
// its category).  Useful for the Learning Tracker tab in the Control Tower.
// ---------------------------------------------------------------------------

const LEARNING_CATEGORIES = [
  'Automation',
  'AI Companion',
  'Finance',
  'Sales',
  'Content',
  'Real Estate',
  'General',
];

app.get('/api/learning', rateLimiter, (_req, res) => {
  const bots = readBots();
  const deadline = '2026-06-22';
  const today = new Date();
  const deadlineDate = new Date(deadline);
  const totalMs = new Date('2026-01-01').getTime();
  const elapsedMs = today.getTime() - totalMs;
  const totalRangeMs = deadlineDate.getTime() - totalMs;
  const overallProgress = Math.min(100, Math.max(0, Math.round((elapsedMs / totalRangeMs) * 100)));
  const daysRemaining = Math.max(0, Math.ceil((deadlineDate - today) / (1000 * 60 * 60 * 24)));

  // Build per-category stats from catalog
  const categoryMap = {};
  for (const cat of LEARNING_CATEGORIES) {
    const catBots = bots.filter((b) => (b.category || 'General') === cat);
    const activeCatBots = catBots.filter((b) => b.status === 'active').length;
    categoryMap[cat] = {
      category: cat,
      bots_total: catBots.length,
      bots_active: activeCatBots,
      progress: catBots.length > 0 ? Math.min(100, overallProgress + activeCatBots * 2) : 0,
    };
  }

  // Per-bot learning scores (score = active bots weighted by tier)
  const TIER_WEIGHT = { FREE: 1, PRO: 2, ENTERPRISE: 3, ELITE: 4 };
  const botScores = bots.map((b) => ({
    name: b.name,
    category: b.category || 'General',
    tier: b.tier || 'FREE',
    status: b.status,
    learning_score: b.status === 'active' ? (TIER_WEIGHT[b.tier] ?? 1) * 25 : 0,
  }));

  return res.json({
    deadline,
    days_remaining: daysRemaining,
    scraping_active: today <= deadlineDate,
    overall_progress: overallProgress,
    categories: Object.values(categoryMap),
    top_bots: botScores
      .sort((a, b) => b.learning_score - a.learning_score)
      .slice(0, 5),
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// GET /api/revenue — revenue metrics derived from the bot catalog
//
// Computes Monthly Recurring Revenue (MRR), revenue by category/tier, and
// highest-earning bots.  Based on catalog price data (bots.json).
// ---------------------------------------------------------------------------

app.get('/api/revenue', rateLimiter, (_req, res) => {
  const bots = readBots();

  const activeBots = bots.filter((b) => b.status === 'active');
  const mrr = activeBots.reduce((sum, b) => sum + (b.price_usd ?? 0), 0);
  const arr = mrr * 12;
  const totalCatalogValue = bots.reduce((sum, b) => sum + (b.price_usd ?? 0), 0);

  // Revenue by tier
  const tierRevenue = {};
  for (const b of activeBots) {
    const t = b.tier || 'FREE';
    tierRevenue[t] = (tierRevenue[t] ?? 0) + (b.price_usd ?? 0);
  }

  // Revenue by category
  const categoryRevenue = {};
  for (const b of activeBots) {
    const c = b.category || 'General';
    categoryRevenue[c] = (categoryRevenue[c] ?? 0) + (b.price_usd ?? 0);
  }

  // Top earners
  const topEarners = [...activeBots]
    .filter((b) => (b.price_usd ?? 0) > 0)
    .sort((a, b) => (b.price_usd ?? 0) - (a.price_usd ?? 0))
    .slice(0, 5)
    .map((b) => ({ name: b.name, tier: b.tier, price_usd: b.price_usd, category: b.category }));

  return res.json({
    mrr,
    arr,
    total_catalog_value: totalCatalogValue,
    active_revenue_bots: activeBots.filter((b) => (b.price_usd ?? 0) > 0).length,
    by_tier: tierRevenue,
    by_category: categoryRevenue,
    top_earners: topEarners,
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// GET /api/alerts — active system alerts
//
// Surfaces stale bots (no heartbeat for >5 min), error-status bots, and a
// deadline countdown warning when ≤7 days remain.
// ---------------------------------------------------------------------------

const STALE_THRESHOLD_MS = 5 * 60 * 1000; // 5 minutes
const DEADLINE_WARN_DAYS = 7;

app.get('/api/alerts', rateLimiter, (_req, res) => {
  const bots = readBots();
  const now = Date.now();
  const alerts = [];

  // Stale-heartbeat alerts
  for (const b of bots) {
    if (b.lastHeartbeat) {
      const age = now - new Date(b.lastHeartbeat).getTime();
      if (age > STALE_THRESHOLD_MS) {
        const mins = Math.round(age / 60_000);
        alerts.push({
          id: `stale-${b.name}`,
          severity: 'warning',
          type: 'stale_heartbeat',
          message: `Bot "${b.name}" has not sent a heartbeat for ${mins} minutes.`,
          bot: b.name,
          since: b.lastHeartbeat,
        });
      }
    }
  }

  // Error-status alerts
  for (const b of bots) {
    if (b.status === 'error') {
      alerts.push({
        id: `error-${b.name}`,
        severity: 'critical',
        type: 'bot_error',
        message: `Bot "${b.name}" is reporting an error status.`,
        bot: b.name,
      });
    }
  }

  // Deadline countdown warning
  const deadline = new Date('2026-06-22');
  const daysRemaining = Math.max(0, Math.ceil((deadline - new Date()) / (1000 * 60 * 60 * 24)));
  if (daysRemaining <= DEADLINE_WARN_DAYS) {
    alerts.push({
      id: 'deadline-warning',
      severity: daysRemaining === 0 ? 'critical' : 'warning',
      type: 'deadline',
      message:
        daysRemaining === 0
          ? 'Deep learning deadline has passed. Scraping is no longer active.'
          : `Deep learning deadline in ${daysRemaining} day${daysRemaining === 1 ? '' : 's'}.`,
    });
  }

  return res.json({
    alerts,
    count: alerts.length,
    critical: alerts.filter((a) => a.severity === 'critical').length,
    warning: alerts.filter((a) => a.severity === 'warning').length,
    timestamp: new Date().toISOString(),
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
