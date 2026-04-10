/**
 * DreamCo Git Engine (v1.0)
 * ──────────────────────────────────────────────────────────────────────────
 * Handles all git operations for DreamCo bots:
 *   - Permission validation via GitHub API
 *   - Auto branch creation (bot/<BOT_NAME>/<timestamp>)
 *   - Structured commit messages
 *   - Safe push using DREAMCO_TOKEN
 *   - Automatic PR creation via GitHub API
 *   - Retry with exponential back-off (3 attempts)
 *   - Local failure queue for deferred retries
 *
 * Required env vars:
 *   DREAMCO_TOKEN  – Personal Access Token with repo + workflow + pull-requests
 *   BOT_NAME       – (optional) identifier for the calling bot; defaults to "core_bot"
 *
 * Usage:
 *   node git-engine.js
 */

'use strict';

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// ── Helpers ────────────────────────────────────────────────────────────────
const QUEUE_DIR = path.join(__dirname, 'queue');
const REPO = 'DreamCo-Technologies/Dreamcobots';
const BASE_BRANCH = 'main';
const API_BASE = 'https://api.github.com';

/**
 * Execute a shell command, streaming stdout/stderr to the console.
 * Returns a resolved Promise so it can be safely awaited inside async retry.
 * @param {string} cmd
 * @returns {Promise<void>}
 */
function run(cmd) {
  return Promise.resolve().then(() => execSync(cmd, { stdio: 'inherit' }));
}

/**
 * Make a JSON GitHub API request.
 * @param {string} endpoint  - path after API_BASE (e.g. "/user")
 * @param {object} [options] - fetch options
 * @returns {Promise<object>}
 */
async function githubRequest(endpoint, options = {}) {
  const token = process.env.DREAMCO_TOKEN;
  if (!token) {
    throw new Error(
      'DREAMCO_TOKEN is not set. Add it to Settings → Secrets → Actions.'
    );
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      Authorization: `token ${token}`,
      'Content-Type': 'application/json',
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`GitHub API ${endpoint} → ${res.status}: ${body}`);
  }

  return res.json();
}

// ── 1. Git Permission Validator ────────────────────────────────────────────

/**
 * Validate that DREAMCO_TOKEN grants write access to the target repo.
 * @returns {Promise<string>} authenticated GitHub login
 */
async function validateGitAccess() {
  console.log('🔐 Validating GitHub token access...');
  const user = await githubRequest('/user');
  console.log(`   Authenticated as: ${user.login}`);

  const repo = await githubRequest(`/repos/${REPO}`);
  const perms = repo.permissions || {};
  if (!perms.push && !perms.admin) {
    throw new Error(
      `Token user "${user.login}" does not have write access to ${REPO}.\n` +
        "Fix: add the user to the org with Write/Owner role, or use a PAT with 'repo' scope."
    );
  }

  console.log('   ✅ Token has write access.');
  return user.login;
}

// ── 2. Auto Retry (exponential back-off) ──────────────────────────────────

/**
 * Retry an async function up to `times` attempts with exponential back-off.
 * @param {() => Promise<any>} fn
 * @param {number} [times=3]
 * @returns {Promise<any>}
 */
async function retry(fn, times = 3) {
  let lastError;
  for (let attempt = 1; attempt <= times; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
      if (attempt < times) {
        const delay = attempt * 5000;
        console.warn(
          `   ⚠️  Attempt ${attempt}/${times} failed: ${err.message}. Retrying in ${delay / 1000}s…`
        );
        await new Promise((r) => setTimeout(r, delay));
      }
    }
  }
  throw lastError;
}

// ── 3. Local Failure Queue ─────────────────────────────────────────────────

/**
 * Persist a failed commit payload to the local queue for later retry.
 * @param {{ branch: string, message: string, timestamp: string }} commit
 */
function enqueueFailure(commit) {
  if (!fs.existsSync(QUEUE_DIR)) {
    fs.mkdirSync(QUEUE_DIR, { recursive: true });
  }
  const file = path.join(QUEUE_DIR, `${Date.now()}.json`);
  fs.writeFileSync(file, JSON.stringify(commit, null, 2));
  console.warn(`   📥 Failure queued for later retry: ${file}`);
}

// ── 4. Auto PR Creator ────────────────────────────────────────────────────

/**
 * Create a pull request for the given branch.
 * @param {string} branch
 * @param {string} botName
 * @returns {Promise<string>} PR URL
 */
async function createPR(branch, botName) {
  console.log(`🔀 Creating pull request for branch: ${branch}`);

  const pr = await retry(() =>
    githubRequest(`/repos/${REPO}/pulls`, {
      method: 'POST',
      body: JSON.stringify({
        title: `[${botName}] Auto update – ${new Date().toISOString()}`,
        head: branch,
        base: BASE_BRANCH,
        body:
          'Generated automatically by the **DreamCo Git Engine**.\n\n' +
          `- Bot: \`${botName}\`\n` +
          `- Branch: \`${branch}\`\n` +
          `- Timestamp: ${new Date().toUTCString()}`,
      }),
    })
  );

  console.log(`   ✅ PR created: ${pr.html_url}`);
  return pr.html_url;
}

// ── 5. Main Engine ────────────────────────────────────────────────────────

async function main() {
  const botName = process.env.BOT_NAME || 'core_bot';
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const branch = `bot/${botName}/${timestamp}`;
  const commitMsg = `[${botName}] auto update ${new Date().toISOString()}`;

  console.log('🚀 DreamCo Git Engine starting…');
  console.log(`   Bot:    ${botName}`);
  console.log(`   Branch: ${branch}`);

  // Step 1 – validate token
  await retry(() => validateGitAccess());

  // Step 2 – configure git identity (required in CI)
  await run('git config user.email "bot@dreamco-technologies.com"');
  await run('git config user.name "DreamCo Bot"');

  // Step 3 – create isolated branch
  await run(`git checkout -b ${branch}`);

  // Step 4 – stage all changes
  await run('git add .');

  // Check if there is anything to commit
  try {
    await run('git diff --cached --quiet');
    console.log('   ℹ️  Nothing to commit. Exiting cleanly.');
    return;
  } catch {
    // non-zero exit means there are staged changes — proceed
  }

  // Step 5 – commit
  await run(`git commit -m "${commitMsg}"`);

  // Step 6 – push + PR with retry & failure queue
  const token = process.env.DREAMCO_TOKEN;
  const pushUrl = `https://x-access-token:${token}@github.com/${REPO}.git`;

  const commitPayload = { branch, message: commitMsg, timestamp };

  try {
    await retry(() => run(`git push "${pushUrl}" ${branch}`));
    await createPR(branch, botName);
  } catch (err) {
    console.error(`❌ Push/PR failed after retries: ${err.message}`);
    enqueueFailure(commitPayload);
    process.exit(1);
  }

  console.log('✅ DreamCo Git Engine completed successfully.');
}

main().catch((err) => {
  console.error(`❌ Fatal error: ${err.message}`);
  process.exit(1);
});
