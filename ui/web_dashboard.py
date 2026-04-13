"""
DreamCo Web Dashboard — Flask-based centralized control interface.

Provides a real-time web UI to:
  - Monitor bot activity, performance logs, and revenue.
  - Enable manual bot creation, management, and overrides.
  - Visualize system behavior via REST endpoints consumed by a browser.
  - Launch high-revenue bots live via Go Live buttons.
  - Display live GitHub Actions workflow runs and artifacts (read-only).
  - Show Quantum Bot system health.

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
  POST /api/bots/<name>/go_live   — Deploy / activate a bot instance
  GET  /api/bots/catalog          — Full bot catalog with Go Live status
  GET  /api/revenue               — Revenue summary JSON
  GET  /api/leaderboard           — Bot leaderboard (top by composite KPI)
  GET  /api/underperformers       — Bots with composite score < threshold
  POST /api/record_run            — Record a bot run with KPIs
  GET  /api/history/<bot_name>    — Run history for a specific bot
  GET  /api/github/workflows      — Live GitHub Actions workflow runs (read-only)
  GET  /api/github/artifacts      — GitHub Actions artifact list (read-only)
  GET  /api/quantum/status        — Quantum Bot system health check
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Optional

try:
    from flask import Flask, jsonify, request, Response
    _FLASK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FLASK_AVAILABLE = False

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _requests = None  # type: ignore[assignment]
    _REQUESTS_AVAILABLE = False

from bots.ai_learning_system.database import BotPerformanceDB
from bots.control_center.control_center import ControlCenter


# ---------------------------------------------------------------------------
# GitHub Actions helpers (read-only)
# ---------------------------------------------------------------------------

_GITHUB_API_BASE = "https://api.github.com"
_DEFAULT_REPO = "DreamCo-Technologies/Dreamcobots"

# Clamp per_page to this range for GitHub API requests
_GITHUB_PER_PAGE_MIN = 1
_GITHUB_PER_PAGE_MAX = 100

# Cached QuantumAIBot check result (reset on each process start)
_quantum_cache: dict = {}
_QUANTUM_CACHE_TTL_S = 60


def _github_headers() -> dict:
    """Return HTTP headers for GitHub API calls, including auth if available."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_github_workflows(repo: str = _DEFAULT_REPO, per_page: int = 10) -> dict:
    """Fetch the most recent GitHub Actions workflow runs for *repo*.

    Returns a dict with ``runs`` (list) and ``source`` (``"github_api"`` or
    ``"unavailable"``).  Never raises — failures produce a safe placeholder
    payload so the dashboard always renders.
    """
    if not _REQUESTS_AVAILABLE:
        return {"runs": [], "source": "unavailable", "reason": "requests library not installed"}

    per_page = max(_GITHUB_PER_PAGE_MIN, min(_GITHUB_PER_PAGE_MAX, per_page))
    url = f"{_GITHUB_API_BASE}/repos/{repo}/actions/runs"
    try:
        resp = _requests.get(
            url,
            headers=_github_headers(),
            params={"per_page": per_page},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            runs = [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "workflow_id": r.get("workflow_id"),
                    "status": r["status"],
                    "conclusion": r.get("conclusion"),
                    "branch": r.get("head_branch"),
                    "event": r.get("event"),
                    "run_started_at": r.get("run_started_at"),
                    "updated_at": r.get("updated_at"),
                    "url": r.get("html_url"),
                }
                for r in data.get("workflow_runs", [])
            ]
            return {"runs": runs, "total_count": data.get("total_count", len(runs)), "source": "github_api"}
        return {
            "runs": [],
            "source": "unavailable",
            "reason": f"GitHub API returned HTTP {resp.status_code}",
        }
    except Exception:  # noqa: BLE001
        return {"runs": [], "source": "unavailable", "reason": "GitHub API request failed"}


def _fetch_github_artifacts(repo: str = _DEFAULT_REPO, per_page: int = 10) -> dict:
    """Fetch the most recent GitHub Actions artifacts for *repo*.

    Returns a dict with ``artifacts`` (list) and ``source``.  Never raises.
    """
    if not _REQUESTS_AVAILABLE:
        return {"artifacts": [], "source": "unavailable", "reason": "requests library not installed"}

    per_page = max(_GITHUB_PER_PAGE_MIN, min(_GITHUB_PER_PAGE_MAX, per_page))
    url = f"{_GITHUB_API_BASE}/repos/{repo}/actions/artifacts"
    try:
        resp = _requests.get(
            url,
            headers=_github_headers(),
            params={"per_page": per_page},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            artifacts = [
                {
                    "id": a["id"],
                    "name": a["name"],
                    "size_in_bytes": a.get("size_in_bytes", 0),
                    "created_at": a.get("created_at"),
                    "expires_at": a.get("expires_at"),
                    "expired": a.get("expired", False),
                    "url": a.get("url"),
                }
                for a in data.get("artifacts", [])
            ]
            return {"artifacts": artifacts, "total_count": data.get("total_count", len(artifacts)), "source": "github_api"}
        return {
            "artifacts": [],
            "source": "unavailable",
            "reason": f"GitHub API returned HTTP {resp.status_code}",
        }
    except Exception:  # noqa: BLE001
        return {"artifacts": [], "source": "unavailable", "reason": "GitHub API request failed"}


def _check_quantum_bot_status() -> dict:
    """Return a cached Quantum Bot health summary (read-only).

    Instantiates QuantumAIBot (FREE tier) at most once per
    ``_QUANTUM_CACHE_TTL_S`` seconds to avoid expensive repeated
    construction on every request.  Never raises.
    """
    global _quantum_cache  # noqa: PLW0603
    import time as _time

    now = _time.monotonic()
    if _quantum_cache and now - _quantum_cache.get("_cached_at", 0) < _QUANTUM_CACHE_TTL_S:
        result = {k: v for k, v in _quantum_cache.items() if not k.startswith("_")}
        result["checked_at"] = datetime.now(timezone.utc).isoformat()
        return result

    try:
        _ai_models_dir = os.path.join(os.path.dirname(__file__), "..", "bots", "ai-models-integration")
        import sys as _sys  # noqa: PLC0415
        if _ai_models_dir not in _sys.path:
            _sys.path.insert(0, _ai_models_dir)

        from bots.quantum_ai_bot.quantum_ai_bot import QuantumAIBot  # noqa: PLC0415
        from bots.ai_learning_system.tiers import Tier  # noqa: PLC0415

        bot = QuantumAIBot(tier=Tier.FREE)
        result = {
            "status": "ok",
            "bot": "QuantumAIBot",
            "tier": bot.tier.value,
            "engines": [
                "QuantumCircuitSimulator",
                "HybridQuantumAIModel",
                "QuantumOptimizer",
                "QuantumPartnershipManager",
            ],
        }
    except Exception:  # noqa: BLE001
        result = {
            "status": "error",
            "bot": "QuantumAIBot",
            "reason": "Quantum Bot health check failed",
        }

    _quantum_cache = {**result, "_cached_at": now}
    result["checked_at"] = datetime.now(timezone.utc).isoformat()
    return result


# ---------------------------------------------------------------------------
# Bot catalog — all high-revenue bots available for Go Live deployment
# ---------------------------------------------------------------------------

_BOT_CATALOG: list[dict] = [
    {
        "name": "multi_source_lead_scraper",
        "display_name": "Lead Generator Bot",
        "emoji": "🎯",
        "description": "Scrapes qualified leads from Google, LinkedIn, Twitter, Reddit & Yelp. AI-scored, CRM-exportable.",
        "revenue_model": "$29–$299/mo subscription",
        "category": "Sales & Marketing",
        "priority": 1,
    },
    {
        "name": "real_estate_bot",
        "display_name": "Real Estate Finder Bot",
        "emoji": "🏠",
        "description": "Finds investment properties, calculates cap rates, cash flow, and ROI across 10 US cities.",
        "revenue_model": "$29–$299/mo subscription",
        "category": "Real Estate",
        "priority": 2,
    },
    {
        "name": "ai_side_hustle_bot",
        "display_name": "AI Hustle Generator",
        "emoji": "💰",
        "description": "Identifies, launches, and monetizes side hustles with AI-powered content, income calculators & marketing plans.",
        "revenue_model": "$29–$99/mo subscription",
        "category": "Entrepreneurship",
        "priority": 3,
    },
    {
        "name": "stripe_payment_bot",
        "display_name": "Stripe Payment Bot",
        "emoji": "💳",
        "description": "Full Stripe integration: checkouts, subscriptions, invoices, webhooks, fraud detection & Connect.",
        "revenue_model": "2.2–2.9% transaction fee + $29–$299/mo",
        "category": "Payments",
        "priority": 4,
    },
    {
        "name": "fiverr_bot",
        "display_name": "Fiverr Automation Bot",
        "emoji": "🎨",
        "description": "Automates Fiverr gig creation, order management, client communication, and upselling.",
        "revenue_model": "$29–$99/mo subscription",
        "category": "Freelance",
        "priority": 5,
    },
    {
        "name": "crypto_bot",
        "display_name": "Crypto Trading Bot",
        "emoji": "₿",
        "description": "Algorithmic crypto portfolio management, price alerts, and auto-trading strategies.",
        "revenue_model": "$29–$299/mo subscription",
        "category": "Finance",
        "priority": 6,
    },
    {
        "name": "open_claw_bot",
        "display_name": "Client Acquisition Bot",
        "emoji": "🤝",
        "description": "Automates client outreach, proposal generation, and deal closing across multiple channels.",
        "revenue_model": "$99–$299/mo subscription",
        "category": "Sales",
        "priority": 7,
    },
    {
        "name": "affiliate_bot",
        "display_name": "Affiliate Marketing Bot",
        "emoji": "🔗",
        "description": "Manages affiliate programs, tracks commissions, and automates partner payouts.",
        "revenue_model": "$29–$99/mo + commission share",
        "category": "Marketing",
        "priority": 8,
    },
    {
        "name": "ai_chatbot",
        "display_name": "AI Customer Support Bot",
        "emoji": "💬",
        "description": "GPT-powered customer support with tier-based conversation limits and CRM integration.",
        "revenue_model": "$29–$299/mo subscription",
        "category": "Customer Service",
        "priority": 9,
    },
    {
        "name": "deal_finder_bot",
        "display_name": "Deal Finder Bot",
        "emoji": "🔍",
        "description": "Scans marketplaces for arbitrage opportunities and profit-generating deals.",
        "revenue_model": "$29–$99/mo subscription",
        "category": "E-Commerce",
        "priority": 10,
    },
]


# ---------------------------------------------------------------------------
# HTML landing page (self-contained, no external CDN needed)
# ---------------------------------------------------------------------------

_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DreamCo Empire Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #0d0d0d; color: #e0e0e0; }
    header {
      background: linear-gradient(90deg, #1a1a2e, #16213e);
      padding: 18px 32px;
      display: flex;
      align-items: center;
      gap: 14px;
      border-bottom: 2px solid #00d4aa;
    }
    header h1 { font-size: 1.6rem; color: #00d4aa; letter-spacing: 1px; }
    header span { font-size: 0.85rem; color: #aaa; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; padding: 24px; }
    .card {
      background: #1a1a2e;
      border: 1px solid #2a2a4a;
      border-radius: 10px;
      padding: 20px;
    }
    .card h2 { font-size: 0.85rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .card .value { font-size: 2rem; font-weight: 700; color: #00d4aa; }
    .card .sub { font-size: 0.75rem; color: #666; margin-top: 4px; }
    table { width: 100%; border-collapse: collapse; margin-top: 6px; }
    th { text-align: left; font-size: 0.75rem; color: #888; border-bottom: 1px solid #2a2a4a; padding: 6px 4px; }
    td { font-size: 0.8rem; padding: 6px 4px; border-bottom: 1px solid #1a1a2e; }
    .badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 600;
    }
    .badge-ok     { background: #0d3320; color: #00d4aa; }
    .badge-live   { background: #0a3a10; color: #22cc44; }
    .badge-err    { background: #3d1010; color: #ff6b6b; }
    .badge-idle   { background: #1a2a1a; color: #888; }
    footer { text-align: center; color: #444; padding: 20px; font-size: 0.75rem; }
    #refresh-note { text-align: right; color: #555; font-size: 0.72rem; padding: 0 24px 4px; }

    /* Bot catalog cards */
    .bot-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
      padding: 0 24px 24px;
    }
    .bot-card {
      background: #1a1a2e;
      border: 1px solid #2a2a4a;
      border-radius: 10px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: border-color 0.2s;
    }
    .bot-card:hover { border-color: #00d4aa; }
    .bot-card.live { border-color: #22cc44; }
    .bot-card .bot-title {
      font-size: 1rem;
      font-weight: 700;
      color: #e0e0e0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .bot-card .bot-desc { font-size: 0.78rem; color: #888; line-height: 1.4; }
    .bot-card .bot-revenue {
      font-size: 0.75rem;
      color: #00d4aa;
      font-weight: 600;
    }
    .bot-card .bot-category {
      font-size: 0.7rem;
      color: #666;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .go-live-btn {
      margin-top: 4px;
      padding: 8px 16px;
      background: linear-gradient(135deg, #00d4aa, #0090ff);
      border: none;
      border-radius: 6px;
      color: #fff;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      letter-spacing: 0.5px;
      transition: opacity 0.15s, transform 0.1s;
      align-self: flex-start;
    }
    .go-live-btn:hover { opacity: 0.88; transform: translateY(-1px); }
    .go-live-btn:active { transform: translateY(0); }
    .go-live-btn:disabled {
      background: #0a3a10;
      color: #22cc44;
      cursor: default;
      opacity: 1;
    }
    .go-live-btn.loading { opacity: 0.6; cursor: wait; }
    .live-indicator {
      display: inline-block;
      width: 8px;
      height: 8px;
      background: #22cc44;
      border-radius: 50%;
      margin-left: 6px;
      box-shadow: 0 0 6px #22cc44;
      animation: pulse 1.4s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.35; }
    }
    .section-header {
      padding: 4px 24px 12px;
      font-size: 0.85rem;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>🤖 DreamCo Empire Dashboard</h1>
      <span id="ts">Loading…</span>
    </div>
  </header>

  <div class="grid" id="kpi-cards">
    <div class="card"><h2>Registered Bots</h2><div class="value" id="total-bots">—</div></div>
    <div class="card"><h2>Total Revenue</h2><div class="value" id="total-revenue">—</div><div class="sub">USD</div></div>
    <div class="card"><h2>Avg Composite KPI</h2><div class="value" id="avg-kpi">—</div><div class="sub">0–100 scale</div></div>
    <div class="card"><h2>Underperformers</h2><div class="value" id="underperformers">—</div><div class="sub">score &lt; 30</div></div>
  </div>

  <!-- ── HIGH-REVENUE BOT CATALOG ── -->
  <p class="section-header">🚀 High-Revenue Bots — Go Live</p>
  <div class="bot-grid" id="bot-catalog">
    <div class="card" style="color:#555">Loading bot catalog…</div>
  </div>

  <div style="padding: 0 24px 24px;">
    <div class="card">
      <h2 style="margin-bottom:12px;">Bot Leaderboard</h2>
      <table>
        <thead>
          <tr>
            <th>#</th><th>Bot Name</th><th>Efficiency</th>
            <th>ROI</th><th>Reliability</th><th>Composite</th><th>Runs</th>
          </tr>
        </thead>
        <tbody id="leaderboard-body">
          <tr><td colspan="7" style="color:#555">Loading…</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div style="padding: 0 24px 24px;">
    <div class="card">
      <h2 style="margin-bottom:12px;">Revenue by Source</h2>
      <table>
        <thead><tr><th>Source</th><th>Amount (USD)</th></tr></thead>
        <tbody id="revenue-body">
          <tr><td colspan="2" style="color:#555">Loading…</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- ── QUANTUM BOT SYSTEM HEALTH ── -->
  <p class="section-header">⚛️ Quantum Bot — System Health</p>
  <div class="grid" id="quantum-health" style="padding-top:0">
    <div class="card">
      <h2>Quantum Status</h2>
      <div class="value" id="quantum-status">—</div>
      <div class="sub" id="quantum-tier"></div>
    </div>
    <div class="card">
      <h2>Quantum Engines</h2>
      <div id="quantum-engines" style="font-size:0.8rem;color:#aaa;margin-top:6px">Loading…</div>
    </div>
    <div class="card">
      <h2>Last Checked</h2>
      <div class="value" style="font-size:1rem;color:#aaa" id="quantum-checked">—</div>
    </div>
  </div>

  <!-- ── WORKFLOW MONITOR ── -->
  <p class="section-header">⚙️ GitHub Actions — Workflow Monitor (Live, Read-Only)</p>
  <div style="padding: 0 24px 24px;">
    <div class="card">
      <h2 style="margin-bottom:12px;">Recent Workflow Runs</h2>
      <table id="workflow-table">
        <thead>
          <tr>
            <th>Workflow</th><th>Branch</th><th>Event</th>
            <th>Status</th><th>Conclusion</th><th>Started</th><th>Link</th>
          </tr>
        </thead>
        <tbody id="workflow-body">
          <tr><td colspan="7" style="color:#555">Loading…</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- ── ARTIFACTS ── -->
  <p class="section-header">📦 GitHub Actions — Artifacts</p>
  <div style="padding: 0 24px 24px;">
    <div class="card">
      <h2 style="margin-bottom:12px;">Available Artifacts</h2>
      <table>
        <thead>
          <tr><th>Name</th><th>Size</th><th>Created</th><th>Expires</th><th>Status</th></tr>
        </thead>
        <tbody id="artifact-body">
          <tr><td colspan="5" style="color:#555">Loading…</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <p id="refresh-note">Auto-refreshes every 15 s</p>
  <footer>DreamCo Empire OS — Powered by the GLOBAL AI SOURCES FLOW framework</footer>

  <script>
    // Track which bots are live in this session
    const liveBots = new Set();

    async function goLive(botName, btn) {
      btn.classList.add('loading');
      btn.disabled = true;
      btn.textContent = '⏳ Deploying…';
      try {
        const res = await fetch(`/api/bots/${encodeURIComponent(botName)}/go_live`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tier: 'pro' }),
        });
        const data = await res.json();
        if (res.ok) {
          liveBots.add(botName);
          btn.textContent = '✅ Live';
          btn.classList.remove('loading');
          btn.closest('.bot-card').classList.add('live');
          const ind = document.createElement('span');
          ind.className = 'live-indicator';
          btn.after(ind);
        } else {
          btn.textContent = '⚠ Error';
          btn.classList.remove('loading');
          btn.disabled = false;
        }
      } catch (e) {
        btn.textContent = '⚠ Error';
        btn.classList.remove('loading');
        btn.disabled = false;
      }
    }

    async function loadWorkflows() {
      try {
        const [wf, art] = await Promise.all([
          fetch('/api/github/workflows').then(r => r.json()),
          fetch('/api/github/artifacts').then(r => r.json()),
        ]);

        const wfBody = document.getElementById('workflow-body');
        const runs = wf.runs || [];
        if (runs.length) {
          const conclusionColor = c => {
            if (c === 'success') return '#22cc44';
            if (c === 'failure') return '#ff4444';
            if (c === 'cancelled') return '#ff9900';
            return '#888';
          };
          wfBody.innerHTML = runs.map(r => `
            <tr>
              <td>${r.name || '—'}</td>
              <td>${r.branch || '—'}</td>
              <td>${r.event || '—'}</td>
              <td>${r.status || '—'}</td>
              <td style="color:${conclusionColor(r.conclusion)};font-weight:600">${r.conclusion || '—'}</td>
              <td>${r.run_started_at ? new Date(r.run_started_at).toLocaleString() : '—'}</td>
              <td>${r.url ? `<a href="${r.url}" target="_blank" rel="noopener" style="color:#00d4aa">View</a>` : '—'}</td>
            </tr>`).join('');
        } else {
          const msg = wf.reason ? `Unavailable: ${wf.reason}` : 'No workflow runs found.';
          wfBody.innerHTML = `<tr><td colspan="7" style="color:#555">${msg}</td></tr>`;
        }

        const artBody = document.getElementById('artifact-body');
        const artifacts = art.artifacts || [];
        if (artifacts.length) {
          artBody.innerHTML = artifacts.map(a => {
            const kb = a.size_in_bytes ? (a.size_in_bytes / 1024).toFixed(1) + ' KB' : '—';
            const created = a.created_at ? new Date(a.created_at).toLocaleString() : '—';
            const expires = a.expires_at ? new Date(a.expires_at).toLocaleDateString() : '—';
            const statusBadge = a.expired
              ? '<span style="color:#ff4444">Expired</span>'
              : '<span style="color:#22cc44">Active</span>';
            return `<tr><td>${a.name}</td><td>${kb}</td><td>${created}</td><td>${expires}</td><td>${statusBadge}</td></tr>`;
          }).join('');
        } else {
          const msg = art.reason ? `Unavailable: ${art.reason}` : 'No artifacts found.';
          artBody.innerHTML = `<tr><td colspan="5" style="color:#555">${msg}</td></tr>`;
        }
      } catch (e) {
        console.error('Workflow load error:', e);
      }
    }

    async function loadQuantum() {
      try {
        const q = await fetch('/api/quantum/status').then(r => r.json());
        const statusEl = document.getElementById('quantum-status');
        const tierEl = document.getElementById('quantum-tier');
        const engEl = document.getElementById('quantum-engines');
        const checkedEl = document.getElementById('quantum-checked');
        if (q.status === 'ok') {
          statusEl.textContent = '✅ OK';
          statusEl.style.color = '#22cc44';
          tierEl.textContent = 'Tier: ' + (q.tier || '—');
          engEl.innerHTML = (q.engines || []).map(e => `<div>✓ ${e}</div>`).join('');
        } else {
          statusEl.textContent = '⚠ Error';
          statusEl.style.color = '#ff4444';
          tierEl.textContent = q.reason || '';
          engEl.textContent = '';
        }
        checkedEl.textContent = q.checked_at ? new Date(q.checked_at).toLocaleTimeString() : '—';
      } catch (e) {
        console.error('Quantum status load error:', e);
      }
    }

    async function loadCatalog() {
      try {
        const data = await fetch('/api/bots/catalog').then(r => r.json());
        const grid = document.getElementById('bot-catalog');
        grid.innerHTML = '';
        (data.catalog || []).forEach(bot => {
          const isLive = liveBots.has(bot.name) || bot.is_live;
          const card = document.createElement('div');
          card.className = 'bot-card' + (isLive ? ' live' : '');
          card.innerHTML = `
            <div class="bot-title">${bot.emoji || '🤖'} ${bot.display_name}</div>
            <div class="bot-category">${bot.category}</div>
            <div class="bot-desc">${bot.description}</div>
            <div class="bot-revenue">💰 ${bot.revenue_model}</div>
            <button
              class="go-live-btn"
              onclick="goLive('${bot.name}', this)"
              ${isLive ? "disabled" : ""}
            >${isLive ? '✅ Live' : '🚀 Go Live'}</button>
            ${isLive ? '<span class="live-indicator"></span>' : ''}
          `;
          grid.appendChild(card);
        });
      } catch (e) {
        console.error('Catalog load error:', e);
      }
    }

    async function loadAll() {
      try {
        const [status, leader, revenue] = await Promise.all([
          fetch('/api/status').then(r => r.json()),
          fetch('/api/leaderboard').then(r => r.json()),
          fetch('/api/revenue').then(r => r.json()),
        ]);

        document.getElementById('ts').textContent = new Date().toLocaleString();
        document.getElementById('total-bots').textContent = status.registered_bots ?? '—';
        document.getElementById('total-revenue').textContent =
          '$' + (revenue.total_income_usd ?? 0).toFixed(2);
        document.getElementById('avg-kpi').textContent =
          status.avg_composite_kpi != null ? status.avg_composite_kpi.toFixed(1) : '—';
        document.getElementById('underperformers').textContent =
          status.underperformers ?? '—';

        const lbBody = document.getElementById('leaderboard-body');
        if (leader.leaderboard && leader.leaderboard.length) {
          lbBody.innerHTML = leader.leaderboard.map((b, i) => `
            <tr>
              <td>${i + 1}</td>
              <td>${b.bot_name}</td>
              <td>${b.efficiency_score.toFixed(1)}</td>
              <td>${b.roi_score.toFixed(1)}</td>
              <td>${b.reliability_score.toFixed(1)}</td>
              <td><strong style="color:#00d4aa">${b.composite_score.toFixed(1)}</strong></td>
              <td>${b.total_runs}</td>
            </tr>`).join('');
        } else {
          lbBody.innerHTML = '<tr><td colspan="7" style="color:#555">No data yet — record some bot runs.</td></tr>';
        }

        const revBody = document.getElementById('revenue-body');
        const bySource = revenue.by_source ?? {};
        const entries = Object.entries(bySource);
        if (entries.length) {
          revBody.innerHTML = entries
            .sort((a, b) => b[1] - a[1])
            .map(([src, amt]) => `<tr><td>${src}</td><td>$${amt.toFixed(2)}</td></tr>`)
            .join('');
        } else {
          revBody.innerHTML = '<tr><td colspan="2" style="color:#555">No revenue recorded yet.</td></tr>';
        }

      } catch (e) {
        console.error('Dashboard load error:', e);
      }
    }

    loadCatalog();
    loadAll();
    loadWorkflows();
    loadQuantum();
    setInterval(() => { loadAll(); loadWorkflows(); loadQuantum(); }, 15000);
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

    @app.route("/api/bots/catalog")
    def api_bots_catalog() -> Response:
        """Return the full high-revenue bot catalog with Go Live status."""
        registered = set(cc.get_status().get("bots", {}).keys())
        catalog = []
        for bot in _BOT_CATALOG:
            entry = dict(bot)
            entry["is_live"] = bot["name"] in registered
            catalog.append(entry)
        return jsonify({"catalog": catalog, "total": len(catalog)})

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

    @app.route("/api/bots/<bot_name>/go_live", methods=["POST"])
    def api_go_live(bot_name: str) -> Response:
        """
        Activate / deploy a bot instance.

        Registers the bot with the ControlCenter if not already registered,
        records an initial run, and returns the deployment record.

        Request JSON (optional)
        -----------------------
        tier : str
            Desired subscription tier (``free``, ``pro``, ``enterprise``).
            Defaults to ``pro``.

        Returns
        -------
        201
            Deployment record with status, timestamp, and bot metadata.
        400
            If ``bot_name`` is blank.
        """
        bot_name = bot_name.strip()
        if not bot_name:
            return jsonify({"error": "bot_name is required."}), 400

        data = request.get_json(silent=True) or {}
        tier_str = data.get("tier", "pro")

        class _LiveStub:
            """Minimal live bot stub."""
            def __init__(self, t: str):
                from bots.ai_learning_system.tiers import Tier as LSTier
                try:
                    self.tier = LSTier(t)
                except ValueError:
                    self.tier = LSTier.FREE

        # Register (idempotent — no-op if already present)
        cc.register_bot(bot_name, _LiveStub(tier_str))

        # Record the go-live run event
        perf_db.record_run(
            bot_name=bot_name,
            kpis={"revenue_usd": 0.0, "tasks_completed": 0},
            status="ok",
            notes=f"Go Live deployment — tier: {tier_str}",
        )

        deployment = {
            "bot_name": bot_name,
            "status": "live",
            "tier": tier_str,
            "deployed_at": datetime.now(timezone.utc).isoformat(),
            "message": f"Bot '{bot_name}' is now live on the {tier_str} tier.",
        }
        return jsonify(deployment), 201

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
    # GitHub Actions — read-only workflow monitor
    # ---------------------------------------------------------------

    @app.route("/api/github/workflows")
    def api_github_workflows() -> Response:
        """Return recent GitHub Actions workflow runs (read-only)."""
        repo = os.environ.get("GITHUB_REPOSITORY", _DEFAULT_REPO)
        per_page = max(_GITHUB_PER_PAGE_MIN, min(_GITHUB_PER_PAGE_MAX, request.args.get("per_page", 10, type=int)))
        data = _fetch_github_workflows(repo=repo, per_page=per_page)
        return jsonify(data)

    @app.route("/api/github/artifacts")
    def api_github_artifacts() -> Response:
        """Return recent GitHub Actions artifacts (read-only)."""
        repo = os.environ.get("GITHUB_REPOSITORY", _DEFAULT_REPO)
        per_page = max(_GITHUB_PER_PAGE_MIN, min(_GITHUB_PER_PAGE_MAX, request.args.get("per_page", 10, type=int)))
        data = _fetch_github_artifacts(repo=repo, per_page=per_page)
        return jsonify(data)

    # ---------------------------------------------------------------
    # Quantum Bot — system health check (read-only)
    # ---------------------------------------------------------------

    @app.route("/api/quantum/status")
    def api_quantum_status() -> Response:
        """Return Quantum Bot health status (read-only instantiation check)."""
        return jsonify(_check_quantum_bot_status())

    return app


__all__ = ["create_app", "_BOT_CATALOG", "_fetch_github_workflows", "_fetch_github_artifacts", "_check_quantum_bot_status"]
