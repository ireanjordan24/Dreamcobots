import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { Octokit } from "@octokit/rest";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json());

const BOTS_FILE = path.join(__dirname, '..', 'config', 'bots.json');
const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

/**
 * Read and parse bots.json on every call to ensure data freshness.
 * Returns the parsed bots array or throws if the file is unavailable or malformed.
 */
function readBots() {
  const raw = fs.readFileSync(BOTS_FILE, 'utf8');
  return JSON.parse(raw);
}

// ---------------------------------------------------------------------------
// GET /api/get-bots
// Returns the full list of bots from bots.json in real time.
// Re-reads the file on each request to ensure data freshness.
// ---------------------------------------------------------------------------
app.get('/api/get-bots', (req, res) => {
  try {
    const bots = readBots();
    return res.json({
      success: true,
      count: bots.length,
      bots,
      timestamp: new Date().toISOString(),
    });
  } catch (err) {
    if (err.code === 'ENOENT') {
      return res.status(503).json({
        success: false,
        error: 'Bot registry unavailable: bots.json not found.',
      });
    }
    if (err instanceof SyntaxError) {
      return res.status(500).json({
        success: false,
        error: 'Bot registry malformed: bots.json contains invalid JSON.',
      });
    }
    return res.status(500).json({
      success: false,
      error: 'Internal server error while reading bot registry.',
    });
  }
});

// ---------------------------------------------------------------------------
// POST /api/bot-heartbeat
// Updates the lastHeartbeat timestamp for the named bot.
// ---------------------------------------------------------------------------
app.post('/api/bot-heartbeat', (req, res) => {
  const { botName } = req.body;
  if (!botName) {
    return res.status(400).json({ error: 'botName is required.' });
  }
  try {
    const bots = readBots();
    const bot = bots.find(b => b.name === botName);
    if (!bot) {
      return res.status(404).json({ error: `Bot '${botName}' not found.` });
    }
    bot.lastHeartbeat = new Date().toISOString();
    fs.writeFileSync(BOTS_FILE, JSON.stringify(bots, null, 2));
    return res.json({ status: 'updated', botName, lastHeartbeat: bot.lastHeartbeat });
  } catch (err) {
    return res.status(500).json({ error: 'Failed to update heartbeat.' });
  }
});

// ---------------------------------------------------------------------------
// POST /api/github-webhook
// Receives GitHub webhook events and triggers automation accordingly.
// ---------------------------------------------------------------------------
app.post('/api/github-webhook', (req, res) => {
  const event = req.headers['x-github-event'];
  const payload = req.body;
  console.log(`GitHub Event: ${event}`);

  switch (event) {
    case 'pull_request':
      if (payload.action === 'closed' && payload.pull_request?.merged) {
        console.log(`Merged PR: ${payload.pull_request.title}`);
        // Trigger auto-upgrade across dependent bots
      }
      break;
    case 'issues':
      if (payload.action === 'opened' && payload.issue?.labels?.some(l => l.name === 'bug')) {
        console.log(`Bug issue detected: ${payload.issue.title}`);
        // Trigger bot auto-fix
      }
      break;
    default:
      break;
  }

  res.sendStatus(200);
});

const PORT = process.env.PORT || 4000;

/* istanbul ignore next */
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => console.log(`🚀 Control Tower API running on port ${PORT}`));
}

export { app, readBots };
