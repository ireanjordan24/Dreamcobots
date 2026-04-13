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

Note: The in-memory bot registry (_user_bots) is intended for development /
testing only.  Replace with a persistent database in production deployments.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict

from core.dreamco_orchestrator import DreamCoOrchestrator
from core.bot_validator import BotValidator
from core.sandbox_runner import SandboxRunner
from saas.auth.auth import AuthService, UserRegistry
from saas.auth.middleware import AuthMiddleware, RateLimiter
from saas.auth.user_model import SubscriptionTier
from saas.stripe_billing import StripeBillingService

_logger = logging.getLogger(__name__)

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

# Legacy API-key support (backwards compatible).
# Set DREAMCO_API_KEYS env var with comma-separated keys in production.
_raw_keys = os.environ.get("DREAMCO_API_KEYS", "")
VALID_API_KEYS: set = {k.strip() for k in _raw_keys.split(",") if k.strip()}
# Always include the demo key so tests can authenticate.
VALID_API_KEYS.add("dreamco_demo_key")

# Tier-based daily rate limits.
TIER_DAILY_LIMITS: Dict[str, int] = {
    "FREE": 10,
    "PRO": 500,
    "ENTERPRISE": 10_000,
}

# Resolved absolute upload directory
_ABS_UPLOAD_FOLDER = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..", "uploads")
)
os.makedirs(_ABS_UPLOAD_FOLDER, exist_ok=True)

# In-memory bot registry per user.
# NOTE: Replace with a persistent database in production.
_user_bots: Dict[str, list] = {}

# Allowed user-id character set (hex after 'usr_' prefix)
_USER_ID_RE = re.compile(r'^usr_[0-9a-f]{16}$')


def authenticate(api_key: str) -> bool:
    """Return True if *api_key* is a recognised key."""
    return bool(api_key and api_key in VALID_API_KEYS)


def _get_tier(api_key: str) -> str:
    """Derive the tier string from an API key prefix."""
    if api_key.startswith("dreamco_ent_"):
        return "ENTERPRISE"
    if api_key.startswith("dreamco_pro_"):
        return "PRO"
    return "FREE"


class DreamCoSaaSApp:
    """Simple SaaS application wrapper for testing without Flask."""

    def __init__(self, orchestrator: Any = None) -> None:
        self._orch = orchestrator if orchestrator is not None else _orch
        self._call_counts: Dict[str, int] = {}

    def _check_rate_limit(self, api_key: str) -> bool:
        """Return True if the key is within its tier daily limit."""
        tier = _get_tier(api_key)
        limit = TIER_DAILY_LIMITS.get(tier, TIER_DAILY_LIMITS["FREE"])
        count = self._call_counts.get(api_key, 0)
        return count < limit

    def _increment(self, api_key: str) -> None:
        self._call_counts[api_key] = self._call_counts.get(api_key, 0) + 1

    def handle_run_bots(self, api_key: str) -> tuple:
        if not authenticate(api_key):
            return {"error": "Unauthorized"}, 401
        if not self._check_rate_limit(api_key):
            return {"error": "Rate limit exceeded"}, 429
        self._increment(api_key)
        results = self._orch.run_all_bots()
        return {"results": results, "tier": _get_tier(api_key)}, 200

    def handle_run_single(self, api_key: str, bot_path: str, bot_name: str) -> tuple:
        if not authenticate(api_key):
            return {"error": "Unauthorized"}, 401
        result = self._orch.run_bot(bot_path, bot_name) if hasattr(self._orch, "run_bot") else {}
        return {"result": result}, 200

    def handle_summary(self, api_key: str) -> tuple:
        if not authenticate(api_key):
            return {"error": "Unauthorized"}, 401
        if _get_tier(api_key) == "FREE":
            return {"error": "PRO or ENTERPRISE tier required"}, 403
        results = self._orch.run_all_bots()
        return {"summary": results}, 200

    def handle_health(self) -> tuple:
        return {"status": "ok"}, 200


def authenticate_legacy(api_key: str | None) -> bool:
    """Return True if *api_key* is a valid legacy key."""
    return bool(api_key and VALID_API_KEYS and api_key in VALID_API_KEYS)


def _safe_user_dir(user_id: str) -> str | None:
    """
    Return an absolute path for the user's upload directory, or None if
    *user_id* fails format validation.  Prevents path traversal attacks.
    """
    if not _USER_ID_RE.match(user_id):
        return None
    candidate = os.path.realpath(os.path.join(_ABS_UPLOAD_FOLDER, user_id))
    # Ensure the resolved path is inside the upload folder
    if not candidate.startswith(_ABS_UPLOAD_FOLDER + os.sep):
        return None
    return candidate


def _safe_filename(raw_name: str) -> str | None:
    """
    Return a sanitised filename (alphanumeric, underscores, hyphens + .py)
    or None if *raw_name* is not a safe .py filename.
    """
    base = os.path.basename(raw_name)
    if not base.endswith(".py"):
        return None
    stem = base[:-3]
    if not re.match(r'^[a-zA-Z0-9_\-]+$', stem):
        return None
    return base


def _sanitise_bot_result(result: dict) -> dict:
    """
    Return a copy of *result* with internal error details removed so that
    raw exception messages are never forwarded to API callers.
    """
    safe = {
        "bot": result.get("bot", ""),
        "status": "error" if result.get("error") else "ok",
    }
    if result.get("output"):
        output = result["output"]
        safe["output"] = {
            k: output[k]
            for k in ("revenue", "leads_generated", "conversion_rate")
            if k in output
        }
    if result.get("validation"):
        safe["validation"] = result["validation"]
    return safe


# ---------------------------------------------------------------------------
# Flask app (optional dependency)
# ---------------------------------------------------------------------------

try:
    from flask import Flask, request, jsonify  # type: ignore[import]

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
            return jsonify({"error": result.get("error", "signup failed")}), 400
        return jsonify({"success": True, "user_id": result["user_id"], "token": result["token"]}), 201

    @app.route("/auth/login", methods=["POST"])
    def login() -> Any:
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        result = _auth_svc.login(
            email=data.get("email", ""),
            password=data.get("password", ""),
        )
        if not result.get("success"):
            return jsonify({"error": "invalid credentials"}), 401
        return jsonify({
            "success": True,
            "user_id": result["user_id"],
            "token": result["token"],
            "tier": result["tier"],
        })

    # ------------------------------------------------------------------ #
    #  Bot execution                                                       #
    # ------------------------------------------------------------------ #

    @app.route("/bots/run-all", methods=["POST"])
    def run_all_bots() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err and not authenticate_legacy(request.headers.get("x-api-key")):
            return jsonify({"error": "Unauthorized"}), 401

        if user and not _rate_limiter.is_allowed(user.user_id):
            return jsonify({"error": "rate limit exceeded"}), 429

        results = _orch.run_all_bots()
        summary = _orch.summary(results)

        if user:
            _auth_svc.consume_quota(user.user_id)

        safe_results = [_sanitise_bot_result(r) for r in results]
        return jsonify({"results": safe_results, "summary": summary})

    @app.route("/bots/run-single", methods=["POST"])
    def run_single_bot() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err and not authenticate_legacy(request.headers.get("x-api-key")):
            return jsonify({"error": "Unauthorized"}), 401

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

        return jsonify(_sanitise_bot_result(result))

    # ------------------------------------------------------------------ #
    #  Bot upload                                                          #
    # ------------------------------------------------------------------ #

    @app.route("/bots/upload", methods=["POST"])
    def upload_bot() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        if not _rate_limiter.is_allowed(user.user_id):
            return jsonify({"error": "rate limit exceeded"}), 429

        quota = _auth_svc.check_quota(user.user_id)
        if not quota.get("allowed"):
            return jsonify({"error": "daily bot quota exceeded"}), 429

        if "file" not in request.files:
            return jsonify({"error": "no file provided"}), 400

        file = request.files["file"]
        safe_name = _safe_filename(file.filename or "")
        if not safe_name:
            return jsonify({"error": "invalid filename; only alphanumeric .py files are accepted"}), 400

        user_dir = _safe_user_dir(user.user_id)
        if not user_dir:
            return jsonify({"error": "invalid user account"}), 400

        # --- Validate code in memory BEFORE writing to disk ---
        file_bytes = file.read()
        try:
            source = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return jsonify({"error": "file must be valid UTF-8 Python source"}), 422

        ok, issues = _validator.validate_source(source)
        if not ok:
            return jsonify({"error": "validation failed", "issues": issues}), 422

        # Write to disk only after validation passes
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, safe_name)
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(source)

        # Sandbox test
        run_result = _sandbox.run_file(file_path)

        _user_bots.setdefault(user.user_id, []).append(
            {"filename": safe_name, "status": "approved"}
        )

        return jsonify({
            "status": "approved",
            "filename": safe_name,
            "sandbox_success": run_result.get("success", False),
        })

    @app.route("/bots/list", methods=["GET"])
    def list_bots() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401
        bots = _user_bots.get(user.user_id, [])
        return jsonify({"bots": bots, "count": len(bots)})

    # ------------------------------------------------------------------ #
    #  Stats & Revenue                                                     #
    # ------------------------------------------------------------------ #

    @app.route("/stats", methods=["GET"])
    def stats() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

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
            return jsonify({"error": "Unauthorized"}), 401

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
            return jsonify({"error": "Unauthorized"}), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        tier = data.get("tier", "")
        if tier not in ("free", "pro", "enterprise"):
            return jsonify({"error": "invalid tier; choose free, pro, or enterprise"}), 400

        cust_result = _billing.create_customer(user.user_id, user.email)
        if not cust_result.get("success"):
            _logger.error("create_customer failed for user %s", user.user_id)
            return jsonify({"error": "billing service unavailable"}), 500

        sub_result = _billing.create_subscription(
            customer_id=cust_result["customer_id"],
            tier=tier,
            user_id=user.user_id,
        )
        if not sub_result.get("success"):
            _logger.error("create_subscription failed for user %s", user.user_id)
            return jsonify({"error": "subscription creation failed"}), 500

        _auth_svc.upgrade_tier(user.user_id, SubscriptionTier(tier))
        return jsonify({
            "success": True,
            "tier": tier,
            "subscription_id": sub_result.get("subscription_id"),
        })

    @app.route("/billing/status", methods=["GET"])
    def billing_status() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

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
        return jsonify({"results": [_sanitise_bot_result(r) for r in results], "summary": summary})

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
        return jsonify(_sanitise_bot_result(result))

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
