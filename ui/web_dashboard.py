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
    .badge-ok   { background: #0d3320; color: #00d4aa; }
    .badge-err  { background: #3d1010; color: #ff6b6b; }
    .badge-idle { background: #1a2a1a; color: #888; }
    footer { text-align: center; color: #444; padding: 20px; font-size: 0.75rem; }
    #refresh-note { text-align: right; color: #555; font-size: 0.72rem; padding: 0 24px 4px; }
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

  <p id="refresh-note">Auto-refreshes every 15 s</p>
  <footer>DreamCo Empire OS — Powered by the GLOBAL AI SOURCES FLOW framework</footer>

  <script>
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

    loadAll();
    setInterval(loadAll, 15000);
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

    return app


__all__ = ["create_app"]
