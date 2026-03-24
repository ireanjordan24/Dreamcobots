/**
 * diagnose.js — DreamCobots System Diagnostics
 *
 * Performs health checks on the project environment:
 *   - Required files present
 *   - package.json scripts integrity
 *   - Node.js version compatibility
 *   - npm dependencies installed
 *   - Key bot directories present
 *
 * Exit codes:
 *   0 — all checks passed (CI: no auto-fix needed)
 *   1 — one or more checks failed (CI: triggers apply-fix)
 */

'use strict';

const fs   = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = __dirname;
let issues = [];

// ── Helpers ────────────────────────────────────────────────────────────────

function check(label, fn) {
  try {
    const result = fn();
    if (result) {
      console.log(`  ✅  ${label}`);
    } else {
      console.error(`  ❌  ${label}`);
      issues.push(label);
    }
  } catch (err) {
    console.error(`  ❌  ${label} — ${err.message}`);
    issues.push(`${label}: ${err.message}`);
  }
}

function fileExists(rel) {
  return fs.existsSync(path.join(ROOT, rel));
}

// ── Checks ─────────────────────────────────────────────────────────────────

console.log('\n🔍  DreamCobots Diagnostics\n');

// 1. Required root files
console.log('📁  Required files:');
['package.json', 'index.js', 'apply-fix.js', 'deploy.js', 'requirements.txt'].forEach(f => {
  check(f, () => fileExists(f));
});

// 2. package.json scripts integrity
console.log('\n📦  package.json scripts:');
const pkg = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8'));
const requiredScripts = ['start', 'test', 'build', 'diagnose', 'apply-fix', 'deploy'];
requiredScripts.forEach(s => {
  check(`script "${s}"`, () => Boolean(pkg.scripts && pkg.scripts[s]));
});

// 3. Node.js version (>=14 required)
console.log('\n🟢  Node.js version:');
check('Node.js >= 14', () => {
  const major = parseInt(process.versions.node.split('.')[0], 10);
  return major >= 14;
});

// 4. node_modules installed
console.log('\n📂  Dependencies:');
check('node_modules present', () => fileExists('node_modules'));
check('express installed', () => fileExists('node_modules/express'));

// 5. Key bot directories
console.log('\n🤖  Bot directories:');
['bots', 'bots/fiverr_bot', 'bots/multi_source_lead_scraper', 'bots/ci_auto_fix_bot'].forEach(d => {
  check(d, () => fileExists(d));
});

// 6. GitHub workflows present
console.log('\n⚙️   CI workflows:');
check('.github/workflows/', () => fileExists('.github/workflows'));

// ── Summary ────────────────────────────────────────────────────────────────

console.log('\n─────────────────────────────────────');
if (issues.length === 0) {
  console.log('✅  All checks passed. System is healthy.\n');
  process.exit(0);
} else {
  console.error(`❌  ${issues.length} issue(s) detected:\n`);
  issues.forEach(i => console.error(`    • ${i}`));
  console.error('\nRun `npm run apply-fix` to attempt automatic remediation.\n');
  process.exit(1);
}
