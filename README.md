# DreamCObots Repository

Welcome to the **DreamCObots** project — a unified ecosystem of 35+ AI-powered bots built for the DreamCo platform. Every bot in this repository follows the **GLOBAL AI SOURCES FLOW** framework, ensuring performance, efficiency, scalability, and seamless interoperability.

---

## Architecture Overview

```
GLOBAL AI SOURCES FLOW
┌─────────────────────────────────────────────────┐
│  Research Papers │ GitHub │ Kaggle │ AI Labs     │
│  US │ China │ India │ EU │ Global Labs           │
└─────────────────────────────────────────────────┘
                      │
                      ▼
          Data Ingestion → Classifier → Sandbox Lab
          → Analytics → Hybrid Evolution Engine
          → Deployment → Profit/Market Intelligence
          → Governance & Security
                      │
                      ▼
              BuddyAI Orchestration Layer
          (register / route / broadcast bots)
                      │
                      ▼
        ┌─────────────────────────────────────┐
        │         35+ Specialized Bots        │
        └─────────────────────────────────────┘
```

All bots share:
- **Three subscription tiers**: FREE · PRO · ENTERPRISE
- **BuddyAI integration**: register with the central orchestrator via `chat()` or `process()`
- **Framework compliance**: every bot references the `GlobalAISourcesFlow` pipeline

---

## Installation

```bash
git clone https://github.com/ireanjordan24/Dreamcobots.git
cd Dreamcobots
pip install -r requirements.txt
```

Run all 1 800+ tests:

```bash
python -m pytest tests/ -v
```

Check framework compliance:

```bash
python tools/check_bot_framework.py
```

---

## Bot Directory

### 🤖 Core AI Platform
| Bot | Location | Description |
|-----|----------|-------------|
| AI Models Integration | `bots/ai-models-integration/` | 20 models across NLP, CV, Generative AI, Data Analytics |
| AI Chatbot | `bots/ai_chatbot/` | Tier-aware chatbot built on the model integration layer |
| AI Learning System | `bots/ai_learning_system/` | Adaptive learning with hybrid engine, sandbox, analytics |
| Global Learning System | `global_learning_system/` | Microservice architecture for continuous AI learning |

### 💰 Finance & Payments
| Bot | Location | Description |
|-----|----------|-------------|
| DreamCo Payments | `bots/dreamco_payments/` | Full-stack payment processing (Stripe rival) |
| Finance Bot | `bots/finance_bot/` | Personal & business financial management |
| Mining Bot | `bots/mining_bot/` | Multi-strategy crypto mining with fraud detection |
| Stock Trading Bot | `bots/stock_trading_bot/` | AI-powered stock analysis and trading signals |
| Affiliate Bot | `bots/affiliate_bot/` | Automated affiliate marketing & commission tracking |
| Money Finder Bot | `bots/money_finder_bot/` | Discovers unclaimed money & financial opportunities |

### 🏪 Retail & Commerce
| Bot | Location | Description |
|-----|----------|-------------|
| Discount Dominator | `bots/discount_dominator/` | 200-setting retail intelligence engine (settings 401-600) |
| Shopify Automation Bot | `bots/shopify_automation_bot/` | End-to-end Shopify store automation |
| CRM Automation Bot | `bots/crm_automation_bot/` | Customer relationship management automation |
| Lead Generation Bot | `bots/lead_generation_bot/` | AI-powered lead capture and qualification |
| Real Estate Bot | `bots/real_estate_bot/` | Property search, valuation, and investment analysis |
| Car Flipping Bot | `bots/car_flipping_bot/` | Vehicle sourcing, valuation, and resale optimization |
| Deal Finder Bot | `bots/deal_finder_bot/` | Automated deal discovery and price comparison |

### 🎨 Creator Economy
| Bot | Location | Description |
|-----|----------|-------------|
| Creator Empire | `bots/creator_empire/` | Talent agency, streaming, events, monetization |
| Creator Economy Bot | `bots/creator_economy/` | Multi-platform creator revenue management |
| AI Writing Bot | `bots/ai_writing_bot/` | Content creation, copywriting, and editing |
| Social Media Bot | `bots/social_media_bot/` | Cross-platform scheduling and analytics |

### 🏢 Business & Professional
| Bot | Location | Description |
|-----|----------|-------------|
| Business Automation Bot | `bots/business_automation/` | End-to-end business process automation |
| Automation Bot | `bots/automation_bot/` | General-purpose workflow automation |
| Government Contract Bot | `bots/government-contract-grant-bot/` | Contract search & grant application drafting |
| Lawsuit Finder Bot | `bots/lawsuit_finder_bot/` | Legal case discovery and analysis |
| Marketing Bot | `bots/marketing_bot/` | Multi-channel campaign management |
| Revenue Growth Bot | `bots/revenue_growth_bot/` | Revenue optimization and growth strategies |
| Software Bot | `bots/software_bot/` | Code generation and software project management |
| App Builder Bot | `bots/app_builder_bot/` | No-code/low-code app development assistance |
| Coding Assistant Bot | `bots/coding_assistant_bot/` | AI pair programmer and code reviewer |

### 👤 Lifestyle & Health
| Bot | Location | Description |
|-----|----------|-------------|
| 211 Resource Bot | `bots/211-resource-eligibility-bot/` | Community resource finder with GPS routing |
| Health & Wellness Bot | `bots/health_wellness_bot/` | Personalized health tracking and recommendations |
| Lifestyle Bot | `bots/lifestyle_bot/` | Daily routine optimization and goal tracking |
| Education Bot | `bots/education_bot/` | Personalized learning paths and tutoring |

### 🔒 Security & Fraud
| Bot | Location | Description |
|-----|----------|-------------|
| Security Tech Bot | `bots/security_tech_bot/` | Cybersecurity monitoring and threat detection |
| Fraud Detection Bot | `bots/fraud_detection_bot/` | Real-time transaction fraud analysis |
| Customer Support Bot | `bots/customer_support_bot/` | AI-powered multi-channel customer service |

### 🎮 Platform
| Component | Location | Description |
|-----------|----------|-------------|
| Control Center | `bots/control_center/` | Unified dashboard for all bot management |
| BuddyAI | `BuddyAI/` | Central orchestration layer (EventBus + BuddyBot) |
| Framework | `framework/` | Global AI Sources Flow pipeline |

---

## Subscription Tiers

All bots support three tiers (configured via `DREAMCOBOTS_TIER` env var or constructor arg):

| Tier | Price/month | Requests/month | Support |
|------|-------------|----------------|---------|
| **FREE** | $0 | 500 | Community |
| **PRO** | varies | 10,000+ | Email (48h SLA) |
| **ENTERPRISE** | varies | Unlimited | Dedicated 24/7 |

```python
from tiers import Tier

# Example: create a PRO-tier bot
bot = SomeDreamCoBot(tier=Tier.PRO)
```

---

## BuddyAI Orchestration

```python
from BuddyAI.buddy_bot import BuddyBot
from BuddyAI.event_bus import EventBus
from tiers import Tier

# Create orchestrator
hub = BuddyBot(tier=Tier.PRO)

# Register bots (supports both chat() and process() protocols)
hub.register_bot("payments", DreamcoPaymentsBot(Tier.STARTER))
hub.register_bot("chatbot", Chatbot(tier=Tier.PRO))

# Route messages
result = hub.route_message("chatbot", "Hello!")

# Broadcast to all bots
responses = hub.broadcast("system status check")

# Subscribe to events
hub.event_bus.subscribe("bot_registered", lambda p: print(f"Bot joined: {p['name']}"))
```

---

## Global AI Sources Framework

Every bot is wired into the 8-stage Global AI Sources Flow pipeline:

```python
from framework import GlobalAISourcesFlow

flow = GlobalAISourcesFlow(bot_name="MyBot")
result = flow.run_pipeline(
    raw_data={"domain": "my_domain"},
    learning_method="supervised",
)
# result["pipeline_complete"] == True
```

---

## Deployment Steps

1. Push changes to the `main` branch.
2. GitHub Actions CI automatically runs all 1 800+ tests in parallel jobs.
3. The framework compliance checker verifies all bots reference the Global AI Sources Flow.
4. Enable **GitHub Pages** in repository settings for frontend hosting.

---

## Development

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific bot's tests
python -m pytest tests/test_dreamco_payments.py -v

# Check framework compliance
python tools/check_bot_framework.py

# Run with coverage (optional)
pip install pytest-cov
python -m pytest tests/ --cov=bots --cov-report=html
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines.

---

## AI Model Editions — Free & Paid Tiers

All AI model integrations support three subscription tiers:

| Tier | Price/month | Requests/month | Models | Support |
|------|-------------|----------------|--------|---------|
| **Free** | $0.00 | 500 | 9 | Community |
| **Pro** | $49.00 | 10,000 | 18 | Email (48 h SLA) |
| **Enterprise** | $299.00 | Unlimited | 20 | Dedicated 24/7 |

See full documentation in:
- [`bots/ai-models-integration/README.md`](bots/ai-models-integration/README.md)
- [`bots/ai_chatbot/README.md`](bots/ai_chatbot/README.md)


> **Contributors:** All bots must follow the **GLOBAL AI SOURCES FLOW** mandatory architecture.
> See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---
## GLOBAL AI SOURCES FLOW — Mandatory Architecture

Every DreamCo bot must implement the eight-stage pipeline defined in
`framework/global_ai_sources_flow.py`:

```
GLOBAL AI SOURCES → Data Ingestion → Learning Classifier → Sandbox Test Lab
  → Performance Analytics → Hybrid Evolution Engine → Deployment Engine
  → Profit & Market Intelligence → Governance + Security
```

See [`framework/global_ai_sources_flow.py`](framework/global_ai_sources_flow.py)
and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full specification and
contribution requirements.

To check that all bots in the repository comply with the framework, run:

```bash
python tools/check_bot_framework.py
```

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
## Folder Explanation
### `framework`
- Contains the mandatory **GLOBAL AI SOURCES FLOW** pipeline module
  (`global_ai_sources_flow.py`) that every bot must import and use.

### `tools`
- `check_bot_framework.py` — static analysis script to verify all bot files
  reference the framework.

### `bots`
- Contains all bot scripts such as the `government-contract-grant-bot`.
- `bots/ai-models-integration/` — tiered AI model integration (free/pro/enterprise).
- `bots/ai_chatbot/` — tier-aware AI chatbot built on top of the model integration.
- `config.json` needs to be configured with required API keys and bot settings.

### `examples`
- Contains example use cases for different bots like `Referral Bot` and `Hustle Bot`.

---
## How to Run Bots Locally
1. Navigate to the bot directory. For example:
   ```bash
   cd bots/government-contract-grant-bot
   ```
2. Run the bot script. For example:
   ```bash
   python bot.py
   ```
3. Make sure necessary APIs and configurations are set before running.

---
## GitHub Pages Instructions
1. Navigate to **Settings > Pages**.
2. Select the `deployment-setup` branch and root directory as the publishing source.
3. Save your settings to host the frontend.

---