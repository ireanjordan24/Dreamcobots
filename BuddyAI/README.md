# BuddyAI

This directory contains the central AI code to manage and communicate with all bots.

---

## Residual Income Automation System

BuddyBot is Dreamco's autonomous residual-income management system. It tracks, optimises, and grows income from multiple passive streams using modular, AI-powered components.

### Module Overview

| Module | Description |
|---|---|
| `config.py` | Loads configuration from environment variables or `config.json` |
| `event_bus.py` | Lightweight publish/subscribe event bus decoupling all modules |
| `income_tracker.py` | Fetches & aggregates income data from 7 source adapters |
| `dashboard.py` | Renders income reports to console and disk |
| `content_automation.py` | Generates blog posts, e-books, SaaS ideas, and video outlines |
| `market_analysis.py` | Scans market trends and scores passive-income opportunities |
| `ml_optimizer.py` | Predicts revenue trends and optimises income stream configs |
| `buddy_bot.py` | Main orchestrator – wires all modules together |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full automation cycle
python -m BuddyAI.buddy_bot run

# Collect & display income only
python -m BuddyAI.buddy_bot income

# Run market analysis
python -m BuddyAI.buddy_bot market

# Generate content for a niche
python -m BuddyAI.buddy_bot content --niche "passive income" --type blog

# Optimise a specific idea
python -m BuddyAI.buddy_bot optimise "AI Blog Network"
```

---

## Configuration

Copy `BuddyAI/config.json.example` to `BuddyAI/config.json` and fill in your API keys,
**or** set environment variables prefixed with `BUDDYAI_`:

```bash
export BUDDYAI_YOUTUBE_API_KEY=your_key_here
export BUDDYAI_OPENAI_API_KEY=your_key_here
```

The system works without any credentials using built-in stub implementations.

---

## Running Tests

```bash
pytest tests/test_buddy_bot.py -v
```

---

## Architecture

All modules communicate through the shared `EventBus`. This decouples components
so each can be developed, tested, and replaced independently.

```
BuddyBot (orchestrator)
 ├── IncomeTracker  ──── publishes: income.collected, income.summarized
 ├── Dashboard      ──── subscribes: income.summarized
 ├── ContentAutomation── publishes: content.blog_post_created, …
 ├── MarketAnalysis ──── publishes: market.analysis_complete, …
 ├── IncomePredictor
 └── OptimizationEngine─ publishes: optimizer.result, optimizer.scale_plan
```

---

## Extending the System

### Adding a new income source

1. Create a class inheriting from `IncomeSourceAdapter` in `income_tracker.py`
2. Implement the `fetch()` method to return an `IncomeRecord`
3. Add your class to `_DEFAULT_ADAPTERS`

### Integrating a real API

Replace the stub `fetch()` implementation with real HTTP calls. The adapter
interface guarantees the rest of the system continues to work unchanged.
