# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
"""
DreamCobots SaaS-Selling & Demo Bot
====================================
A lightweight Flask web application that:
  - Showcases 6 automation services via interactive mini-demos
  - Captures leads via a contact/quote form (SQLite storage)
  - Provides keyword-based FAQ chatbot (optional OpenAI upgrade)
  - Displays dynamic pricing tiers
  - Records analytics on demo and chat activity

Usage
-----
    python bot.py --init-db   # initialise the database (first run)
    python bot.py             # start the server on port 5000
"""

import argparse
import json
import os
import random
import sys

from flask import Flask, jsonify, redirect, render_template, request, url_for

# Allow running directly from this directory or from the repo root.
sys.path.insert(0, os.path.dirname(__file__))

import database as db
from nlp import get_faq_response

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dreamcobots-dev-secret")

# ---------------------------------------------------------------------------
# Pricing tiers
# ---------------------------------------------------------------------------
PRICING_TIERS = [
    {
        "name": "Starter",
        "price": "$99",
        "period": "/ month",
        "description": "Perfect for solo founders and small businesses.",
        "features": [
            "1 custom bot",
            "Basic NLP FAQ chatbot",
            "Email support",
            "Up to 500 automation runs/mo",
        ],
        "highlight": False,
    },
    {
        "name": "Professional",
        "price": "$299",
        "period": "/ month",
        "description": "For growing teams that need more power.",
        "features": [
            "5 custom bots",
            "Advanced NLP + GPT integration",
            "Income tracking dashboard",
            "Government contract alerts",
            "Priority support",
            "Up to 5,000 automation runs/mo",
        ],
        "highlight": True,
    },
    {
        "name": "Enterprise",
        "price": "Custom",
        "period": "",
        "description": "Unlimited scale for enterprises and agencies.",
        "features": [
            "Unlimited bots",
            "Dedicated account manager",
            "Custom API integrations",
            "White-label options",
            "SLA-backed uptime",
            "Unlimited automation runs",
        ],
        "highlight": False,
    },
]

# ---------------------------------------------------------------------------
# Service catalogue (used on the homepage menu)
# ---------------------------------------------------------------------------
SERVICES = [
    {
        "slug": "custom-bot",
        "title": "Custom Bot Development",
        "icon": "🤖",
        "description": "Demo a basic automation workflow tailored to your business.",
    },
    {
        "slug": "nlp-bot",
        "title": "NLP Bots",
        "icon": "💬",
        "description": "Try a simple chatbot powered by keyword NLP (free tier).",
    },
    {
        "slug": "income-tracking",
        "title": "Residual Income Tracking",
        "icon": "💰",
        "description": "Mock financial tracking dashboard with revenue streams.",
    },
    {
        "slug": "contracts",
        "title": "Government Contract & Grant Bot",
        "icon": "📋",
        "description": "Simulate finding contracts based on your keywords.",
    },
    {
        "slug": "api-integration",
        "title": "API Integration Demos",
        "icon": "🔗",
        "description": "See how APIs are wired together for seamless automation.",
    },
    {
        "slug": "ui-ux",
        "title": "UI/UX Automation",
        "icon": "🎨",
        "description": "Explore front-end automation templates and dashboards.",
    },
]

# ---------------------------------------------------------------------------
# Demo logic helpers (mock data, no external API required)
# ---------------------------------------------------------------------------

MOCK_CONTRACTS = [
    {"id": "W912DR-24-R-0001", "title": "IT Automation Services", "agency": "Dept. of Defence", "value": "$450,000"},
    {"id": "GS-35F-0001X", "title": "Cloud Workflow Automation", "agency": "GSA", "value": "$1,200,000"},
    {"id": "NIH-2024-BOT-01", "title": "Data Processing Bot Development", "agency": "NIH", "value": "$320,000"},
    {"id": "EPA-RPA-2024", "title": "Robotic Process Automation", "agency": "EPA", "value": "$780,000"},
    {"id": "DOE-AI-BOTS-24", "title": "AI Chatbot Platform", "agency": "Dept. of Energy", "value": "$560,000"},
]

MOCK_APIS = [
    {"name": "Stripe", "action": "Payment processed", "status": "✅ 200 OK"},
    {"name": "Twilio", "action": "SMS notification sent", "status": "✅ 201 Created"},
    {"name": "Airtable", "action": "Record written", "status": "✅ 200 OK"},
    {"name": "Slack", "action": "Channel message posted", "status": "✅ 200 OK"},
    {"name": "Google Sheets", "action": "Row appended", "status": "✅ 200 OK"},
]

MOCK_REVENUE_STREAMS = [
    {"source": "Affiliate Program A", "monthly": 1_240, "ytd": 14_880},
    {"source": "SaaS Subscription B", "monthly": 3_500, "ytd": 42_000},
    {"source": "Digital Course C", "monthly": 820, "ytd": 9_840},
    {"source": "Consulting Retainer D", "monthly": 2_000, "ytd": 24_000},
]

UI_TEMPLATES = [
    {
        "name": "Analytics Dashboard",
        "description": "Real-time KPI cards, line charts, and data tables.",
        "tags": ["React", "TailwindCSS", "Chart.js"],
    },
    {
        "name": "Client Portal",
        "description": "Secure login, file upload, and ticket management.",
        "tags": ["Flask", "TailwindCSS", "SQLite"],
    },
    {
        "name": "Lead Capture Landing Page",
        "description": "Conversion-optimised hero + form with CRM webhook.",
        "tags": ["HTML5", "TailwindCSS", "JavaScript"],
    },
    {
        "name": "Invoice Generator",
        "description": "Auto-fill PDF invoices and email them to clients.",
        "tags": ["Python", "WeasyPrint", "Jinja2"],
    },
]


def run_custom_bot_demo(task: str) -> dict:
    steps = [
        f"📥 Input received: «{task}»",
        "🔍 Parsing intent and extracting entities…",
        "⚙️  Dispatching to automation pipeline…",
        "📡 Calling external services…",
        "✅ Task completed successfully!",
    ]
    result = f"Automation result for «{task}»: processed and delivered at {_timestamp()}."
    return {"steps": steps, "result": result}


def run_contract_search(keyword: str) -> list:
    keyword_lower = keyword.lower()
    results = [
        c for c in MOCK_CONTRACTS
        if keyword_lower in c["title"].lower() or keyword_lower in c["agency"].lower()
    ]
    if not results:
        results = random.sample(MOCK_CONTRACTS, k=min(3, len(MOCK_CONTRACTS)))
    return results


def _timestamp() -> str:
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    analytics = db.get_analytics()
    return render_template("index.html", services=SERVICES, analytics=analytics)


@app.route("/demo/custom-bot", methods=["GET", "POST"])
def demo_custom_bot():
    result = None
    task = ""
    if request.method == "POST":
        task = request.form.get("task", "").strip() or "Send weekly report"
        result = run_custom_bot_demo(task)
        db.record_demo("custom-bot", task)
    return render_template("demo_custom_bot.html", result=result, task=task, pricing=PRICING_TIERS)


@app.route("/demo/nlp-bot", methods=["GET", "POST"])
def demo_nlp_bot():
    result = None
    user_message = ""
    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        if user_message:
            result = get_faq_response(user_message)
            db.record_demo("nlp-bot", user_message)
            db.record_chat(user_message, result)
    return render_template("demo_nlp_bot.html", result=result, user_message=user_message, pricing=PRICING_TIERS)


@app.route("/demo/income-tracking")
def demo_income_tracking():
    db.record_demo("income-tracking")
    total_monthly = sum(s["monthly"] for s in MOCK_REVENUE_STREAMS)
    total_ytd = sum(s["ytd"] for s in MOCK_REVENUE_STREAMS)
    return render_template(
        "demo_income_tracking.html",
        streams=MOCK_REVENUE_STREAMS,
        total_monthly=total_monthly,
        total_ytd=total_ytd,
        pricing=PRICING_TIERS,
    )


@app.route("/demo/contracts", methods=["GET", "POST"])
def demo_contracts():
    results = None
    keyword = ""
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip() or "automation"
        results = run_contract_search(keyword)
        db.record_demo("contracts", keyword)
    return render_template("demo_contracts.html", results=results, keyword=keyword, pricing=PRICING_TIERS)


@app.route("/demo/api-integration")
def demo_api_integration():
    db.record_demo("api-integration")
    return render_template("demo_api_integration.html", apis=MOCK_APIS, pricing=PRICING_TIERS)


@app.route("/demo/ui-ux")
def demo_ui_ux():
    db.record_demo("ui-ux")
    return render_template("demo_ui_ux.html", templates=UI_TEMPLATES, pricing=PRICING_TIERS)


@app.route("/lead-gen", methods=["GET", "POST"])
def lead_gen():
    success = False
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        company = request.form.get("company", "").strip()
        service = request.form.get("service", "").strip()
        message = request.form.get("message", "").strip()
        if name and email:
            db.save_lead(name, email, company, service, message)
            success = True
    return render_template("lead_gen.html", success=success, services=SERVICES)


@app.route("/pricing")
def pricing():
    return render_template("pricing.html", tiers=PRICING_TIERS)


@app.route("/faq")
def faq():
    return render_template("faq.html")


# ---------------------------------------------------------------------------
# JSON API endpoints (used by the FAQ chatbot via fetch)
# ---------------------------------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()
    if not user_message:
        return jsonify({"error": "message is required"}), 400
    response = get_faq_response(user_message)
    db.record_chat(user_message, response)
    return jsonify({"response": response})


@app.route("/api/submit-lead", methods=["POST"])
def api_submit_lead():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400
    lead_id = db.save_lead(
        name=name,
        email=email,
        company=str(data.get("company", "")),
        service=str(data.get("service", "")),
        message=str(data.get("message", "")),
    )
    return jsonify({"success": True, "lead_id": lead_id})


@app.route("/api/analytics")
def api_analytics():
    return jsonify(db.get_analytics())


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="DreamCobots SaaS-Selling Bot")
    parser.add_argument("--init-db", action="store_true", help="Initialise the SQLite database and exit")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)), help="Port to listen on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    args = parser.parse_args()

    db.init_db()
    if args.init_db:
        print(f"Database initialised at: {db.DB_PATH}")
        return

    print(f"Starting DreamCobots SaaS Bot on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
