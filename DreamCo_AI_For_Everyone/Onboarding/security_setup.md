# DreamCo Security Setup Guide

## Initial Security Checklist

### GitHub Repository Security
- [ ] Enable branch protection on `main` (require PR reviews)
- [ ] Enable Dependabot alerts (`Settings → Security → Dependabot`)
- [ ] Enable secret scanning (`Settings → Security → Secret scanning`)
- [ ] Enable code scanning with CodeQL
- [ ] Review all repository collaborators and access levels

### Secrets Configuration
Add these secrets in `Repository → Settings → Secrets → Actions`:

| Secret | Required | Description |
|--------|----------|-------------|
| `GITHUB_TOKEN` | Auto | Provided by GitHub, do not set manually |
| `SLACK_WEBHOOK_URL` | Optional | Slack notifications |
| `OPENAI_API_KEY` | Optional | OpenAI bot intelligence |
| `CLAUDE_API_KEY` | Optional | Claude AI integration |
| `STRIPE_SECRET_KEY` | If using payments | Stripe payment processing |
| `CRUNCHBASE_API_KEY` | If using Company Lookup | Company data enrichment |

### Environment Variables (Local)
```bash
cp .env.example .env
# Edit .env — never commit this file
echo ".env" >> .gitignore  # Already included in default .gitignore
```

---

## Security Best Practices

### API Key Rotation
Rotate all API keys every 90 days. Use the automated rotation bot:
```bash
python3 bots/stripe_key_rotation_bot/stripe_key_rotation_bot.py
```

### Access Reviews
Monthly: Review who has write access to the repository.
Quarterly: Rotate all API keys.
Annually: Full security audit of all integrations.

### Incident Response
If a secret is exposed:
1. **Immediately** revoke the compromised key at the provider
2. Generate and set a new key in GitHub Secrets
3. Notify the Security Lead
4. Document in `DreamCo_AI_For_Everyone/Reports/`
5. Update this file if processes need to change

---

## Security Contacts
- Security Lead: Open a GitHub Issue tagged `security-urgent`
- Emergency: Immediately revoke keys and open an issue

_See also: [Data Security Policy](../Policies/data_security.md)_
