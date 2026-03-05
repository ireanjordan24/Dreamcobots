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
### `BuddyAI`
- Central hub for the DreamCobots ecosystem.
- **`buddy_bot.py`** – `BuddyBot` class: bot registration, shared knowledge base, task queue, and event dispatch.
- **`auth.py`** – `AuthModule`: token-based authentication and permission checking.
- **`event_bus.py`** – `EventBus`: lightweight publish/subscribe messaging between bots.

### `bots`
- Contains all bot scripts such as the `government-contract-grant-bot` and the new `dreamcobot`.
- **`dreamcobot/dreamcobot.py`** – `DreamCobot`: user-facing bot that integrates with `BuddyBot`.
- `config.json` needs to be configured with required API keys and bot settings.

### `examples`
- Contains example use cases for different bots like `Referral Bot` and `Hustle Bot`.

### `tests`
- Unit and integration tests for the BuddyAI framework and DreamCobot integration.

---
## DreamCobot ↔ BuddyBot Integration

### Overview
DreamCobot connects to the `BuddyBot` hub at startup and leverages its shared services:

| Feature | BuddyAI module |
|---|---|
| Authentication & authorization | `BuddyAI.auth.AuthModule` |
| Bot-to-bot messaging | `BuddyAI.event_bus.EventBus` |
| Shared knowledge base | `BuddyBot.set/get_knowledge()` |
| Shared task queue | `BuddyBot.push/pop_task()` |

### Quick Start
```python
from BuddyAI.buddy_bot import BuddyBot
from bots.dreamcobot.dreamcobot import DreamCobot

# 1. Create the hub
buddy = BuddyBot(name="MyHub")

# 2. Connect DreamCobot
dream = DreamCobot.create_and_start(buddy)

# 3. Handle a user message (broadcasts a 'user.message' event)
print(dream.handle_user_message("Hello, DreamCobot!"))

# 4. Share data via the knowledge base
dream.store_knowledge("onboarding_step", 1)
print(dream.retrieve_knowledge("onboarding_step"))   # 1

# 5. Push a task into the shared queue
dream.assign_task({"type": "goal_setting", "user": "Alex"})
task = dream.process_next_task()
print(task)   # {'type': 'goal_setting', 'user': 'Alex'}

# 6. Shut down cleanly
dream.stop()
```

### Adding More Bots
Every additional bot follows the same pattern:
1. Call `buddy.register_bot(bot_id, permissions=[...])` to register and receive a token.
2. Subscribe to events with `buddy.subscribe_event(event, handler)`.
3. Use `buddy.push_task / pop_task` and `buddy.set/get_knowledge` for collaboration.

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
## Running Tests
```bash
pip install -r requirements.txt
pytest tests/ -v
```

---
## GitHub Pages Instructions
1. Navigate to **Settings > Pages**.
2. Select the `deployment-setup` branch and root directory as the publishing source.
3. Save your settings to host the frontend.

---