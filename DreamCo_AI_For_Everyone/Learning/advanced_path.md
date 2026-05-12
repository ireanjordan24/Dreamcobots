# DreamCo AI Advanced Learning Path

## Overview
For contributors who have completed the Beginner Path and want to build, extend,
and deploy production-grade DreamCo bots.

---

## Module 1 — Bot Architecture
- Study `framework/global_ai_sources_flow.py` — the 8-stage mandatory pipeline
- Read `CONTRIBUTING.md` for architecture requirements
- Run `python tools/check_bot_framework.py` after every new bot

## Module 2 — Building a New Bot
### Scaffold
```bash
cp -r bots/integration_feedback_bot bots/my_new_bot
# Rename classes and update tiers.py, __init__.py
```
### Required Structure
```
bots/my_new_bot/
├── __init__.py
├── tiers.py              # FREE/PRO/ENTERPRISE config
├── my_new_bot.py         # Main bot class
└── README.md
```
### Register in Bot Library
Add a `BotEntry` to `bots/global_bot_network/bot_library.py` → `BOT_LIBRARY` list.

## Module 3 — GitHub Actions Integration
- Create `.github/workflows/my_new_bot.yml`
- Pattern: checkout → setup-python → install deps → run bot → commit data
- Add `workflow_dispatch` inputs for manual triggers
- Set `schedule` for automated runs

## Module 4 — Testing
```bash
# Run all tests (excluding backend/dashboard)
python3 -m pytest tests/ --ignore=tests/test_backend.py \
    --ignore=tests/test_web_dashboard.py -q

# Check framework compliance
python3 tools/check_bot_framework.py
```
Target: ≥ 60 tests per bot covering tiers, subsystems, edge cases, and bot library registration.

## Module 5 — Orchestration
```python
from bots.buddy_orchestrator.buddy_orchestrator import BuddyOrchestrator

orch = BuddyOrchestrator()
orch.register_bot("my_new_bot", display_name="My New Bot", tier="PRO")
result = orch.run_bot("my_new_bot")
print(orch.status())
```

## Module 6 — Monitoring & Metrics
- Configure Grafana dashboards using `monitoring/` configs
- Set up Prometheus scraping for bot metrics
- Review `DreamCo_AI_For_Everyone/Metrics/` for KPI tracking guides

## Module 7 — Revenue Integration
- Use `bots/stripe_payment_bot` for billing
- Use `bots/token_billing` for per-use billing
- Review `MONEY_GUIDE.md` for monetization strategies

## Graduation Project
Build a complete bot with:
- [ ] 3 tiers (FREE/PRO/ENTERPRISE)
- [ ] 5+ sub-systems
- [ ] GitHub Actions workflow
- [ ] 60+ passing tests
- [ ] Bot library registration
- [ ] README documentation
