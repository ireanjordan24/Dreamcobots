# Dreamcobots AI Chatbot

A tiered, scalable AI chatbot platform for the Dreamcobots ecosystem.
Supports multiple AI backends—including **KimiK** (Moonshot AI)—with
Free, Intermediate, and Premium subscription tiers, an AI Ecosystem
Directory, partner-recruitment engine, and a full marketing documentation
manager.

---

## Package Structure

```
bots/ai_chatbot/
├── __init__.py        – Public API exports
├── tiers.py           – Tier definitions & feature-gate helpers
├── chatbot.py         – AI chatbot engine (multi-model, tier-aware)
├── analytics.py       – Company analytics, partner recruitment, OnSite flows
└── marketplace.py     – Subscriptions, checkout, marketing doc manager
```

---

## Tiers

| Tier         | Price         | Messages/Day | AI Models               | Key Features |
|--------------|---------------|--------------|-------------------------|--------------|
| **Free**     | $0            | 50           | basic-llm               | Core chat, FAQ, onboarding, history |
| **Intermediate** | $29.99/mo | 500          | basic-llm, advanced-llm | + Analytics dashboard, integrations, email campaigns |
| **Premium**  | $99.99/mo     | Unlimited    | basic-llm, advanced-llm, **kimi-k** | + KimiK AI, partner recruitment, AI ecosystem directory, marketing doc manager, white-label, SLA |

---

## Quick Start

### As a library

```python
from bots.ai_chatbot import AIChatbot, Tier

# Free tier – basic chatbot
bot = AIChatbot(user_id="user_001", tier=Tier.FREE)
print(bot.chat("Hello! What can you do?"))

# Premium tier – KimiK AI
premium_bot = AIChatbot(user_id="user_002", tier=Tier.PREMIUM, model="kimi-k")
print(premium_bot.chat("Analyse our best AI partner candidates."))
```

### CLI

```bash
# Run the chatbot interactively
python -m bots.ai_chatbot.chatbot --tier premium --model kimi-k

# Commands inside the CLI:
#   history   – view conversation history
#   export    – export session as JSON
#   exit      – quit
```

---

## Analytics & Partner Recruitment (Premium)

```python
from bots.ai_chatbot import AnalyticsEngine, Tier

engine = AnalyticsEngine(tier=Tier.PREMIUM)

# Search the AI Ecosystem Directory
results = engine.search_companies(query="kimi", min_score=0.80)
for company in results:
    print(company.name, company.partnership_potential_score)

# Run partner-recruitment analysis
result = engine.run_partner_recruitment(
    requester_name="Dreamcobots",
    focus_areas=["large language models", "enterprise chatbots"],
    top_n=5,
)
print(result.recommended_outreach)

# Generate OnSite signup flow
flow = engine.generate_onsite_signup_flow("developer")
print(flow["steps"])
```

---

## Marketplace & Subscriptions

```python
from bots.ai_chatbot import Marketplace, Tier

mkt = Marketplace()

# Browse pricing
print(mkt.get_pricing_catalogue())

# Create a subscription
sub = mkt.create_subscription("user_001", Tier.PREMIUM)

# Prepare a Stripe-compatible checkout session
checkout = mkt.create_checkout_session("user_001", Tier.PREMIUM)
# Pass checkout.__dict__ to stripe.checkout.Session.create(...)
```

---

## Marketing Documentation Manager (Premium)

```python
from bots.ai_chatbot import Marketplace, Tier

mkt = Marketplace()

# List available layout templates
templates = mkt.list_templates(Tier.PREMIUM)

# Generate a pre-populated marketing document
doc = mkt.create_marketing_document(
    tier=Tier.PREMIUM,
    template_key="partner_brief",
    title="Q2 Partner Outreach",
    brand_name="Dreamcobots",
    value_propositions=[
        "Tiered AI chatbot platform",
        "KimiK long-context reasoning",
        "AI ecosystem partner network",
    ],
)
print(doc.content["sections"])

# White-label configuration
config = mkt.configure_white_label(
    tier=Tier.PREMIUM,
    brand_name="AcmeCorp",
    primary_color="#4F46E5",
    custom_domain="chat.acmecorp.com",
)
```

---

## Running Tests

```bash
cd /path/to/Dreamcobots
python -m pytest tests/test_ai_chatbot.py -v
```

Expected: **62 tests passing**.

---

## KimiK Integration Notes

KimiK (by Moonshot AI) is available on the **Premium tier**.

* API endpoint: `https://api.moonshot.cn/v1/chat/completions`
* Model: `moonshot-v1-128k` (128k-token context window)
* Set `KIMI_K_API_KEY` in your environment to activate live responses.
* Documentation: https://platform.moonshot.cn/docs

---

## AI Ecosystem Directory

The directory is seeded with 7 top AI organisations and can be extended:

| ID       | Organisation        | Score |
|----------|---------------------|-------|
| org_001  | OpenAI              | 0.92  |
| org_002  | Anthropic           | 0.88  |
| org_003  | Moonshot AI (KimiK) | 0.94  |
| org_004  | Hugging Face        | 0.85  |
| org_005  | Google DeepMind     | 0.90  |
| org_006  | Mistral AI          | 0.80  |
| org_007  | Cohere              | 0.83  |
