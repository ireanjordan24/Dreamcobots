# Bots Details Instructions

> **Repository:** DreamCo-Technologies/Dreamcobots &nbsp;|&nbsp; **ID:** 1006128644

## Overview

This document provides detailed instructions about all the bots in the Dreamcobots repository,
including their operations, testing, deployment, and customization options.

All bots must adhere to the **GLOBAL AI SOURCES FLOW** mandatory architecture defined in
`framework/global_ai_sources_flow.py`. See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## Language Composition

| Language   | Files |
|------------|-------|
| Python     | 1,635 |
| JavaScript | 89    |
| Markdown   | 147   |
| JSON       | 41    |
| YAML       | 39    |
| HTML       | 20    |
| JSX        | 10    |
| Java       | 5     |
| Other      | 30+   |

---

## Bot Inventory

### Lead Generation & Sales Pipeline

| Bot | Directory | Description |
|-----|-----------|-------------|
| **LeadGenBot** | `bots/LeadGenBot/` | Automated lead discovery and qualification |
| **EnrichmentBot** | `bots/EnrichmentBot/` | Enriches lead profiles with additional data |
| **OutreachBot** | `bots/OutreachBot/` | Multi-channel outreach campaigns |
| **FollowUpBot** | `bots/FollowUpBot/` | Automated follow-up sequences |
| **CloserBot** | `bots/CloserBot/` | Sales closing assistant |
| **Lead Gen Bot** | `bots/lead_gen_bot/` | AI-powered lead generation |
| **Lead Generator Bot** | `bots/lead_generator_bot/` | Public source lead scraping |
| **Multi Source Lead Scraper** | `bots/multi_source_lead_scraper/` | Aggregates leads from multiple sources |
| **Public Lead Engine** | `bots/public_lead_engine/` | Extracts leads from public directories |
| **CRM Automation Bot** | `bots/crm_automation_bot/` | Syncs and automates CRM workflows |

### Government & Legal

| Bot | Directory | Description |
|-----|-----------|-------------|
| **Government Contract Grant Bot** | `bots/government-contract-grant-bot/` | SAM.gov contract searches and proposal generation |
| **Government Contract Bot** | `bots/government_contract_bot/` | Contract management and compliance |
| **211 Resource Eligibility Bot** | `bots/211-resource-eligibility-bot/` | Social services eligibility checker |
| **Legal Bot** | `bots/legal-bot/` | Legal research and document drafting |
| **Legal Money Bot** | `bots/legal_money_bot/` | Legal financial guidance |
| **Lawsuit Finder Bot** | `bots/lawsuit_finder_bot/` | Identifies relevant lawsuit opportunities |

### Real Estate

| Bot | Directory | Description |
|-----|-----------|-------------|
| **Real Estate Bot** | `bots/real-estate-bot/` | Property search and deal analysis |
| **Home Flipping Analyzer** | `bots/home_flipping_analyzer/` | ROI calculator for flip projects |
| **Foreclosure Finder Bot** | `bots/foreclosure_finder_bot/` | Finds foreclosure listings |
| **Home Buyer Bot** | `bots/home_buyer_bot/` | Guides buyers through the purchasing process |
| **Rental Cashflow Bot** | `bots/rental_cashflow_bot/` | Rental income and cashflow projections |
| **Car Flipping Bot** | `bots/car_flipping_bot/` | Used-car flip opportunity analyzer |
| **Dream Real Estate** | `bots/dream_real_estate/` | Full-stack real-estate automation |

### Finance & Crypto

| Bot | Directory | Description |
|-----|-----------|-------------|
| **Finance Bot** | `bots/finance-bot/` | Personal finance management |
| **Finance Bot (alt)** | `bots/finance_bot/` | Financial planning automation |
| **Crypto Bot** | `bots/crypto_bot/` | Cryptocurrency trading and tracking |
| **Stock Trading Bot** | `bots/stock_trading_bot/` | Equity trading signals |
| **Quantum Hedge Fund Manager** | `bots/quantum_hedge_fund_manager/` | AI-powered portfolio management |
| **Financial Literacy Bot** | `bots/financial_literacy_bot/` | Teaches financial concepts interactively |
| **Money Finder Bot** | `bots/money_finder_bot/` | Discovers unclaimed money and rebates |
| **Mining Bot** | `bots/mining_bot/` | Crypto mining optimization |
| **Profit Calculator Bot** | `bots/profit_calculator_bot/` | Revenue and profit scenario planning |
| **Alidropship Money Bot** | `bots/alidropship_money_bot/` | AliExpress dropship profitability bot |
| **Stack and Profit Bot** | `bots/stack_and_profit_bot/` | Income stacking strategies |

### Marketing & Content

| Bot | Directory | Description |
|-----|-----------|-------------|
| **Marketing Bot** | `bots/marketing-bot/` | Campaign orchestration |
| **Social Media Bot** | `bots/social_media_bot/` | Scheduled posting and engagement |
| **Social Media Manager Bot** | `bots/social_media_manager_bot/` | Full social media management |
| **Ad Copy Generator Bot** | `bots/ad_copy_generator_bot/` | AI ad copy generation |
| **Advertising Marketing Bot** | `bots/advertising_marketing_bot/` | Paid advertising automation |
| **Influencer Bot** | `bots/influencer_bot/` | Influencer outreach and tracking |
| **Logo Generator Bot** | `bots/logo_generator_bot/` | AI logo and brand asset creation |
| **AI Writing Bot** | `bots/ai_writing_bot/` | Long-form content generation |
| **Multi Channel Marketing** | `bots/multi_channel_marketing/` | Cross-platform campaign management |
| **Email Campaign Manager Bot** | `bots/email_campaign_manager_bot/` | Email drip campaign automation |
| **Creator Economy** | `bots/creator_economy/` | Monetization tools for creators |
| **Creator Empire** | `bots/creator_empire/` | Full creator business automation |
| **Cinecore Bot** | `bots/cinecore_bot/` | Video content creation and distribution |
| **Cinecore Lead Engine** | `bots/cinecore_lead_engine/` | Video-based lead generation |

### AI & Technology

| Bot | Directory | Description |
|-----|-----------|-------------|
| **AI Models Integration** | `bots/ai-models-integration/` | Tiered AI model integration (Free/Pro/Enterprise) |
| **AI Chatbot** | `bots/ai_chatbot/` | Tier-aware conversational AI chatbot |
| **AI Brain** | `bots/ai_brain/` | Central AI decision engine |
| **AI Learning System** | `bots/ai_learning_system/` | Continuous ML pipeline |
| **AI Level Up Bot** | `bots/ai_level_up_bot/` | Gamified AI skill progression |
| **AI Marketplace** | `bots/ai_marketplace/` | Marketplace for AI skills and plugins |
| **AI Side Hustle Bots** | `bots/ai-side-hustle-bots/` | AI-powered income generation tools |
| **Quantum AI Bot** | `bots/quantum_ai_bot/` | Quantum computing algorithms for AI |
| **Quantum Decision Bot** | `bots/quantum_decision_bot/` | Quantum-enhanced decision making |
| **Coding Assistant Bot** | `bots/coding_assistant_bot/` | Code generation and review |
| **Devops Bot** | `bots/devops_bot/` | CI/CD and infrastructure automation |
| **Security Tech Bot** | `bots/security_tech_bot/` | Cybersecurity monitoring and response |
| **Cybersecurity Bot** | `bots/cybersecurity-bot/` | Vulnerability scanning and hardening |
| **Software Bot** | `bots/software_bot/` | Software development automation |
| **Dreamco Code Bot** | `bots/dreamco_code_bot/` | DreamCo-specific coding assistant |
| **Space AI Bot** | `bots/space_ai_bot/` | Space mission planning and simulation |
| **Biomedical Bot** | `bots/biomedical_bot/` | Biomedical data analysis |

### Business & SaaS

| Bot | Directory | Description |
|-----|-----------|-------------|
| **Business Launch Pad** | `bots/business_launch_pad/` | Full business launch automation |
| **Business Automation** | `bots/business_automation/` | Back-office process automation |
| **SaaS Bot** | `bots/saas_bot/` | SaaS product management |
| **SaaS Selling Bot** | `bots/saas-selling-bot/` | SaaS sales automation |
| **SaaS Packages Bot** | `bots/saas_packages_bot/` | Package and pricing management |
| **SaaS Upsell** | `bots/saas_upsell/` | Upsell and expansion revenue bot |
| **Enterprise Integrations Bot** | `bots/enterprise_integrations_bot/` | Enterprise system connectors |
| **API Kit Bot** | `bots/api_kit_bot/` | API scaffolding and documentation |
| **App Builder Bot** | `bots/app_builder_bot/` | No-code/low-code app generation |
| **Factory Bot** | `bots/factory_bot/` | Automated production workflows |
| **Entrepreneur Bot** | `bots/entrepreneur-bot/` | Business idea validation and launch |
| **Dreamco Workspace Bot** | `bots/dreamco_workspace_bot/` | Workspace productivity automation |
| **Dreamco Empire OS** | `bots/dreamco_empire_os/` | Unified operating system for all bots |
| **Dreamco Cloud Bot** | `bots/dreamco_cloud_bot/` | Cloud infrastructure management |
| **DreamOps** | `bots/dreamops/` | DevOps and MLOps for DreamCo |
| **DreamAI Invent Hub** | `bots/dreamai_invent_hub/` | AI invention and prototyping lab |
| **Revenue Engine Bot** | `bots/revenue_engine_bot/` | Revenue optimization engine |
| **Revenue Growth Bot** | `bots/revenue_growth_bot/` | Growth hacking automation |
| **Revenue Validation** | `bots/revenue_validation/` | Revenue stream verification |

### E-Commerce & Affiliates

| Bot | Directory | Description |
|-----|-----------|-------------|
| **Ecommerce Bot** | `bots/ecommerce-bot/` | Online store automation |
| **Shopify Automation Bot** | `bots/shopify_automation_bot/` | Shopify store management |
| **Affiliate Bot** | `bots/affiliate_bot/` | Affiliate program management |
| **Discount Dominator** | `bots/discount_dominator/` | Deal and discount aggregation |
| **Deal Finder Bot** | `bots/deal_finder_bot/` | Automated deal discovery |
| **Buyer Network** | `bots/buyer_network/` | Buyer community management |

### HR, Education & Health

| Bot | Directory | Description |
|-----|-----------|-------------|
| **HR Bot** | `bots/hr-bot/` | Human resources automation |
| **Job Application Bot** | `bots/job-application-bot/` | Job search and application automation |
| **Selenium Job Application Bot** | `bots/selenium-job-application-bot/` | Browser-automated job applications |
| **Resume Builder Bot** | `bots/resume_builder_bot/` | AI resume generation |
| **Job Titles Bot** | `bots/job_titles_bot/` | Job title research and matching |
| **Education Bot** | `bots/education-bot/` | Learning and course management |
| **Health Wellness Bot** | `bots/health_wellness_bot/` | Personal health and wellness tracking |
| **Medical Bot** | `bots/medical-bot/` | Medical information and triage |
| **Emotional AI Bot** | `bots/emotional_ai_bot/` | Emotional intelligence and mental wellness |

### Buddy System

| Bot | Directory | Description |
|-----|-----------|-------------|
| **Buddy Bot** | `bots/buddy-bot/` | Personal AI buddy |
| **Buddy Core** | `bots/buddy_core/` | Core Buddy AI engine |
| **Buddy OS** | `bots/buddy_os/` | Buddy operating system |
| **Buddy Teach Bot** | `bots/buddy_teach_bot/` | Learning coach powered by Buddy |
| **Buddy Trainer Bot** | `bots/buddy_trainer_bot/` | AI and robotics trainer |
| **Buddy Trust Bot** | `bots/buddy_trust_bot/` | Trust and reputation management |
| **Buddy Omniscient Bot** | `bots/buddy_omniscient_bot/` | All-knowing companion AI |

### Infrastructure & Operations

| Bot | Directory | Description |
|-----|-----------|-------------|
| **Auto Bot Factory** | `bots/auto_bot_factory/` | Automated bot generation factory |
| **Bot Generator** | `bots/bot_generator/` | Dynamic bot scaffolding |
| **Bot Generator Bot** | `bots/bot_generator_bot/` | Meta-bot that generates new bots |
| **Auto Scaler** | `bots/auto_scaler/` | Dynamic resource scaling |
| **Automation Bot** | `bots/automation_bot/` | General-purpose task automation |
| **Control Center** | `bots/control_center/` | Centralized bot control |
| **Control Tower** | `bots/control_tower/` | High-level orchestration and monitoring |
| **Operational Dashboard** | `bots/operational_dashboard/` | Real-time operations view |
| **Division Performance Dashboard** | `bots/division_performance_dashboard/` | Division-level KPIs |
| **Analytics Dashboard Bot** | `bots/analytics_dashboard_bot/` | Analytics visualization |
| **Forecasting Tools Bot** | `bots/forecasting_tools_bot/` | Predictive analytics and forecasting |
| **Dataforge** | `bots/dataforge/` | Data pipeline and ETL automation |
| **CI Auto Fix Bot** | `bots/ci_auto_fix_bot/` | Auto-repairs failing CI pipelines |
| **PR Validation Bot** | `bots/pr_validation_bot/` | Automated pull request validation |
| **PR Learning Bot** | `bots/pr_learning_bot.py` | Learns from PRs and generates feedback |
| **Repo Bot** | `bots/repo_bot/` | Repository management automation |
| **Dreamco Payments** | `bots/dreamco_payments/` | Payment processing automation |
| **Stripe Integration** | `bots/stripe_integration/` | Stripe payment flows |
| **Stripe Payment Bot** | `bots/stripe_payment_bot/` | Stripe subscription management |
| **Stripe Key Rotation Bot** | `bots/stripe_key_rotation_bot/` | Automatic API key rotation |
| **Token Billing** | `bots/token_billing/` | Token-based billing engine |
| **Global AI Learning Matrix** | `bots/global_ai_learning_matrix/` | Cross-bot knowledge sharing |
| **Global Bot Network** | `bots/global_bot_network/` | Distributed bot mesh network |
| **Predictive Expansion** | `bots/predictive_expansion/` | Market expansion prediction |
| **Localized Bot** | `bots/localized_bot/` | Multi-language and locale support |
| **Smart City Bot** | `bots/smart_city_bot/` | Smart city infrastructure automation |
| **Open Claw Bot** | `bots/open_claw_bot/` | Hardware/robotics interface |

### Miscellaneous

| Bot | Directory | Description |
|-----|-----------|-------------|
| **Big Bro AI** | `bots/big_bro_ai/` | Motivational coaching and accountability |
| **God Bot** | `bots/god_bot/` | Supreme orchestration bot |
| **God Mode Bot** | `bots/god_mode_bot/` | Unrestricted automation mode |
| **Bot Wars Bot** | `bots/bot_wars_bot/` | Competitive bot testing arena |
| **Bot Marketplace** | `bots/bot_marketplace/` | Marketplace for buying/selling bots |
| **Dreamcobot** | `bots/dreamcobot/` | Flagship DreamCo automation bot |
| **Dream Sales Pro** | `bots/dream_sales_pro/` | Professional sales automation |
| **Hustle Bot** | `bots/hustle-bot/` | Side hustle identification and launch |
| **Lifestyle Bot** | `bots/lifestyle_bot/` | Lifestyle optimization assistant |
| **Customer Support Bot** | `bots/customer_support_bot/` | Customer service automation |
| **Fiverr Bot** | `bots/fiverr_bot/` | Fiverr gig management |
| **Referral Bot** | `bots/referral-bot/` | Referral program management |
| **Farewell Bot** | `bots/farewell-bot/` | Graceful bot shutdown and handoff |

---

## Operations

### Starting a Bot

```bash
cd bots/<bot_directory>
python <bot_script>.py
```

### Stopping a Bot

Most bots expose a `stop()` method. Call it programmatically or send SIGINT (`Ctrl+C`).

### Monitoring

- Run the web dashboard: `python ui/web_dashboard.py`
- Check bot status via the **Operational Dashboard** (`bots/operational_dashboard/`).
- Real-time metrics are available through `bots/analytics_dashboard_bot/`.

---

## Testing

### Testing Framework

Tests are located in the `tests/` and `__tests__/` directories. Python tests use **pytest**;
JavaScript tests use **Jest**.

```bash
# Run all Python tests
pytest

# Run all JS tests
npm test
```

### Framework Compliance Check

Verify every bot imports `GlobalAISourcesFlow`:

```bash
python tools/check_bot_framework.py
```

---

## Deployment

### General Deployment

1. Push changes to the `deployment-setup` branch.
2. Enable **GitHub Pages** in repository settings for frontend hosting.
3. Customize GitHub Actions workflows in `.github/workflows/` for bot scheduling.

### Docker

```bash
docker build -t dreamcobots .
docker run --rm dreamcobots
```

Or use Docker Compose:

```bash
docker-compose up
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

---

## Customization Options

### Bot Settings

Each bot reads configuration from its local `config.json` or from environment variables.
Refer to the individual bot's `README.md` for the full list of configurable options.

### Extending Functionality

1. Create a new directory under `bots/`.
2. Add a `main.py` that imports `GlobalAISourcesFlow` and defines a `run()` function.
3. Run `python tools/check_bot_framework.py` to verify compliance.
4. Submit a pull request following the guidelines in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Conclusion

Ensure you follow all instructions carefully to enable smooth operations and modifications of the bots.
For questions or contributions, open an issue or pull request in the
[DreamCo-Technologies/Dreamcobots](https://github.com/DreamCo-Technologies/Dreamcobots) repository.