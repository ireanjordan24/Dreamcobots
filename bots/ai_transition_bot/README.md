# AI Transition Bot

A tier-aware DreamCo AI onboarding kit designed to help businesses successfully transition to AI. Includes three integrated capabilities: a company readiness **Assessment Bot**, structured **Training Modules** for employees, and a plug-and-play **Integration API Kit** for connecting AI into existing workflows.

## Installation

```bash
pip install -r requirements.txt
```

```python
from bots.ai_transition_bot.bot import AITransitionBot
from bots.ai_transition_bot.tiers import get_ai_transition_tier_info
```

## Tiers

| Feature                        | Free ($0/mo)             | Pro ($49/mo)                         | Enterprise ($299/mo)                        |
|--------------------------------|--------------------------|--------------------------------------|---------------------------------------------|
| Readiness assessment           | Summary only             | Full dimension breakdown             | Full breakdown + AI adoption roadmap        |
| Training modules               | 5 (beginner only)        | 30 (beginner + intermediate)         | Unlimited (all levels)                      |
| Integration APIs               | 1                        | 10                                   | Unlimited                                   |
| Workflow mapping               | ❌                       | ✅                                   | ✅                                          |
| Employee skill scoring         | ❌                       | ✅                                   | ✅                                          |
| White-label kit                | ❌                       | ❌                                   | ✅                                          |
| Dedicated onboarding specialist| ❌                       | ❌                                   | ✅                                          |

## Usage

### Run a readiness assessment

```python
from bots.ai_transition_bot.bot import AITransitionBot
from tiers import Tier

bot = AITransitionBot(tier=Tier.PRO)

report = bot.run_assessment({
    "name": "Acme Corp",
    "industry": "manufacturing",
    "size": "medium",
    "scores": {
        "data_infrastructure": 65,
        "talent_skills": 40,
        "process_automation": 55,
        "leadership_strategy": 70,
        "technology_stack": 60,
        "change_management": 35,
    }
})
print(report)
# {
#   "assessment_id": "uuid-...",
#   "company_name": "Acme Corp",
#   "industry": "manufacturing",
#   "overall_score": 54,
#   "readiness_level": "intermediate",
#   "recommendations": [...],
#   "tier": "pro"
# }
```

### Enroll an employee in a training module

```python
enrollment = bot.enroll_training({
    "employee_name": "Jane Smith",
    "level": "intermediate",
    "topic": "AI for Supply Chain"
})
print(enrollment)
# {
#   "enrollment_id": "uuid-...",
#   "employee_name": "Jane Smith",
#   "topic": "AI for Supply Chain",
#   "level": "intermediate",
#   "estimated_duration": "4 hours",
#   "status": "enrolled",
#   "tier": "pro"
# }
```

### Activate an integration

```python
integration = bot.activate_integration({
    "platform": "erp",
    "workflow_name": "inventory_forecast_workflow",
    "config": {"sync_interval": "daily"}
})
print(integration)
# {
#   "integration_id": "uuid-...",
#   "platform": "erp",
#   "workflow_name": "inventory_forecast_workflow",
#   "endpoint_url": "https://api.dreamcobots.ai/integrations/erp",
#   "api_key_stub": "dc_erp_xxxxxxxx",
#   "status": "active",
#   "tier": "pro"
# }
```

### Get session stats

```python
stats = bot.get_stats()
print(stats)
# {
#   "tier": "pro",
#   "requests_used": 3,
#   "requests_remaining": "9997",
#   "assessments_run": 1,
#   "enrollments_created": 1,
#   "integrations_active": 1,
#   "buddy_integration": True
# }
```

## Supported Integration Platforms

`crm` · `erp` · `hr` · `analytics` · `communication` · `document_management` · `e_commerce` · `supply_chain` · `finance` · `customer_support`

## License

MIT
