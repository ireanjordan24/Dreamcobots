# Real Estate Bot

Tier-aware real estate deal finder and ROI analyzer. Searches properties, evaluates deals, estimates ROI, and tracks market trends.

## Tiers

| Feature | FREE | PRO | ENTERPRISE |
|---------|------|-----|------------|
| Locations | 1 | 10 | Unlimited |
| Market trends | ✗ | ✓ | ✓ |
| AI Valuation | ✗ | ✗ | ✓ |
| Predictive analytics | ✗ | ✗ | ✓ |

## Usage

```python
from bots.real_estate_bot.real_estate_bot import RealEstateBot
from tiers import Tier

bot = RealEstateBot(tier=Tier.PRO)
deals = bot.search_deals("austin", budget=400000)
evaluation = bot.evaluate_property("1204 Oak Blvd, Austin TX")
roi = bot.estimate_roi(deals[0])
trends = bot.get_market_trends("phoenix")
```

## Methods

- `search_deals(location, budget)` — returns properties under budget
- `evaluate_property(address)` — returns valuation and cash flow analysis
- `estimate_roi(property)` — returns estimated annual ROI percentage
- `get_market_trends(location)` — returns price trends and inventory data (PRO+)

## Directory Structure

```
bots/real_estate_bot/
├── real_estate_bot.py
├── tiers.py
├── __init__.py
└── README.md
```
