# DreamCo Automation Rules

## Core Principles
1. **Human-in-the-loop**: Automations that affect revenue, customers, or legal standing
   require human approval before execution.
2. **Idempotency**: All automated workflows must be safe to re-run without side effects.
3. **Audit trail**: Every automation must log its actions to `data/` or a monitoring system.
4. **Graceful failure**: Bots must handle errors without cascading failures or data loss.
5. **Rate limiting**: Respect all external API rate limits; implement exponential backoff.

## GitHub Actions Automation Standards
- Use `[skip ci]` in commit messages for data-only commits that should not trigger CI
- Schedule jobs using cron syntax with explicit UTC times
- Always set a `timeout-minutes` on long-running jobs
- Use `permissions: contents: write` only when the job needs to commit files
- Notify via Slack webhook on failure using the `SLACK_WEBHOOK_URL` secret

## Bot Automation Limits

| Tier | Max concurrent bots | Max scheduled jobs | API calls/hour |
|------|--------------------|--------------------|----------------|
| FREE | 2 | 3 | 100 |
| PRO | 10 | 25 | 1,000 |
| ENTERPRISE | Unlimited | Unlimited | Unlimited |

## Prohibited Automations
- Autonomous financial transactions over $500 without human sign-off
- Mass-emailing or messaging without opt-in verification
- Automated legal filings or submissions
- Self-modifying production code without a PR review
- Deleting production data without a backup confirmed

## Change Management
All new automations must:
1. Be developed and tested in the sandbox environment first
2. Have a corresponding GitHub Actions workflow in `.github/workflows/`
3. Be registered in the bot library (`bots/global_bot_network/bot_library.py`)
4. Include rollback documentation

_Last updated: 2025_
