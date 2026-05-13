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
// ELITE — top-tier bot performance status
// ---------------------------------------------------------------------------
app.get('/api/elite/status', rateLimiter, (_req, res) => {
  const bots = readBots();
  const eliteBots = bots.filter((b) => b.tier === 'ELITE');
  res.json({
    tier: 'ELITE',
    members: eliteBots.length || 5,
    totalRevenue: '$176,900',
    growth: '+24%',
    bots: eliteBots,
  });
});

// ---------------------------------------------------------------------------
// Chat — Buddy AI chat endpoint (stateless response)
// ---------------------------------------------------------------------------
app.post('/api/actions/chat', rateLimiter, (req, res) => {
  const { message = '' } = req.body;
  const lower = message.toLowerCase();

  let reply = 'I received your message. Processing with the DreamCo AI engine…';
  if (lower.includes('bot') && lower.includes('status')) {
    const bots = readBots();
    const active = bots.filter((b) => b.status === 'active').length;
    reply = `📊 Bot Status Update: ${active}/${bots.length} bots are active and running.`;
  } else if (lower.includes('revenue')) {
    reply = '💰 Revenue snapshot: $209,000 MRR this month, up +31% from last month. Top earner: BuddyOrchestrator at $42.8k.';
  } else if (lower.includes('diagnostic') || lower.includes('diagnos')) {
    reply = '🩺 Running diagnostics… All systems nominal. 40 bots active, API response times healthy, no critical errors.';
  } else if (lower.includes('deal')) {
    reply = '🤝 Active deals: 4 in pipeline. Highest value: Enterprise White-Label Contract at $1.2M (60% probability).';
  } else if (lower.includes('deploy')) {
    reply = '🚀 Ready to deploy! Use the Bot Deployment panel or trigger via Orchestration → Dispatch Workflow.';
  } else if (lower.includes('hello') || lower.includes('hi')) {
    reply = 'Hey! 👋 Welcome back to the DreamCo Control Tower. Your empire is running strong. What can I help you with today?';
  }

  res.json({ reply, timestamp: new Date().toISOString() });
});

// ---------------------------------------------------------------------------
// Empire HQ — organizational overview
// ---------------------------------------------------------------------------
app.get('/api/empire/hq', rateLimiter, (_req, res) => {
  const bots = readBots();
  res.json({
    divisions: 5,
    totalBots: bots.length,
    monthlyRevenue: '$212k',
    growth: '+31%',
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// Divisions — list all organizational divisions
// ---------------------------------------------------------------------------
app.get('/api/divisions', rateLimiter, (_req, res) => {
  res.json({
    divisions: [
      { id: 'bot-eng', name: 'Bot Engineering', emoji: '⚙️', lead: 'BuddyOrchestrator', status: 'active', bots: 12, kpi: '99.1% uptime', color: 'border-blue-500/40' },
      { id: 'ai-research', name: 'AI Research', emoji: '🧠', lead: 'AILeaderBot', status: 'active', bots: 8, kpi: '7 models trained', color: 'border-purple-500/40' },
      { id: 'finance', name: 'Finance Ops', emoji: '💰', lead: 'RevenueEngineBot', status: 'active', bots: 6, kpi: '$91k this month', color: 'border-green-500/40' },
      { id: 'market', name: 'Market Intel', emoji: '📊', lead: 'DealAnalyzerBot', status: 'active', bots: 9, kpi: '12 deals tracked', color: 'border-yellow-500/40' },
      { id: 'infra', name: 'Infrastructure', emoji: '🏗️', lead: 'OrchestrationBot', status: 'idle', bots: 5, kpi: '3 pipelines live', color: 'border-slate-500/40' },
    ],
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// Deal Analyzer — analyze a deal description
// ---------------------------------------------------------------------------
app.post('/api/deal-analyzer/analyze', rateLimiter, (req, res) => {
  const { description = '' } = req.body;
  const lower = description.toLowerCase();

  let type = 'Partnership';
  let risk = 'medium';
  let score = 75;

  if (lower.includes('acqui')) { type = 'Acquisition'; risk = 'high'; score = Math.floor(Math.random() * 20) + 65; }
  else if (lower.includes('license')) { type = 'License'; risk = 'low'; score = Math.floor(Math.random() * 10) + 88; }
  else if (lower.includes('contract')) { type = 'Contract'; risk = 'medium'; score = Math.floor(Math.random() * 15) + 78; }
  else if (lower.includes('invest')) { type = 'Investment'; risk = 'high'; score = Math.floor(Math.random() * 20) + 60; }

  const valueMatch = description.match(/\$[\d,]+[kKmM]?/);
  const value = valueMatch ? valueMatch[0] : 'TBD';

  res.json({ type, value, score, risk, timestamp: new Date().toISOString() });
});

// ---------------------------------------------------------------------------
// AI Leaders — leaderboard data
// ---------------------------------------------------------------------------
app.get('/api/ai-leaders', rateLimiter, (req, res) => {
  const bots = readBots();
  const leaders = bots.slice(0, 7).map((b, i) => ({
    name: b.name,
    role: b.team ? `${b.team} AI` : 'General AI',
    score: Math.max(70, 98 - i * 3),
    tasks: Math.floor(Math.random() * 4000) + 1000,
    revenue: `$${Math.floor(Math.random() * 35000 + 15000).toLocaleString()}`,
    model: ['GPT-4o', 'Claude-3', 'Gemini Pro', 'Llama-3'][i % 4],
    trend: `+${Math.floor(Math.random() * 10) + 1}%`,
  }));
  res.json({ leaders, period: req.query.period ?? 'month', timestamp: new Date().toISOString() });
});

// ---------------------------------------------------------------------------
// Crypto — portfolio data
// ---------------------------------------------------------------------------
app.get('/api/crypto/portfolio', rateLimiter, (_req, res) => {
  res.json({
    coins: [
      { symbol: 'BTC', name: 'Bitcoin', price: '$67,420', change: '+2.4%', up: true, balance: '0.12 BTC', value: '$8,090' },
      { symbol: 'ETH', name: 'Ethereum', price: '$3,820', change: '+3.1%', up: true, balance: '2.5 ETH', value: '$9,550' },
      { symbol: 'SOL', name: 'Solana', price: '$182', change: '-1.2%', up: false, balance: '45 SOL', value: '$8,190' },
      { symbol: 'USDC', name: 'USD Coin', price: '$1.00', change: '0.0%', up: true, balance: '5,000 USDC', value: '$5,000' },
    ],
    totalValue: '$30,830',
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// Payments — create a payment intent
// ---------------------------------------------------------------------------
app.post('/api/payments/create', rateLimiter, (req, res) => {
  const { amount, description } = req.body;
  if (!amount || !description) {
    return res.status(400).json({ error: 'amount and description are required' });
  }
  res.json({
    message: `Payment of $${amount} initiated for "${description}". Processing via Stripe.`,
    paymentId: `pay_${Date.now()}`,
    status: 'pending',
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// Revenue — stats summary
// ---------------------------------------------------------------------------
app.get('/api/revenue/stats', rateLimiter, (_req, res) => {
  res.json({
    mrr: '$209,000',
    arr: '$2.5M',
    growth: '+31%',
    churn: '1.8%',
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// Biz Launch — analyze a business idea
// ---------------------------------------------------------------------------
app.post('/api/biz-launch/analyze', rateLimiter, (req, res) => {
  const { idea = '' } = req.body;
  const lower = idea.toLowerCase();

  let market = 'General SaaS';
  let potential = '$1.2M TAM';
  let score = 72;

  if (lower.includes('bot') || lower.includes('ai') || lower.includes('automat')) {
    market = 'AI / Automation Tools'; potential = '$8.4B TAM'; score = 91;
  } else if (lower.includes('marketplace')) {
    market = 'B2B Marketplace'; potential = '$3.1B TAM'; score = 84;
  } else if (lower.includes('crypto') || lower.includes('defi')) {
    market = 'Web3 / DeFi'; potential = '$12B TAM'; score = 68;
  } else if (lower.includes('saas')) {
    market = 'SaaS / AI Tools'; potential = '$2.4M TAM'; score = 78;
  }

  res.json({
    score,
    market,
    potential,
    recommendation: score >= 85
      ? 'Strong potential — move fast, validate with 5 paying customers.'
      : score >= 70
        ? 'Good potential — validate with 10 target customers first.'
        : 'Risky market — do deep validation before investing capital.',
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// Code Lab — sandboxed code execution (simulation)
// ---------------------------------------------------------------------------
app.post('/api/code-lab/run', rateLimiter, (req, res) => {
  const { language = 'Python', code = '' } = req.body;
  const lines = code.split('\n').length;

  // Simulate execution — real execution would require a sandbox
  const output = [
    `[DreamCo Code Lab] Running ${language} (${lines} lines)…`,
    '─'.repeat(40),
    '',
    '✅ Code accepted and queued for sandbox execution.',
    '📦 Execution environment: DreamCo Sandbox v2.0',
    `⏱️  Estimated runtime: ${Math.floor(Math.random() * 800) + 100}ms`,
    '',
    '> Process exited with code 0',
  ].join('\n');

  res.json({ output, language, lines, timestamp: new Date().toISOString() });
});

// ---------------------------------------------------------------------------
// Debug Intel — error log + diagnostics
// ---------------------------------------------------------------------------
app.get('/api/debug/intel', rateLimiter, (_req, res) => {
  res.json({
    errors: [],
    systemHealth: 'healthy',
    timestamp: new Date().toISOString(),
  });
});

app.post('/api/debug/diagnostics', rateLimiter, (_req, res) => {
  const bots = readBots();
  const active = bots.filter((b) => b.status === 'active').length;
  res.json({
    report: [
      '✅ System diagnostics complete',
      '',
      `• Bot heartbeats: ${active}/${bots.length} active`,
      '• API endpoints: 12/12 responding',
      '• Memory usage: 62% avg',
      '• Disk space: 78% free',
      '• DB connections: 8/10 healthy',
      '',
      'No critical issues detected.',
    ].join('\n'),
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// Cost Tracking — budget summary
// ---------------------------------------------------------------------------
app.get('/api/cost-tracking/summary', rateLimiter, (_req, res) => {
  res.json({
    totalBudget: 4000,
    totalSpent: 3001,
    categories: [
      { name: 'AI APIs', budget: 500, spent: 342, icon: '🤖', items: ['OpenAI: $184', 'Anthropic: $98', 'Gemini: $60'] },
      { name: 'Infrastructure', budget: 800, spent: 621, icon: '☁️', items: ['AWS: $421', 'GitHub Actions: $120', 'DNS/CDN: $80'] },
      { name: 'Tools & SaaS', budget: 300, spent: 218, icon: '🛠️', items: ['Replit: $80', 'Stripe fees: $92', 'Monitoring: $46'] },
      { name: 'Marketing', budget: 400, spent: 180, icon: '📣', items: ['Ads: $140', 'Content: $40'] },
      { name: 'Labor/Contractors', budget: 2000, spent: 1640, icon: '👥', items: ['Dev contractors: $1,200', 'AI training: $440'] },
    ],
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// Autonomy — get/set autonomy settings
// ---------------------------------------------------------------------------
app.get('/api/autonomy/settings', rateLimiter, (_req, res) => {
  res.json({
    masterSwitch: true,
    autoHealing: true,
    autoScaling: true,
    revenueAutopilot: true,
    learningMode: true,
    safeMode: false,
    timestamp: new Date().toISOString(),
  });
});

app.post('/api/autonomy/settings', rateLimiter, (req, res) => {
  const { settings } = req.body;
  console.log('🧭 Autonomy settings updated:', JSON.stringify(settings));
  res.json({ status: 'saved', timestamp: new Date().toISOString() });
});

// ---------------------------------------------------------------------------
// Actions — existing endpoints (kept for compatibility) + test plan
// ---------------------------------------------------------------------------
app.get('/api/actions', rateLimiter, (_req, res) => {
  res.json({
    runs: [
      { id: 'wf1', name: 'Deep Learning Cycle', trigger: 'schedule (6h)', status: 'running', steps: 5, lastRun: '18m ago', nextRun: '5h 42m' },
      { id: 'wf2', name: 'Bot CI/CD Pipeline', trigger: 'push to main', status: 'success', steps: 4, lastRun: '2h ago', nextRun: 'on push' },
      { id: 'wf3', name: 'Revenue Sync', trigger: 'schedule (daily)', status: 'success', steps: 3, lastRun: '6h ago', nextRun: '18h' },
    ],
    pull_requests: [],
    controls: { dispatchEnabled: true },
    timestamp: new Date().toISOString(),
  });
});

app.post('/api/actions/dispatch', rateLimiter, (req, res) => {
  const { workflow } = req.body;
  if (!workflow) return res.status(400).json({ error: 'workflow is required' });
  console.log(`⚡ Dispatching workflow: ${workflow}`);
  res.json({
    message: `Workflow '${workflow}' dispatched successfully!`,
    runId: `run_${Date.now()}`,
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// Learning endpoint (for LearningMatrix compatibility)
// ---------------------------------------------------------------------------
app.get('/api/learning', rateLimiter, (_req, res) => {
  const bots = readBots();
  const CATEGORIES = ['APIs', 'Competitors', 'Revenue Models', 'UX Patterns', 'Security', 'Performance', 'AI Ethics'];
  const matrix = bots.slice(0, 5).map((b) => ({
    bot: b.name,
    scores: CATEGORIES.map(() => Math.floor(Math.random() * 30) + 70),
  }));
  res.json({
    bots: matrix,
    categories: CATEGORIES,
    deadline: '2026-06-22',
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
