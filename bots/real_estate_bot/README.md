# Real Estate Bot

A tier-aware AI-powered property search and investment analysis bot for the Dreamcobots platform. Finds deals, analyzes properties, and calculates ROI based on your subscription tier.

## Installation

```bash
pip install -r requirements.txt
```

```python
from bots.real_estate_bot.bot import RealEstateBot
from bots.real_estate_bot.tiers import get_real_estate_tier_info
```

## Tiers

| Feature                  | Free ($0/mo)              | Pro ($49/mo)                        | Enterprise ($299/mo)                      |
|--------------------------|---------------------------|-------------------------------------|-------------------------------------------|
| Searches per month       | 10                        | 500                                 | Unlimited                                 |
| Deals returned           | 2 per search              | 5 with scores                       | 10 with full analytics                    |
| Deal scoring             | ❌                        | ✅                                  | ✅                                        |
| Property analysis        | ❌                        | ✅                                  | ✅ (enhanced)                             |
| ROI calculator           | ❌                        | ✅                                  | ✅                                        |
| Predictive pricing       | ❌                        | ❌                                  | ✅                                        |
| Portfolio management     | ❌                        | ❌                                  | ✅                                        |
| MLS integration          | ❌                        | ❌                                  | ✅                                        |

## Usage

### Initialize the bot

```python
from bots.real_estate_bot.bot import RealEstateBot
from tiers import Tier

bot = RealEstateBot(tier=Tier.PRO)
```

### Find property deals

```python
criteria = {
    "location": "Austin, TX",
    "budget": 400000.0,
    "type": "residential"
}

result = bot.find_deals(criteria)
print(result)
# {
#   "deals": [
#     {"property_id": "PROP-ABC123", "address": "100 Main St, Austin, TX",
#      "price": 250000.0, "type": "residential", "score": 0.5},
#     ...
#   ],
#   "count": 5,
#   "tier": "pro"
# }
```

### Analyze a property (PRO/ENTERPRISE)

```python
result = bot.analyze_property("PROP-ABC123")
print(result)
# {
#   "property_id": "PROP-ABC123",
#   "estimated_value": 320000.0,
#   "roi_estimate": 0.07,
#   "risk_score": 0.35,
#   "tier": "pro"
# }
```

### Calculate ROI (PRO/ENTERPRISE)

```python
property_data = {
    "price": 300000.0,
    "rent": 2200.0,
    "expenses": 500.0
}

result = bot.calculate_roi(property_data)
print(result)
# {
#   "property": {"price": 300000.0, "rent": 2200.0, "expenses": 500.0},
#   "annual_roi": 0.068,
#   "monthly_cashflow": 1700.0,
#   "tier": "pro"
# }
```

### Get bot statistics

```python
stats = bot.get_stats()
print(stats)
# {
#   "tier": "pro",
#   "requests_used": 3,
#   "requests_remaining": "497",
#   "buddy_integration": True
# }
```

## License

MIT
