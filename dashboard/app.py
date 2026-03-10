"""Flask dashboard application for DreamCobots platform."""
from flask import Flask, jsonify, request, render_template
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.resource_monitor import ResourceMonitor
from core.dashboard import DashboardData

_resource_monitor = ResourceMonitor()
_resource_monitor.start_monitoring()
_dashboard_data = DashboardData()


def create_app(orchestrator=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dreamcobots-secret-2024")

    @app.route("/")
    def index():
        """Serve the main dashboard page."""
        return render_template("index.html")

    @app.route("/api/metrics")
    def get_metrics():
        """Return current system resource metrics as JSON."""
        try:
            metrics = _resource_monitor.get_metrics()
            _dashboard_data.update_metrics(metrics)
            return jsonify(metrics)
        except Exception as e:
            return jsonify({"error": str(e), "cpu_percent": 0, "ram_percent": 0, "disk_percent": 0})

    @app.route("/api/bots")
    def get_bots():
        """Return status of all registered bots."""
        try:
            if orchestrator:
                statuses = orchestrator.get_all_statuses()
                bots_list = [
                    {"name": name, **status}
                    for name, status in statuses.items()
                ]
            else:
                bots_list = []
            return jsonify({"bots": bots_list, "total": len(bots_list)})
        except Exception as e:
            return jsonify({"error": str(e), "bots": [], "total": 0})

    @app.route("/api/revenue")
    def get_revenue():
        """Return total platform revenue across all bots."""
        try:
            total = 0.0
            bot_revenues = {}
            if orchestrator:
                for name, status in orchestrator.get_all_statuses().items():
                    rev = status.get("revenue", 0.0)
                    total += rev
                    bot_revenues[name] = rev
            return jsonify({
                "total_revenue": round(total, 2),
                "bot_revenues": bot_revenues,
                "currency": "USD",
                "revenue_share_percent": 50,
            })
        except Exception as e:
            return jsonify({"error": str(e), "total_revenue": 0.0})

    @app.route("/api/events")
    def get_events():
        """Return recent platform events and crash log."""
        try:
            events = _dashboard_data.get_events()
            if orchestrator and hasattr(orchestrator, "get_event_log"):
                orch_events = orchestrator.get_event_log()[-20:]
                events = orch_events + events
            return jsonify({"events": events[-50:], "total": len(events)})
        except Exception as e:
            return jsonify({"error": str(e), "events": []})

    @app.route("/api/bot/<name>/start", methods=["POST"])
    def start_bot(name):
        """Start a specific bot by name."""
        try:
            if orchestrator:
                statuses = orchestrator.get_all_statuses()
                if name in statuses:
                    bot = orchestrator._bots.get(name)
                    if bot and hasattr(bot, "start"):
                        bot.start()
                        _dashboard_data.add_event(f"Bot started: {name}")
                        return jsonify({"success": True, "bot": name, "status": "running"})
                    return jsonify({"success": False, "error": f"Cannot start {name}"})
                return jsonify({"success": False, "error": f"Bot {name} not found"})
            return jsonify({"success": False, "error": "No orchestrator available"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @app.route("/api/bot/<name>/stop", methods=["POST"])
    def stop_bot(name):
        """Stop a specific bot by name."""
        try:
            if orchestrator:
                bot = orchestrator._bots.get(name)
                if bot and hasattr(bot, "stop"):
                    bot.stop()
                    _dashboard_data.add_event(f"Bot stopped: {name}")
                    return jsonify({"success": True, "bot": name, "status": "stopped"})
                return jsonify({"success": False, "error": f"Bot {name} not found"})
            return jsonify({"success": False, "error": "No orchestrator available"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @app.route("/api/health")
    def health():
        """Health check endpoint."""
        return jsonify({"status": "ok", "platform": "DreamCobots", "version": "2.0.0",
                        "timestamp": datetime.utcnow().isoformat()})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080, debug=False)
