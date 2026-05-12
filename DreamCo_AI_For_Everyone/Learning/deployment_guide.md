# Bot Deployment Guide

**Version:** 1.0  
**Last Updated:** 2026-05-12

This guide walks you through deploying a Dreamcobots bot from development to
production.

---

## Prerequisites

- Python 3.10+
- `STRIPE_SECRET_KEY` and `GITHUB_TOKEN` set as environment variables or
  GitHub repository secrets.
- A registered bot in `BuddyOrchestrator`.

---

## Step 1 — Verify Your Bot Locally

```bash
python3 -m pytest tests/ --ignore=tests/test_backend.py \
    --ignore=tests/test_web_dashboard.py -q
python3 tools/check_bot_framework.py
```

All tests must pass and the framework check must report zero violations for
your bot before deployment.

---

## Step 2 — Configure GitHub Secrets

In your repository settings (`Settings → Secrets and variables → Actions`),
add:

| Secret | Description |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe live or test secret key |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions |

---

## Step 3 — Push to `main`

The CI/CD pipeline defined in `.github/workflows/bot-cicd.yml` will
automatically:

1. Install dependencies.
2. Run the full Python test suite.
3. Run the framework compliance check.
4. (On success) Log the deployment event.

---

## Step 4 — Register and Go Live

```python
from bots.buddy_orchestrator import BuddyOrchestrator

orch = BuddyOrchestrator()
orch.register_bot(
    "my_bot",
    tier="PRO",
    category="analytics",
    price_usd=49.0,
)
orch.go_live("my_bot")
print(orch.status())
```

---

## Step 5 — Monitor

Use the Control Tower dashboard to observe:
- **Bot Overview** — live/inactive status
- **Analytics** — MAU, uptime, task efficiency
- **Actions** — CI/CD run status

Or query programmatically:

```python
metrics = orch.analytics()
print(f"Task efficiency: {metrics['task_efficiency']}%")
print(f"Bot uptime: {metrics['bot_uptime']}")
```

---

## Rollback

If a deployment causes issues:

1. Revert the commit via `git revert <SHA>` and push.
2. The CI pipeline will re-run and redeploy the previous version.
3. Use `orch.deactivate("my_bot")` to immediately take the bot offline.

---

## Environment-Specific Settings

| Environment | Stripe Key Prefix | Bot Tier |
|---|---|---|
| Development | `sk_test_` | FREE or PRO |
| Staging | `sk_test_` | PRO or ENTERPRISE |
| Production | `sk_live_` | Any tier |

---

*See also: [Beginner-to-Expert Path](beginner_to_expert_path.md) | [CI/CD Workflow](../../.github/workflows/bot-cicd.yml)*
