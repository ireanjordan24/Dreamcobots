# DreamCo Tier 1 Approved Tools

## Overview
Tier 1 tools have passed DreamCo's security review and may be used with internal
business data under standard data-handling protocols.

---

## Core Infrastructure

| Tool | Version | Use Case | Owner |
|------|---------|----------|-------|
| **GitHub Actions** | Latest | CI/CD, automation | DevOps |
| **Docker** | 24+ | Bot containerization | DevOps |
| **Cloudflare** | Enterprise | Edge networking, DDoS protection | Infrastructure |
| **GitHub Copilot** | Latest | Code generation, review | Engineering |

## AI & ML

| Tool | Version | Use Case | Key Secret |
|------|---------|----------|-----------|
| **OpenAI API** | GPT-4+ | Bot intelligence, content | `OPENAI_API_KEY` |
| **Anthropic Claude API** | Claude 3+ | Reasoning, summarization | `CLAUDE_API_KEY` |
| **Google Gemini API** | Gemini 1.5+ | Multimodal analysis | `GEMINI_API_KEY` |
| **GitHub Copilot API** | Latest | Developer assistance | `GITHUB_PAT` |

## Data & Automation

| Tool | Use Case | Key Secret |
|------|----------|-----------|
| **Supabase** | Database, auth backend | `SUPABASE_URL`, `SUPABASE_KEY` |
| **n8n** | No-code workflow automation | `N8N_API_KEY` |
| **LangChain** | LLM orchestration | (depends on LLM) |
| **Stripe** | Payments & subscriptions | `STRIPE_SECRET_KEY` |

## Monitoring & Observability

| Tool | Use Case |
|------|----------|
| **Grafana** | Metrics visualization dashboards |
| **Prometheus** | Metrics collection and alerting |

---

## Adding a Tool to Tier 1
1. Open a GitHub Issue with label `tool-approval-request`
2. Provide: tool name, use case, security review, data classification
3. Security Lead reviews within 5 business days
4. If approved, PR this file with the addition

_See also: [Tier 2 Public Tools](tier2_public_tools.md)_
