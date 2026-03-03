# DreamCObots Repository

Welcome to the DreamCObots project! This repository implements a **comprehensive, modular multipurpose bot framework** for every occupation, app type, business type, and side hustle. Bots include built-in NLP, emotional intelligence, adaptive learning, dataset management, and plug-and-play monetisation.

---

## Framework Architecture

```
framework/
├── __init__.py          # Package exports
├── base_bot.py          # Abstract base class for all bots
├── nlp_engine.py        # NLP: tokenisation, sentiment, intent, entities
├── adaptive_learning.py # Learning engine: history, patterns, fine-tune hooks
├── dataset_manager.py   # Dataset registration, distribution, and selling
└── monetization.py      # Pricing plans and revenue tracking

BuddyAI/
└── buddy_ai.py          # Central AI hub: bot registry, routing, analytics

Occupational_bots/       # Job search, resume building, interview prep
Business_bots/           # Meeting scheduling, project management, invoicing
App_bots/                # User onboarding, support, feature updates
Marketing_bots/          # Social media, email campaigns, customer feedback
Real_Estate_bots/        # Property listings, viewing scheduling, market analysis
Fiverr_bots/             # Service listings, order management, review generation
Side_Hustle_bots/        # Content creator, dropshipping, gig economy advisor

tests/
└── test_framework.py    # 54 unit & integration tests
```

### Core Framework Components

| Component | Description |
|-----------|-------------|
| `BaseBot` | Abstract base: wires NLP + learning + datasets + monetisation. Override `_build_response`. |
| `NLPEngine` | Tokenisation, sentiment analysis, intent detection (16 intents), entity extraction, context window. |
| `AdaptiveLearning` | Interaction history, intent frequency, response-weight reinforcement, fine-tune hook. |
| `DatasetManager` | Dataset CRUD, ethical review enforcement, selling pipeline with payment stub. |
| `MonetizationManager` | Subscription, pay-per-use, one-time, and freemium pricing models with revenue analytics. |
| `BuddyAI` | Central hub: registers bots, NLP-routes messages, manages sessions, aggregates analytics. |

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
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   > The core framework runs on **Python standard library only** (Python ≥ 3.8). Optional packages in `requirements.txt` unlock enhanced NLP, persistence, and payment processing.

---

## Quick Start

### Running a single bot
```python
from Occupational_bots.feature_1 import JobSearchBot

bot = JobSearchBot()
print(bot.chat("Hi! I'm looking for software engineering jobs in New York."))
print(bot.chat("Do you have any datasets I can purchase?"))
print(bot.status())
```

### Using BuddyAI to manage multiple bots
```python
from BuddyAI.buddy_ai import BuddyAI
from Occupational_bots.feature_1 import JobSearchBot
from Business_bots.feature_3 import InvoicingBot
from Marketing_bots.feature_1 import SocialMediaBot

buddy = BuddyAI()
buddy.register(JobSearchBot())
buddy.register(InvoicingBot())
buddy.register(SocialMediaBot())

# BuddyAI routes each message to the best-fit bot automatically
print(buddy.chat("I need help finding a job.", user_id="alice"))
print(buddy.chat("Generate an invoice for $1500.", user_id="bob"))
print(buddy.chat("Schedule a LinkedIn post.", user_id="carol"))

print(buddy.platform_summary())
```

### Selling a dataset
```python
from Occupational_bots.feature_1 import JobSearchBot

bot = JobSearchBot()
datasets = bot.datasets.list_datasets()
result = bot.sell_dataset(datasets[0].dataset_id, buyer_id="researcher-001")
print(result)
```

---

## Running Tests
```bash
python -m pytest tests/ -v
```

---

## Bot Catalogue

### Occupational Bots (`Occupational_bots/`)
| File | Bot | Description |
|------|-----|-------------|
| `feature_1.py` | JobSearch Bot | Job listings, skills matching, OOH data |
| `feature_2.py` | Resume Builder Bot | Step-by-step resume creation, ATS optimisation |
| `feature_3.py` | Interview Prep Bot | Mock interviews, answer scoring, coaching |

### Business Bots (`Business_bots/`)
| File | Bot | Description |
|------|-----|-------------|
| `feature_1.py` | Meeting Scheduler Bot | Calendar coordination, meeting management |
| `feature_2.py` | Project Manager Bot | Milestones, deadlines, agile metrics |
| `feature_3.py` | Invoicing Bot | Invoice generation, billing, payment tracking |

### App Bots (`App_bots/`)
| File | Bot | Description |
|------|-----|-------------|
| `feature_1.py` | Onboarding Bot | Step-by-step app setup, user retention |
| `feature_2.py` | Support Bot | Technical support, issue resolution |
| `feature_3.py` | Feature Updates Bot | Personalised feature announcements |

### Marketing Bots (`Marketing_bots/`)
| File | Bot | Description |
|------|-----|-------------|
| `feature_1.py` | Social Media Bot | Content drafting, platform-specific tips |
| `feature_2.py` | Email Campaign Bot | Campaign creation, subject-line optimisation |
| `feature_3.py` | Customer Feedback Bot | Sentiment analysis, feedback aggregation |

### Real Estate Bots (`Real_Estate_bots/`)
| File | Bot | Description |
|------|-----|-------------|
| `feature_1.py` | Property Listings Bot | Listing search, buyer matching |
| `feature_2.py` | Viewing Scheduler Bot | Appointment booking |
| `feature_3.py` | Market Analysis Bot | Price trends, investment insights |

### Side Hustle Bots (`Side_Hustle_bots/`)
| File | Bot | Description |
|------|-----|-------------|
| `feature_1.py` | Content Creator Bot | Ideation, scheduling, monetisation |
| `feature_2.py` | Dropshipping Bot | Product sourcing, niche selection, scaling |
| `feature_3.py` | Gig Economy Bot | Platform comparisons, peak-hour optimisation |

### Fiverr Bots (`Fiverr_bots/`)
| File | Bot | Description |
|------|-----|-------------|
| `feature_1.py` | Fiverr Listings Bot | Gig creation, SEO optimisation |
| `feature_2.py` | Fiverr Order Bot | Order tracking, deadline management |
| `feature_3.py` | Fiverr Review Bot | Review requests, reputation management |

---

## Building Your Own Bot

```python
from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel

class DoctorBot(BaseBot):
    def __init__(self):
        super().__init__(name="Doctor Bot", domain="healthcare", category="occupational")

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Clinical NLP Corpus",
            description="De-identified clinical notes for NLP research.",
            domain="healthcare",
            size_mb=250.0,
            price_usd=499.00,
            license="CC-BY-4.0",
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        if intent == "greeting":
            return f"{self._emotion_prefix()}Hello! I'm {self.name}. How can I assist today?"
        if intent == "dataset_purchase":
            return f"I offer healthcare datasets. {self._dataset_offer()}"
        return f"{self._emotion_prefix()}How can I help with your healthcare question?"
```

---

## Deployment Steps
To deploy bots or static content:
1. Push changes to the `deployment-setup` branch.
2. Enable **GitHub Pages** in repository settings for frontend hosting.
3. Add and customize workflows to automate bot tasks (see GitHub Actions).

---

## GitHub Pages Instructions
1. Navigate to **Settings > Pages**.
2. Select the `deployment-setup` branch and root directory as the publishing source.
3. Save your settings to host the frontend.

---