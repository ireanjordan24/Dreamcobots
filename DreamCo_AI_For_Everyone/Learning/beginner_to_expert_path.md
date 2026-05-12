# Beginner-to-Expert Learning Path

**Version:** 1.0  
**Last Updated:** 2026-05-12

This structured learning path takes you from zero to confidently building,
deploying, and monetising bots in the Dreamcobots ecosystem.

---

## Level 1 — Beginner (Estimated: 2–3 hours)

**Goal:** Understand the ecosystem and run your first bot.

### Step 1 — Read the Foundations
- [README.md](../../README.md) — ecosystem overview
- [AI Policy](../Policies/AI_POLICY.md) — responsible use rules
- [Approved Tools](../Policies/approved_tools.md) — what you can use

### Step 2 — Set Up Your Environment
```bash
git clone https://github.com/DreamCo-Technologies/Dreamcobots.git
cd Dreamcobots
pip install -r requirements.txt
cp .env.example .env  # fill in your API keys
```

### Step 3 — Run Your First Bot
```python
from bots.buddy_orchestrator import BuddyOrchestrator

orch = BuddyOrchestrator()
orch.register_bot("my_first_bot", tier="FREE", category="ai")
result = orch.run_bot("my_first_bot", task="hello world")
print(result)
```

### Step 4 — Explore the Control Tower
Open the React dashboard at `dreamco-control-tower/` to see the Bot Overview,
Analytics, and Marketplace tabs.

**Checkpoint:** You can register and run a bot; you understand tier differences.

---

## Level 2 — Intermediate (Estimated: 4–6 hours)

**Goal:** Build a custom bot and connect it to the orchestrator.

### Step 1 — Extend BaseBot
```python
from core.base_bot import BaseBot

class MyReportBot(BaseBot):
    bot_id = "my_report_bot"
    name   = "My Report Bot"
    category = "analytics"

    def run(self, task: dict) -> dict:
        # Your logic here
        revenue = self.monetize(amount=10.0, source="api_call")
        report  = self.report()
        return self._success(data={"report": report, "revenue": revenue})
```

### Step 2 — Add Monetization
Use the `monetize()` method on `BaseBot` to track revenue events. Connect
to `StripePaymentBot` for real checkout sessions and subscriptions.

### Step 3 — Connect to the Orchestrator
```python
orch.register_bot(
    "my_report_bot",
    tier="PRO",
    category="analytics",
    price_usd=29.0,
    features=["automated-reports", "csv-export"],
    module_path="bots.my_report_bot",
)
orch.go_live("my_report_bot")
```

### Step 4 — Write Tests
Consult `tests/test_buddy_orchestrator.py` for testing patterns.

**Checkpoint:** You have a custom bot with monetization wired to the orchestrator.

---

## Level 3 — Advanced (Estimated: 6–10 hours)

**Goal:** Deploy bots in production with CI/CD, monitoring, and analytics.

### Step 1 — Set Up CI/CD
Review `.github/workflows/bot-cicd.yml` to understand how bots are
automatically linted, tested, and deployed on every push to `main`.

### Step 2 — Enable Observability
```python
orch.ingest("active_users", 2500)
orch.ingest("api_cost_usd", 12.50)
metrics = orch.analytics()
print(metrics)
```

### Step 3 — Run Bots Concurrently
```python
import asyncio

results = asyncio.run(orch.run_all_async())
```

### Step 4 — White-Label a Bot for Resellers
```python
wl = orch.white_label_bot(
    bot_id="my_report_bot",
    client_name="acme_corp",
    markup_pct=25,
)
print(wl)
```

**Checkpoint:** Bots pass CI, deploy automatically, emit analytics, and can be
resold as white-label products.

---

## Level 4 — Expert (Ongoing)

**Goal:** Architect multi-bot systems and govern the ecosystem.

- Design orchestration flows using `run_all_async()` for maximum concurrency.
- Contribute retraining strategies via `framework/retraining_optimizer.py`.
- Integrate PostgreSQL/Supabase for persistent bot state (replacing JSON).
- Build Grafana dashboards from Prometheus metrics exported by bots.
- Mentor others and contribute to the AI Advocates programme.

---

## Learning Resources

| Resource | Link |
|---|---|
| Deployment Guide | [deployment_guide.md](deployment_guide.md) |
| Adoption Dashboard | [adoption_dashboard.md](../Metrics/adoption_dashboard.md) |
| Bot Architecture | [bots/](../../bots/) |
| Orchestrator Tests | [tests/test_buddy_orchestrator.py](../../tests/test_buddy_orchestrator.py) |
