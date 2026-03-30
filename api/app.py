"""
DreamCo SaaS API

Exposes the DreamCo Money Operating System to paying users via an HTTP API.
Uses Flask when available; falls back to a stdlib http.server stub so the
module is always importable (useful for tests without Flask installed).

Endpoints
---------
POST /run-bots       Run all registered bots (requires x-api-key header)
POST /run-single     Run a single named bot   (requires x-api-key header)
GET  /health         Liveness probe (no auth required)

Monetisation tiers (recommended pricing):
  FREE       -- 5 runs/day
  $29/mo     -- unlimited access
  $99/mo     -- automation + scaling insights
  $499+      -- done-for-you service
"""

from __future__ import annotations

import os
from typing import Any, Dict

from core.dreamco_orchestrator import DreamCoOrchestrator

# ---------------------------------------------------------------------------
# API key store (replace with database in production)
# ---------------------------------------------------------------------------

_raw_keys = os.environ.get("DREAMCO_API_KEYS", "dreamco_pro_123")
VALID_API_KEYS: set[str] = {k.strip() for k in _raw_keys.split(",") if k.strip()}


def authenticate(api_key: str | None) -> bool:
    """Return True if *api_key* is in the valid key set."""
    return bool(api_key and api_key in VALID_API_KEYS)


# ---------------------------------------------------------------------------
# Orchestrator (shared across requests)
# ---------------------------------------------------------------------------

_orch = DreamCoOrchestrator()


# ---------------------------------------------------------------------------
# Flask app (optional dependency)
# ---------------------------------------------------------------------------

try:
    from flask import Flask, request, jsonify  # type: ignore[import]

    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health() -> Any:
        return jsonify({"status": "ok", "service": "dreamco-api"})

    @app.route("/run-bots", methods=["POST"])
    def run_bots() -> Any:
        api_key = request.headers.get("x-api-key")
        if not authenticate(api_key):
            return jsonify({"error": "Unauthorized"}), 401

        results = _orch.run_all_bots()
        summary = _orch.summary(results)
        return jsonify({"results": results, "summary": summary})

    @app.route("/run-single", methods=["POST"])
    def run_single() -> Any:
        api_key = request.headers.get("x-api-key")
        if not authenticate(api_key):
            return jsonify({"error": "Unauthorized"}), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        bot_path: str = data.get("path", "")
        bot_name: str = data.get("name", "")

        if not bot_path or not bot_name:
            return jsonify({"error": "Both 'path' and 'name' are required"}), 400

        result = _orch.run_bot(bot_path, bot_name)
        return jsonify(result)

    FLASK_AVAILABLE = True

except ImportError:  # pragma: no cover — Flask not installed in all envs
    app = None  # type: ignore[assignment]
    FLASK_AVAILABLE = False


def create_app() -> Any:
    """Return the Flask application instance (or None if Flask is unavailable)."""
    return app


def main() -> None:  # pragma: no cover
    if not FLASK_AVAILABLE:
        print("Flask is not installed.  Run: pip install flask")
        return
    port = int(os.environ.get("API_PORT", 5000))
    app.run(debug=False, port=port)


if __name__ == "__main__":  # pragma: no cover
    main()
