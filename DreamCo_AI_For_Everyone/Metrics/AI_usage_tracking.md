# DreamCo AI Usage Tracking

## What We Track
All DreamCo AI usage is tracked to measure ROI, identify gaps, and improve adoption.

---

## Tracked Metrics

### Bot Usage
- Bot ID and display name
- Tier (FREE/PRO/ENTERPRISE)
- Invocation count (daily/weekly/monthly)
- Success vs. failure rate
- Average execution time
- GitHub Actions workflow trigger source (manual/push/schedule)

### API Usage
- OpenAI API calls per bot
- Tokens consumed (input/output)
- Estimated cost per bot
- Rate limit incidents

### Automation Coverage
- Percentage of repetitive tasks automated
- Human-hours saved per workflow
- Automations by category (finance, real estate, lead gen, etc.)

---

## Data Sources

| Source | Collection Method |
|--------|------------------|
| GitHub Actions | Workflow run logs via GitHub API |
| Bot logs | `data/integration_log.json`, `data/companies.json` |
| Grafana/Prometheus | Real-time metrics scraping |
| BuddyOrchestrator | `github_actions_status()` method |

---

## Tracking Implementation

### In GitHub Actions
Every workflow automatically logs run outcomes. The Integration Feedback Bot
captures this data daily:
```
Actions → Integration Feedback Bot → scheduled 08:00 UTC
```

### In Python Bots
```python
# All bots log to data/integration_log.json via IntegrationFeedbackBot
from bots.integration_feedback_bot.integration_feedback_bot import IntegrationFeedbackBot
tracker = IntegrationFeedbackBot(tier=Tier.FREE)
tracker.log_integration(platform="MyBot", status="success", details="Task completed")
```

### Via BuddyOrchestrator
```python
from bots.buddy_orchestrator.buddy_orchestrator import BuddyOrchestrator
orch = BuddyOrchestrator()
status = orch.github_actions_status(per_page=20)
print(status["runs"])
```

---

## Privacy
- No PII is logged in usage tracking
- All tracking data is stored in the repository (`data/` directory)
- Access follows data classification in `Policies/data_security.md`
