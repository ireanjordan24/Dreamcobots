"""
DreamCo Lite — Flask Backend

Routes
------
GET  /                 → Serve the single-page UI
POST /api/leads        → Find leads for a niche + location
POST /api/messages     → Generate outreach messages for provided leads
POST /api/run-automation → Find leads + generate messages in one shot
POST /api/debug        → Analyse an error log and suggest fixes
GET  /api/health       → Health-check endpoint
"""

from __future__ import annotations

import os
import sys
import logging

# Ensure the repo root is on sys.path so dreamco_lite can be imported both
# when run from the repo root and from the dreamco_lite/ directory itself.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from flask import Flask, request, jsonify, send_from_directory  # noqa: E402
from flask_cors import CORS  # noqa: E402

from dreamco_lite.money_bot import MoneyBot  # noqa: E402
from dreamco_lite.debug_bot import DebugBot  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=None)
CORS(app)

_money_bot = MoneyBot()
_debug_bot = DebugBot()

_FRONTEND_DIR = os.path.join(_HERE, "frontend")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bad_request(msg: str):
    return jsonify({"error": msg}), 400


def _server_error(msg: str):
    return jsonify({"error": msg}), 500


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "dreamco-lite"})


@app.get("/")
def index():
    return send_from_directory(_FRONTEND_DIR, "index.html")


@app.post("/api/leads")
def find_leads():
    """
    Body: {"niche": "...", "location": "..."}
    Returns: {"leads": [...]}
    """
    data = request.get_json(silent=True) or {}
    niche = (data.get("niche") or "").strip()
    location = (data.get("location") or "").strip()

    if not niche or not location:
        return _bad_request("Both 'niche' and 'location' are required.")

    try:
        leads = _money_bot.find_leads(niche, location)
        return jsonify({"leads": leads})
    except ValueError as exc:
        return _bad_request(str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /api/leads")
        return _server_error(str(exc))


@app.post("/api/messages")
def generate_messages():
    """
    Body: {"leads": [...], "niche": "..."}
    Returns: {"results": [...]}  (each lead extended with outreach_message)
    """
    data = request.get_json(silent=True) or {}
    leads = data.get("leads") or []
    niche = (data.get("niche") or "").strip()

    if not isinstance(leads, list):
        return _bad_request("'leads' must be a list.")
    if not niche:
        return _bad_request("'niche' is required.")

    try:
        results = _money_bot.generate_messages(leads, niche)
        return jsonify({"results": results})
    except Exception as exc:
        logger.exception("Unexpected error in /api/messages")
        return _server_error(str(exc))


@app.post("/api/run-automation")
def run_automation():
    """
    Body: {"niche": "...", "location": "..."}
    Returns: {"results": [...]}  (leads + outreach messages)
    """
    data = request.get_json(silent=True) or {}
    niche = (data.get("niche") or "").strip()
    location = (data.get("location") or "").strip()

    if not niche or not location:
        return _bad_request("Both 'niche' and 'location' are required.")

    try:
        results = _money_bot.run_automation(niche, location)
        return jsonify({"results": results})
    except ValueError as exc:
        return _bad_request(str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /api/run-automation")
        return _server_error(str(exc))


@app.post("/api/debug")
def debug_log():
    """
    Body: {"log": "..."}
    Returns: {"explanation": "...", "fixes": [...], "source": "..."}
    """
    data = request.get_json(silent=True) or {}
    log = (data.get("log") or "").strip()

    if not log:
        return _bad_request("'log' field is required.")

    try:
        result = _debug_bot.analyze(log)
        return jsonify(result)
    except Exception as exc:
        logger.exception("Unexpected error in /api/debug")
        return _server_error(str(exc))


# ---------------------------------------------------------------------------
# Dev server entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("DREAMCO_LITE_PORT", "5050"))
    debug = os.getenv("APP_ENV", "development") == "development"
    logger.info("Starting DreamCo Lite on http://0.0.0.0:%d", port)
    app.run(host="0.0.0.0", port=port, debug=debug)
