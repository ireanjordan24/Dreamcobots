# 🏰 DreamCo Control Tower

**Centralized command center for the entire DreamCo bot ecosystem.**

One place to see, control, and scale every Buddy Bot and repository without touching individual GitHub repos manually.

---

## Architecture

```
dreamco-control-tower/
├── backend/
│   ├── server.js            # Express API (heartbeat, webhooks, REST endpoints)
│   ├── bot-manager.js       # Bot registry + auto-upgrade logic
│   ├── repo-manager.js      # GitHub repo monitoring via Octokit
│   ├── auto-upgrade-bots.js # Auto-merge, auto-PR, auto-heal scripts
│   ├── heartbeat-check.js   # Live status check for all bots
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # React + Tailwind dashboard
│   │   └── main.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── config/
│   ├── bots.json            # Registered bot registry
│   └── repos.json           # Monitored repository registry
└── package.json
```

The Python integration module lives at `bots/control_tower/control_tower.py` and provides native Python wrappers for heartbeat pings, GitHub API calls, and registry sync.

---

## Features

### 🤖 Centralized Bot Registry
- Tracks all bots and repos
- Shows status: `active`, `updating`, `conflict detected`, `offline`
- Logs every heartbeat, upgrade, and PR

### 🔄 Auto-Upgrade & Self-Healing
- Pull latest changes from `origin/main`
- Resolve conflicts automatically with `merge -X theirs`
- Run formatters and linters
- Commit, push, and open Pull Requests automatically
- Re-trigger failed GitHub Actions workflow runs

### 📊 Live Dashboard
- React + Tailwind UI with real-time bot statuses
- Repository monitoring: open PRs, issues, last commit, workflow results
- One-click upgrade per bot
- Conflict alerts for repos needing attention

### 🪝 GitHub Webhooks
- Receive `push`, `pull_request`, `issues`, and `workflow_run` events
- Trigger dependent bot upgrades on PR merge
- Auto-fix issues labelled `bug`
- Self-heal on workflow failures

---

## Quick Start

### Prerequisites
- Node.js ≥ 18
- `GITHUB_TOKEN` environment variable (Personal Access Token with `repo` and `workflow` scopes)

### Backend

```bash
cd dreamco-control-tower/backend
npm install
GITHUB_TOKEN=ghp_... node server.js
# Server starts on http://localhost:3001
```

### Frontend

```bash
cd dreamco-control-tower/frontend
npm install
npm run dev
# Dashboard opens on http://localhost:3000
```

### CLI Tools

```bash
# Check heartbeat status of all bots
node backend/heartbeat-check.js

# Run auto-upgrade for all bots
node backend/auto-upgrade-bots.js

# Run auto-upgrade for a single bot
node backend/auto-upgrade-bots.js --bot LeadGenerationBot

# Trigger the bot manager
node backend/bot-manager.js
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/heartbeat` | Control Tower liveness check |
| GET | `/api/bots` | List all bots with heartbeat status |
| GET | `/api/bots/:name` | Single bot status |
| POST | `/api/bots/:name/upgrade` | Trigger upgrade for a bot |
| GET | `/api/repos` | List monitored repositories |
| GET | `/api/repos/:owner/:repo` | Repository status (PRs, issues, commits) |
| GET | `/api/dashboard` | Aggregated dashboard data |
| POST | `/webhook` | GitHub webhook receiver |

---

## Configuration

### `config/bots.json`

```json
[
  {
    "name": "LeadGenerationBot",
    "repoName": "Dreamcobots",
    "repoPath": "./bots/multi_source_lead_scraper",
    "branch": "main",
    "owner": "ireanjordan24",
    "status": "active",
    "tier": "pro"
  }
]
```

### `config/repos.json`

```json
[
  {
    "name": "Dreamcobots",
    "owner": "ireanjordan24",
    "defaultBranch": "main",
    "autoUpgrade": true
  }
]
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub PAT with `repo` + `workflow` scopes |
| `PORT` | Backend server port (default: `3001`) |
| `CONTROL_TOWER_URL` | Backend URL for Python heartbeat client (default: `http://localhost:3001`) |
| `STRIPE_KEY` | Stripe secret key for revenue tracking (optional) |
| `WEBHOOK_SECRET` | GitHub webhook secret for signature verification (optional) |

---

## Python Integration

```python
from bots.control_tower.control_tower import (
    HeartbeatClient,
    GitHubRepoManager,
    BotRegistrySync,
)

# Send a heartbeat ping from a Python bot
client = HeartbeatClient()
client.ping("LeadGenerationBot", status="active")

# Query GitHub repo status
mgr = GitHubRepoManager(token=os.environ["GITHUB_TOKEN"])
status = mgr.get_repo_status("ireanjordan24", "Dreamcobots")
print(status["summary"])

# Register a new bot in the registry
sync = BotRegistrySync()
sync.register(
    name="NewBot",
    repo_name="Dreamcobots",
    owner="ireanjordan24",
    tier="pro",
)
```

---

## Deployment

| Component | Recommended Platform |
|-----------|---------------------|
| Frontend | Vercel / Netlify |
| Backend | AWS EC2 / Lambda / Heroku |
| Database | JSON (starter) → MongoDB (1000+ bots) |

---

## Automation Triggers

| Event | Action |
|-------|--------|
| PR merged in main repo | All dependent bots auto-update |
| Issue labelled `bug` | Bot attempts fix, opens PR |
| Workflow failed | Self-heal: re-run workflow |
| New repo detected | Clone template, register bot, begin monitoring |
