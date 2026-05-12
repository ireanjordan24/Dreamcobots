# DreamCo Revenue Metrics

## Overview
Revenue metrics track how DreamCo bots generate, protect, and optimize revenue.

---

## Revenue KPIs

| KPI | Target | Tracking Source |
|-----|--------|----------------|
| Revenue per Bot | Varies by tier | Stripe dashboard |
| Monthly Recurring Revenue (MRR) | Growth >10%/month | `bots/dreamco_payments` |
| Revenue per Automation | Positive ROI | Manual calculation |
| Churn Rate | <5% | Subscription bot logs |
| Bot Activation Rate | >80% of purchased bots | `data/integration_log.json` |
| Average Revenue per User (ARPU) | >$49/month | Stripe analytics |

---

## Revenue by Bot Tier

| Tier | Price | Target Active Users | Target MRR |
|------|-------|--------------------|-----------:|
| FREE | $0 | 200 | $0 |
| PRO | $49/mo | 50 | $2,450 |
| ENTERPRISE | $199/mo | 10 | $1,990 |
| **Total** | | **260** | **$4,440** |

---

## Revenue Tracking Integration

### Stripe Integration
```python
from bots.stripe_payment_bot.stripe_payment_bot import StripePaymentBot
bot = StripePaymentBot(tier=Tier.PRO)
revenue = bot.get_monthly_revenue()
```

### Revenue Engine Bot
```python
from bots.revenue_engine_bot.revenue_engine_bot import RevenueEngineBot
engine = RevenueEngineBot()
report = engine.generate_revenue_report()
```

---

## Revenue Optimization Strategies
1. **Upsell path**: FREE → PRO: Highlight metrics and advocate features
2. **PRO → ENTERPRISE**: Highlight BotTierClassifier and RetrainingOptimizer
3. **Bundle offers**: Combine bots in marketplace packages
4. **Usage-based billing**: `bots/token_billing` for per-API-call pricing

---

## Monthly Revenue Report
```
Actions → AI Enablement Hub → Run workflow → report_type=revenue
```
Results saved to `DreamCo_AI_For_Everyone/Reports/revenue_YYYY_MM.md`
