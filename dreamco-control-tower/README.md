# 🏰 DreamCo Control Tower

> **Centralized command center** for the entire DreamCo bot ecosystem.  
> One dashboard to monitor, deploy, update, and scale every bot — fully automated.

---

## Architecture

```
dreamco-control-tower/
│
├── backend/
│   ├── server.js          ← Express API server (Node.js)
│   ├── bot-manager.js     ← GitHub-integrated bot operations & heartbeat
│   ├── repo-manager.js    ← GitHub repo status, PR detection, conflict alerts
│   ├── revenue-tracker.js ← Stripe + PayPal revenue aggregation
│   └── api/
│       ├── bots.js        ← /api/bots routes
│       ├── repos.js       ← /api/repos routes
│       └── revenue.js     ← /api/revenue routes
│
├── frontend/
│   └── index.html         ← React dashboard (CDN, no build step)
│
├── automation/
│   └── auto-upgrade-bots.js  ← Scheduled upgrade engine
│
├── config/
│   ├── bots.json          ← Bot registry
│   ├── users.json         ← User accounts
│   └── payments.json      ← Payment provider config
│
└── package.json
```

---

## Quick Start

```bash
cd dreamco-control-tower
npm install

# Set environment variables
export GITHUB_TOKEN=ghp_xxx
export GITHUB_OWNER=ireanjordan24
export STRIPE_SECRET_KEY=sk_live_xxx   # optional
export PAYPAL_CLIENT_ID=xxx            # optional
export PAYPAL_CLIENT_SECRET=xxx        # optional

npm start
# → http://localhost:4000
```

---

## Features

### 1️⃣ Centralized Bot Registry
- Tracks all bots, their repos, and live/offline status
- JSON-backed; MongoDB-ready for 1000+ bots

### 2️⃣ Real-Time Heartbeat Monitoring
- Each bot pings `POST /api/bots/:name/ping`
- Dashboard auto-refreshes live/offline status every 15 s

### 3️⃣ GitHub Integration
- Fetch open PRs, last commits, and workflow status per repo
- Detect conflicts and workflow failures with visual alerts
- Auto-merge conflicts and create upgrade PRs

### 4️⃣ One-Click Bot Deployment
- Fill out name, tier, and niche → bot registered instantly
- Workflows auto-configured via GitHub API (requires token)

### 5️⃣ Revenue Analytics
- Aggregates Stripe + PayPal totals in one view
- Per-provider breakdown with error hints when unconfigured

### 6️⃣ Auto-Upgrade Engine
- Pull latest code across all repos
- Auto-resolve git conflicts (`-X theirs`)
- Create auto-upgrade PRs
- Schedule with cron or run on demand

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bots` | All bots with heartbeat status |
| GET | `/api/bots/:name` | Single bot status |
| POST | `/api/bots/:name/ping` | Record heartbeat |
| POST | `/api/bots/:name/pull` | Git pull latest |
| POST | `/api/bots/:name/pr` | Create auto-upgrade PR |
| GET | `/api/repos/:name` | GitHub repo status |
| POST | `/api/repos/multi` | Multiple repos at once |
| GET | `/api/revenue` | Revenue summary |
| POST | `/api/upgrade-all` | Auto-upgrade all bots |
| GET | `/api/heartbeat` | All heartbeat statuses |

---

## Auto-Upgrade Script

```bash
# Dry-run (safe — no git or API calls)
node automation/auto-upgrade-bots.js --dry-run

# Live run (requires GITHUB_TOKEN)
node automation/auto-upgrade-bots.js
```

---

## Scaling with MongoDB

Replace the JSON file store with MongoDB by setting:

```env
MONGODB_URI=mongodb://localhost:27017/dreamco
```

The `BotRegistry` class in the Python backend and the bot manager in the
Node.js backend both support drop-in MongoDB adapters.

---

## Dashboard Tabs

| Tab | What you see |
|-----|-------------|
| 📊 Overview | Live/offline counts, revenue, bot status table |
| 🤖 Bots | Full registry with ping/pull actions |
| 🔗 GitHub | Per-repo PR count, last commit, workflow status |
| 💰 Revenue | Stripe + PayPal totals with provider breakdown |
| 🚀 Deploy | One-click bot deployment form |
| ⚙️ Automation | Heartbeat monitor + one-click auto-upgrade |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Recommended | GitHub personal access token (for API calls) |
| `GITHUB_OWNER` | Optional | GitHub username (default: `ireanjordan24`) |
| `PORT` | Optional | Server port (default: `4000`) |
| `STRIPE_SECRET_KEY` | Optional | Stripe live/test secret key |
| `PAYPAL_CLIENT_ID` | Optional | PayPal REST API client ID |
| `PAYPAL_CLIENT_SECRET` | Optional | PayPal REST API client secret |
| `PAYPAL_MODE` | Optional | `sandbox` or `live` (default: `sandbox`) |
| `MONGODB_URI` | Optional | MongoDB connection URI for persistent registry |

---

*Part of the DreamCo Empire — powered by the GLOBAL AI SOURCES FLOW framework.*
