# Approved AI Tools & Integrations

**Version:** 1.0  
**Last Updated:** 2026-05-12

This document lists AI tools and third-party integrations that have been vetted
and approved for use in the Dreamcobots ecosystem.

---

## Tier Legend

| Tier | Meaning |
|---|---|
| ✅ **Approved** | Fully vetted; cleared for all tiers |
| 🟡 **Conditional** | Approved with restrictions (see notes) |
| ❌ **Not Approved** | Must not be used without explicit waiver |

---

## Language Models

| Tool | Provider | Tier | Notes |
|---|---|---|---|
| GPT-4o | OpenAI | ✅ Approved | No PII in prompts |
| Claude 3 Sonnet | Anthropic | ✅ Approved | No PII in prompts |
| Gemini 1.5 Pro | Google | 🟡 Conditional | EMEA data residency review required |
| LLaMA 3 (self-hosted) | Meta | ✅ Approved | Must be deployed behind DreamCo VPC |
| GPT-3.5-turbo | OpenAI | 🟡 Conditional | Legacy only; migrate to GPT-4o |

---

## AI Frameworks & SDKs

| Tool | Use Case | Tier |
|---|---|---|
| LangChain | Agent / chain orchestration | ✅ Approved |
| LlamaIndex | RAG and document Q&A | ✅ Approved |
| Hugging Face Transformers | Model fine-tuning | 🟡 Conditional |
| OpenAI Python SDK | Direct API calls | ✅ Approved |
| Anthropic SDK | Direct API calls | ✅ Approved |

---

## Automation & Workflow Tools

| Tool | Use Case | Tier |
|---|---|---|
| GitHub Actions | CI/CD pipelines | ✅ Approved |
| Prometheus + Grafana | Observability | ✅ Approved |
| Supabase / PostgreSQL | Persistent storage | ✅ Approved |
| Stripe SDK | Payments | ✅ Approved |
| Slack SDK | Notifications | ✅ Approved |

---

## Prohibited Tools

- Any LLM accessed without HTTPS and a valid API key.
- Tools that store prompts or outputs for model training without explicit
  opt-in consent from DreamCo users.
- Browser-extension-based AI tools that read user screen data.

---

## Requesting Approval for a New Tool

1. Open an issue in this repository tagged `ai-tool-review`.
2. Provide the tool name, use case, data handling documentation, and a
   security assessment.
3. The AI Governance Team will respond within 5 business days.

---

*See also: [AI Policy](AI_POLICY.md) | [Data Security](data_security.md)*
