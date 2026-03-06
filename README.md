# DreamCobots Repository

Welcome to **DreamCobots** — a versatile, user-friendly platform for automation and income generation. This repository contains a growing collection of collaborative bots (cobots) designed to automate tasks, generate income, and empower users across multiple industries.

---

## 🚀 Why DreamCobots?

- **Non-Technical Friendly**: Each bot ships with detailed setup guides and Docker support — no coding required to get started.
- **Platform Integrations**: All bots support Zapier, N8n, and other SaaS workflows out of the box.
- **Income Generation**: Bots are designed not just for automation, but to actively generate revenue streams.
- **Self-Marketing**: Built-in marketing capabilities help bots promote themselves across platforms.
- **Open & Extensible**: Standardized templates make it easy to add new bots and customize existing ones.

---

## 🤖 Bot Categories

### Active Bots (`bots/`)

| Bot | Description | Docs |
|-----|-------------|------|
| [Government Contract Automation Bot](bots/government-contract-grant-bot/) | Automates SAM.gov contract searches and proposal generation | [README](bots/government-contract-grant-bot/README.md) |
| [211 Resource Eligibility Bot](bots/211-resource-eligibility-bot/) | Helps users find local social services and check eligibility | [README](bots/211-resource-eligibility-bot/README.md) |
| [Selenium Job Application Bot](bots/selenium-job-application-bot/) | Automates job searching and applications on multiple platforms | [README](bots/selenium-job-application-bot/README.md) |
| [AI Side Hustle Bots](bots/ai-side-hustle-bots/) | AI-powered tools to identify and monetize side hustles | [README](bots/ai-side-hustle-bots/README.md) |

### Legacy Bot Templates

| Category | Description |
|----------|-------------|
| `App_bots/` | App-focused automation bots |
| `Business_bots/` | Business process automation |
| `Fiverr_bots/` | Freelancing platform automation |
| `Marketing_bots/` | Marketing and outreach automation |
| `Occupational_bots/` | Occupation-specific automation |
| `Real_Estate_bots/` | Real estate listing and analysis bots |

---

## 📦 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/ireanjordan24/Dreamcobots.git
   cd Dreamcobots
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🏃 Quick Start

Navigate to a bot directory and run it:

```bash
# Government Contract Automation Bot
cd bots/government-contract-grant-bot
python government_contract_grant_bot.py

# 211 Resource Eligibility Bot
cd bots/211-resource-eligibility-bot
python bot.py

# Selenium Job Application Bot
cd bots/selenium-job-application-bot
python bot.py

# AI Side Hustle Bots
cd bots/ai-side-hustle-bots
python bot.py
```

### Run with Docker

Each bot includes a `Dockerfile` for containerized deployment:

```bash
cd bots/<bot-name>
docker build -t dreamcobots-<bot-name> .
docker run dreamcobots-<bot-name>
```

---

## ⚙️ Configuration

Each bot uses `config.json` or environment variables for settings. Copy the example config and fill in your API keys:

```bash
cp bots/config.json bots/<bot-name>/config.json
# Edit config.json with your API keys and preferences
```

---

## 🔗 Integrations

All bots support integration with:

- **Zapier** — Connect to 5,000+ apps without code
- **N8n** — Self-hosted workflow automation
- **Make.com (Integromat)** — Visual automation builder
- **GitHub Actions** — CI/CD and scheduled automation

See [MARKETING.md](MARKETING.md) for integration guides and marketing strategies.

---

## 🚢 Deployment

- **Docker**: Each bot has a `Dockerfile` — see individual bot READMEs.
- **GitHub Actions**: CI/CD workflows in `.github/workflows/`.
- **GitHub Pages**: Push to `deployment-setup` branch and enable Pages in repository settings.

---

## 📚 Documentation

- [MARKETING.md](MARKETING.md) — Marketing guide, competitive advantages, platform integration
- [bots/README.md](bots/README.md) — Overview of all active bots
- Individual bot READMEs contain full setup, usage, and deployment instructions.

---