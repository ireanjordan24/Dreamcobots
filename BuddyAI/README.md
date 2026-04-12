# BuddyAI

This directory contains the central AI code to manage and communicate with all bots.

## Modules

| File | Description |
|---|---|
| `buddy_bot.py` | `BuddyBot` — central hub for bot registration, event dispatch, knowledge base, and task queue |
| `auth.py` | `AuthModule` — token-based authentication and permission management |
| `event_bus.py` | `EventBus` — lightweight pub/sub event bus for bot-to-bot messaging |

## Usage

```python
from BuddyAI.buddy_bot import BuddyBot

buddy = BuddyBot(name="MyHub")

# Register a bot and get its secret token
token = buddy.register_bot("mybot", permissions=["task:run", "knowledge:read"])

# Shared knowledge base
buddy.set_knowledge("greeting", "hello")
buddy.get_knowledge("greeting")   # "hello"

# Shared task queue
buddy.push_task({"type": "onboard", "user_id": 7})
task = buddy.pop_task()

# Event bus
buddy.subscribe_event("user.joined", lambda p: print("User joined:", p))
buddy.publish_event("user.joined", {"user_id": 7})
```