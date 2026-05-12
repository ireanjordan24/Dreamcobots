# DreamCo First Bot Launch Guide

## Goal
Launch your first DreamCo bot from scratch and understand the output.

---

## Choose Your First Bot

### Recommended for Beginners

| Bot | Complexity | GitHub Actions Ready |
|-----|-----------|---------------------|
| Integration Feedback Bot | ⭐ Easy | ✅ Yes |
| Company Lookup Bot | ⭐⭐ Medium | ✅ Yes |
| AI Enablement Hub | ⭐⭐ Medium | ✅ Yes |

---

## Launch Path 1: Integration Feedback Bot (Easiest)

### Via Python
```python
import sys
sys.path.insert(0, ".")
from bots.integration_feedback_bot.integration_feedback_bot import IntegrationFeedbackBot
from bots.integration_feedback_bot.tiers import Tier

bot = IntegrationFeedbackBot(tier=Tier.FREE)
result = bot.log_integration(
    platform="GitHub Actions",
    status="success",
    details="First launch successful!"
)
print(result)
```

### Via GitHub Actions
1. Go to [Actions → Integration Feedback Bot](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/integration-feedback.yml)
2. Click **Run workflow**
3. Fill in: platform=`My Platform`, status=`success`, details=`First run!`
4. Click **Run workflow**

---

## Launch Path 2: Company Lookup Bot

### Via Python
```python
import sys
sys.path.insert(0, ".")
from bots.company_lookup_bot.company_lookup_bot import CompanyLookupBot
from bots.company_lookup_bot.tiers import Tier

bot = CompanyLookupBot(tier=Tier.FREE)
result = bot.lookup("Stripe")
print(result["company"])
```

### Via GitHub Actions
1. Go to [Actions → Company Lookup Bot](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/company-lookup.yml)
2. Click **Run workflow**
3. Enter companies: `Stripe, Shopify, OpenAI`
4. Click **Run workflow**

---

## Launch Path 3: AI Enablement Hub

### Via GitHub Actions
1. Go to [Actions → AI Enablement Hub](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/ai-enablement-hub.yml)
2. Click **Run workflow**
3. Choose `report_type=summary`
4. Click **Run workflow**

---

## Understanding Bot Output

All bots log to `data/integration_log.json`. View with:
```bash
cat data/integration_log.json | python3 -m json.tool | head -30
```

---

## What's Next?
- Explore more bots in `bots/global_bot_network/bot_library.py`
- Learn to build your own bot in [Advanced Path](../Learning/advanced_path.md)
