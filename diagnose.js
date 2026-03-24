/**
 * diagnose.js — DreamCobots CI Diagnostics Script
 *
 * Collects and reports diagnostic information useful for debugging CI failures:
 *   - Runtime versions (Node.js, npm)
 *   - package.json metadata and script inventory
 *   - Installed dependency count and presence of node_modules
 *   - Environment variables relevant to CI (non-sensitive)
 *   - .nvmrc / .eslintrc.json presence
 *   - package-lock.json integrity
 */

'use strict';

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.resolve(__dirname);

function section(title) {
  console.log(`\n${'═'.repeat(60)}`);
  console.log(` ${title}`);
  console.log('═'.repeat(60));
}

function run(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
  } catch {
    return '(unavailable)';
  }
}

// ─── Runtime ──────────────────────────────────────────────────────────────────
section('Runtime Versions');
console.log(`  Node.js : ${process.version}`);
console.log(`  npm     : ${run('npm --version')}`);
console.log(`  OS      : ${process.platform} ${process.arch}`);
console.log(`  CWD     : ${ROOT}`);

// ─── package.json ─────────────────────────────────────────────────────────────
section('package.json');
const pkgPath = path.join(ROOT, 'package.json');
try {
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  console.log(`  name      : ${pkg.name}`);
  console.log(`  version   : ${pkg.version}`);
  console.log(`  engines   : ${JSON.stringify(pkg.engines || {})}`);
  console.log(`  scripts   : ${Object.keys(pkg.scripts || {}).join(', ') || '(none)'}`);
  const deps = Object.keys(pkg.dependencies || {});
  const devDeps = Object.keys(pkg.devDependencies || {});
  console.log(`  dependencies    (${deps.length}): ${deps.join(', ') || '(none)'}`);
  console.log(`  devDependencies (${devDeps.length}): ${devDeps.join(', ') || '(none)'}`);
} catch (err) {
  console.error(`  ERROR reading package.json: ${err.message}`);
}

// ─── Config files ─────────────────────────────────────────────────────────────
section('Config Files');
const FILES_TO_CHECK = [
  '.nvmrc',
  '.eslintrc.json',
  '.eslintrc.js',
  '.eslintrc.yaml',
  'package-lock.json',
  '.gitignore',
  'Dockerfile',
  'docker-compose.yml',
];
for (const f of FILES_TO_CHECK) {
  const full = path.join(ROOT, f);
  if (fs.existsSync(full)) {
    const stat = fs.statSync(full);
    let extra = '';
    if (f === '.nvmrc') {
      extra = ` → ${fs.readFileSync(full, 'utf8').trim()}`;
    }
    console.log(`  ✅ ${f} (${stat.size} bytes)${extra}`);
  } else {
    console.log(`  ⚠️  ${f} — not found`);
  }
}

// ─── node_modules ─────────────────────────────────────────────────────────────
section('node_modules');
const nmPath = path.join(ROOT, 'node_modules');
if (fs.existsSync(nmPath)) {
  const count = fs.readdirSync(nmPath).filter(n => !n.startsWith('.')).length;
  console.log(`  ✅ node_modules present — ${count} top-level packages`);
} else {
  console.log('  ⚠️  node_modules not found — run `npm ci` or `npm install`');
}

// ─── CI Environment ───────────────────────────────────────────────────────────
section('CI Environment Variables (non-sensitive)');
const CI_VARS = ['CI', 'NODE_ENV', 'GITHUB_ACTIONS', 'GITHUB_WORKFLOW', 'GITHUB_RUN_ID', 'PORT'];
for (const v of CI_VARS) {
  console.log(`  ${v.padEnd(20)}: ${process.env[v] || '(not set)'}`);
}

// ─── Summary ──────────────────────────────────────────────────────────────────
section('Summary');
console.log('  Diagnostics complete. Review the sections above to identify issues.');
console.log('  Run `npm run apply-fix` to automatically validate and fix common problems.\n');

