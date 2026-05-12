# Engagement Tracker

**Version:** 1.0  
**Last Updated:** 2026-05-12

The Engagement Tracker measures how deeply users are interacting with the
Dreamcobots ecosystem — beyond just access (MAU) — to understand quality of
engagement and identify coaching opportunities.

---

## Engagement Dimensions

| Dimension | Signal | Data Source |
|---|---|---|
| **Breadth** | Number of distinct users running bots | `orch.analytics()["mau"]` |
| **Depth** | Average runs per user per month | Run history / user count |
| **Diversity** | Number of distinct bots used | Bot catalog + run history |
| **Revenue per User** | Total revenue / MAU | `total_revenue_usd / mau` |
| **Advocate Reach** | % of team attended an AI event | Advocate monthly report |

---

## Tracking Setup

### 1. Record Active Users
At the end of each month, ingest the active user count:

```python
orch.ingest("active_users", <monthly_active_user_count>)
```

### 2. Record API Costs
Pull the cost from your OpenAI / Anthropic billing dashboard and ingest:

```python
orch.ingest("api_cost_usd", <total_api_spend_this_month>)
```

### 3. Pull the Snapshot
```python
snapshot = orch.analytics()
```

### 4. Log to your Metrics Store
Persist the snapshot to Supabase or PostgreSQL for trending over time:

```sql
INSERT INTO engagement_snapshots
    (snapshot_at, mau, api_cost_usd, task_efficiency, total_revenue_usd)
VALUES
    (:snapshot_at, :mau, :api_cost_usd, :task_efficiency, :total_revenue_usd);
```

---

## KPIs and Thresholds

| KPI | Green | Amber | Red |
|---|---|---|---|
| MAU growth MoM | > 10% | 0–10% | Negative |
| Bot uptime (avg) | ≥ 95% | 85–94% | < 85% |
| Task efficiency | ≥ 90% | 80–89% | < 80% |
| Revenue per user | > $5 | $1–$5 | < $1 |
| Advocate event attendance | > 70% | 40–70% | < 40% |

---

## Monthly Engagement Report Template

**Reporting Period:** YYYY-MM  
**Prepared by:** [AI Advocate Name]

| Metric | Value | Status |
|---|---|---|
| MAU | — | 🟢 / 🟡 / 🔴 |
| MoM MAU growth | —% | 🟢 / 🟡 / 🔴 |
| Avg bot uptime | —% | 🟢 / 🟡 / 🔴 |
| Task efficiency | —% | 🟢 / 🟡 / 🔴 |
| API cost (USD) | — | 🟢 / 🟡 / 🔴 |
| Total revenue (USD) | — | — |
| Advocate events held | — | — |
| Team attendance | —% | 🟢 / 🟡 / 🔴 |

**Top Win this Month:**  
[Describe one success story]

**Top Blocker this Month:**  
[Describe one issue and proposed action]

---

*See also: [Adoption Dashboard](adoption_dashboard.md)*
