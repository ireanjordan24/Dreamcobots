# DreamCObots Repository

Welcome to the DreamCObots project! This repository outlines our groundbreaking mission to develop and deploy 3000 collaborative robots (cobots) designed for transforming industries worldwide. Explore our documentation, system details, and user guides to understand every aspect of this ambitious endeavor.

---
## Installation Instructions
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/ireanjordan24/Dreamcobots.git
   ```
2. Navigate to the directory:
   ```bash
   cd Dreamcobots
   ```
3. Install dependencies (if any bot scripts depend on a specific package manager, such as `pip` for Python):
   ```bash
   pip install -r requirements.txt
   ```

---
## Deployment Steps
To deploy bots or static content:
1. Push changes to the `deployment-setup` branch.
2. Enable **GitHub Pages** in repository settings for frontend hosting.
3. Add and customize workflows to automate bot tasks (see GitHub Actions).

---
## AI Model Editions — Free & Paid Tiers

All AI model integrations support three subscription tiers:

| Tier       | Price/month | Requests/month | Models | Support            |
|------------|-------------|----------------|--------|--------------------|
| **Free**   | $0.00       | 500            | 9      | Community          |
| **Pro**    | $49.00      | 10,000         | 18     | Email (48 h SLA)   |
| **Enterprise** | $299.00 | Unlimited      | 20     | Dedicated 24/7     |

### Free Edition
- GPT-3.5 Turbo, BERT Base, T5 Small *(NLP)*
- YOLOv5, ResNet-50 *(Computer Vision)*
- DALL-E 2, Stable Diffusion 1.4 *(Generative AI)*
- Prophet, XGBoost *(Data Analytics)*

### Pro Edition ($49/month)
Everything in Free, **plus**:
- GPT-4, BERT Large, T5-XL *(NLP)*
- YOLOv8, ResNet-152 *(Computer Vision)*
- DALL-E 3, Stable Diffusion XL *(Generative AI)*
- AutoML, LightGBM *(Data Analytics)*
- Batch processing, fine-tuning, analytics dashboard

### Enterprise Edition ($299/month)
Everything in Pro, **plus**:
- CLIP, GPT-4 Vision *(multimodal)*
- Custom models, SLA guarantee, dedicated support, white-label

To switch tiers, set `DREAMCOBOTS_TIER=FREE|PRO|ENTERPRISE` in your environment
or pass `tier=Tier.PRO` when constructing `AIModelsIntegration` / `Chatbot`.

See full documentation in:
- [`bots/ai-models-integration/README.md`](bots/ai-models-integration/README.md)
- [`bots/ai_chatbot/README.md`](bots/ai_chatbot/README.md)

---
## Sector Bots

Each sector bot is tier-aware (FREE / PRO / ENTERPRISE) and integrates with
BuddyAI for unified orchestration.

| Bot | Directory | README |
|-----|-----------|--------|
| AI Chatbot | `bots/ai_chatbot/` | [README](bots/ai_chatbot/README.md) |
| AI Models Integration | `bots/ai-models-integration/` | [README](bots/ai-models-integration/README.md) |
| Business Automation | `bots/business_automation/` | [README](bots/business_automation/README.md) |
| Finance Bot | `bots/finance_bot/` | [README](bots/finance_bot/README.md) |
| Marketing Bot | `bots/marketing_bot/` | [README](bots/marketing_bot/README.md) |
| Real Estate Bot | `bots/real_estate_bot/` | [README](bots/real_estate_bot/README.md) |
| Creator Economy Bot | `bots/creator_economy/` | [README](bots/creator_economy/README.md) |
| Lawsuit Finder Bot | `bots/lawsuit_finder_bot/` | [README](bots/lawsuit_finder_bot/README.md) |
| Government Contract & Grant Bot | `bots/government-contract-grant-bot/` | [README](bots/government-contract-grant-bot/README.md) |

---
## BuddyAI — Central Dialogue Hub

All sector bots integrate with **BuddyAI**, the central orchestration layer:

```python
from BuddyAI import BuddyBot
from bots.finance_bot import FinanceBot
from bots.marketing_bot import MarketingBot
from bots.ai_chatbot.tiers import Tier

buddy = BuddyBot()
buddy.register_bot("finance", FinanceBot(tier=Tier.PRO))
buddy.register_bot("marketing", MarketingBot(tier=Tier.PRO))

print(buddy.chat("finance", "Analyze my Q3 cash flow")["message"])
print(buddy.chat("marketing", "Write an email for our product launch")["message"])
```

See full documentation in [`BuddyAI/README.md`](BuddyAI/README.md).

---
## Folder Explanation

### `BuddyAI/`
Central dialogue integration layer.  Provides `BuddyBot` (bot registry & router)
and `EventBus` (pub/sub event system).  See [`BuddyAI/README.md`](BuddyAI/README.md).

### `bots/`
All sector bot packages, each with a standardised structure:
```
bots/<sector>/
├── <sector>_bot.py   # Main tier-aware bot class
├── tiers.py          # Sector-specific tier configuration
├── __init__.py
└── README.md
```

- `bots/ai-models-integration/` — tiered AI model integration (free/pro/enterprise).
- `bots/ai_chatbot/` — tier-aware AI chatbot.
- `bots/business_automation/` — workflow & task automation.
- `bots/finance_bot/` — personal & business finance assistant.
- `bots/marketing_bot/` — digital marketing & campaign automation.
- `bots/real_estate_bot/` — property search & investment analysis.
- `bots/creator_economy/` — creator monetisation & brand deals.
- `bots/lawsuit_finder_bot/` — legal case research & lawsuit discovery.
- `bots/government-contract-grant-bot/` — government contracts & grant finder.
- `config.json` — configure API keys and bot settings.

### `tests/`
Pytest test suites for all bots.  Run the full suite with:
```bash
python -m pytest tests/ -v
```

### `examples/`
Example use cases for different bots like `Referral Bot` and `Hustle Bot`.

---
## How to Run Bots Locally

```python
# Import any sector bot and start chatting
from bots.business_automation import BusinessAutomationBot
from bots.ai_chatbot.tiers import Tier

bot = BusinessAutomationBot(tier=Tier.PRO)
result = bot.chat("Schedule a team meeting for Monday 9 AM")
print(result["message"])
```

---
## Running Tests

```bash
# Full test suite
python -m pytest tests/ -v

# Single bot
python -m pytest tests/test_business_automation.py -v
python -m pytest tests/test_finance_bot.py -v
python -m pytest tests/test_marketing_bot.py -v
python -m pytest tests/test_real_estate_bot.py -v
python -m pytest tests/test_creator_economy.py -v
python -m pytest tests/test_lawsuit_finder_bot.py -v
python -m pytest tests/test_government_contract_grant_bot.py -v
python -m pytest tests/test_buddy_bot.py -v
```

---
## GitHub Pages Instructions
1. Navigate to **Settings > Pages**.
2. Select the `deployment-setup` branch and root directory as the publishing source.
3. Save your settings to host the frontend.

---