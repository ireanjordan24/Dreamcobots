# DreamCo AI Beginner Learning Path

## Overview
This path takes you from zero to running your first DreamCo bot in under 30 minutes.

## Prerequisites
- A GitHub account
- Python 3.11+ installed
- Basic command-line familiarity

---

## Step 1 — Clone & Setup (5 min)
```bash
git clone https://github.com/DreamCo-Technologies/Dreamcobots.git
cd Dreamcobots
pip install -r requirements.txt
```

## Step 2 — Run the Framework Check (2 min)
```bash
python tools/check_bot_framework.py
```
This confirms all bots comply with the GLOBAL AI SOURCES FLOW architecture.

## Step 3 — Run Your First Bot (5 min)
```bash
python - <<'EOF'
import sys
sys.path.insert(0, ".")
from bots.integration_feedback_bot.integration_feedback_bot import IntegrationFeedbackBot
from bots.integration_feedback_bot.tiers import Tier

bot = IntegrationFeedbackBot(tier=Tier.FREE)
result = bot.log_integration(platform="GitHub Actions", status="success",
                              details="My first DreamCo integration!")
print(result)
EOF
```

## Step 4 — Explore the Bot Library (5 min)
```bash
python - <<'EOF'
import sys
sys.path.insert(0, ".")
from bots.global_bot_network.bot_library import BOT_LIBRARY
for entry in BOT_LIBRARY[:5]:
    print(f"{entry.bot_id}: {entry.description[:60]}...")
EOF
```

## Step 5 — Trigger a Workflow (5 min)
Go to [Actions → Company Lookup Bot](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/company-lookup.yml)
and click **Run workflow** with a company name like "Stripe".

## Step 6 — Join the Community
- Open [GitHub Discussions](https://github.com/DreamCo-Technologies/Dreamcobots/discussions)
- Introduce yourself and share what you're building

## Next Steps
- Read [Advanced Learning Path](advanced_path.md)
- Study [Prompt Engineering](prompt_engineering.md)
- Review [AI Policies](../Policies/acceptable_use.md)
