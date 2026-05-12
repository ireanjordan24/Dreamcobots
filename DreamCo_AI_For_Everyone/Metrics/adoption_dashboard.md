# DreamCo AI Adoption Dashboard

## Overview
This dashboard tracks DreamCo's AI adoption maturity across all teams and systems.
Data feeds are pulled from GitHub Actions runs, bot logs, and Grafana.

---

## Key Adoption KPIs

| KPI | Target | Measurement |
|-----|--------|-------------|
| Monthly Active Users (MAU) | 100% team adoption | GitHub Actions unique triggerers |
| Monthly Engaged Users | 70% of MAU | Users with >3 bot interactions/month |
| New Bot Activations | 5/month | Bot library registrations |
| Workflow Run Success Rate | >99% | GitHub Actions success/failure ratio |
| Mean Time to Recovery | <5 min | Workflow failure recovery time |
| Onboarding Completion Rate | >90% | Users who completed beginner path |

---

## Maturity Model

### Level 1 — Aware
- Team members know AI tools exist
- At least one bot has been run manually

### Level 2 — Experimenting
- Regular manual bot usage
- At least 2 GitHub Actions workflows active

### Level 3 — Integrating
- Bots integrated into daily workflows
- Automated scheduling configured
- Metrics being tracked

### Level 4 — Optimizing
- Cross-system orchestration via BuddyOrchestrator
- Revenue metrics tracked per bot
- Advocate network active

### Level 5 — Leading
- Full AI operating system deployed
- All 4 phases of the DreamCo Maturity Roadmap complete
- Contributing patterns back to the community

---

## Dashboard Links
- **Grafana**: `http://localhost:3000` (local) or configured Grafana Cloud URL
- **GitHub Actions**: [View all workflow runs](https://github.com/DreamCo-Technologies/Dreamcobots/actions)
- **Bot Library**: `bots/global_bot_network/bot_library.py`

---

## Monthly Reporting
Generate the monthly adoption report by running the AI Enablement Hub workflow:
```
Actions → AI Enablement Hub → Run workflow → report_type=monthly
```
