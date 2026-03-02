# Bots

This directory contains all bot scripts and automation tools used in the
Dreamcobots project.

---

## Directory Structure

```
bots/
├── config.json                          # Shared configuration (API keys, settings)
└── government-contract-grant-bot/
    └── government_contract_grant_bot.py # Government Contract & Grant Bot
```

---

## Configuration (`config.json`)

Edit `config.json` to set your API credentials and search preferences before
running any bot.  Key fields:

| Field | Description |
|-------|-------------|
| `api_key` | API key for external data sources (leave empty if unused) |
| `log_level` | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, or `ERROR` |
| `contracts.search_keywords` | Keywords used when searching for government contracts |
| `grants.search_keywords` | Keywords used when searching for grant opportunities |
| `notifications.enabled` | Set to `true` to enable email notifications |
| `notifications.email` | Recipient email address for notifications |

> **Security note:** Never commit real API keys.  Use environment variables or
> Replit Secrets instead, and keep `api_key` empty in the committed file.

---

## Bots

### GovernmentContractGrantBot

**File:** `government-contract-grant-bot/government_contract_grant_bot.py`

Automates the discovery and processing of US government contracts and grants.

**Usage:**

```bash
python bots/government-contract-grant-bot/government_contract_grant_bot.py
```

**Methods:**

| Method | Description |
|--------|-------------|
| `start()` | Initialises the bot and prints a startup message |
| `process_contracts()` | Searches and processes government contract listings |
| `process_grants()` | Searches and processes grant opportunity listings |
| `run()` | Runs the full pipeline: start → contracts → grants |

---

## Debugging

Run the top-level `debug.py` utility to validate bot configuration and run a
quick stress test:

```bash
python debug.py
```

See [debug.py](../debug.py) for full documentation.