# 211 Resource & Eligibility Checker Bot

A conversational chatbot that helps users **find local resources** and **check program eligibility** using 211 data, FPL-based rules, and geolocation matching.

---

## Features

| Feature | Description |
|---|---|
| Resource Search | Queries the 211 API for housing, food, mental health, utilities, and more |
| Eligibility Checker | Determines qualification for SNAP, Medicaid, CHIP, WIC, and Rent Assistance using FPL thresholds |
| Geolocation Matching | Narrows results to a user-specified city or ZIP code |
| Multilingual Support | English and Spanish built in; add new languages by extending `config.py` |
| Privacy-first | All session data is ephemeral (in-memory only) and purged after a configurable TTL |
| Mock/Demo Mode | Works fully without an API key using curated mock data |

---

## Quick Start

### 1. Install dependencies

```bash
cd bots/211-resource-eligibility-bot
pip install -r requirements.txt
```

### 2. (Optional) Configure environment variables

```bash
# 211 API credentials — obtain a free key at https://developer.211.org
export API_211_KEY="your-key-here"
export API_211_BASE_URL="https://api.211.org/search/v1/resources"

# Session TTL in seconds (default: 3600 = 1 hour)
export SESSION_TTL_SECONDS=3600
```

If `API_211_KEY` is not set, the bot falls back to built-in mock data so you can demo it immediately.

### 3. Run the CLI

```bash
python bot.py
```

---

## Sample Interaction

```
============================================================
  211 Resource & Eligibility Checker Bot
  Type 'help' for options or 'quit' to exit.
============================================================

Bot: Hello! I'm the 211 Resource & Eligibility Checker...

You: I need help paying rent

Bot: What city or zip code are you in?

You: 10001

Bot: Here are resources near you:

1. City Housing Authority – Emergency Shelter (demo data)
   📍 123 Main St, Anytown, USA
   📞 1-800-555-0101
   Emergency shelter for families and individuals in crisis.
   🔗 https://example.org/housing
...

You: Am I eligible for SNAP?

Bot: What is your approximate annual household income (in USD)?

You: 24000

Bot: How many people are in your household (including yourself)?

You: 3

Bot: Based on the information you provided, here is your eligibility:

  SNAP: ✓ Likely Eligible
    Supplemental Nutrition Assistance Program (food stamps)
    (Your income is 92.9% of FPL; threshold is 130% of FPL)

  Medicaid: ✓ Likely Eligible
  ...
```

---

## Running Tests

```bash
# From the repository root
pytest tests/test_211_bot.py -v
```

---

## Architecture

```
bots/211-resource-eligibility-bot/
├── bot.py               # Main bot logic & CLI entry point
├── api_client.py        # 211 API + mock data layer
├── eligibility_engine.py# FPL-based eligibility calculations
├── database.py          # In-memory session store with TTL
├── config.py            # Configuration & translations
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

### Conversation State Machine

```
idle
 ├─ resource intent   → awaiting_location_for_resource → idle (show results)
 ├─ eligibility intent→ awaiting_income
 │                      → awaiting_household_size → idle (show eligibility)
 └─ language change   → idle (switch language, show welcome)
```

---

## Embedding in a Web Framework

The `ResourceEligibilityBot` class is framework-agnostic. Example with **Flask**:

```python
from flask import Flask, request, jsonify
from bot import ResourceEligibilityBot

app = Flask(__name__)
bot = ResourceEligibilityBot()
sessions = {}

@app.post("/chat/start")
def start():
    session_id = bot.start_session()
    return jsonify({"session_id": session_id, "message": bot.get_welcome_message(session_id)})

@app.post("/chat/message")
def message():
    data = request.json
    reply = bot.handle_message(data["session_id"], data["text"])
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
```

---

## Privacy & Compliance

* No user data is written to disk.
* Sessions expire automatically after `SESSION_TTL_SECONDS` (default: 1 hour).
* In production, replace the in-memory store with an encrypted Redis or Firestore instance configured with TTL policies.
* If the bot collects health-related information, ensure deployment adheres to **HIPAA** guidelines and consult legal counsel.

---

## Extending the Bot

### Add a new resource category

1. Add keywords to `_RESOURCE_KEYWORDS` in `bot.py`.
2. Add mock data to `_MOCK_RESOURCES` in `api_client.py`.
3. Add the category string to `RESOURCE_CATEGORIES` in `config.py`.

### Add a new eligibility program

Add an entry to `PROGRAMS` in `config.py`:

```python
"NewProgram": {
    "description": "Description of the program",
    "fpl_threshold": 1.50,   # 150% of FPL
    "category": "health",
},
```

### Add a new language

1. Add the ISO 639-1 code to `SUPPORTED_LANGUAGES` in `config.py`.
2. Add a translation dict to `TRANSLATIONS` in `config.py`.
3. Add the natural-language keyword → code mapping to `_LANGUAGE_MAP` in `bot.py`.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Conversational logic | Python 3.9+ |
| 211 API integration | `urllib` (stdlib) |
| Session storage | In-memory (extensible to Redis / Firebase) |
| Web embedding | Flask or FastAPI |
| Hosting | AWS / Azure / GCP |
| Testing | pytest |
