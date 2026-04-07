/**
 * DreamCo Control Tower — Auto-Upgrade Engine
 *
 * Runs scheduled or on-demand upgrade operations across all registered bots:
 *   1. Pull latest code from origin/main (with auto-conflict resolution)
 *   2. Optionally run smoke tests
 *   3. Create auto-upgrade pull requests on GitHub
 *   4. Log results to the console (and optionally to a JSON log file)
 *
 * Usage
 * -----
 *   node automation/auto-upgrade-bots.js
 *   node automation/auto-upgrade-bots.js --dry-run
 */

import "dotenv/config";
import { readFileSync, writeFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { pullLatest, createPullRequest } from "../backend/bot-manager.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes("--dry-run");

// ---------------------------------------------------------------------------
// Load bots
// ---------------------------------------------------------------------------

function loadBots() {
  const raw = readFileSync(join(__dirname, "../config/bots.json"), "utf-8");
  return JSON.parse(raw);
}

// ---------------------------------------------------------------------------
// Core upgrade loop
// ---------------------------------------------------------------------------

async function runUpgrade() {
  const bots = loadBots();
  const timestamp = new Date().toISOString();
  const results = [];

  console.log("=".repeat(60));
  console.log("🏰 DreamCo Control Tower — Auto-Upgrade Engine");
  console.log(`   Timestamp : ${timestamp}`);
  console.log(`   Dry-run   : ${DRY_RUN}`);
  console.log(`   Bots      : ${bots.length}`);
  console.log("=".repeat(60));

  for (const bot of bots) {
    console.log(`\n🤖 Processing: ${bot.name} (repo: ${bot.repo})`);
    const result = {
      name: bot.name,
      repo: bot.repo,
      timestamp,
      pull: null,
      pr: null,
      success: false,
    };

    // --- Step 1: Pull latest code ---
    if (bot.repoPath && !DRY_RUN) {
      console.log(`  📥 Pulling latest for ${bot.repoPath}…`);
      result.pull = pullLatest(bot.repoPath);
      if (result.pull.success) {
        console.log(`  ✅ Pull succeeded`);
      } else {
        console.warn(`  ⚠️  Pull issue: ${result.pull.error}`);
      }
    } else {
      console.log(`  ⏭️  Pull skipped (dry-run=${DRY_RUN}, repoPath=${bot.repoPath || "not set"})`);
      result.pull = { skipped: true };
    }

    // --- Step 2: Create upgrade PR ---
    if (bot.repo && !DRY_RUN) {
      console.log(`  🔀 Creating auto-upgrade PR for ${bot.repo}…`);
      result.pr = await createPullRequest({
        repo: bot.repo,
        head: "auto-upgrade",
        title: `🤖 Auto-upgrade: ${bot.name} — ${timestamp}`,
        body: [
          "Automated upgrade by DreamCo Control Tower.",
          "",
          `- **Bot**: \`${bot.name}\``,
          `- **Tier**: ${bot.tier}`,
          `- **Timestamp**: ${timestamp}`,
          "- **Source**: GLOBAL AI SOURCES FLOW auto-upgrade engine",
        ].join("\n"),
      });
      if (result.pr.success) {
        console.log(`  ✅ PR created: ${result.pr.prUrl}`);
      } else {
        console.warn(`  ⚠️  PR skipped: ${result.pr.error}`);
      }
    } else {
      console.log(`  ⏭️  PR skipped (dry-run=${DRY_RUN}, repo=${bot.repo || "not set"})`);
      result.pr = { skipped: true };
    }

    result.success =
      (result.pull?.success !== false) && (result.pr?.success !== false);
    results.push(result);
  }

  // --- Summary ---
  const succeeded = results.filter((r) => r.success).length;
  const failed = results.length - succeeded;

  console.log("\n" + "=".repeat(60));
  console.log(`📊 Upgrade complete: ${succeeded}/${results.length} succeeded, ${failed} failed`);
  console.log("=".repeat(60));

  // Write log file
  const logPath = join(__dirname, "../upgrade-log.json");
  writeFileSync(logPath, JSON.stringify({ timestamp, results, succeeded, failed }, null, 2));
  console.log(`\n📁 Full log written to: ${logPath}`);

  return { succeeded, failed, results };
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

runUpgrade().catch((err) => {
  console.error("💥 Auto-upgrade engine crashed:", err);
  process.exit(1);
});
