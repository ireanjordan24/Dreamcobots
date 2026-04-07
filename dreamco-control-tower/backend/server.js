/**
 * DreamCo Control Tower — Express API Server
 *
 * Endpoints
 * ---------
 *   GET  /                        — Health check / server info
 *   GET  /api/bots                — All bots with heartbeat status
 *   GET  /api/bots/:name          — Single bot status
 *   POST /api/bots/:name/ping     — Record heartbeat ping
 *   POST /api/bots/:name/pull     — Git pull latest
 *   POST /api/bots/:name/pr       — Create auto-upgrade PR
 *   GET  /api/repos/:name         — GitHub repo status
 *   POST /api/repos/multi         — Multiple repos at once
 *   GET  /api/revenue             — Revenue summary
 *   POST /api/upgrade-all         — Run auto-upgrade for all bots
 *   GET  /api/heartbeat           — All heartbeat statuses
 *
 * Usage
 * -----
 *   cd dreamco-control-tower
 *   npm install
 *   GITHUB_TOKEN=xxx node backend/server.js
 */

import "dotenv/config";
import express from "express";
import cors from "cors";
import rateLimit from "express-rate-limit";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

import botsRouter from "./api/bots.js";
import reposRouter from "./api/repos.js";
import revenueRouter from "./api/revenue.js";
import botManager from "./bot-manager.js";
import { pullLatest, createPullRequest } from "./bot-manager.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT || 4000;

const app = express();
app.use(cors());
app.use(express.json());

// Rate limiting — protect all API and static routes
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,   // 15 minutes
  max: 200,                    // max requests per window per IP
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "Too many requests — please try again later." },
});
app.use(limiter);

// Serve the React frontend from ../frontend
app.use(express.static(join(__dirname, "../frontend")));

// ---------------------------------------------------------------------------
// API Routes
// ---------------------------------------------------------------------------

app.use("/api/bots", botsRouter);
app.use("/api/repos", reposRouter);
app.use("/api/revenue", revenueRouter);

// Health check
app.get("/api", (req, res) => {
  res.json({
    name: "DreamCo Control Tower API",
    version: "1.0.0",
    status: "ok",
    timestamp: new Date().toISOString(),
    endpoints: [
      "GET  /api/bots",
      "GET  /api/bots/:name",
      "POST /api/bots/:name/ping",
      "POST /api/bots/:name/pull",
      "POST /api/bots/:name/pr",
      "GET  /api/repos/:name",
      "POST /api/repos/multi",
      "GET  /api/revenue",
      "POST /api/upgrade-all",
      "GET  /api/heartbeat",
    ],
  });
});

// All heartbeat statuses
app.get("/api/heartbeat", (req, res) => {
  const hb = botManager.getAllHeartbeats();
  const live = Object.values(hb).filter((h) => h.status === "live").length;
  const offline = Object.values(hb).filter((h) => h.status === "offline").length;
  res.json({ live, offline, total: Object.keys(hb).length, bots: hb });
});

// Upgrade-all: pull latest + create PRs for all configured bots
app.post("/api/upgrade-all", async (req, res) => {
  const dryRun = req.body?.dry_run !== false; // safe default
  const bots = botManager.loadBots();
  const results = [];

  for (const bot of bots) {
    const result = { name: bot.name, repo: bot.repo, timestamp: new Date().toISOString() };

    if (!dryRun && bot.repoPath) {
      result.pull = pullLatest(bot.repoPath);
    } else {
      result.pull = { skipped: true, dry_run: dryRun };
    }

    if (!dryRun && bot.repo) {
      result.pr = await createPullRequest({
        repo: bot.repo,
        head: "auto-upgrade",
        title: `🤖 Auto-upgrade from DreamCo Control Tower — ${bot.name}`,
      });
    } else {
      result.pr = { skipped: true, dry_run: dryRun };
    }

    result.success = !result.pull?.error && !result.pr?.error;
    results.push(result);
  }

  const succeeded = results.filter((r) => r.success).length;
  res.json({
    total: results.length,
    succeeded,
    failed: results.length - succeeded,
    dry_run: dryRun,
    timestamp: new Date().toISOString(),
    results,
  });
});

// Fallback: serve the frontend SPA for any non-API route
app.get("*", (req, res) => {
  res.sendFile(join(__dirname, "../frontend/index.html"));
});

// ---------------------------------------------------------------------------
// Start server
// ---------------------------------------------------------------------------

app.listen(PORT, () => {
  console.log(`🏰 DreamCo Control Tower running at http://localhost:${PORT}`);
  console.log(`📡 API available at  http://localhost:${PORT}/api`);
});

export default app;
