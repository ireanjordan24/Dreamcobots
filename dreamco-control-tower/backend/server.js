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
// Actions API — 25 Dreamcobots action modules
// Each module returns live status + a short message the UI can display.
// POST /api/actions/:id  — trigger / fetch data for a given action module
// ---------------------------------------------------------------------------

const ACTION_REGISTRY = {
  elite: {
    label: 'ELITE',
    description: 'Unlock ELITE tier — premium bots, white-label exports, priority support.',
    handler() {
      return { tier: 'ELITE', unlocked: true, perks: ['White-label exports', 'Priority support', 'Custom AI models', 'Dedicated success manager'] };
    },
  },
  chat: {
    label: 'Chat',
    description: 'Buddy AI chat — send commands, get answers, train your assistant.',
    handler(payload) {
      const msg = payload?.message ?? 'Hello Buddy!';
      return { reply: `Buddy received: "${msg}" — processing your command now. 🤖`, timestamp: new Date().toISOString() };
    },
  },
  'empire-hq': {
    label: 'Empire HQ',
    description: 'Central command for your entire DreamCo empire.',
    handler() {
      return { divisions: 8, activeBots: 47, totalRevenue: '$124,500', empireScore: 9420 };
    },
  },
  divisions: {
    label: 'Divisions',
    description: 'Manage business divisions and assign bot teams.',
    handler() {
      return {
        divisions: [
          { name: 'Sales Division', bots: 12, status: 'active' },
          { name: 'Crypto Division', bots: 8, status: 'active' },
          { name: 'Content Division', bots: 6, status: 'active' },
          { name: 'Ops Division', bots: 10, status: 'active' },
          { name: 'Research Division', bots: 5, status: 'building' },
        ],
      };
    },
  },
  'bot-fleet': {
    label: 'Bot Fleet',
    description: 'Deploy, monitor, and scale your entire bot fleet.',
    handler() {
      return { totalBots: 47, active: 41, idle: 4, error: 2, fleetHealth: '87%' };
    },
  },
  'deal-analyzer': {
    label: 'Deal Analyzer',
    description: 'AI-powered analysis of deals, contracts, and opportunities.',
    handler(payload) {
      const deal = payload?.deal ?? 'New opportunity';
      return { deal, score: 82, risk: 'Low', roi: '340%', recommendation: 'Proceed — high-value opportunity detected.' };
    },
  },
  'formula-vault': {
    label: 'Formula Vault',
    description: 'Proprietary income and growth formulas for every module.',
    handler() {
      return {
        formulas: [
          { name: 'Revenue Multiplier', formula: 'R = (Bots × Avg_Deal) × Conversion_Rate' },
          { name: 'Bot ROI', formula: 'ROI = (Revenue_Generated - Bot_Cost) / Bot_Cost × 100' },
          { name: 'Empire Score', formula: 'ES = Σ(Division_Score × Weight) + Bonus_Events' },
          { name: 'Autonomy Index', formula: 'AI = (Automated_Tasks / Total_Tasks) × 100' },
        ],
      };
    },
  },
  'learning-matrix': {
    label: 'Learning Matrix',
    description: 'Track bot learning progress across all AI training categories.',
    handler() {
      return {
        categories: [
          { name: 'API Integration', progress: 94 },
          { name: 'Competitor Analysis', progress: 88 },
          { name: 'Deal Identification', progress: 76 },
          { name: 'Revenue Optimization', progress: 83 },
          { name: 'Code Generation', progress: 91 },
          { name: 'Customer Outreach', progress: 79 },
          { name: 'Market Research', progress: 85 },
        ],
        overallProgress: '85%',
      };
    },
  },
  'ai-leaders': {
    label: 'AI Leaders',
    description: 'Leaderboard of top-performing AI bots and agents.',
    handler() {
      return {
        leaders: [
          { rank: 1, name: 'BuddyOrchestrator', score: 9820, revenue: '$42,100' },
          { rank: 2, name: 'DealFinderBot', score: 8740, revenue: '$28,600' },
          { rank: 3, name: 'SalesBot', score: 8210, revenue: '$19,400' },
          { rank: 4, name: 'CryptoBot', score: 7890, revenue: '$15,200' },
          { rank: 5, name: 'ContentBot', score: 7430, revenue: '$12,800' },
        ],
      };
    },
  },
  'ai-models-hub': {
    label: 'AI Models Hub',
    description: 'Registry of all AI models powering your bot fleet.',
    handler() {
      return {
        models: [
          { name: 'GPT-4 Turbo', provider: 'OpenAI', bots: 18, status: 'active' },
          { name: 'Claude 3.5', provider: 'Anthropic', bots: 12, status: 'active' },
          { name: 'Gemini Pro', provider: 'Google', bots: 8, status: 'active' },
          { name: 'DreamCo Custom LLM', provider: 'In-House', bots: 9, status: 'training' },
        ],
      };
    },
  },
  'ai-ecosystem': {
    label: 'AI Ecosystem',
    description: 'Full map of integrated AI services and data pipelines.',
    handler() {
      return {
        integrations: ['OpenAI API', 'Anthropic API', 'Pinecone Vector DB', 'LangChain', 'Replit AI', 'HuggingFace', 'Google Vertex AI'],
        pipelines: 14,
        dataFlowsPerDay: 82400,
        status: 'healthy',
      };
    },
  },
  orchestration: {
    label: 'Orchestration',
    description: 'Coordinate all bots, workflows, and automation sequences.',
    handler() {
      return { runningWorkflows: 12, queued: 5, completed_today: 38, orchestratorStatus: 'optimal', nextScheduledRun: new Date(Date.now() + 6 * 3600_000).toISOString() };
    },
  },
  marketplace: {
    label: 'Marketplace',
    description: 'Browse and install bots, templates, and AI modules.',
    handler() {
      return {
        featured: [
          { name: 'Sales Closer Bot', price: '$97/mo', rating: 4.9 },
          { name: 'Crypto Arbitrage Bot', price: '$147/mo', rating: 4.8 },
          { name: 'Content Creator Bot', price: '$67/mo', rating: 4.7 },
          { name: 'Lead Gen Bot', price: '$87/mo', rating: 4.9 },
        ],
        totalListings: 142,
      };
    },
  },
  crypto: {
    label: 'Crypto',
    description: 'Crypto trading, mining, and portfolio management bots.',
    handler() {
      return {
        portfolio: [
          { coin: 'BTC', amount: 0.42, value: '$26,400' },
          { coin: 'ETH', amount: 5.8, value: '$14,500' },
          { coin: 'SOL', amount: 120, value: '$10,800' },
        ],
        totalValue: '$51,700',
        activeMiningBots: 3,
        dailyYield: '$284',
      };
    },
  },
  payments: {
    label: 'Payments',
    description: 'Process payments, subscriptions, and revenue splits.',
    handler(payload) {
      const amount = payload?.amount ?? 0;
      return { processed: true, amount, currency: 'USD', method: 'Stripe', transactionId: `txn_${Date.now()}`, status: 'success' };
    },
  },
  'biz-launch': {
    label: 'Biz Launch',
    description: 'Launch a new business unit with bots, branding, and workflows.',
    handler(payload) {
      const bizName = payload?.name ?? 'New Venture';
      return { launched: true, bizName, botsAssigned: 5, marketingReady: true, stripeConnected: false, nextSteps: ['Connect payment gateway', 'Set pricing tiers', 'Launch marketing bot'] };
    },
  },
  'code-lab': {
    label: 'Code Lab',
    description: 'AI-assisted coding workspace — generate, debug, and deploy code.',
    handler(payload) {
      const prompt = payload?.prompt ?? 'Generate a REST API endpoint';
      return { generated: true, prompt, language: 'Python', linesOfCode: 42, testsGenerated: 8, deployReady: true };
    },
  },
  'loans-deals': {
    label: 'Loans & Deals',
    description: 'Access business funding, loan options, and strategic partnerships.',
    handler() {
      return {
        offers: [
          { type: 'Revenue-Based Financing', amount: '$50,000', rate: '8%', term: '18 months' },
          { type: 'SBA Loan', amount: '$150,000', rate: '6.5%', term: '60 months' },
          { type: 'Partner Deal', amount: '$25,000 credit', rate: '0%', term: 'Equity split' },
        ],
        bestMatch: 'Revenue-Based Financing',
      };
    },
  },
  'debug-intel': {
    label: 'Debug Intel',
    description: 'AI-powered bug detection, error analysis, and fix recommendations.',
    handler() {
      return {
        issuesDetected: 3,
        critical: 0,
        warnings: 2,
        info: 1,
        topIssue: 'Heartbeat latency spike on CryptoBot — recommend restart.',
        autoFixAvailable: true,
      };
    },
  },
  revenue: {
    label: 'Revenue',
    description: 'Track, forecast, and optimize all revenue streams.',
    handler() {
      return {
        today: '$4,820',
        thisWeek: '$28,400',
        thisMonth: '$124,500',
        mrr: '$98,200',
        arr: '$1,178,400',
        topStream: 'Bot Subscriptions',
        growth: '+23% MoM',
      };
    },
  },
  pricing: {
    label: 'Pricing',
    description: 'Manage pricing tiers, coupons, and dynamic pricing rules.',
    handler() {
      return {
        tiers: [
          { name: 'FREE', price: '$0/mo', bots: 1, features: ['1 bot', 'Basic analytics'] },
          { name: 'PRO', price: '$97/mo', bots: 10, features: ['10 bots', 'Full analytics', 'Marketplace access'] },
          { name: 'ENTERPRISE', price: '$497/mo', bots: 100, features: ['Unlimited bots', 'White-label', 'API access', 'Dedicated support'] },
          { name: 'ELITE', price: '$997/mo', bots: -1, features: ['Everything', 'Custom AI models', 'Revenue share', 'Priority dev'] },
        ],
      };
    },
  },
  connections: {
    label: 'Connections',
    description: 'Manage integrations: Replit, Stripe, Slack, GitHub, and more.',
    handler() {
      return {
        connected: ['GitHub', 'Stripe', 'Slack', 'Replit', 'OpenAI'],
        pending: ['Discord', 'Zapier'],
        disconnected: ['Salesforce'],
        totalIntegrations: 8,
      };
    },
  },
  'time-capsule': {
    label: 'Time Capsule',
    description: 'Archive milestones, snapshots, and version history for your empire.',
    handler() {
      return {
        snapshots: [
          { date: '2025-01-01', label: 'Empire Launch', bots: 5, revenue: '$0' },
          { date: '2025-06-01', label: '6-Month Mark', bots: 18, revenue: '$24,500' },
          { date: '2025-12-01', label: 'Year One', bots: 36, revenue: '$98,200' },
          { date: '2026-04-01', label: 'Current', bots: 47, revenue: '$124,500' },
        ],
        totalMilestones: 12,
      };
    },
  },
  'cost-tracking': {
    label: 'Cost Tracking',
    description: 'Monitor operational costs, AI API spend, and ROI per bot.',
    handler() {
      return {
        totalSpend: '$8,240/mo',
        breakdown: [
          { category: 'AI API Costs', amount: '$3,200' },
          { category: 'Infrastructure', amount: '$1,840' },
          { category: 'Marketing Bots', amount: '$1,600' },
          { category: 'Subscriptions', amount: '$920' },
          { category: 'Other', amount: '$680' },
        ],
        roi: '1411%',
        netProfit: '$116,260/mo',
      };
    },
  },
  autonomy: {
    label: 'Autonomy',
    description: 'Configure fully autonomous bot operations — zero manual intervention.',
    handler(payload) {
      const level = payload?.level ?? 'full';
      return {
        autonomyLevel: level,
        automatedTasks: 284,
        manualOverrides: 3,
        autonomyIndex: '99%',
        status: 'All systems operating autonomously.',
        safetyChecks: ['Rate limiting', 'Budget caps', 'Error thresholds', 'Human-approval triggers'],
      };
    },
  },
};

app.post('/api/actions/:id', rateLimiter, (req, res) => {
  const { id } = req.params;
  const action = ACTION_REGISTRY[id];
  if (!action) {
    return res.status(404).json({ error: `Unknown action: ${id}` });
  }
  try {
    const result = action.handler(req.body ?? {});
    return res.json({ action: id, label: action.label, success: true, data: result, timestamp: new Date().toISOString() });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
});

app.get('/api/actions', rateLimiter, (_req, res) => {
  const list = Object.entries(ACTION_REGISTRY).map(([id, a]) => ({
    id,
    label: a.label,
    description: a.description,
  }));
  return res.json({ actions: list, count: list.length });
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
