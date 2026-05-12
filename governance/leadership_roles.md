# DreamCo Governance — Leadership Roles

## AI Governance Philosophy
DreamCo's AI governance follows the principle that **AI enablement dies without ownership**.
Every system must have a Directly Responsible Individual (DRI) who owns its success.

---

## Leadership Structure

```
AI Operations Director
├── Automation Director
├── Security Lead
├── Deployment Lead
├── Revenue Systems Lead
└── Infrastructure Lead
```

---

## Role Definitions

### AI Operations Director
**Responsibilities**:
- Own the DreamCo AI Enablement strategy and roadmap
- Chair monthly AI review meetings
- Approve new AI tools for Tier 1 status
- Sign off on policy updates and changes
- Report AI KPIs to stakeholders
- Resolve cross-team AI adoption blockers

**Authority**:
- Final decision on AI tool approvals
- Policy override authority
- Budget approval for AI infrastructure

**KPIs**:
- Monthly Active Users (target: 100% team adoption)
- Workflow Success Rate (target: >99%)
- Advocate Network Size (target: 25+ for PRO tier)

---

### Automation Director
**Responsibilities**:
- Own GitHub Actions workflow standards and review process
- Approve new workflow PRs before merge
- Maintain `DreamCo_AI_For_Everyone/Policies/automation_rules.md`
- Coach teams on workflow design and CI/CD best practices
- Monitor automation uptime and performance

**KPIs**:
- Workflow Success Rate (target: >99%)
- Automation Coverage (target: >80% of repetitive tasks)
- Mean Time to Recovery (target: <5 minutes)

---

### Security Lead
**Responsibilities**:
- Own data security and compliance across all AI systems
- Review all tool approval requests within 5 business days
- Lead security incident response
- Maintain `DreamCo_AI_For_Everyone/Policies/data_security.md`
- Conduct quarterly security audits

**KPIs**:
- Zero data breaches
- 100% secret rotation compliance (90-day cycle)
- Tool approval backlog: 0 open >5 days

---

### Deployment Lead
**Responsibilities**:
- Own bot deployment pipeline and Docker/Cloudflare infrastructure
- Review and approve bot releases
- Maintain deployment runbooks
- Monitor bot uptime and availability

**KPIs**:
- Deployment Success Rate (target: >99%)
- Bot Uptime (target: >99.9%)
- Mean Deployment Time (target: <10 minutes)

---

### Revenue Systems Lead
**Responsibilities**:
- Own bot monetization architecture and pricing strategy
- Monitor revenue metrics and Stripe integration health
- Review billing bot changes
- Develop upsell and upgrade workflows

**KPIs**:
- MRR Growth (target: >10%/month)
- Churn Rate (target: <5%)
- Revenue per Bot (positive ROI on all active bots)

---

### Infrastructure Lead
**Responsibilities**:
- Own Grafana, Prometheus, Docker, and Cloudflare infrastructure
- Maintain monitoring configurations in `monitoring/`
- Respond to infrastructure incidents
- Train advocates on observability tools

**KPIs**:
- System Uptime (target: >99.9%)
- MTTD — Mean Time to Detect (target: <2 minutes)
- Infrastructure Cost (within budget)

---

## Governance Meetings

| Meeting | Frequency | Participants | Purpose |
|---------|-----------|-------------|---------|
| AI Operations Review | Monthly | All leads | KPI review, strategy |
| Security Review | Monthly | Security Lead + Director | Incidents, compliance |
| Bot Release Review | Weekly | Deployment Lead + Director | Deployment approvals |
| Community All-Hands | Quarterly | All advocates | Culture, wins, roadmap |

---

## DRI Assignment
All DRI roles are tracked in this document.
Open a PR to assign yourself or nominate a colleague.

| Role | Current DRI |
|------|------------|
| AI Operations Director | _(open)_ |
| Automation Director | _(open)_ |
| Security Lead | _(open)_ |
| Deployment Lead | _(open)_ |
| Revenue Systems Lead | _(open)_ |
| Infrastructure Lead | _(open)_ |

_See also: [Advocate Roles](../DreamCo_AI_For_Everyone/Advocates/advocate_roles.md)_
