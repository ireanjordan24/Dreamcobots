"""
Flask REST API for the SaaS Selling Bot.

Endpoints:
  GET  /api/tools              – List all tools (optionally filter by category)
  GET  /api/tools/<id>         – Get a single tool
  GET  /api/categories         – List all categories with counts
  GET  /api/search?q=<query>   – Search tools
  POST /api/tools              – Add a new tool (admin)
  POST /api/subscribe          – Subscribe (email + plan)
  POST /api/recommend          – AI-powered recommendations
  POST /api/chat               – Chatbot endpoint
  GET  /api/affiliate/click/<id> – Track affiliate click & redirect
  GET  /api/revenue            – Revenue dashboard
  GET  /api/plans              – Subscription plan details
  POST /api/webhook/stripe     – Stripe webhook handler
  GET  /                       – Serve the frontend
"""

import os
import json

from flask import Flask, request, jsonify, redirect, send_from_directory, abort
from flask_cors import CORS

import database as db
from ai_integration import get_recommendations, chatbot_response
from payment import create_checkout_session, handle_webhook, get_plans
from affiliate import track_click, get_revenue_dashboard, mark_conversion

app = Flask(__name__, static_folder="frontend")
CORS(app)

# ─────────────────────────────────────────────────────────────
# Frontend
# ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("frontend", filename)


# ─────────────────────────────────────────────────────────────
# Tools API
# ─────────────────────────────────────────────────────────────

@app.route("/api/tools", methods=["GET"])
def list_tools():
    category = request.args.get("category", "").strip()
    if category:
        tools = db.get_tools_by_category(category)
    else:
        tools = db.get_all_tools()
    return jsonify({"tools": tools, "count": len(tools)})


@app.route("/api/tools/<int:tool_id>", methods=["GET"])
def get_tool(tool_id):
    tool = db.get_tool_by_id(tool_id)
    if not tool:
        return jsonify({"error": "Tool not found"}), 404
    return jsonify(tool)


@app.route("/api/tools", methods=["POST"])
def add_tool():
    data = request.get_json(silent=True) or {}
    required = ["name", "category", "description"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    tool = {
        "name": data["name"],
        "category": data["category"],
        "description": data["description"],
        "api_url": data.get("api_url", ""),
        "pricing": data.get("pricing", "Free"),
        "affiliate_link": data.get("affiliate_link", ""),
        "docs_url": data.get("docs_url", ""),
    }
    try:
        db.add_tool(tool)
        return jsonify({"success": True, "message": "Tool added successfully"}), 201
    except Exception as exc:
        return jsonify({"error": str(exc)}), 409


# ─────────────────────────────────────────────────────────────
# Categories & Search
# ─────────────────────────────────────────────────────────────

@app.route("/api/categories", methods=["GET"])
def list_categories():
    categories = db.get_categories()
    return jsonify({"categories": categories})


@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    results = db.search_tools(query)
    return jsonify({"results": results, "count": len(results), "query": query})


# ─────────────────────────────────────────────────────────────
# Subscriptions & Plans
# ─────────────────────────────────────────────────────────────

@app.route("/api/plans", methods=["GET"])
def plans():
    return jsonify({"plans": get_plans()})


@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    plan = data.get("plan", "free").strip()

    if not email:
        return jsonify({"error": "Email is required"}), 400
    if plan not in ("free", "pro", "enterprise"):
        return jsonify({"error": "Invalid plan. Choose: free, pro, enterprise"}), 400

    result = create_checkout_session(email=email, plan=plan)
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400


# ─────────────────────────────────────────────────────────────
# AI Recommendations & Chatbot
# ─────────────────────────────────────────────────────────────

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Field 'query' is required"}), 400

    user_context = data.get("context", {})
    recommendation = get_recommendations(query, user_context)
    return jsonify({"recommendation": recommendation, "query": query})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Field 'message' is required"}), 400

    response = chatbot_response(history, message)
    return jsonify({"response": response})


# ─────────────────────────────────────────────────────────────
# Affiliate Tracking
# ─────────────────────────────────────────────────────────────

@app.route("/api/affiliate/click/<int:tool_id>", methods=["GET"])
def affiliate_click(tool_id):
    session_id = request.args.get("sid") or request.cookies.get("saasbot_sid")
    result = track_click(tool_id=tool_id, session_id=session_id)
    if not result["success"]:
        return jsonify(result), 404
    # Redirect user to the affiliate URL
    return redirect(result["affiliate_url"])


@app.route("/api/affiliate/convert/<int:tool_id>", methods=["POST"])
def affiliate_convert(tool_id):
    data = request.get_json(silent=True) or {}
    commission = float(data.get("commission", 5.0))
    result = mark_conversion(tool_id=tool_id, commission=commission)
    return jsonify(result)


@app.route("/api/revenue", methods=["GET"])
def revenue():
    dashboard = get_revenue_dashboard()
    return jsonify(dashboard)


# ─────────────────────────────────────────────────────────────
# Stripe Webhook
# ─────────────────────────────────────────────────────────────

@app.route("/api/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")
    result = handle_webhook(payload=payload, sig_header=sig_header)
    if result.get("status") == "error":
        return jsonify(result), 400
    return jsonify(result)


# ─────────────────────────────────────────────────────────────
# Payment redirect pages
# ─────────────────────────────────────────────────────────────

@app.route("/payment/success")
def payment_success():
    session_id = request.args.get("session_id", "")
    return f"""
    <!DOCTYPE html><html><head><title>Payment Successful</title>
    <style>body{{font-family:sans-serif;text-align:center;padding:60px;background:#f0fdf4;}}
    h1{{color:#16a34a;}}a{{color:#2563eb;}}</style></head>
    <body><h1>🎉 Payment Successful!</h1>
    <p>Thank you for subscribing to SaaSBot Pro.</p>
    <p><a href="/">← Back to Dashboard</a></p>
    </body></html>
    """


@app.route("/payment/cancel")
def payment_cancel():
    return """
    <!DOCTYPE html><html><head><title>Payment Cancelled</title>
    <style>body{{font-family:sans-serif;text-align:center;padding:60px;background:#fef2f2;}}
    h1{{color:#dc2626;}}a{{color:#2563eb;}}</style></head>
    <body><h1>Payment Cancelled</h1>
    <p>No charges were made.</p>
    <p><a href="/">← Back to Dashboard</a></p>
    </body></html>
    """


# ─────────────────────────────────────────────────────────────
# Startup
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    db.init_db()
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print(f"🚀 SaaS Selling Bot API running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
