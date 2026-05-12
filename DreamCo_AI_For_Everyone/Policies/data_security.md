# DreamCo AI Data Security Policy

## Data Classification

| Class | Description | AI Tool Rules |
|-------|-------------|---------------|
| **Public** | Marketing materials, open-source code | Any approved tool |
| **Internal** | Business strategies, roadmaps | Tier 1 tools only |
| **Confidential** | Customer data, credentials, PII | Never enter into AI tools |
| **Restricted** | Legal, financial, health records | Human-only processing |

## Key Rules
1. **Never enter credentials** (API keys, passwords, tokens) into any AI interface.
2. **Never enter customer PII** (names, emails, phone numbers, addresses) into AI tools.
3. **Always use environment variables** for secrets in GitHub Actions and scripts.
4. **Rotate keys regularly** — use `bots/stripe_key_rotation_bot` for Stripe keys.
5. **Log all AI interactions** involving business data for audit purposes.

## GitHub Secrets Management
- Store all API keys as GitHub repository or organization secrets
- Reference secrets via `${{ secrets.SECRET_NAME }}` in workflows
- Never hardcode secrets in workflow files or source code
- Review and rotate secrets at least every 90 days

## Incident Response
If you suspect a data breach or unauthorized AI data exposure:
1. Immediately revoke and rotate any compromised credentials
2. Notify the Security Lead within 1 hour
3. Open a GitHub Issue tagged `security-incident` (private repo)
4. Document the incident in `DreamCo_AI_For_Everyone/Reports/`

_Last updated: 2025_
