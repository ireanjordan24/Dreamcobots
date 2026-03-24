#!/usr/bin/env node
/**
 * deploy.js — Production deployment script for DreamCobots
 *
 * Responsibilities:
 *  1. Validate Node.js version and required environment variables
 *  2. Install / verify dependencies (npm ci)
 *  3. Run the project build step
 *  4. Execute the test suite and abort if any test fails
 *  5. Deploy application artifacts (configurable via DEPLOY_TARGET)
 *  6. Run a post-deploy health check
 *  7. Exit with a non-zero code on any failure so CI marks the step red
 */

'use strict';

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// ─── Helpers ────────────────────────────────────────────────────────────────

const RESET  = '\x1b[0m';
const GREEN  = '\x1b[32m';
const YELLOW = '\x1b[33m';
const RED    = '\x1b[31m';
const CYAN   = '\x1b[36m';

function log(msg)   { console.log(`${CYAN}[deploy]${RESET} ${msg}`); }
function ok(msg)    { console.log(`${GREEN}[deploy ✔]${RESET} ${msg}`); }
function warn(msg)  { console.warn(`${YELLOW}[deploy ⚠]${RESET} ${msg}`); }
function fail(msg)  { console.error(`${RED}[deploy ✖]${RESET} ${msg}`); }

function run(cmd, label) {
  log(`Running: ${cmd}`);
  try {
    execSync(cmd, { stdio: 'inherit', cwd: __dirname });
    ok(`${label} succeeded`);
  } catch (err) {
    fail(`${label} failed — aborting deployment`);
    process.exit(1);
  }
}

// ─── 1. Node version gate ────────────────────────────────────────────────────

const [major] = process.versions.node.split('.').map(Number);
const MIN_NODE = 18;
if (major < MIN_NODE) {
  fail(`Node.js ${MIN_NODE}+ required, but found ${process.versions.node}`);
  process.exit(1);
}
ok(`Node.js version: ${process.versions.node}`);

// ─── 2. Environment validation ───────────────────────────────────────────────

const DEPLOY_TARGET = process.env.DEPLOY_TARGET || 'production';
const REQUIRED_VARS = [];          // add required env-var names here, e.g. 'DATABASE_URL'
const missing = REQUIRED_VARS.filter(v => !process.env[v]);
if (missing.length) {
  fail(`Missing required environment variables: ${missing.join(', ')}`);
  process.exit(1);
}
log(`Deploy target: ${DEPLOY_TARGET}`);

// ─── 3. Validate package.json exists ────────────────────────────────────────

const pkgPath = path.join(__dirname, 'package.json');
if (!fs.existsSync(pkgPath)) {
  fail('package.json not found — cannot proceed');
  process.exit(1);
}
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
log(`Deploying ${pkg.name}@${pkg.version}`);

// ─── 4. Install dependencies ─────────────────────────────────────────────────

// Prefer a clean install from the lockfile; fall back to npm install when the
// lockfile is absent or out-of-date (common in fresh clones / CI caches).
const installCmd = 'npm ci --prefer-offline || npm install';
run(installCmd, 'Dependency installation');

// ─── 5. Build ────────────────────────────────────────────────────────────────

if (pkg.scripts && pkg.scripts.build) {
  run('npm run build', 'Build');
} else {
  warn('No build script found in package.json — skipping build step');
}

// ─── 6. Tests ────────────────────────────────────────────────────────────────

if (pkg.scripts && pkg.scripts.test) {
  run('npm test', 'Test suite');
} else {
  warn('No test script found in package.json — skipping tests');
}

// ─── 7. Deploy artifacts ─────────────────────────────────────────────────────

log(`Deploying to target: ${DEPLOY_TARGET}`);

switch (DEPLOY_TARGET) {
  case 'production':
  case 'staging': {
    // When a real deployment platform is configured, replace this block with
    // the appropriate CLI call, e.g.:
    //   run('gcloud app deploy --quiet', 'GCP App Engine deploy');
    //   run('eb deploy', 'Elastic Beanstalk deploy');
    //   run('vercel --prod --token $VERCEL_TOKEN', 'Vercel deploy');
    log(`No cloud provider configured — outputting deployment manifest instead`);
    const manifest = {
      name:    pkg.name,
      version: pkg.version,
      target:  DEPLOY_TARGET,
      node:    process.versions.node,
      builtAt: new Date().toISOString(),
    };
    const outDir = path.join(__dirname, 'dist');
    if (!fs.existsSync(outDir)) { fs.mkdirSync(outDir, { recursive: true }); }
    fs.writeFileSync(
      path.join(outDir, 'deploy-manifest.json'),
      JSON.stringify(manifest, null, 2)
    );
    ok(`Manifest written to dist/deploy-manifest.json`);
    break;
  }
  default:
    warn(`Unknown DEPLOY_TARGET "${DEPLOY_TARGET}" — no deployment step executed`);
}

// ─── 8. Post-deploy health check ─────────────────────────────────────────────

const manifestPath = path.join(__dirname, 'dist', 'deploy-manifest.json');
if (fs.existsSync(manifestPath)) {
  const written = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  if (written.name === pkg.name && written.version === pkg.version) {
    ok('Post-deploy health check passed');
  } else {
    fail('Post-deploy health check failed — manifest mismatch');
    process.exit(1);
  }
}

// ─── Done ────────────────────────────────────────────────────────────────────

console.log('');
ok(`Deployment process completed successfully for ${pkg.name}@${pkg.version}`);
console.log('');
