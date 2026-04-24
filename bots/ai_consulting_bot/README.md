# AI Consulting Bot

A tier-aware DreamCo consulting service that pairs businesses with AI transition experts, manages consulting sessions, and generates phased AI adoption roadmaps.

## Installation

```bash
pip install -r requirements.txt
```

```python
from bots.ai_consulting_bot.bot import AIConsultingBot
from bots.ai_consulting_bot.tiers import get_ai_consulting_tier_info
```

## Tiers

| Feature                        | Free ($0/mo)             | Pro ($49/mo)                    | Enterprise ($299/mo)                       |
|--------------------------------|--------------------------|---------------------------------|--------------------------------------------|
| Consulting sessions/month      | 1                        | 10                              | Unlimited                                  |
| Expert matching                | Community pool           | Dedicated expert                | Senior strategist + dedicated team         |
| AI adoption roadmap            | ❌                       | ✅                              | ✅ + milestones & executive briefing       |
| Session transcripts            | ❌                       | ✅                              | ✅                                         |
| Change management playbook     | ❌                       | ❌                              | ✅                                         |
| White-glove onboarding         | ❌                       | ❌                              | ✅                                         |

## Usage

### Match an expert

```python
from bots.ai_consulting_bot.bot import AIConsultingBot
from tiers import Tier

bot = AIConsultingBot(tier=Tier.PRO)

expert = bot.match_expert({
    "company_name": "HealthFirst Inc",
    "industry": "healthcare",
    "size": "medium",
    "goals": ["automate patient intake", "predictive diagnostics"]
})
print(expert)
# {
#   "expert_id": "uuid-...",
#   "name": "DreamCo Expert — Healthcare Ai",
#   "domain": "healthcare_ai",
#   "experience_years": 7,
#   "availability": "scheduled (24h response)",
#   "match_score": 88,
#   "tier": "pro"
# }
```

### Book a session

```python
session = bot.book_session({
    "company_name": "HealthFirst Inc",
    "expert_id": expert["expert_id"],
    "topic": "AI for Patient Intake Automation",
    "scheduled_at": "2026-05-01T10:00:00Z"
})
print(session)
# {
#   "session_id": "uuid-...",
#   "status": "confirmed",
#   "agenda": [...],
#   "transcript_url": "https://docs.dreamcobots.ai/sessions/uuid-...",
#   "tier": "pro"
# }
```

### Generate a roadmap

```python
roadmap = bot.generate_roadmap({
    "company_name": "HealthFirst Inc",
    "industry": "healthcare",
    "readiness_score": 55,
    "objectives": ["automate patient intake", "reduce admin overhead"]
})
print(roadmap)
# {
#   "roadmap_id": "uuid-...",
#   "total_phases": 5,
#   "phases": [...],
#   "estimated_total_weeks": 34,
#   "tier": "pro"
# }
```

## License

MIT
