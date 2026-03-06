# DreamCObots Repository

Welcome to the DreamCObots project! This repository outlines our groundbreaking mission to develop and deploy 3000 collaborative robots (cobots) designed for transforming industries worldwide. Explore our documentation, system details, and user guides to understand every aspect of this ambitious endeavor.

---
## Installation Instructions
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/ireanjordan24/Dreamcobots.git
   ```
2. Navigate to the directory:
   ```bash
   cd Dreamcobots
   ```
3. Install dependencies (if any bot scripts depend on a specific package manager, such as `pip` for Python):
   ```bash
   pip install -r requirements.txt
   ```

---
## Deployment Steps
To deploy bots or static content:
1. Push changes to the `deployment-setup` branch.
2. Enable **GitHub Pages** in repository settings for frontend hosting.
3. Add and customize workflows to automate bot tasks (see GitHub Actions).

---
## AI Chatbot – Tiered Platform

The `bots/ai_chatbot/` package provides a production-ready, tiered AI chatbot
system with KimiK integration, partner-recruitment tools, and a marketing
documentation manager.

### Tiers

| Tier             | Price       | Highlights |
|------------------|-------------|------------|
| **Free**         | $0          | Core chat, FAQ, onboarding (50 msg/day) |
| **Intermediate** | $29.99/mo   | Analytics dashboard, integrations, email campaigns |
| **Premium**      | $99.99/mo   | KimiK AI, partner recruitment, AI ecosystem directory, marketing docs, white-label |

### Quick Start

```python
from bots.ai_chatbot import AIChatbot, Tier

bot = AIChatbot(user_id="user_001", tier=Tier.PREMIUM, model="kimi-k")
print(bot.chat("Find our best AI ecosystem partners."))
```

See [`bots/ai_chatbot/README.md`](bots/ai_chatbot/README.md) for full documentation.

---
## Folder Explanation
### `bots`
- `ai_chatbot/` – Tiered AI chatbot with KimiK, analytics, marketplace, and marketing doc manager.
- `government-contract-grant-bot/` – Government contract and grant processing bot.
- `config.json` needs to be configured with required API keys and bot settings.

### `examples`
- Contains example use cases for different bots like `Referral Bot` and `Hustle Bot`.

---
## How to Run Bots Locally
1. Navigate to the bot directory. For example:
   ```bash
   cd bots/government-contract-grant-bot
   ```
2. Run the bot script. For example:
   ```bash
   python bot.py
   ```
3. Make sure necessary APIs and configurations are set before running.

---
## GitHub Pages Instructions
1. Navigate to **Settings > Pages**.
2. Select the `deployment-setup` branch and root directory as the publishing source.
3. Save your settings to host the frontend.

---