import request from 'supertest';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

process.env.NODE_ENV = 'test';

const BOTS_FILE = path.join(__dirname, '..', 'config', 'bots.json');

const SAMPLE_BOTS = [
  {
    name: 'buddy-bot',
    repoName: 'Dreamcobots',
    repoPath: './bots/buddy_bot',
    status: 'active',
    tier: 'PRO',
    category: 'AI Companion',
    description: 'The most human-like AI companion.',
    price_usd: 49,
    features: ['Emotion detection', 'Voice synthesis'],
    lastHeartbeat: null,
    lastUpdate: null,
    pendingPRs: 0,
  },
  {
    name: 'sales-bot',
    repoName: 'Dreamcobots',
    repoPath: './bots/sales_bot',
    status: 'idle',
    tier: 'FREE',
    category: 'Sales',
    description: 'Automated sales outreach.',
    price_usd: 0,
    features: ['LeadQualifier', 'EmailSequencer'],
    lastHeartbeat: null,
    lastUpdate: null,
    pendingPRs: 0,
  },
];

let app;
let originalBotsContent;

beforeAll(async () => {
  originalBotsContent = fs.readFileSync(BOTS_FILE, 'utf8');
  const module = await import('../backend/server.js');
  app = module.default;
});

afterAll(() => {
  fs.writeFileSync(BOTS_FILE, originalBotsContent);
});

beforeEach(() => {
  fs.writeFileSync(BOTS_FILE, JSON.stringify(SAMPLE_BOTS, null, 2));
});

// ---------------------------------------------------------------------------
// GET /api/catalog
// ---------------------------------------------------------------------------

describe('GET /api/catalog', () => {
  test('returns 200', async () => {
    const res = await request(app).get('/api/catalog');
    expect(res.status).toBe(200);
  });

  test('returns a JSON array', async () => {
    const res = await request(app).get('/api/catalog');
    expect(Array.isArray(res.body)).toBe(true);
  });

  test('array length matches bots.json length', async () => {
    const res = await request(app).get('/api/catalog');
    expect(res.body.length).toBe(SAMPLE_BOTS.length);
  });

  test('each item has bot_id', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => expect(item).toHaveProperty('bot_id'));
  });

  test('each item has display_name', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => expect(item).toHaveProperty('display_name'));
  });

  test('each item has tier', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => expect(item).toHaveProperty('tier'));
  });

  test('each item has price_usd', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => expect(item).toHaveProperty('price_usd'));
  });

  test('each item has features array', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => {
      expect(item).toHaveProperty('features');
      expect(Array.isArray(item.features)).toBe(true);
    });
  });

  test('each item has is_live boolean', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => {
      expect(item).toHaveProperty('is_live');
      expect(typeof item.is_live).toBe('boolean');
    });
  });

  test('active bot is_live is true', async () => {
    const res = await request(app).get('/api/catalog');
    const buddy = res.body.find((b) => b.bot_id === 'buddy_bot');
    expect(buddy.is_live).toBe(true);
  });

  test('idle bot is_live is false', async () => {
    const res = await request(app).get('/api/catalog');
    const sales = res.body.find((b) => b.bot_id === 'sales_bot');
    expect(sales.is_live).toBe(false);
  });

  test('dashes in name converted to underscores in bot_id', async () => {
    const res = await request(app).get('/api/catalog');
    res.body.forEach((item) => {
      expect(item.bot_id).not.toContain('-');
    });
  });

  test('display_name is title-cased', async () => {
    const res = await request(app).get('/api/catalog');
    const buddy = res.body.find((b) => b.bot_id === 'buddy_bot');
    // "buddy-bot" → "Buddy Bot"
    expect(buddy.display_name).toBe('Buddy Bot');
  });

  test('propagates description from bots.json', async () => {
    const res = await request(app).get('/api/catalog');
    const buddy = res.body.find((b) => b.bot_id === 'buddy_bot');
    expect(buddy.description).toBe('The most human-like AI companion.');
  });

  test('propagates features from bots.json', async () => {
    const res = await request(app).get('/api/catalog');
    const buddy = res.body.find((b) => b.bot_id === 'buddy_bot');
    expect(buddy.features).toContain('Emotion detection');
  });

  test('returns empty array when bots.json is empty', async () => {
    fs.writeFileSync(BOTS_FILE, '[]');
    const res = await request(app).get('/api/catalog');
    expect(res.status).toBe(200);
    expect(res.body).toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// GET /api/orchestrator
// ---------------------------------------------------------------------------

describe('GET /api/orchestrator', () => {
  test('returns 200', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(res.status).toBe(200);
  });

  test('has orchestrator field', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(res.body).toHaveProperty('orchestrator', 'BuddyOrchestrator');
  });

  test('has github_repo field', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(res.body).toHaveProperty('github_repo');
    expect(typeof res.body.github_repo).toBe('string');
  });

  test('has catalog_size matching bots.json', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(res.body.catalog_size).toBe(SAMPLE_BOTS.length);
  });

  test('has scrape_deadline field', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(res.body).toHaveProperty('scrape_deadline', '2026-06-22');
  });

  test('has days_until_deadline as non-negative number', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(typeof res.body.days_until_deadline).toBe('number');
    expect(res.body.days_until_deadline).toBeGreaterThanOrEqual(0);
  });

  test('has scraping_active boolean', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(typeof res.body.scraping_active).toBe('boolean');
  });

  test('has timestamp as valid ISO string', async () => {
    const res = await request(app).get('/api/orchestrator');
    expect(typeof res.body.timestamp).toBe('string');
    expect(() => new Date(res.body.timestamp)).not.toThrow();
  });

  test('scraping_active is true before June 22 2026', async () => {
    // Current date (2026-05-02) is before deadline
    const res = await request(app).get('/api/orchestrator');
    expect(res.body.scraping_active).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// GET /api/actions
// ---------------------------------------------------------------------------

describe('GET /api/actions', () => {
  test('returns 200', async () => {
    const res = await request(app).get('/api/actions');
    expect(res.status).toBe(200);
  });

  test('has runs array', async () => {
    const res = await request(app).get('/api/actions');
    expect(Array.isArray(res.body.runs)).toBe(true);
  });

  test('has pull_requests array', async () => {
    const res = await request(app).get('/api/actions');
    expect(Array.isArray(res.body.pull_requests)).toBe(true);
  });

  test('has controls array', async () => {
    const res = await request(app).get('/api/actions');
    expect(Array.isArray(res.body.controls)).toBe(true);
  });

  test('includes builder simulation sql control', async () => {
    const res = await request(app).get('/api/actions');
    const control = res.body.controls.find((c) => c.id === 'builder-simulation-sql');
    expect(control).toBeDefined();
    expect(control.workflow).toBe('builder-simulation-sql.yml');
  });

  test('has source field', async () => {
    const res = await request(app).get('/api/actions');
    expect(res.body).toHaveProperty('source');
  });

  test('has repo field', async () => {
    const res = await request(app).get('/api/actions');
    expect(res.body).toHaveProperty('repo');
  });

  test('has fetched_at ISO timestamp', async () => {
    const res = await request(app).get('/api/actions');
    expect(res.body).toHaveProperty('fetched_at');
    expect(typeof res.body.fetched_at).toBe('string');
  });

  test('does not throw without GITHUB_TOKEN', async () => {
    const orig = process.env.GITHUB_TOKEN;
    delete process.env.GITHUB_TOKEN;
    const res = await request(app).get('/api/actions');
    expect(res.status).toBe(200);
    if (orig !== undefined) {
      process.env.GITHUB_TOKEN = orig;
    }
  });

  test('returns content-type json', async () => {
    const res = await request(app).get('/api/actions');
    expect(res.headers['content-type']).toMatch(/application\/json/);
  });
});

describe('POST /api/actions/dispatch', () => {
  test('returns 503 when GITHUB_TOKEN is missing', async () => {
    const orig = process.env.GITHUB_TOKEN;
    delete process.env.GITHUB_TOKEN;
    const res = await request(app)
      .post('/api/actions/dispatch')
      .send({ workflow: 'integration-feedback.yml', inputs: {} });
    expect(res.status).toBe(503);
    if (orig !== undefined) {
      process.env.GITHUB_TOKEN = orig;
    }
  });

  test('returns 400 for unsupported workflow', async () => {
    const orig = process.env.GITHUB_TOKEN;
    process.env.GITHUB_TOKEN = 'test-token';
    const res = await request(app)
      .post('/api/actions/dispatch')
      .send({ workflow: 'unknown.yml', inputs: {} });
    expect(res.status).toBe(400);
    if (orig === undefined) {
      delete process.env.GITHUB_TOKEN;
    } else {
      process.env.GITHUB_TOKEN = orig;
    }
  });
});

describe('GET /api/actions/chat', () => {
  test('returns 200 and history array', async () => {
    const res = await request(app).get('/api/actions/chat');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body.history)).toBe(true);
  });
});

describe('POST /api/actions/chat', () => {
  test('returns 400 when message is missing', async () => {
    const res = await request(app).post('/api/actions/chat').send({ message: '' });
    expect(res.status).toBe(400);
  });

  test('returns buddy reply and history for valid message', async () => {
    const res = await request(app).post('/api/actions/chat').send({
      message: 'Buddy help me with testing',
      sender: 'user',
      targetBots: ['buddy-bot'],
    });
    expect(res.status).toBe(200);
    expect(typeof res.body.reply).toBe('string');
    expect(Array.isArray(res.body.history)).toBe(true);
    expect(Array.isArray(res.body.training_signals)).toBe(true);
  });
});

describe('POST /api/actions/test-plan', () => {
  test('returns 400 when botName is missing', async () => {
    const res = await request(app).post('/api/actions/test-plan').send({});
    expect(res.status).toBe(400);
  });

  test('returns no-sql test plan for known bot', async () => {
    const res = await request(app).post('/api/actions/test-plan').send({
      botName: 'buddy-bot',
      depth: 'deep',
    });
    expect(res.status).toBe(200);
    expect(res.body.requested_bot).toBe('buddy-bot');
    expect(res.body.resolved_bot).toBe('buddy-bot');
    expect(Array.isArray(res.body.no_sql_steps)).toBe(true);
    expect(res.body.recommended_workflow).toBe('builder-simulation-sql.yml');
  });
});

describe('Charge monitoring APIs', () => {
  test('returns charge summary with policy', async () => {
    const res = await request(app).get('/api/actions/charges');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('summary');
    expect(res.body).toHaveProperty('policy');
    expect(Array.isArray(res.body.pending_approvals)).toBe(true);
  });

  test('creates charge preview and requires approval', async () => {
    const res = await request(app).post('/api/actions/charges/preview').send({
      description: 'Model API tokens',
      units: 1000,
      unit_cost_usd: 0.002,
    });
    expect(res.status).toBe(201);
    expect(res.body.approval_required).toBe(true);
    expect(res.body.preview).toHaveProperty('preview_id');
    expect(res.body.preview.status).toBe('pending_approval');
  });

  test('approves a charge preview', async () => {
    const previewRes = await request(app).post('/api/actions/charges/preview').send({
      description: 'Model API tokens',
      units: 500,
      unit_cost_usd: 0.003,
    });
    const previewId = previewRes.body.preview.preview_id;
    const approveRes = await request(app).post('/api/actions/charges/approve').send({
      preview_id: previewId,
      approved_by: 'unit-test',
    });
    expect(approveRes.status).toBe(200);
    expect(approveRes.body.approved.status).toBe('approved');
  });
});

describe('POST /api/actions/buddy-command', () => {
  test('runs single-target buddy command for known bot', async () => {
    const res = await request(app).post('/api/actions/buddy-command').send({
      target: 'buddy-bot',
      runMode: 'single',
      validation: 'deep',
    });
    expect(res.status).toBe(200);
    expect(res.body.mode).toBe('single');
    expect(res.body.target_count).toBe(1);
    expect(Array.isArray(res.body.results)).toBe(true);
  });

  test('returns 404 for unknown target bot', async () => {
    const res = await request(app).post('/api/actions/buddy-command').send({
      target: 'ghost-bot',
      runMode: 'single',
      validation: 'standard',
    });
    expect(res.status).toBe(404);
  });
});
