# Adoption Dashboard Guide

**Version:** 1.0  
**Last Updated:** 2026-05-12

This guide explains how to read and act on the Dreamcobots AI Adoption
Dashboard.

---

## What is the Adoption Dashboard?

The Adoption Dashboard gives leadership and AI Advocates a real-time view of
how broadly and effectively AI bots are being used across the organisation.

Access it via the Control Tower React frontend → **Analytics** tab, or via
the programmatic API:

```python
from bots.buddy_orchestrator import BuddyOrchestrator

orch = BuddyOrchestrator()
# Ingest data from your systems
orch.ingest("active_users", 2500)
orch.ingest("api_cost_usd", 18.75)

dashboard = orch.analytics()
print(dashboard)
```

---

## Key Metrics

### Monthly Active Users (MAU)
- **Definition:** Number of distinct users who triggered at least one bot
  action in the current calendar month.
- **Source:** Ingested via `orch.ingest("active_users", <count>)`.
- **Target:** ≥ 20% of total team headcount by end of each quarter.

### API Cost (USD)
- **Definition:** Total spend on external AI API calls (OpenAI, Anthropic,
  etc.) for the current month.
- **Source:** Ingested via `orch.ingest("api_cost_usd", <amount>)`.
- **Target:** Track month-over-month; alert if > 120% of previous month.

### Bot Uptime (%)
- **Definition:** Per-bot success rate based on run history
  (`successful_runs / total_runs × 100`).
- **Target:** ≥ 95% for all production bots.
- **Action if below target:** Review recent failures, check integrations.

### Task Efficiency (%)
- **Definition:** Percentage of all bot runs that completed successfully
  across the entire catalog.
- **Target:** ≥ 90% overall.

### Total Revenue (USD)
- **Definition:** Aggregate revenue attributed to bot monetization events.
- **Source:** Recorded via `bot.monetize(amount, source)` and tracked in
  the orchestrator.

---

## Reading the Dashboard Output

```json
{
  "mau": 2500,
  "api_cost_usd": 18.75,
  "bot_uptime": {
    "sales_bot": 98.5,
    "report_bot": 92.0
  },
  "task_efficiency": 95.2,
  "total_revenue_usd": 4320.00,
  "snapshot_at": "2026-05-12T00:00:00+00:00"
}
```

---

## Maturity Scoring

| Score | Criteria |
|---|---|
| **1 — Exploring** | < 3 bots registered, MAU < 10 |
| **2 — Building** | 3–10 bots, MAU 10–100, ≥ 1 live bot |
| **3 — Scaling** | > 10 bots, MAU > 100, task efficiency ≥ 80% |
| **4 — Optimising** | MAU > 1 000, efficiency ≥ 95%, revenue tracked |
| **5 — Transforming** | MAU > 10 000, white-label bots deployed, full CI/CD |

---

## Monthly Review Template

| Metric | Current | Target | Delta | Action |
|---|---|---|---|---|
| MAU | — | — | — | — |
| API Cost (USD) | — | — | — | — |
| Avg Bot Uptime | — | 95% | — | — |
| Task Efficiency | — | 90% | — | — |
| Revenue (USD) | — | — | — | — |

---

*See also: [Engagement Tracker](engagement_tracker.md)*
