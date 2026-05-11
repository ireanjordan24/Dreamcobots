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
// GET /api/actions — live GitHub Actions workflow runs (read-only)
//
// Fetches the most recent workflow runs from the GitHub REST API.
// Requires the GITHUB_TOKEN env variable for authenticated requests.
// Gracefully degrades when the token is absent or the API is unreachable.
// ---------------------------------------------------------------------------

const GITHUB_API_BASE = 'https://api.github.com';
const DEFAULT_REPO = process.env.GITHUB_REPO || 'DreamCo-Technologies/Dreamcobots';
const ACTIONS_PER_PAGE = 12;
const PULL_REQUESTS_PER_PAGE = 20;
const DEFAULT_REF = process.env.GITHUB_DEFAULT_REF || 'main';
const WORKFLOW_CONTROLS = [
  {
    id: 'integration-feedback',
    label: 'Integration Feedback',
    category: 'Integrations',
    workflow: 'integration-feedback.yml',
    description: 'Runs integration feedback logging with validation gates.',
    defaultInputs: {
      platform: 'GitHub Actions',
      status: 'success',
      details: 'Control Tower manual run.',
      version: '',
    },
  },
  {
    id: 'company-lookup',
    label: 'Company Lookup',
    category: 'Skill Building',
    workflow: 'company-lookup.yml',
    description: 'Runs company lookup automation with validation gates.',
    defaultInputs: {
      companies: 'Stripe, Shopify, OpenAI',
      tier: 'pro',
    },
  },
  {
    id: 'soak-24h',
    label: '24-Hour Wall Check',
    category: 'System Health',
    workflow: 'system-soak-24h.yml',
    description: 'Runs the production-readiness soak cycle and publishes artifacts.',
    defaultInputs: {
      cycles: '24',
      pause_seconds: '0',
    },
    isPermanent: true,
  },
  {
    id: 'builder-simulation-sql',
    label: 'Builder Simulation + SQL Lab',
    category: 'Builder Lab',
    workflow: 'builder-simulation-sql.yml',
    description:
      'Game-builder/simulation-builder/vibe-coder lab with bot skill checks and SQL action testing (create/read/update/delete/all).',
    defaultInputs: {
      mode: 'simulation_builder',
      sql_action: 'all',
      skill_suite: 'all',
    },
  },
];

function buildGitHubHeaders(token) {
  const headers = {
    'User-Agent': 'dreamco-control-tower',
    Accept: 'application/vnd.github+json',
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

async function githubApiRequest({ repo, token, method = 'GET', apiPath, body = null }) {
  const { default: https } = await import('https');
  return new Promise((resolve) => {
    const headers = buildGitHubHeaders(token);
    const url = new URL(`/repos/${repo}${apiPath}`, GITHUB_API_BASE);
    const payload = body ? JSON.stringify(body) : null;
    if (payload) {
      headers['Content-Type'] = 'application/json';
      headers['Content-Length'] = Buffer.byteLength(payload);
    }

    const req = https.request(
      {
        hostname: url.hostname,
        path: url.pathname + url.search,
        method,
        headers,
      },
      (res) => {
        let responseBody = '';
        res.on('data', (chunk) => (responseBody += chunk));
        res.on('end', () => {
          let data = null;
          if (responseBody) {
            try {
              data = JSON.parse(responseBody);
            } catch {
              data = null;
            }
          }
          resolve({
            ok: (res.statusCode ?? 500) >= 200 && (res.statusCode ?? 500) < 300,
            statusCode: res.statusCode ?? 500,
            data,
          });
        });
      },
    );

    if (payload) {
      req.write(payload);
    }
    req.end();
    req.on('error', () =>
      resolve({
        ok: false,
        statusCode: 503,
        data: null,
      }),
    );
    req.setTimeout(5000, () => {
      req.destroy();
      resolve({
        ok: false,
        statusCode: 504,
        data: null,
      });
    });
  });
}

async function fetchGitHubWorkflowRuns(repo, token) {
  const response = await githubApiRequest({
    repo,
    token,
    apiPath: `/actions/runs?per_page=${ACTIONS_PER_PAGE}`,
  });
  if (!response.ok || !response.data) {
    return { runs: [], source: 'unavailable' };
  }
  const runs = (response.data.workflow_runs ?? []).map((r) => ({
    id: r.id,
    name: r.name,
    status: r.status,
    conclusion: r.conclusion,
    branch: r.head_branch,
    event: r.event,
    run_started_at: r.run_started_at,
    url: r.html_url,
  }));
  return { runs, source: 'github_api' };
}

async function fetchGitHubPullRequests(repo, token) {
  const response = await githubApiRequest({
    repo,
    token,
    apiPath: `/pulls?state=all&sort=updated&direction=desc&per_page=${PULL_REQUESTS_PER_PAGE}`,
  });
  if (!response.ok || !Array.isArray(response.data)) {
    return { pullRequests: [], source: 'unavailable' };
  }
  const pullRequests = response.data.map((pr) => ({
    id: pr.id,
    number: pr.number,
    title: pr.title,
    state: pr.state,
    draft: Boolean(pr.draft),
    merged_at: pr.merged_at,
    updated_at: pr.updated_at,
    user: pr.user?.login ?? 'unknown',
    url: pr.html_url,
  }));
  return { pullRequests, source: 'github_api' };
}

function resolveWorkflowControl(workflowFile) {
  return WORKFLOW_CONTROLS.find((control) => control.workflow === workflowFile) ?? null;
}

app.get('/api/actions', rateLimiter, async (req, res) => {
  const token = process.env.GITHUB_TOKEN || '';
  const [runsResult, pullRequestsResult] = await Promise.all([
    fetchGitHubWorkflowRuns(DEFAULT_REPO, token),
    fetchGitHubPullRequests(DEFAULT_REPO, token),
  ]);
  return res.json({
    repo: DEFAULT_REPO,
    runs: runsResult.runs,
    pull_requests: pullRequestsResult.pullRequests,
    source:
      runsResult.source === 'github_api' || pullRequestsResult.source === 'github_api'
        ? 'github_api'
        : 'unavailable',
    controls: WORKFLOW_CONTROLS,
    fetched_at: new Date().toISOString(),
  });
});

app.post('/api/actions/dispatch', rateLimiter, async (req, res) => {
  const token = process.env.GITHUB_TOKEN || '';
  if (!token) {
    return res.status(503).json({
      error: 'GITHUB_TOKEN is required to dispatch workflows.',
    });
  }

  const workflow = String(req.body?.workflow || '').trim();
  const control = resolveWorkflowControl(workflow);
  if (!control) {
    return res.status(400).json({
      error: 'Unsupported workflow. Use one of the configured control workflows.',
    });
  }

  const ref = String(req.body?.ref || DEFAULT_REF).trim() || DEFAULT_REF;
  const incomingInputs = req.body?.inputs && typeof req.body.inputs === 'object' ? req.body.inputs : {};
  const inputs = { ...control.defaultInputs, ...incomingInputs };

  const dispatchResponse = await githubApiRequest({
    repo: DEFAULT_REPO,
    token,
    method: 'POST',
    apiPath: `/actions/workflows/${encodeURIComponent(workflow)}/dispatches`,
    body: { ref, inputs },
  });

  if (!dispatchResponse.ok) {
    return res.status(dispatchResponse.statusCode).json({
      status: 'error',
      workflow,
      ref,
      message: 'GitHub rejected the workflow dispatch request.',
    });
  }

  return res.status(202).json({
    status: 'accepted',
    workflow,
    ref,
    inputs,
    triggered_at: new Date().toISOString(),
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
