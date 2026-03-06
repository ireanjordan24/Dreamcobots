# DreamCobots SaaS-Selling & Demo Bot

A lightweight Flask web application that simultaneously **tests** scaled-down versions
of DreamCobots automation services **and sells** full-service subscriptions.

## Features

| Feature | Details |
|---|---|
| 🤖 6 Interactive Demos | Custom Bot, NLP, Income Tracking, Government Contracts, API Integration, UI/UX |
| 📬 Lead Generation | Contact/quote form with SQLite storage |
| 💰 Dynamic Pricing | Three-tier pricing displayed after each demo |
| ❓ FAQ Chatbot | Keyword NLP (free) — optional OpenAI GPT upgrade |
| 📊 Analytics | Demo runs, lead counts, and chat interactions tracked automatically |

## Quick Start

```bash
cd bots/saas-selling-bot

# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialise the database
python bot.py --init-db

# 3. Start the server (default port 5000)
python bot.py
```

Visit **http://localhost:5000** in your browser.

## Optional: OpenAI GPT Integration

Set the environment variable to upgrade the FAQ chatbot to GPT-3.5-turbo:

```bash
export OPENAI_API_KEY=sk-...
python bot.py
```

Without this variable the bot uses its free built-in keyword NLP engine.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `5000` | TCP port for the Flask server |
| `SECRET_KEY` | `dreamcobots-dev-secret` | Flask session secret (change in production!) |
| `SAAS_BOT_DB` | `saas_bot.db` (same dir) | Path to the SQLite database file |
| `OPENAI_API_KEY` | *(not set)* | Optional OpenAI API key for GPT chatbot |

## Project Structure

```
bots/saas-selling-bot/
├── bot.py          # Main Flask application + CLI entry-point
├── database.py     # SQLite helpers (leads, demo events, chat events)
├── nlp.py          # Keyword NLP engine + optional OpenAI wrapper
├── requirements.txt
├── README.md
└── templates/
    ├── base.html
    ├── index.html
    ├── demo_custom_bot.html
    ├── demo_nlp_bot.html
    ├── demo_income_tracking.html
    ├── demo_contracts.html
    ├── demo_api_integration.html
    ├── demo_ui_ux.html
    ├── lead_gen.html
    ├── pricing.html
    └── faq.html
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/chat` | JSON chatbot (`{"message": "…"}`) |
| `POST` | `/api/submit-lead` | JSON lead capture (`{"name","email","company","service","message"}`) |
| `GET` | `/api/analytics` | JSON analytics summary |

## Deployment

The app is compatible with any free-tier cloud host:

- **Heroku**: add a `Procfile` with `web: python bots/saas-selling-bot/bot.py`
- **Railway / Render**: point start command to `python bot.py`
- **Replit**: set the run command to `python bot.py`

Set `SECRET_KEY` to a strong random value and set `PORT` as required by the platform.

## Running Tests

```bash
# From the repository root
pip install -r requirements.txt
pytest tests/test_saas_selling_bot.py -v
```
