# Government Contract & Grant Bot

A tier-aware bot for discovering government contracts, checking grant eligibility,
and managing compliance on the Dreamcobots platform.

---

## Tier Overview

| Tier       | Price/month | Requests/month | Key Features                           | Support          |
|------------|-------------|----------------|----------------------------------------|------------------|
| Free       | $0.00       | 500            | Basic search, eligibility check        | Community        |
| Pro        | $49.00      | 10,000         | Advanced search, drafting, SAM.gov     | Email (48 h SLA) |
| Enterprise | $299.00     | Unlimited       | Compliance tracking, custom matching   | Dedicated 24/7   |

---

## Features per Tier

| Feature                        | Free | Pro | Enterprise |
|-------------------------------|------|-----|------------|
| Contract search (basic)        | ✓    | ✓   | ✓          |
| Grant eligibility check        | ✓    | ✓   | ✓          |
| 5 searches/day                 | ✓    |     |            |
| Advanced contract search       |      | ✓   | ✓          |
| Grant application drafting     |      | ✓   | ✓          |
| SAM.gov integration            |      | ✓   | ✓          |
| 100 searches/day               |      | ✓   |            |
| Priority contract alerts       |      |     | ✓          |
| Custom grant matching          |      |     | ✓          |
| Compliance tracking            |      |     | ✓          |
| Unlimited searches             |      |     | ✓          |
| Dedicated contract specialist  |      |     | ✓          |

---

## Quick Start

```python
import sys, os
sys.path.insert(0, "bots/ai-models-integration")
from tiers import Tier

from bots.government_contract_grant_bot.government_contract_grant_bot import GovernmentContractGrantBot

# Free tier — basic search
bot = GovernmentContractGrantBot(tier=Tier.FREE)
result = bot.search_contracts("cybersecurity services")
print(result)

# Check eligibility
eligibility = bot.check_grant_eligibility({
    "name": "Acme Corp",
    "type": "small_business",
    "sector": "IT",
})
print(eligibility)

# Pro tier — draft a grant application
pro_bot = GovernmentContractGrantBot(tier=Tier.PRO)
draft = pro_bot.draft_grant_application("GR-001", {"name": "Acme Corp"})
print(draft["draft"])

# Enterprise — compliance tracking
ent_bot = GovernmentContractGrantBot(tier=Tier.ENTERPRISE)
compliance = ent_bot.track_compliance("GOV-0001")
print(compliance)

# Tier info
bot.describe_tier()
bot.show_upgrade_path()
```

---

## Directory Structure

```
bots/government-contract-grant-bot/
├── government_contract_grant_bot.py  # Main bot class
├── tiers.py                          # Bot-specific tier config
├── __init__.py
└── README.md                         # This file
```
