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
## Folder Explanation
### `bots`
- Contains all bot scripts such as the `government-contract-grant-bot`.
- `config.json` needs to be configured with required API keys and bot settings.
- See [`bots/README.md`](bots/README.md) for full documentation.

### `examples`
- Contains example use cases for different bots like `Referral Bot` and `Hustle Bot`.
- `stress_test.py` — load / stress tests that validate every bot can handle repeated invocations.

### `debug.py`
- Top-level debugging and diagnostic utility.
- Validates environment, loads configuration, tests bot interfaces, and runs a stress test.
- Run with: `python debug.py`

### `replit.md`
- Step-by-step guide for running the project on [Replit](https://replit.com).

---
## How to Run Bots Locally
1. Navigate to the bot directory. For example:
   ```bash
   cd bots/government-contract-grant-bot
   ```
2. Run the bot script. For example:
   ```bash
   python government_contract_grant_bot.py
   ```
3. Make sure necessary APIs and configurations are set in `bots/config.json` before running.

---
## Debugging
Run the debug utility from the repository root to validate your setup:
```bash
python debug.py
```

Run the stress tests to verify all bots handle repeated calls correctly:
```bash
python examples/stress_test.py
```

---
## GitHub Pages Instructions
1. Navigate to **Settings > Pages**.
2. Select the `deployment-setup` branch and root directory as the publishing source.
3. Save your settings to host the frontend.

---