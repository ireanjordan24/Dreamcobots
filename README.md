# DreamCObots Repository

Welcome to the DreamCObots project! This repository is the **DreamCo AI Bot App Store** — a comprehensive platform for deploying AI-powered bots across industries. Our mission is to develop and deploy collaborative AI bots designed to transform businesses worldwide.

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
or pass `tier=Tier.PRO` when constructing any bot class.

See full documentation in:
- [`bots/ai-models-integration/README.md`](bots/ai-models-integration/README.md)
- [`bots/ai_chatbot/README.md`](bots/ai_chatbot/README.md)

---
## 🤖 Bot Marketplace — 10 High-Priority Bots

The DreamCo Bot App Store launches with 10 fully standardized, tier-aware bots covering the most profitable AI automation niches. Each bot integrates with the BuddyAI system and supports SaaS recurring subscriptions.

| Bot | Directory | Key Features | Starting Price |
|-----|-----------|--------------|---------------|
| **Customer Support AI Bot** | `bots/customer_support_bot/` | Ticket routing, sentiment analysis, CRM integration | Free |
| **Lead Generation Bot** | `bots/lead_generation_bot/` | AI lead scoring, email sequences, CRM sync | Free |
| **AI Writing/Marketing Bot** | `bots/ai_writing_bot/` | Content generation, SEO optimization, templates | Free |
| **Real Estate Deal Finder Bot** | `bots/real_estate_bot/` | Property search, ROI calculator, MLS integration | Free |
| **Stock Trading Bot** | `bots/stock_trading_bot/` | Trading signals, backtesting, algorithmic strategies | Free |
| **Shopify Automation Bot** | `bots/shopify_automation_bot/` | Order processing, inventory sync, workflow automation | Free |
| **CRM Automation Bot** | `bots/crm_automation_bot/` | Contact management, pipeline automation, AI insights | Free |
| **Social Media Growth Bot** | `bots/social_media_bot/` | Post scheduling, engagement analytics, hashtag AI | Free |
| **Coding Assistant Bot** | `bots/coding_assistant_bot/` | Code completion, review, unit test generation | Free |
| **Fraud Detection Bot** | `bots/fraud_detection_bot/` | Transaction analysis, ML risk scoring, compliance reports | Free |

### Quick Start — Any Bot

```python
from bots.customer_support_bot.bot import CustomerSupportBot
from bots.ai_writing_bot.bot import AIWritingBot
# Import path uses the bots/ package directly
import sys, os
sys.path.insert(0, 'bots/ai-models-integration')
from tiers import Tier

# All bots follow the same tier-aware interface
bot = CustomerSupportBot(tier=Tier.PRO)
result = bot.handle_ticket({"message": "My order is late!", "category": "shipping"})
print(result["response"])

writer = AIWritingBot(tier=Tier.ENTERPRISE)
content = writer.generate_content({"topic": "AI trends", "type": "blog post"})
print(content["content"])
```

### BuddyAI Integration

Every bot exposes a `get_stats()` method with `"buddy_integration": True`, enabling seamless connection to the BuddyAI orchestration system:

```python
stats = bot.get_stats()
# {"tier": "pro", "requests_used": 42, "requests_remaining": "9958", "buddy_integration": True}
```

---
## Folder Explanation
### `bots`
- Contains all bot scripts and packages.
- `bots/ai-models-integration/` — tiered AI model integration (free/pro/enterprise).
- `bots/ai_chatbot/` — tier-aware AI chatbot built on top of the model integration.
- `bots/customer_support_bot/` — Customer Support AI Bot.
- `bots/lead_generation_bot/` — Lead Generation Bot.
- `bots/ai_writing_bot/` — AI Writing/Marketing Bot.
- `bots/real_estate_bot/` — Real Estate Deal Finder Bot.
- `bots/stock_trading_bot/` — Stock Trading Bot.
- `bots/shopify_automation_bot/` — Shopify Automation Bot.
- `bots/crm_automation_bot/` — CRM Automation Bot.
- `bots/social_media_bot/` — Social Media Growth Bot.
- `bots/coding_assistant_bot/` — Coding Assistant Bot.
- `bots/fraud_detection_bot/` — Fraud Detection Bot.
- `config.json` needs to be configured with required API keys and bot settings.

### `BuddyAI`
- Contains the central AI orchestration layer that connects all bots.

### `examples`
- Contains example use cases for different bots like `Referral Bot` and `Hustle Bot`.

---
## How to Run Bots Locally
1. Navigate to the bot directory. For example:
   ```bash
   cd bots/customer_support_bot
   ```
2. Run the bot script. For example:
   ```bash
   python bot.py
   ```
3. Make sure necessary APIs and configurations are set before running.

---
## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

All 10 marketplace bots have comprehensive test coverage in `tests/`.

---
## GitHub Pages Instructions
1. Navigate to **Settings > Pages**.
2. Select the `deployment-setup` branch and root directory as the publishing source.
3. Save your settings to host the frontend.

---