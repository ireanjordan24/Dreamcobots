# Government Contract & Grant Bot

Tier-aware assistant for finding and applying for government contracts and grant
funding opportunities on the Dreamcobots platform.

---

## Overview

The Government Contract & Grant Bot helps small businesses, nonprofits, and
consultants discover SAM.gov opportunities, find SBIR/STTR grants, write
compliant proposals, track bid status, and manage a full multi-agency contract
pipeline — all through a conversational interface.

---

## Tiers & Pricing

| Tier | Price/month | Requests/month | Highlights |
|---|---|---|---|
| **Free** | $0 | 500 | SAM.gov search, grant browse, eligibility checker |
| **Pro** | $49 | 10,000 | SBIR/STTR finder, proposal writer, compliance checklist |
| **Enterprise** | $299 | Unlimited | Teaming partner finder, set-aside optimizer, audit packages |

---

## Quick Start

```python
from bots.government_contract_grant_bot import GovernmentContractGrantBot
from bots.ai_chatbot.tiers import Tier

bot = GovernmentContractGrantBot(tier=Tier.PRO)

# Natural-language chat
response = bot.chat("Find SBIR grants for AI startups")
print(response["message"])

# Structured opportunity search
result = bot.search_opportunities("AI research", agency="NSF")
print(result["opportunities"])

# List available tools
print(bot.list_tools())
```

---

## Available Tools

### Free
- `opportunity_search` — search SAM.gov for open solicitations
- `grant_browse` — browse federal grant databases (Grants.gov)
- `eligibility_checker` — check eligibility for small-business set-asides

### Pro (includes all Free)
- `sbir_grant_finder` — find Phase I/II SBIR and STTR opportunities
- `contract_bid_tracker` — track open bids and award notifications
- `proposal_writer` — AI-assisted RFP/proposal drafting
- `compliance_checklist` — FAR/DFARS compliance checklists

### Enterprise (includes all Pro)
- `teaming_partner_finder` — find complementary small-business partners
- `set_aside_optimizer` — 8(a), HUBZone, SDVOSB, WOSB optimization
- `audit_package_generator` — audit-ready proposal packages
- `contract_pipeline_manager` — multi-agency pipeline CRM

---

## Monetization

- **SaaS subscription** — FREE / PRO ($49/mo) / ENTERPRISE ($299/mo)
- **Success fee** — optional percentage of awarded contract value (ENTERPRISE)
- **API pay-per-use** — per-search pricing for procurement platforms
- **White-label** — branded portals for government contract consultants (ENTERPRISE)

---

## BuddyAI Integration

```python
from BuddyAI import BuddyBot
from bots.government_contract_grant_bot import GovernmentContractGrantBot
from bots.ai_chatbot.tiers import Tier

buddy = BuddyBot()
buddy.register_bot("grants", GovernmentContractGrantBot(tier=Tier.PRO))
response = buddy.chat("grants", "What SBIR grants are available for cybersecurity?")
print(response["message"])
```

---

## Directory Structure

```
bots/government-contract-grant-bot/
├── government_contract_grant_bot.py   # Main bot class + tier config
└── README.md
```

## Running Tests

```bash
python -m pytest tests/test_government_contract_grant_bot.py -v
```
