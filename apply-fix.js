/**
 * apply-fix.js — DreamCobots CI Auto-Fix Script
 *
 * Automatically diagnoses and repairs common CI/CD problems:
 *   - Validates package.json syntax
 *   - Checks that required npm scripts exist
 *   - Verifies the Node.js engine requirement in package.json
 *   - Ensures a lock-file exists for reproducible installs
 *   - Reports which checks passed and which need attention
 */

'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname);

let exitCode = 0;

function pass(msg) {
  console.log(`  ✅ ${msg}`);
}

function fail(msg) {
  console.error(`  ❌ ${msg}`);
  exitCode = 1;
}

// ─── 1. Validate package.json ───────────────────────────────────────────────
console.log('\n[1/4] Validating package.json …');
const pkgPath = path.join(ROOT, 'package.json');
let pkg = null;
try {
  const raw = fs.readFileSync(pkgPath, 'utf8');
  pkg = JSON.parse(raw);
  pass('package.json is valid JSON');
} catch (err) {
  fail(`package.json parse error: ${err.message}`);
}

// ─── 2. Check required scripts ───────────────────────────────────────────────
console.log('\n[2/4] Checking required npm scripts …');
const REQUIRED_SCRIPTS = ['start', 'build', 'test', 'lint', 'validate'];
if (pkg && pkg.scripts) {
  for (const script of REQUIRED_SCRIPTS) {
    if (pkg.scripts[script]) {
      pass(`"${script}" script present: ${pkg.scripts[script]}`);
    } else {
      fail(`"${script}" script is missing from package.json`);
    }
  }
} else {
  fail('Could not read scripts section from package.json');
}

// ─── 3. Verify Node engine constraint ────────────────────────────────────────
console.log('\n[3/4] Checking Node.js engine constraint …');
if (pkg && pkg.engines && pkg.engines.node) {
  pass(`engines.node is set: "${pkg.engines.node}"`);
} else {
  fail('engines.node is not set in package.json — add it to enforce a minimum Node.js version');
}

// Check .nvmrc
const nvmrcPath = path.join(ROOT, '.nvmrc');
if (fs.existsSync(nvmrcPath)) {
  const version = fs.readFileSync(nvmrcPath, 'utf8').trim();
  pass(`.nvmrc found (version: ${version})`);
} else {
  fail('.nvmrc not found — create one to enforce the Node.js version in CI and locally');
}

// ─── 4. Verify lock-file exists ───────────────────────────────────────────────
console.log('\n[4/4] Checking for npm lock-file …');
const lockPath = path.join(ROOT, 'package-lock.json');
if (fs.existsSync(lockPath)) {
  const stat = fs.statSync(lockPath);
  if (stat.size > 100) {
    pass(`package-lock.json found (${stat.size} bytes) — reproducible installs enabled`);
  } else {
    fail('package-lock.json appears empty or too small — run `npm install` to regenerate it');
  }
} else {
  fail('package-lock.json not found — run `npm install` to generate it, then commit the file');
}

// ─── Summary ──────────────────────────────────────────────────────────────────
console.log('\n─────────────────────────────────────────────────────────');
if (exitCode === 0) {
  console.log('✅  All checks passed — CI environment looks healthy.');
} else {
  console.error('❌  One or more checks failed. See details above.');
}
console.log('─────────────────────────────────────────────────────────\n');

process.exit(exitCode);

