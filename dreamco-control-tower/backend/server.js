/**
 * DreamCo Control Tower — Express Backend Server
 *
 * Provides REST API endpoints for:
 *   GET  /api/heartbeat          — Control Tower liveness check
 *   GET  /api/bots               — List all registered bots and their status
 *   GET  /api/bots/:name         — Single bot status
 *   POST /api/bots/:name/upgrade — Trigger bot upgrade
 *   GET  /api/repos              — List monitored repositories
 *   GET  /api/repos/:owner/:repo — Repository status (PRs, issues, commits)
 *   POST /webhook                — GitHub webhook receiver
 *   GET  /api/dashboard          — Aggregated dashboard data
 */

import express from "express";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import path from "path";
import { checkAllBots } from "./heartbeat-check.js";
import { getRepoStatus } from "./repo-manager.js";
import { upgradeSingleBot } from "./bot-manager.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CONFIG_DIR = path.join(__dirname, "..", "config");

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

// ---------------------------------------------------------------------------
// CORS helper for local development
// ---------------------------------------------------------------------------
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function loadBots() {
  try {
    return JSON.parse(readFileSync(path.join(CONFIG_DIR, "bots.json"), "utf8"));
  } catch {
    return [];
  }
}

function loadRepos() {
  try {
    return JSON.parse(readFileSync(path.join(CONFIG_DIR, "repos.json"), "utf8"));
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// Routes
// ---------------------------------------------------------------------------

/** Control Tower heartbeat — confirms backend is alive. */
app.get("/api/heartbeat", (_req, res) => {
  res.json({
    status: "ok",
    service: "DreamCo Control Tower",
    timestamp: new Date().toISOString(),
  });
});

/** List all bots with live heartbeat status. */
app.get("/api/bots", async (_req, res) => {
  try {
    const heartbeats = await checkAllBots();
    res.json({ bots: heartbeats, total: heartbeats.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/** Single bot status. */
app.get("/api/bots/:name", async (req, res) => {
  try {
    const bots = await checkAllBots();
    const bot = bots.find(
      (b) => b.name.toLowerCase() === req.params.name.toLowerCase()
    );
    if (!bot) return res.status(404).json({ error: "Bot not found" });
    res.json(bot);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/** Trigger upgrade for a single bot. */
app.post("/api/bots/:name/upgrade", async (req, res) => {
  try {
    const allBots = loadBots();
    const botConfig = allBots.find(
      (b) => b.name.toLowerCase() === req.params.name.toLowerCase()
    );
    if (!botConfig) return res.status(404).json({ error: "Bot not found" });
    const result = await upgradeSingleBot(botConfig);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/** List all monitored repos with cached metadata. */
app.get("/api/repos", async (_req, res) => {
  try {
    const repos = loadRepos();
    const token = process.env.GITHUB_TOKEN;
    if (!token) {
      return res.json({ repos, total: repos.length, note: "GITHUB_TOKEN not set — live data unavailable" });
    }
    const enriched = await Promise.all(
      repos.map((r) => getRepoStatus(r.owner, r.name, token))
    );
    res.json({ repos: enriched, total: enriched.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/** Single repo status. */
app.get("/api/repos/:owner/:repo", async (req, res) => {
  try {
    const token = process.env.GITHUB_TOKEN;
    if (!token) return res.status(503).json({ error: "GITHUB_TOKEN not configured" });
    const status = await getRepoStatus(req.params.owner, req.params.repo, token);
    res.json(status);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/** Aggregated dashboard payload used by the React frontend. */
app.get("/api/dashboard", async (_req, res) => {
  try {
    const heartbeats = await checkAllBots();
    const repos = loadRepos();
    const active = heartbeats.filter((b) => b.status === "active").length;
    const offline = heartbeats.filter((b) => b.status === "offline").length;

    res.json({
      timestamp: new Date().toISOString(),
      summary: {
        totalBots: heartbeats.length,
        activeBots: active,
        offlineBots: offline,
        totalRepos: repos.length,
      },
      bots: heartbeats,
      repos,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GitHub Webhook receiver.
 *
 * Supported events: push, pull_request, issues, workflow_run.
 * In production, verify the X-Hub-Signature-256 header using WEBHOOK_SECRET.
 */
app.post("/webhook", (req, res) => {
  const event = req.headers["x-github-event"];
  const payload = req.body;

  console.log(`[webhook] Received event: ${event}`);

  switch (event) {
    case "push":
      console.log(`[webhook] Push to ${payload.repository?.full_name} on ${payload.ref}`);
      break;
    case "pull_request":
      console.log(
        `[webhook] PR #${payload.number} ${payload.action} in ${payload.repository?.full_name}`
      );
      break;
    case "issues":
      console.log(
        `[webhook] Issue #${payload.issue?.number} ${payload.action}: ${payload.issue?.title}`
      );
      break;
    case "workflow_run":
      console.log(
        `[webhook] Workflow "${payload.workflow_run?.name}" ${payload.action} — ${payload.workflow_run?.conclusion ?? "in progress"}`
      );
      break;
    default:
      console.log(`[webhook] Unhandled event: ${event}`);
  }

  res.json({ received: true, event });
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
app.listen(PORT, () => {
  console.log(`🏰 DreamCo Control Tower backend running on port ${PORT}`);
});

export default app;
