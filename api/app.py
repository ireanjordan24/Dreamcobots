"""
DreamCo SaaS API — Production-hardened REST API for the DreamCo platform.

Endpoints
---------
GET  /health                 Liveness probe (no auth required)
POST /auth/signup            Create account (returns token)
POST /auth/login             Authenticate (returns token)

POST /bots/run-all           Run all registered bots (Bearer token auth)
POST /bots/run-single        Run one named bot      (Bearer token auth)
POST /bots/upload            Upload & sandbox-test a bot file
GET  /bots/list              List the current user's uploaded bots

GET  /stats                  Bot execution stats for the current user
GET  /revenue                Revenue summary (PRO+ required)

POST /billing/subscribe      Create or upgrade a Stripe subscription
GET  /billing/status         Current subscription status
"""

from __future__ import annotations

import os
from typing import Any, Dict

from core.dreamco_orchestrator import DreamCoOrchestrator
from core.bot_validator import BotValidator
from core.sandbox_runner import SandboxRunner
from saas.auth.auth import AuthService, UserRegistry
from saas.auth.middleware import AuthMiddleware, RateLimiter
from saas.auth.user_model import SubscriptionTier
from saas.stripe_billing import StripeBillingService

# ---------------------------------------------------------------------------
# Shared service instances
# ---------------------------------------------------------------------------

_orch = DreamCoOrchestrator()
_registry = UserRegistry()
_auth_svc = AuthService(registry=_registry)
_middleware = AuthMiddleware(auth_service=_auth_svc)
_rate_limiter = RateLimiter(max_requests=60, window_seconds=60)
_validator = BotValidator()
_sandbox = SandboxRunner(timeout_seconds=10)
_billing = StripeBillingService(simulation_mode=not os.environ.get("STRIPE_API_KEY"))

# Legacy API-key support (backwards compatible)
_raw_keys = os.environ.get("DREAMCO_API_KEYS", "dreamco_pro_123")
VALID_API_KEYS: set = {k.strip() for k in _raw_keys.split(",") if k.strip()}

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory bot registry per user
_user_bots: Dict[str, list] = {}


def authenticate_legacy(api_key: str | None) -> bool:
    """Return True if *api_key* is a valid legacy key."""
    return bool(api_key and api_key in VALID_API_KEYS)


# ---------------------------------------------------------------------------
# Flask app (optional dependency)
# ---------------------------------------------------------------------------

try:
    import json as _json
    from flask import Flask, request, jsonify  # type: ignore[import]
    import os as _os

    app = Flask(__name__)

    # ------------------------------------------------------------------ #
    #  Health                                                              #
    # ------------------------------------------------------------------ #

    @app.route("/health", methods=["GET"])
    def health() -> Any:
        return jsonify({"status": "ok", "service": "dreamco-api"})

    # ------------------------------------------------------------------ #
    #  Auth                                                                #
    # ------------------------------------------------------------------ #

    @app.route("/auth/signup", methods=["POST"])
    def signup() -> Any:
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        result = _auth_svc.signup(
            username=data.get("username", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
        )
        if not result.get("success"):
            return jsonify(result), 400
        return jsonify(result), 201

    @app.route("/auth/login", methods=["POST"])
    def login() -> Any:
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        result = _auth_svc.login(
            email=data.get("email", ""),
            password=data.get("password", ""),
        )
        if not result.get("success"):
            return jsonify(result), 401
        return jsonify(result)

    # ------------------------------------------------------------------ #
    #  Bot execution                                                       #
    # ------------------------------------------------------------------ #

    @app.route("/bots/run-all", methods=["POST"])
    def run_all_bots() -> Any:
        # Support both Bearer token and legacy API key
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err and not authenticate_legacy(request.headers.get("x-api-key")):
            return jsonify({"error": err or "Unauthorized"}), 401

        if user and not _rate_limiter.is_allowed(user.user_id):
            return jsonify({"error": "rate limit exceeded"}), 429

        results = _orch.run_all_bots()
        summary = _orch.summary(results)

        if user:
            _auth_svc.consume_quota(user.user_id)

        return jsonify({"results": results, "summary": summary})

    @app.route("/bots/run-single", methods=["POST"])
    def run_single_bot() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err and not authenticate_legacy(request.headers.get("x-api-key")):
            return jsonify({"error": err or "Unauthorized"}), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        bot_path: str = data.get("path", "")
        bot_name: str = data.get("name", "")

        if not bot_path or not bot_name:
            return jsonify({"error": "Both 'path' and 'name' are required"}), 400

        if user and not _rate_limiter.is_allowed(user.user_id):
            return jsonify({"error": "rate limit exceeded"}), 429

        result = _orch.run_bot(bot_path, bot_name)
        if user:
            _auth_svc.consume_quota(user.user_id)

        return jsonify(result)

    # ------------------------------------------------------------------ #
    #  Bot upload                                                          #
    # ------------------------------------------------------------------ #

    @app.route("/bots/upload", methods=["POST"])
    def upload_bot() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": err}), 401

        if not _rate_limiter.is_allowed(user.user_id):
            return jsonify({"error": "rate limit exceeded"}), 429

        # Check quota
        quota = _auth_svc.check_quota(user.user_id)
        if not quota.get("allowed"):
            return jsonify({"error": "daily bot quota exceeded", "quota": quota}), 429

        if "file" not in request.files:
            return jsonify({"error": "no file provided"}), 400

        file = request.files["file"]
        if not file.filename or not file.filename.endswith(".py"):
            return jsonify({"error": "only .py files are accepted"}), 400

        # Save to user-specific uploads directory
        user_dir = _os.path.join(UPLOAD_FOLDER, user.user_id)
        _os.makedirs(user_dir, exist_ok=True)
        file_path = _os.path.join(user_dir, _os.path.basename(file.filename))
        file.save(file_path)

        # Validate
        ok, issues = _validator.validate_file(file_path)
        if not ok:
            _os.unlink(file_path)
            return jsonify({"error": "validation failed", "issues": issues}), 422

        # Sandbox test
        run_result = _sandbox.run_file(file_path)

        # Register bot
        _user_bots.setdefault(user.user_id, []).append(
            {"filename": file.filename, "path": file_path, "status": "approved"}
        )

        return jsonify({
            "status": "approved",
            "filename": file.filename,
            "sandbox_output": run_result.get("output", ""),
            "sandbox_error": run_result.get("error", ""),
        })

    @app.route("/bots/list", methods=["GET"])
    def list_bots() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": err}), 401
        bots = _user_bots.get(user.user_id, [])
        return jsonify({"bots": bots, "count": len(bots)})

    # ------------------------------------------------------------------ #
    #  Stats & Revenue                                                     #
    # ------------------------------------------------------------------ #

    @app.route("/stats", methods=["GET"])
    def stats() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": err}), 401

        quota = _auth_svc.check_quota(user.user_id)
        return jsonify({
            "user_id": user.user_id,
            "tier": user.tier.value,
            "quota": quota,
            "bots_uploaded": len(_user_bots.get(user.user_id, [])),
        })

    @app.route("/revenue", methods=["GET"])
    def revenue() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": err}), 401

        tier_err = _middleware.require_tier(user, SubscriptionTier.PRO)
        if tier_err:
            return jsonify({"error": tier_err}), 403

        summary = _billing.revenue_summary()
        return jsonify(summary)

    # ------------------------------------------------------------------ #
    #  Billing                                                             #
    # ------------------------------------------------------------------ #

    @app.route("/billing/subscribe", methods=["POST"])
    def subscribe() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": err}), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        tier = data.get("tier", "")
        if tier not in ("free", "pro", "enterprise"):
            return jsonify({"error": "invalid tier; choose free, pro, or enterprise"}), 400

        cust_result = _billing.create_customer(user.user_id, user.email)
        if not cust_result.get("success"):
            return jsonify(cust_result), 500

        sub_result = _billing.create_subscription(
            customer_id=cust_result["customer_id"],
            tier=tier,
            user_id=user.user_id,
        )
        if sub_result.get("success"):
            _auth_svc.upgrade_tier(user.user_id, SubscriptionTier(tier))

        return jsonify(sub_result)

    @app.route("/billing/status", methods=["GET"])
    def billing_status() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": err}), 401

        return jsonify({
            "user_id": user.user_id,
            "tier": user.tier.value,
            "revenue_summary": _billing.revenue_summary(),
        })

    # Legacy endpoints (backwards compatible)
    @app.route("/run-bots", methods=["POST"])
    def run_bots_legacy() -> Any:
        api_key = request.headers.get("x-api-key")
        if not authenticate_legacy(api_key):
            return jsonify({"error": "Unauthorized"}), 401
        results = _orch.run_all_bots()
        summary = _orch.summary(results)
        return jsonify({"results": results, "summary": summary})

    @app.route("/run-single", methods=["POST"])
    def run_single_legacy() -> Any:
        api_key = request.headers.get("x-api-key")
        if not authenticate_legacy(api_key):
            return jsonify({"error": "Unauthorized"}), 401
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        bot_path: str = data.get("path", "")
        bot_name: str = data.get("name", "")
        if not bot_path or not bot_name:
            return jsonify({"error": "Both 'path' and 'name' are required"}), 400
        result = _orch.run_bot(bot_path, bot_name)
        return jsonify(result)

    FLASK_AVAILABLE = True

except ImportError:  # pragma: no cover — Flask not installed
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
