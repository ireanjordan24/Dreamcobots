# DreamCobots

> **Autonomous AI Bot Platform** — a production-ready ecosystem of specialised bots
> that collect, process, and monetise data while automating high-value business workflows.

---

## Project Overview

DreamCobots is a modular Python platform that orchestrates a fleet of 16 autonomous
AI bots, each targeting a distinct vertical: finance, legal, healthcare, real estate,
government contracting, e-commerce, and more. At the centre of the platform sits
**DataForge**, a data-intelligence engine that ingests structured outputs from every
bot, generates high-quality synthetic training datasets, enforces regulatory compliance
(GDPR, CCPA, HIPAA), and publishes curated datasets to leading AI/ML marketplaces.

**Key numbers:**
- 16 specialised bots (15 vertical bots + DataForge)
- 100+ API integrations
- 231 passing unit/integration tests
- Regulatory compliance built-in (GDPR · CCPA · HIPAA)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        DreamCobots Platform                       │
│                                                                    │
│  ┌────────────┐  ┌─────────┐  ┌──────────┐  ┌────────────────┐  │
│  │FinanceBot  │  │LegalBot │  │MedicalBot│  │  14 more bots  │  │
│  └─────┬──────┘  └────┬────┘  └────┬─────┘  └───────┬────────┘  │
│        └──────────────┴────────────┴────────────────┘            │
│                               │                                    │
│                  ┌────────────▼───────────┐                       │
│                  │      Orchestrator       │                       │
│                  │  (thread-safe routing)  │                       │
│                  └────────────┬───────────┘                       │
│                               │                                    │
│                  ┌────────────▼───────────┐                       │
│                  │       DataForge Bot     │                       │
│                  │  Dataset Gen · Comply   │                       │
│                  │  Marketplace · Publish  │                       │
│                  └────────────────────────┘                       │
└──────────────────────────────────────────────────────────────────┘
         │                 │                  │
   HuggingFace          Kaggle        AWS / Direct API
```

---

## Bot Ecosystem

| # | Bot | Directory | Specialisation |
|---|-----|-----------|---------------|
| 1 | **DataForge** | `bots/dataforge/` | Data generation, compliance & marketplace |
| 2 | **Finance Bot** | `bots/finance-bot/` | Market data, portfolio analysis |
| 3 | **Legal Bot** | `bots/legal-bot/` | Contract analysis, regulatory research |
| 4 | **Medical Bot** | `bots/medical-bot/` | Healthcare data, clinical summaries |
| 5 | **Real Estate Bot** | `bots/real-estate-bot/` | Property listings, market trends |
| 6 | **Government Contract & Grant Bot** | `bots/government-contract-grant-bot/` | Federal contracts & grants |
| 7 | **E-commerce Bot** | `bots/ecommerce-bot/` | Product data, pricing optimisation |
| 8 | **Marketing Bot** | `bots/marketing-bot/` | Campaign analytics, audience segmentation |
| 9 | **HR Bot** | `bots/hr-bot/` | Talent acquisition, HR analytics |
| 10 | **Education Bot** | `bots/education-bot/` | Learning content, skill gap analysis |
| 11 | **Entrepreneur Bot** | `bots/entrepreneur-bot/` | Business intelligence, opportunity scoring |
| 12 | **Hustle Bot** | `bots/hustle-bot/` | Gig economy, side-income automation |
| 13 | **Cybersecurity Bot** | `bots/cybersecurity-bot/` | Threat intelligence, vulnerability data |
| 14 | **Referral Bot** | `bots/referral-bot/` | Referral tracking, growth automation |
| 15 | **Buddy Bot** | `bots/buddy-bot/` | User engagement, conversational AI |
| 16 | **Farewell Bot** | `bots/farewell-bot/` | Churn analysis, offboarding workflows |

---

## Quick Start

### Docker (recommended)

```bash
# 1. Copy environment template
cp .env.example .env
# Edit .env with your actual API keys

# 2. Build and run
docker compose up --build
```

The platform is available on **port 8000**.

### Local Development

```bash
# 1. Clone
git clone https://github.com/ireanjordan24/Dreamcobots.git
cd Dreamcobots

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env  # fill in your keys

# 4. Run
python main.py run

# 5. Check status
python main.py status
```

### Run Tests

```bash
python -m pytest tests/ -v
```

---

## API Documentation

| Guide | Location |
|-------|----------|
| DataForge overview | [`bots/dataforge/docs/README.md`](bots/dataforge/docs/README.md) |
| API integration (100+ APIs) | [`bots/dataforge/docs/API_GUIDE.md`](bots/dataforge/docs/API_GUIDE.md) |
| Legal & compliance | [`bots/dataforge/docs/LEGAL_COMPLIANCE.md`](bots/dataforge/docs/LEGAL_COMPLIANCE.md) |
| User data selling guide | [`bots/dataforge/docs/USER_SELLING_GUIDE.md`](bots/dataforge/docs/USER_SELLING_GUIDE.md) |

---

## Repository Structure

```
Dreamcobots/
├── main.py                  # CLI entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── core/                    # Orchestrator, watchdog, resource monitor
├── bots/                    # All bot implementations
│   ├── dataforge/           # DataForge engine
│   └── <vertical-bot>/      # One directory per bot
├── framework/               # Shared framework utilities
├── stress_test/             # Load testing & debug tools
├── dashboard/               # Metrics & reporting dashboard
├── compliance/              # Top-level compliance checker
├── marketplace/             # Marketplace manager
└── tests/                   # 231 passing tests
```

---

## License

Proprietary — All rights reserved. © DreamCobots.