"""
DreamCo SaaS API — Tier-Aware REST Endpoint

Exposes the DreamCo orchestrator as a monetised HTTP API:

  POST /run-bots       → run all registered bots (requires API key)
  POST /run-single     → run a specific bot by path and name
  GET  /summary        → revenue and scaling summary
  GET  /health         → liveness probe

Monetisation tiers
------------------
  FREE         → up to 5 runs/day, single-bot execution only
  PRO  $29/mo  → up to 100 runs/day, multi-bot execution
  ENTERPRISE   → unlimited runs, full analytics

The API key is read from the ``x-api-key`` HTTP header and validated
against the ``DREAMCO_API_KEYS`` environment variable (comma-separated).
If the env var is absent, the hard-coded demo key is used for testing.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import GlobalAISourcesFlow  # noqa: F401
from core.dreamco_orchestrator import DreamCoOrchestrator


# ---------------------------------------------------------------------------
# API key management
# ---------------------------------------------------------------------------

_ENV_KEYS = os.environ.get("DREAMCO_API_KEYS", "")
_DEFAULT_DEMO_KEY = "dreamco_demo_key"  # non-secret demo — replace in production

VALID_API_KEYS: List[str] = [k.strip() for k in _ENV_KEYS.split(",") if k.strip()] or [
    _DEFAULT_DEMO_KEY
]

# Tier definitions mapped to API key prefixes
TIER_MAP: Dict[str, str] = {
    "dreamco_free_": "FREE",
    "dreamco_pro_": "PRO",
    "dreamco_ent_": "ENTERPRISE",
    "dreamco_demo_key": "FREE",  # demo gets FREE tier
}

TIER_DAILY_LIMITS: Dict[str, int] = {
    "FREE": 5,
    "PRO": 100,
    "ENTERPRISE": 999_999,
}


def _get_tier(api_key: str) -> str:
    """Resolve tier from API key prefix."""
    for prefix, tier in TIER_MAP.items():
        if api_key.startswith(prefix) or api_key == prefix.rstrip("_"):
            return tier
    return "FREE"


def authenticate(api_key: str) -> bool:
    """Return True if the API key is valid."""
    return api_key in VALID_API_KEYS


# ---------------------------------------------------------------------------
# SaaS App
# ---------------------------------------------------------------------------


class DreamCoSaaSApp:
    """
    Lightweight SaaS application wrapper around DreamCoOrchestrator.

    Provides the same interface as the Flask routes but without Flask as a
    hard dependency, so it can be unit-tested without a running server.

    When Flask is available you can mount it as::

        from api.app import DreamCoSaaSApp, create_flask_app
        flask_app = create_flask_app()
        flask_app.run()
    """

    def __init__(self, orchestrator: DreamCoOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator or DreamCoOrchestrator()
        self._usage: Dict[str, int] = {}  # api_key → daily run count

    # ------------------------------------------------------------------
    # Route handlers (framework-agnostic)
    # ------------------------------------------------------------------

    def handle_run_bots(self, api_key: str) -> tuple[dict, int]:
        """POST /run-bots handler."""
        if not authenticate(api_key):
            return {"error": "Unauthorized"}, 401

        tier = _get_tier(api_key)
        limit = TIER_DAILY_LIMITS[tier]
        used = self._usage.get(api_key, 0)

        if used >= limit:
            return {"error": f"Daily limit of {limit} reached for tier {tier}"}, 429

        results = self.orchestrator.run_all_bots()
        self._usage[api_key] = used + 1
        return {"results": results, "tier": tier, "runs_used": self._usage[api_key]}, 200

    def handle_run_single(self, api_key: str, path: str, name: str) -> tuple[dict, int]:
        """POST /run-single handler."""
        if not authenticate(api_key):
            return {"error": "Unauthorized"}, 401

        result = self.orchestrator.run_bot(path, name)
        return {"result": result}, 200

    def handle_summary(self, api_key: str) -> tuple[dict, int]:
        """GET /summary handler."""
        if not authenticate(api_key):
            return {"error": "Unauthorized"}, 401

        tier = _get_tier(api_key)
        if tier == "FREE":
            return {"error": "Upgrade to PRO for analytics access"}, 403

        return self.orchestrator.get_summary(), 200

    def handle_health(self) -> tuple[dict, int]:
        """GET /health handler."""
        return {"status": "ok", "service": "DreamCo SaaS API"}, 200


# ---------------------------------------------------------------------------
# Optional Flask integration
# ---------------------------------------------------------------------------


def create_flask_app(orchestrator: DreamCoOrchestrator | None = None):  # pragma: no cover
    """
    Create and return a Flask application.

    Only call this when Flask is installed.  Import is deferred so that
    the module can be imported without Flask in testing environments.
    """
    from flask import Flask, request, jsonify  # type: ignore[import]

    flask_app = Flask(__name__)
    saas = DreamCoSaaSApp(orchestrator=orchestrator)

    @flask_app.route("/run-bots", methods=["POST"])
    def run_bots():
        api_key = request.headers.get("x-api-key", "")
        body, status = saas.handle_run_bots(api_key)
        return jsonify(body), status

    @flask_app.route("/run-single", methods=["POST"])
    def run_single():
        api_key = request.headers.get("x-api-key", "")
        data = request.json or {}
        body, status = saas.handle_run_single(api_key, data.get("path", ""), data.get("name", ""))
        return jsonify(body), status

    @flask_app.route("/summary", methods=["GET"])
    def summary():
        api_key = request.headers.get("x-api-key", "")
        body, status = saas.handle_summary(api_key)
        return jsonify(body), status

    @flask_app.route("/health", methods=["GET"])
    def health():
        body, status = saas.handle_health()
        return jsonify(body), status

    return flask_app


if __name__ == "__main__":  # pragma: no cover
    app = create_flask_app()
    app.run(debug=False, port=5000)
