# DreamCo Control Tower 🏰

> **Central command centre for the entire DreamCo bot ecosystem.**  
> One place to see, control, and scale every Buddy Bot and repo without touching individual GitHub repos manually.

---

## Architecture

```
dreamco-control-tower/
│
├── backend/
│   ├── bot_manager.py       # Bot registry — register, heartbeat, status
│   ├── repo_manager.py      # GitHub repo monitoring + PR creation
│   ├── auto_upgrader.py     # Pull/merge/test/PR pipeline per bot
│   └── revenue_tracker.py  # Multi-provider payment analytics
│
├── automation/
│   └── auto_upgrade_bots.py # CLI entry-point: upgrade all bots
│
├── config/
│   ├── bots.json            # Bot registry (persisted)
│   ├── repos.json           # Repo registry (persisted)
│   └── settings.json        # Tower-wide configuration
│
└── README.md
```

---

## Features

### 1 — Centralised Bot Registry (`bot_manager.py`)
- Register, remove, and query up to **1 000+ bots**.
- Track status: `active`, `updating`, `conflict`, `offline`, `onboarding`.
- Record heartbeats, last updates, and last PR timestamps.
- Persist state to `config/bots.json`.

### 2 — GitHub Repo Integration (`repo_manager.py`)
- Monitor open PRs, open issues, last commit, and latest workflow result.
- Sync all repos with a single call to `sync_all()`.
- Create Pull Requests via the GitHub REST API.
- Reads `GITHUB_TOKEN` from the environment for authenticated requests.

### 3 — Auto-Upgrade Pipeline (`auto_upgrader.py`)
```
git pull --rebase origin main
  → conflict? → git merge -X theirs origin/main
  → run pytest / npm test
  → open PR "🤖 Auto-upgrade from DreamCo Control Tower"
  → update bot registry
```

### 4 — Revenue Tracker (`revenue_tracker.py`)
- Aggregates payments from **Stripe**, **PayPal**, and **Square**.
- Provider adapters are swappable — wire real SDK calls in production.
- Returns summaries: total revenue, by-provider, by-bot, top bots.

### 5 — Automation Script (`automation/auto_upgrade_bots.py`)
```bash
# Upgrade all bots against live GitHub
python automation/auto_upgrade_bots.py

# Preview what would happen — no git or API calls
DRY_RUN=1 python automation/auto_upgrade_bots.py

# Skip tests during upgrade
RUN_TESTS=0 python automation/auto_upgrade_bots.py
```

---

## Quick Start

```python
from dreamco_control_tower.backend.bot_manager import BotManager
from dreamco_control_tower.backend.repo_manager import RepoManager
from dreamco_control_tower.backend.auto_upgrader import AutoUpgrader
from dreamco_control_tower.backend.revenue_tracker import RevenueTracker

# --- Bot registry
bm = BotManager()
bm.register_bot("affiliate_bot", "Dreamcobots", "bots/affiliate_bot", tier="pro")
bm.update_heartbeat("affiliate_bot")
print(bm.get_summary())

# --- Repo monitoring
rm = RepoManager()
rm.add_repo("Dreamcobots", "ireanjordan24")
status = rm.sync_repo("Dreamcobots")   # calls GitHub API

# --- Auto-upgrade
upgrader = AutoUpgrader(bm, rm, repo_root="/path/to/repo")
result = upgrader.upgrade_bot("affiliate_bot")

# --- Revenue
rt = RevenueTracker()
rt.add_entry(199.99, bot_name="affiliate_bot", provider="stripe")
print(rt.get_summary())
```

---

## Environment Variables

| Variable        | Purpose                                             |
|-----------------|-----------------------------------------------------|
| `GITHUB_TOKEN`  | GitHub Personal Access Token (repo + PR scope)     |
| `STRIPE_KEY`    | Stripe secret key (production revenue tracking)    |
| `REPO_ROOT`     | Filesystem root of the cloned Dreamcobots repo      |
| `RUN_TESTS`     | Set to `0` to skip test execution during upgrades  |
| `DRY_RUN`       | Set to `1` to preview upgrades without side-effects|

---

## Deployment

| Layer     | Recommended                        |
|-----------|------------------------------------|
| Backend   | Python + Flask / FastAPI on AWS Lambda or Heroku |
| Frontend  | React + Tailwind on Vercel / Netlify (connects to the Python REST API) |
| Database  | JSON files (starter) → MongoDB (scale to 1 000+ bots) |
| Secrets   | Environment variables / AWS Secrets Manager |

---

## Automation Triggers

| Event                       | Action                                           |
|-----------------------------|--------------------------------------------------|
| PR merged on `main`         | Trigger `upgrade_all()` for dependent bots       |
| Issue labeled `bug`         | Bot attempts fix, opens auto-PR                  |
| Workflow fails              | `AutoUpgrader` runs self-healing pipeline        |
| New repo added              | `add_repo()` + `register_bot()` auto-onboarding |

---

## Tests

```bash
# From the repo root
pytest tests/test_control_tower.py -v
```
