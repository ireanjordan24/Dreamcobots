# DreamCo New User Setup

## Welcome to DreamCobots!
This guide gets you from zero to running your first automated workflow in under 30 minutes.

---

## Prerequisites
- [ ] GitHub account with access to [DreamCo-Technologies/Dreamcobots](https://github.com/DreamCo-Technologies/Dreamcobots)
- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] Git installed (`git --version`)
- [ ] pip installed (`pip --version`)

---

## Step 1 — Clone the Repository (2 min)
```bash
git clone https://github.com/DreamCo-Technologies/Dreamcobots.git
cd Dreamcobots
```

## Step 2 — Install Dependencies (3 min)
```bash
pip install -r requirements.txt
```

## Step 3 — Verify Setup (2 min)
```bash
python tools/check_bot_framework.py
```
All bots should pass the framework check.

## Step 4 — Run Your First Bot (5 min)
```bash
python3 - <<'EOF'
import sys
sys.path.insert(0, ".")
from bots.integration_feedback_bot.integration_feedback_bot import IntegrationFeedbackBot
from bots.integration_feedback_bot.tiers import Tier

bot = IntegrationFeedbackBot(tier=Tier.FREE)
result = bot.log_integration(
    platform="GitHub Actions",
    status="success",
    details="DreamCo onboarding complete!"
)
print("✅ Setup successful!")
print(f"   Platform: {result['entry']['platform']}")
print(f"   Status: {result['entry']['status']}")
EOF
```

## Step 5 — Configure Secrets (5 min)
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` with your API keys. **Never commit `.env` to git.**

For GitHub Actions secrets, go to:
`Repository → Settings → Secrets and variables → Actions`

Add your secrets (e.g., `SLACK_WEBHOOK_URL`, `OPENAI_API_KEY`).

## Step 6 — Trigger Your First Workflow (5 min)
1. Go to [Actions](https://github.com/DreamCo-Technologies/Dreamcobots/actions)
2. Click **Integration Feedback Bot**
3. Click **Run workflow**
4. Use defaults and click **Run workflow**
5. Watch the run succeed!

## Step 7 — Read Policies (5 min)
Review the [AI Acceptable Use Policy](../Policies/acceptable_use.md) before using AI tools.

## Step 8 — Join the Community (2 min)
Open [GitHub Discussions](https://github.com/DreamCo-Technologies/Dreamcobots/discussions)
and introduce yourself!

---

## You're Ready! 🚀
Next steps:
- [Beginner Learning Path](../Learning/beginner_path.md)
- [Advanced Learning Path](../Learning/advanced_path.md)
- [Become an Advocate](../Advocates/advocate_program.md)
