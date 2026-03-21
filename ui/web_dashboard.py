"""
DreamCo Web Dashboard — Flask-based centralized control interface.

Provides a real-time web UI to:
  - Monitor bot activity, performance logs, and revenue.
  - Enable manual bot creation, management, and overrides.
  - Visualize system behavior via REST endpoints consumed by a browser.

Usage
-----
    from ui.web_dashboard import create_app

    app = create_app()
    app.run(debug=True, port=5050)

Endpoints
---------
  GET  /                          — Dashboard HTML landing page
  GET  /api/status                — System-wide status JSON
  GET  /api/bots                  — Registered bot list with KPI scores
  POST /api/bots/register         — Register a new bot { "name": "...", "tier": "..." }
  GET  /api/revenue               — Revenue summary JSON
  GET  /api/leaderboard           — Bot leaderboard (top by composite KPI)
  GET  /api/underperformers       — Bots with composite score < threshold
  POST /api/record_run            — Record a bot run with KPIs
  GET  /api/history/<bot_name>    — Run history for a specific bot
  GET  /api/heartbeat             — Heartbeat summary for all monitored bots
  POST /api/heartbeat/ping        — Ping a bot { "bot_name": "..." }
  GET  /api/registry              — Full bot registry summary
  GET  /api/github/<repo>         — GitHub repo status for <repo>
  POST /api/deploy                — Deploy / register a new bot
  POST /api/upgrade-all           — Trigger auto-upgrade for all registry bots
"""

from __future__ import annotations

from typing import Any, Optional

try:
    from flask import Flask, jsonify, request, Response
    _FLASK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FLASK_AVAILABLE = False

from bots.ai_learning_system.database import BotPerformanceDB
from bots.control_center.control_center import ControlCenter
from bots.control_center.auto_upgrade import AutoUpgradeEngine


# ---------------------------------------------------------------------------
# HTML landing page (self-contained, no external CDN needed)
# ---------------------------------------------------------------------------

_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DreamCo Control Tower</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #0d0d0d; color: #e0e0e0; }
    header {
      background: linear-gradient(90deg, #1a1a2e, #16213e);
      padding: 18px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 2px solid #00d4aa;
    }
    header h1 { font-size: 1.6rem; color: #00d4aa; letter-spacing: 1px; }
    header span { font-size: 0.85rem; color: #aaa; }
    .tabs { display: flex; gap: 0; border-bottom: 1px solid #2a2a4a; padding: 0 24px; background: #111; }
    .tab {
      padding: 12px 20px; cursor: pointer; font-size: 0.85rem; color: #888;
      border-bottom: 3px solid transparent; transition: color 0.2s;
    }
    .tab.active, .tab:hover { color: #00d4aa; border-bottom-color: #00d4aa; }
    .tab-content { display: none; padding: 24px; }
    .tab-content.active { display: block; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card {
      background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 10px; padding: 20px;
    }
    .card h2 { font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .card .value { font-size: 2rem; font-weight: 700; color: #00d4aa; }
    .card .sub { font-size: 0.72rem; color: #666; margin-top: 4px; }
    .card.live-card .value { color: #00e676; }
    .card.warn-card .value { color: #ffab40; }
    .card.err-card .value { color: #ff6b6b; }
    table { width: 100%; border-collapse: collapse; margin-top: 6px; }
    th { text-align: left; font-size: 0.72rem; color: #888; border-bottom: 1px solid #2a2a4a; padding: 6px 4px; }
    td { font-size: 0.8rem; padding: 6px 4px; border-bottom: 1px solid #1a1a2e; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.68rem; font-weight: 600; }
    .badge-live   { background: #0d3320; color: #00e676; }
    .badge-ok     { background: #0d3320; color: #00d4aa; }
    .badge-err    { background: #3d1010; color: #ff6b6b; }
    .badge-idle   { background: #1a2a1a; color: #888; }
    .badge-warn   { background: #3d2a00; color: #ffab40; }
    .badge-offline { background: #2a1a1a; color: #ff6b6b; }
    btn, .btn {
      display: inline-block; padding: 8px 16px; border-radius: 6px; font-size: 0.8rem;
      cursor: pointer; border: none; font-weight: 600; transition: opacity 0.2s;
    }
    .btn-primary { background: #00d4aa; color: #0d0d0d; }
    .btn-secondary { background: #1a2a4a; color: #00d4aa; border: 1px solid #00d4aa; }
    .btn:hover { opacity: 0.85; }
    input, select {
      background: #111; border: 1px solid #2a2a4a; color: #e0e0e0;
      padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; width: 100%; margin-bottom: 10px;
    }
    label { font-size: 0.78rem; color: #888; display: block; margin-bottom: 4px; }
    .form-group { margin-bottom: 14px; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .alert { padding: 10px 14px; border-radius: 6px; font-size: 0.8rem; margin-bottom: 12px; }
    .alert-success { background: #0d3320; color: #00e676; }
    .alert-error   { background: #3d1010; color: #ff6b6b; }
    footer { text-align: center; color: #444; padding: 20px; font-size: 0.75rem; }
    #refresh-note { text-align: right; color: #555; font-size: 0.72rem; padding: 0 24px 4px; }
    .section-title { font-size: 1rem; color: #00d4aa; margin-bottom: 16px; font-weight: 600; }
    .health-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }
    .health-dot.healthy { background: #00e676; }
    .health-dot.degraded { background: #ff6b6b; }
    .empty-state { color: #555; font-size: 0.8rem; padding: 20px 0; text-align: center; }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>🏰 DreamCo Control Tower</h1>
      <span id="ts">Loading…</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
      <span class="health-dot" id="health-dot"></span>
      <span id="health-label" style="font-size:0.8rem;color:#888">—</span>
    </div>
  </header>

  <div class="tabs">
    <div class="tab active" onclick="switchTab('overview')">📊 Overview</div>
    <div class="tab" onclick="switchTab('bots')">🤖 Bots</div>
    <div class="tab" onclick="switchTab('github')">🔗 GitHub</div>
    <div class="tab" onclick="switchTab('revenue')">💰 Revenue</div>
    <div class="tab" onclick="switchTab('deploy')">🚀 Deploy</div>
    <div class="tab" onclick="switchTab('automation')">⚙️ Automation</div>
  </div>

  <!-- OVERVIEW TAB -->
  <div id="tab-overview" class="tab-content active">
    <div class="grid">
      <div class="card live-card"><h2>Live Bots</h2><div class="value" id="live-bots">—</div><div class="sub">heartbeat active</div></div>
      <div class="card"><h2>Registered Bots</h2><div class="value" id="total-bots">—</div></div>
      <div class="card"><h2>Total Revenue</h2><div class="value" id="total-revenue">—</div><div class="sub">USD</div></div>
      <div class="card"><h2>Avg Composite KPI</h2><div class="value" id="avg-kpi">—</div><div class="sub">0–100 scale</div></div>
      <div class="card warn-card"><h2>Underperformers</h2><div class="value" id="underperformers">—</div><div class="sub">score &lt; 30</div></div>
      <div class="card err-card"><h2>Offline Bots</h2><div class="value" id="offline-bots">—</div><div class="sub">missed heartbeat</div></div>
    </div>
    <div class="card">
      <div class="section-title">Recent Activity</div>
      <table><thead><tr><th>Bot</th><th>Status</th><th>Tier</th><th>Last Run</th><th>Runs</th></tr></thead>
      <tbody id="overview-bots"></tbody></table>
    </div>
  </div>

  <!-- BOTS TAB -->
  <div id="tab-bots" class="tab-content">
    <div class="section-title">Bot Registry</div>
    <div class="card">
      <table><thead><tr>
        <th>Bot Name</th><th>Status</th><th>Repo</th><th>Last Heartbeat</th>
        <th>Efficiency</th><th>ROI</th><th>Composite</th>
      </tr></thead>
      <tbody id="bots-table"></tbody></table>
    </div>
    <br/>
    <div class="card">
      <div class="section-title">Bot Leaderboard</div>
      <table><thead><tr><th>#</th><th>Bot</th><th>Efficiency</th><th>ROI</th><th>Reliability</th><th>Composite</th><th>Runs</th></tr></thead>
      <tbody id="leaderboard-body"></tbody></table>
    </div>
  </div>

  <!-- GITHUB TAB -->
  <div id="tab-github" class="tab-content">
    <div class="section-title">GitHub Repository Status</div>
    <div style="display:flex;gap:12px;margin-bottom:16px;align-items:flex-end;">
      <div style="flex:1"><label>Repository name</label><input id="gh-repo-input" placeholder="e.g. Dreamcobots" /></div>
      <button class="btn btn-primary" onclick="loadGithubRepo()">Check Repo</button>
    </div>
    <div id="gh-result" class="card" style="display:none;"></div>
    <br/>
    <div class="card">
      <div class="section-title">Conflict Alerts</div>
      <div id="conflict-table" class="empty-state">No conflict data — check a repository above.</div>
    </div>
  </div>

  <!-- REVENUE TAB -->
  <div id="tab-revenue" class="tab-content">
    <div class="section-title">Revenue Analytics</div>
    <div class="grid">
      <div class="card"><h2>Total Income</h2><div class="value" id="rev-total">—</div><div class="sub">USD</div></div>
      <div class="card"><h2>Revenue Entries</h2><div class="value" id="rev-entries">—</div></div>
    </div>
    <div class="card">
      <h2 style="margin-bottom:12px">Revenue by Source</h2>
      <table><thead><tr><th>Source</th><th>Amount (USD)</th><th>% of Total</th></tr></thead>
      <tbody id="revenue-body"></tbody></table>
    </div>
  </div>

  <!-- DEPLOY TAB -->
  <div id="tab-deploy" class="tab-content">
    <div class="section-title">🚀 One-Click Bot Deployment</div>
    <div style="max-width:560px;">
      <div id="deploy-alert" style="display:none;" class="alert"></div>
      <div class="card">
        <div class="form-row">
          <div class="form-group">
            <label>Bot Name *</label>
            <input id="deploy-name" placeholder="e.g. real_estate_bot" />
          </div>
          <div class="form-group">
            <label>GitHub Repo Name</label>
            <input id="deploy-repo" placeholder="e.g. Dreamcobots" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Tier</label>
            <select id="deploy-tier">
              <option value="free">Free</option>
              <option value="pro">Pro ($99/mo)</option>
              <option value="enterprise">Enterprise ($299/mo)</option>
            </select>
          </div>
          <div class="form-group">
            <label>Niche / Template</label>
            <select id="deploy-niche">
              <option value="">General</option>
              <option value="real_estate">Real Estate</option>
              <option value="sales">Sales / Lead Gen</option>
              <option value="fiverr">Fiverr Gigs</option>
              <option value="crypto">Crypto / Trading</option>
              <option value="affiliate">Affiliate Marketing</option>
            </select>
          </div>
        </div>
        <button class="btn btn-primary" onclick="deployBot()" style="width:100%">🚀 Deploy Bot</button>
      </div>
    </div>
  </div>

  <!-- AUTOMATION TAB -->
  <div id="tab-automation" class="tab-content">
    <div class="section-title">⚙️ Automation Controls</div>
    <div id="auto-alert" style="display:none;" class="alert"></div>
    <div class="grid" style="max-width:800px;">
      <div class="card" style="text-align:center;">
        <h2>Auto-Upgrade All</h2>
        <div class="sub" style="margin:10px 0">Pull latest, resolve conflicts, create PRs for all bots</div>
        <button class="btn btn-primary" onclick="triggerUpgradeAll()">⚡ Run Now</button>
      </div>
      <div class="card" style="text-align:center;">
        <h2>Heartbeat Check</h2>
        <div class="sub" style="margin:10px 0">Refresh live/offline status for all monitored bots</div>
        <button class="btn btn-secondary" onclick="loadHeartbeat()">🔄 Refresh</button>
      </div>
    </div>
    <br/>
    <div class="card">
      <div class="section-title">Heartbeat Monitor</div>
      <table><thead><tr><th>Bot</th><th>Status</th><th>Last Ping</th><th>Seconds Ago</th></tr></thead>
      <tbody id="heartbeat-table"><tr><td colspan="4" class="empty-state">Loading…</td></tr></tbody></table>
    </div>
    <br/>
    <div class="card">
      <div class="section-title">Auto-Upgrade Log</div>
      <div id="upgrade-log" class="empty-state">Run auto-upgrade to see results.</div>
    </div>
  </div>

  <p id="refresh-note">Auto-refreshes every 15 s</p>
  <footer>DreamCo Control Tower — Powered by the GLOBAL AI SOURCES FLOW framework</footer>

  <script>
    // ---- Tab switching ----
    function switchTab(name) {
      document.querySelectorAll('.tab').forEach((t, i) => {
        const ids = ['overview','bots','github','revenue','deploy','automation'];
        t.classList.toggle('active', ids[i] === name);
      });
      document.querySelectorAll('.tab-content').forEach(c => {
        c.classList.toggle('active', c.id === 'tab-' + name);
      });
      if (name === 'bots') { loadBots(); loadLeaderboard(); }
      if (name === 'revenue') loadRevenue();
      if (name === 'automation') loadHeartbeat();
    }

    // ---- Helpers ----
    function badgeHtml(status) {
      const cls = {live:'live', ok:'ok', idle:'idle', error:'err', offline:'offline',
                   updated:'ok', running:'ok', conflict_detected:'warn'}[status] || 'idle';
      return `<span class="badge badge-${cls}">${status}</span>`;
    }

    // ---- Overview ----
    async function loadOverview() {
      try {
        const [status, leader, revenue, hb] = await Promise.all([
          fetch('/api/status').then(r => r.json()),
          fetch('/api/leaderboard').then(r => r.json()),
          fetch('/api/revenue').then(r => r.json()),
          fetch('/api/heartbeat').then(r => r.json()),
        ]);

        document.getElementById('ts').textContent = new Date().toLocaleString();
        document.getElementById('total-bots').textContent = status.registered_bots ?? '—';
        document.getElementById('total-revenue').textContent = '$' + (revenue.total_income_usd ?? 0).toFixed(2);
        document.getElementById('avg-kpi').textContent =
          status.avg_composite_kpi != null ? status.avg_composite_kpi.toFixed(1) : '—';
        document.getElementById('underperformers').textContent = status.underperformers ?? '—';
        document.getElementById('live-bots').textContent = hb.live ?? '—';
        document.getElementById('offline-bots').textContent = hb.offline ?? '—';

        const dot = document.getElementById('health-dot');
        const lbl = document.getElementById('health-label');
        const h = status.health || 'unknown';
        dot.className = 'health-dot ' + (h === 'healthy' ? 'healthy' : 'degraded');
        lbl.textContent = h;

        const botsData = status.bot_status?.bots ?? {};
        const tbody = document.getElementById('overview-bots');
        const entries = Object.entries(botsData);
        if (entries.length) {
          tbody.innerHTML = entries.map(([name, b]) => `
            <tr>
              <td>${name}</td>
              <td>${badgeHtml(b.status)}</td>
              <td>${b.tier ?? '—'}</td>
              <td>${b.last_run ? new Date(b.last_run).toLocaleString() : '—'}</td>
              <td>${b.run_count ?? 0}</td>
            </tr>`).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No bots registered yet.</td></tr>';
        }
      } catch(e) { console.error('Overview load error:', e); }
    }

    // ---- Bots ----
    async function loadBots() {
      try {
        const data = await fetch('/api/bots').then(r => r.json());
        const tbody = document.getElementById('bots-table');
        if (data.bots && data.bots.length) {
          tbody.innerHTML = data.bots.map(b => `
            <tr>
              <td>${b.bot_name}</td>
              <td>${badgeHtml(b.status ?? 'idle')}</td>
              <td>${b.repo_name ?? '—'}</td>
              <td>${b.last_heartbeat ? new Date(b.last_heartbeat).toLocaleString() : '—'}</td>
              <td>${b.efficiency_score != null ? b.efficiency_score.toFixed(1) : '—'}</td>
              <td>${b.roi_score != null ? b.roi_score.toFixed(1) : '—'}</td>
              <td><strong style="color:#00d4aa">${b.composite_score != null ? b.composite_score.toFixed(1) : '—'}</strong></td>
            </tr>`).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No bots registered.</td></tr>';
        }
      } catch(e) { console.error('Bots load error:', e); }
    }

    async function loadLeaderboard() {
      try {
        const leader = await fetch('/api/leaderboard').then(r => r.json());
        const lbBody = document.getElementById('leaderboard-body');
        if (leader.leaderboard && leader.leaderboard.length) {
          lbBody.innerHTML = leader.leaderboard.map((b, i) => `
            <tr>
              <td>${i+1}</td><td>${b.bot_name}</td>
              <td>${b.efficiency_score.toFixed(1)}</td><td>${b.roi_score.toFixed(1)}</td>
              <td>${b.reliability_score.toFixed(1)}</td>
              <td><strong style="color:#00d4aa">${b.composite_score.toFixed(1)}</strong></td>
              <td>${b.total_runs}</td>
            </tr>`).join('');
        } else {
          lbBody.innerHTML = '<tr><td colspan="7" class="empty-state">No leaderboard data.</td></tr>';
        }
      } catch(e) { console.error('Leaderboard load error:', e); }
    }

    // ---- GitHub ----
    async function loadGithubRepo() {
      const repo = document.getElementById('gh-repo-input').value.trim();
      if (!repo) return;
      const el = document.getElementById('gh-result');
      el.style.display = 'block';
      el.innerHTML = '<span style="color:#888">Loading…</span>';
      try {
        const data = await fetch('/api/github/' + encodeURIComponent(repo)).then(r => r.json());
        el.innerHTML = `
          <div class="section-title">${data.repo} — ${badgeHtml(data.online ? 'live' : 'offline')}</div>
          <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>
          <tr><td>Open PRs</td><td>${data.open_prs ?? '—'}</td></tr>
          <tr><td>Last Commit</td><td>${data.last_commit_sha ? data.last_commit_sha + ' — ' + (data.last_commit_message || '') : '—'}</td></tr>
          <tr><td>Last Commit At</td><td>${data.last_commit_at || '—'}</td></tr>
          <tr><td>Last Workflow</td><td>${data.last_workflow_name || '—'} ${badgeHtml(data.last_workflow_status ?? 'unknown')}</td></tr>
          ${data.error ? '<tr><td>Error</td><td style="color:#ff6b6b">' + data.error + '</td></tr>' : ''}
          </tbody></table>`;
        const conflictEl = document.getElementById('conflict-table');
        if (data.last_workflow_status === 'failure') {
          conflictEl.innerHTML = `<div class="alert alert-error">⚠️ Workflow failure detected in <strong>${data.repo}</strong>. Consider running Auto-Upgrade.</div>`;
        } else if (data.open_prs > 3) {
          conflictEl.innerHTML = `<div class="alert" style="background:#3d2a00;color:#ffab40">⚡ ${data.open_prs} open PRs in <strong>${data.repo}</strong> — review recommended.</div>`;
        } else {
          conflictEl.innerHTML = '<div class="empty-state">No conflict alerts for this repository.</div>';
        }
      } catch(e) {
        el.innerHTML = `<span style="color:#ff6b6b">Error: ${e.message}</span>`;
      }
    }

    // ---- Revenue ----
    async function loadRevenue() {
      try {
        const revenue = await fetch('/api/revenue').then(r => r.json());
        document.getElementById('rev-total').textContent = '$' + (revenue.total_income_usd ?? 0).toFixed(2);
        document.getElementById('rev-entries').textContent = revenue.entry_count ?? 0;
        const total = revenue.total_income_usd || 1;
        const bySource = revenue.by_source ?? {};
        const entries = Object.entries(bySource);
        const tbody = document.getElementById('revenue-body');
        if (entries.length) {
          tbody.innerHTML = entries.sort((a,b) => b[1]-a[1]).map(([src, amt]) =>
            `<tr><td>${src}</td><td>$${amt.toFixed(2)}</td><td>${((amt/total)*100).toFixed(1)}%</td></tr>`
          ).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="3" class="empty-state">No revenue recorded yet.</td></tr>';
        }
      } catch(e) { console.error('Revenue load error:', e); }
    }

    // ---- Deploy ----
    async function deployBot() {
      const name = document.getElementById('deploy-name').value.trim();
      const repo = document.getElementById('deploy-repo').value.trim();
      const tier = document.getElementById('deploy-tier').value;
      const niche = document.getElementById('deploy-niche').value;
      const alertEl = document.getElementById('deploy-alert');
      if (!name) { showAlert(alertEl, 'error', 'Bot name is required.'); return; }
      try {
        const resp = await fetch('/api/deploy', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({bot_name: name, repo_name: repo, tier, niche}),
        });
        const data = await resp.json();
        if (resp.ok) {
          showAlert(alertEl, 'success', `✅ Bot "${name}" deployed successfully! Status: ${data.status}`);
          document.getElementById('deploy-name').value = '';
          document.getElementById('deploy-repo').value = '';
        } else {
          showAlert(alertEl, 'error', data.error || 'Deployment failed.');
        }
      } catch(e) { showAlert(alertEl, 'error', 'Network error: ' + e.message); }
    }

    // ---- Heartbeat ----
    async function loadHeartbeat() {
      try {
        const hb = await fetch('/api/heartbeat').then(r => r.json());
        const tbody = document.getElementById('heartbeat-table');
        const bots = hb.bots ?? {};
        const entries = Object.entries(bots);
        if (entries.length) {
          tbody.innerHTML = entries.map(([name, s]) => `
            <tr>
              <td>${name}</td>
              <td>${badgeHtml(s.status)}</td>
              <td>${s.pinged_at ? new Date(s.pinged_at).toLocaleString() : '—'}</td>
              <td>${s.seconds_since_ping != null ? s.seconds_since_ping + 's' : '—'}</td>
            </tr>`).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="4" class="empty-state">No heartbeat data yet.</td></tr>';
        }
      } catch(e) { console.error('Heartbeat load error:', e); }
    }

    // ---- Automation ----
    async function triggerUpgradeAll() {
      const alertEl = document.getElementById('auto-alert');
      showAlert(alertEl, 'success', '⏳ Running auto-upgrade…');
      try {
        const resp = await fetch('/api/upgrade-all', {method: 'POST'});
        const data = await resp.json();
        const logEl = document.getElementById('upgrade-log');
        if (data.results && data.results.length) {
          logEl.innerHTML = '<table><thead><tr><th>Bot</th><th>Repo</th><th>Result</th><th>Time</th></tr></thead><tbody>' +
            data.results.map(r => `<tr>
              <td>${r.bot_name}</td><td>${r.repo_name || '—'}</td>
              <td>${badgeHtml(r.success ? 'ok' : 'error')}</td>
              <td>${new Date(r.timestamp).toLocaleString()}</td>
            </tr>`).join('') + '</tbody></table>';
        } else {
          logEl.innerHTML = '<div class="empty-state">No bots in registry to upgrade. Register bots first.</div>';
        }
        showAlert(alertEl, 'success',
          `✅ Upgrade complete: ${data.succeeded}/${data.total} succeeded.`);
        loadHeartbeat();
      } catch(e) { showAlert(alertEl, 'error', 'Error: ' + e.message); }
    }

    function showAlert(el, type, msg) {
      el.style.display = 'block';
      el.className = 'alert alert-' + type;
      el.textContent = msg;
      if (type === 'success') setTimeout(() => el.style.display = 'none', 6000);
    }

    // ---- Boot ----
    loadOverview();
    setInterval(loadOverview, 15000);
  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app(
    control_center: Optional["ControlCenter"] = None,
    db: Optional[BotPerformanceDB] = None,
) -> Any:
    """Create and configure the Flask dashboard application.

    Parameters
    ----------
    control_center : ControlCenter, optional
        An existing ControlCenter instance.  A new one is created if omitted.
    db : BotPerformanceDB, optional
        An existing BotPerformanceDB.  A new in-memory DB is created if omitted.

    Returns
    -------
    Flask application instance (or a stub if Flask is not installed).
    """
    if not _FLASK_AVAILABLE:
        raise ImportError(
            "Flask is required for the web dashboard. "
            "Install it with: pip install flask flask-cors"
        )

    cc = control_center or ControlCenter()
    perf_db = db or BotPerformanceDB()

    app = Flask(__name__)

    # ---------------------------------------------------------------
    # Landing page
    # ---------------------------------------------------------------

    @app.route("/")
    def index() -> Response:
        return Response(_DASHBOARD_HTML, mimetype="text/html")

    # ---------------------------------------------------------------
    # Status
    # ---------------------------------------------------------------

    @app.route("/api/status")
    def api_status() -> Response:
        monitoring = cc.get_monitoring_dashboard()
        db_stats = perf_db.get_stats()
        return jsonify({
            **monitoring,
            "avg_composite_kpi": db_stats["avg_composite_score"],
            "underperformers": db_stats["underperformers_below_30"],
        })

    # ---------------------------------------------------------------
    # Bots
    # ---------------------------------------------------------------

    @app.route("/api/bots")
    def api_bots() -> Response:
        bot_status = cc.get_status()
        scores = {s["bot_name"]: s for s in perf_db.get_all_scores()}
        bots = []
        for name, meta in bot_status.get("bots", {}).items():
            entry = dict(meta)
            entry["bot_name"] = name
            entry.update(scores.get(name, {}))
            bots.append(entry)
        return jsonify({"bots": bots, "total": len(bots)})

    @app.route("/api/bots/register", methods=["POST"])
    def api_register_bot() -> Response:
        data = request.get_json(silent=True) or {}
        name = data.get("name", "").strip()
        if not name:
            return jsonify({"error": "Bot name is required."}), 400

        class _Stub:
            """Minimal stub registered when no real bot instance is provided."""
            def __init__(self, tier_str: str):
                from bots.ai_learning_system.tiers import Tier as LSTier
                try:
                    self.tier = LSTier(tier_str)
                except ValueError:
                    self.tier = LSTier.FREE

        cc.register_bot(name, _Stub(data.get("tier", "free")))
        return jsonify({"registered": name, "status": "ok"}), 201

    # ---------------------------------------------------------------
    # Revenue
    # ---------------------------------------------------------------

    @app.route("/api/revenue")
    def api_revenue() -> Response:
        return jsonify(cc.get_income_summary())

    # ---------------------------------------------------------------
    # Leaderboard
    # ---------------------------------------------------------------

    @app.route("/api/leaderboard")
    def api_leaderboard() -> Response:
        top_n = request.args.get("top", 10, type=int)
        return jsonify({"leaderboard": perf_db.get_leaderboard(top_n=top_n)})

    # ---------------------------------------------------------------
    # Underperformers
    # ---------------------------------------------------------------

    @app.route("/api/underperformers")
    def api_underperformers() -> Response:
        threshold = request.args.get("threshold", 30.0, type=float)
        return jsonify({
            "threshold": threshold,
            "underperformers": perf_db.get_underperformers(threshold=threshold),
        })

    # ---------------------------------------------------------------
    # Record run
    # ---------------------------------------------------------------

    @app.route("/api/record_run", methods=["POST"])
    def api_record_run() -> Response:
        data = request.get_json(silent=True) or {}
        bot_name = data.get("bot_name", "").strip()
        if not bot_name:
            return jsonify({"error": "bot_name is required."}), 400
        entry = perf_db.record_run(
            bot_name=bot_name,
            kpis=data.get("kpis", {}),
            status=data.get("status", "ok"),
            notes=data.get("notes", ""),
        )
        return jsonify(entry), 201

    # ---------------------------------------------------------------
    # Run history
    # ---------------------------------------------------------------

    @app.route("/api/history/<bot_name>")
    def api_history(bot_name: str) -> Response:
        limit = request.args.get("limit", 50, type=int)
        history = perf_db.get_run_history(bot_name, limit=limit)
        return jsonify({"bot_name": bot_name, "history": history})

    # ---------------------------------------------------------------
    # Heartbeat
    # ---------------------------------------------------------------

    @app.route("/api/heartbeat")
    def api_heartbeat() -> Response:
        summary = cc.heartbeat.summary()
        all_status = cc.heartbeat.get_all_status()
        return jsonify({**summary, "bots": all_status})

    @app.route("/api/heartbeat/ping", methods=["POST"])
    def api_heartbeat_ping() -> Response:
        data = request.get_json(silent=True) or {}
        bot_name = data.get("bot_name", "").strip()
        if not bot_name:
            return jsonify({"error": "bot_name is required."}), 400
        result = cc.ping_bot(bot_name, metadata=data.get("metadata"))
        return jsonify(result), 200

    # ---------------------------------------------------------------
    # Bot Registry
    # ---------------------------------------------------------------

    @app.route("/api/registry")
    def api_registry() -> Response:
        return jsonify({
            "summary": cc.registry.summary(),
            "bots": cc.registry.get_all(),
        })

    # ---------------------------------------------------------------
    # GitHub repo status
    # ---------------------------------------------------------------

    @app.route("/api/github/<repo_name>")
    def api_github_repo(repo_name: str) -> Response:
        status = cc.get_github_repo_status(repo_name)
        return jsonify(status)

    # ---------------------------------------------------------------
    # Deploy a new bot
    # ---------------------------------------------------------------

    @app.route("/api/deploy", methods=["POST"])
    def api_deploy() -> Response:
        data = request.get_json(silent=True) or {}
        bot_name = data.get("bot_name", "").strip()
        if not bot_name:
            return jsonify({"error": "bot_name is required."}), 400

        result = cc.deploy_bot(
            bot_name=bot_name,
            repo_name=data.get("repo_name", ""),
            tier=data.get("tier", "free"),
            config={"niche": data.get("niche", "")},
        )
        return jsonify(result), 201

    # ---------------------------------------------------------------
    # Trigger auto-upgrade across all registry bots
    # ---------------------------------------------------------------

    @app.route("/api/upgrade-all", methods=["POST"])
    def api_upgrade_all() -> Response:
        engine = AutoUpgradeEngine(
            registry=cc.registry,
            github=cc.github,
            dry_run=True,          # safe default — set False with token in prod
        )
        summary = engine.run_all()
        return jsonify(summary), 200

    return app


__all__ = ["create_app"]
