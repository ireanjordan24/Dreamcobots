# DreamCo Automation Mastery Guide

## Core Automation Philosophy
DreamCo automates everything that is:
- Repetitive (done more than 3× manually)
- Time-sensitive (must happen at specific intervals)
- Error-prone (where human mistakes are costly)
- Scalable (volume that exceeds human capacity)

---

## GitHub Actions Mastery

### Anatomy of a DreamCo Workflow
```yaml
name: Bot Name
on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      input_name:
        description: "What it does"
        required: true
        default: "default_value"
  schedule:
    - cron: "0 8 * * *"  # Daily 08:00 UTC

jobs:
  job-name:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      actions: read
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - name: Run bot
        env:
          API_KEY: ${{ secrets.API_KEY }}
        run: python bots/my_bot/runner.py
```

### Best Practices
- Always pin action versions (`@v4` not `@latest`)
- Use `[skip ci]` for data commits to prevent loops
- Cache pip dependencies with `actions/cache`
- Set `timeout-minutes: 15` on all jobs

---

## n8n Automation Patterns

### DreamCo → n8n Integration
1. Trigger: GitHub webhook → n8n
2. Process: n8n transforms and routes data
3. Action: n8n calls DreamCo bot API or GitHub workflow dispatch

### Recommended Workflows
- **Lead Capture**: Form submission → Company Lookup Bot → CRM
- **Revenue Alert**: Stripe webhook → Revenue Bot → Slack
- **Bot Health**: Cron → All bots health check → Dashboard

---

## LangChain for Bot Intelligence

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

template = PromptTemplate(
    input_variables=["company", "tier"],
    template="Analyze {company} as a {tier} DreamCo bot customer..."
)
chain = LLMChain(llm=llm, prompt=template)
result = chain.run(company="Stripe", tier="ENTERPRISE")
```

---

## Automation KPIs to Track
- Workflow success rate (target: >99%)
- Mean time to recovery (target: <5 min)
- Automations completed per day
- Human-hours saved per week
- Revenue generated per automation

_See also: [Metrics/productivity_metrics.md](../Metrics/productivity_metrics.md)_
