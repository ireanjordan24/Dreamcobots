# Finance Bot

A tier-aware budget tracking and financial management bot on the Dreamcobots platform.

---

## Tier Overview

| Tier       | Price/month | Requests/month | Support          |
|------------|-------------|----------------|------------------|
| Free       | $0.00       | 500            | Community        |
| Pro        | $49.00      | 10,000         | Email (48 h SLA) |
| Enterprise | $299.00     | Unlimited       | Dedicated 24/7   |

---

## Features per Tier

| Feature                         | Free | Pro | Enterprise |
|--------------------------------|------|-----|------------|
| Basic budget tracking           | ✓    | ✓   | ✓          |
| Expense categorization          | ✓    | ✓   | ✓          |
| Monthly spending reports        | ✓    | ✓   | ✓          |
| Investment portfolio tracking   |      | ✓   | ✓          |
| Tax estimation                  |      | ✓   | ✓          |
| Multi-account sync              |      | ✓   | ✓          |
| Cash flow forecasting           |      | ✓   | ✓          |
| Bill reminders                  |      | ✓   | ✓          |
| AI financial advisor            |      |     | ✓          |
| Tax filing automation           |      |     | ✓          |
| Custom financial models         |      |     | ✓          |
| Multi-currency support          |      |     | ✓          |
| Audit-ready reports             |      |     | ✓          |
| Bank-level security             |      |     | ✓          |

---

## Quick Start

```python
import sys
sys.path.insert(0, "bots/ai-models-integration")
from tiers import Tier
from bots.finance_bot.finance_bot import FinanceBot

# Free tier — basic tracking
bot = FinanceBot(tier=Tier.FREE)
bot.log_income("salary", 3000.0)
bot.log_expense("food", 400.0, "Groceries")
bot.log_expense("transport", 150.0, "Bus pass")
summary = bot.get_budget_summary()
print(summary)

# Pro tier — cash flow forecast
pro_bot = FinanceBot(tier=Tier.PRO)
pro_bot.log_income("salary", 5000.0)
pro_bot.log_expense("rent", 1500.0)
forecast = pro_bot.forecast_cashflow(months=3)
print(forecast)

# Pro tier — tax estimate
taxes = pro_bot.estimate_taxes(income=60000.0, deductions=5000.0)
print(taxes)

# Tier info
bot.describe_tier()
bot.show_upgrade_path()
```

---

## Directory Structure

```
bots/finance_bot/
├── finance_bot.py  # Main bot class
├── tiers.py        # Bot-specific tier config
├── __init__.py
└── README.md       # This file
```
