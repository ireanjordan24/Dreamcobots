# Real Estate Bot

Tier-aware property search and transaction assistant for the Dreamcobots platform.

---

## Overview

The Real Estate Bot helps home buyers, investors, and agents search listings,
analyse investment returns, calculate rental yields, pull comparable sales, and
manage full property deal pipelines — all through a conversational interface.

---

## Tiers & Pricing

| Tier | Price/month | Requests/month | Highlights |
|---|---|---|---|
| **Free** | $0 | 500 | Property search, market overview, mortgage estimator |
| **Pro** | $49 | 10,000 | Investment analysis, rental yield, comps reports, alerts |
| **Enterprise** | $299 | Unlimited | MLS integration, portfolio manager, deal pipeline CRM |

---

## Quick Start

```python
from bots.real_estate_bot import RealEstateBot
from bots.ai_chatbot.tiers import Tier

bot = RealEstateBot(tier=Tier.PRO)

# Natural-language chat
response = bot.chat("Find 3-bedroom homes under $400k in Austin, TX")
print(response["message"])

# Structured property search
result = bot.search_properties({
    "location": "Austin, TX",
    "max_price": 400_000,
    "bedrooms": 3,
})
print(result["results"])
```

---

## Available Tools

### Free
- `property_search` — search public MLS and Zillow-style listings
- `market_overview` — price trends and days-on-market stats
- `mortgage_estimator` — monthly payment calculator

### Pro (includes all Free)
- `investment_analyzer` — ROI, cap rate, and cash-on-cash return
- `rental_yield_calculator` — gross and net rental yield
- `comps_report` — comparable sales in a 1-mile radius
- `deal_alerts` — email/SMS notifications for new listings

### Enterprise (includes all Pro)
- `mls_integration` — direct MLS data feed
- `portfolio_manager` — multi-property performance dashboard
- `deal_pipeline_crm` — track offers, contingencies, and closings
- `commercial_underwriter` — NOI, DSCR, and LTV underwriting

---

## Monetization

- **SaaS subscription** — FREE / PRO ($49/mo) / ENTERPRISE ($299/mo)
- **API pay-per-use** — per-search pricing for high-volume integrations
- **White-label** — branded portals for real estate brokerages (ENTERPRISE)

---

## BuddyAI Integration

```python
from BuddyAI import BuddyBot
from bots.real_estate_bot import RealEstateBot
from bots.ai_chatbot.tiers import Tier

buddy = BuddyBot()
buddy.register_bot("real_estate", RealEstateBot(tier=Tier.PRO))
response = buddy.chat("real_estate", "What is the rental yield on a $300k property?")
print(response["message"])
```

---

## Directory Structure

```
bots/real_estate_bot/
├── real_estate_bot.py   # Main bot class
├── tiers.py             # Tier config (tools & features)
├── __init__.py
└── README.md
```

## Running Tests

```bash
python -m pytest tests/test_real_estate_bot.py -v
```
