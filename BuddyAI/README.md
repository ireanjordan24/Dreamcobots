# BuddyAI — Central Dialogue Integration Layer

BuddyAI is the central orchestration hub for all Dreamcobots sector bots.  It
provides:

- **BuddyBot** — a registry and router that connects any number of sector bots
  under a single conversational interface.
- **EventBus** — a lightweight publish/subscribe event bus that lets bots and
  external systems react to lifecycle and dialogue events in real time.

---

## Quick Start

```python
from BuddyAI import BuddyBot, EventBus
from bots.finance_bot import FinanceBot
from bots.real_estate_bot import RealEstateBot
from bots.ai_chatbot.tiers import Tier

# Create the central hub
buddy = BuddyBot()

# Register sector bots
buddy.register_bot("finance", FinanceBot(tier=Tier.PRO))
buddy.register_bot("real_estate", RealEstateBot(tier=Tier.FREE))

# Route messages
response = buddy.chat("finance", "What is my portfolio balance?")
print(response["message"])

response = buddy.chat("real_estate", "Find 3-bed homes in Austin under $400k")
print(response["message"])
```

---

## BuddyBot API

### `register_bot(name, bot)`
Register a sector bot under a given name.  The bot must implement
`chat(message) -> dict` and `describe_tier() -> str`.

### `unregister_bot(name)`
Remove a previously registered bot.

### `list_bots() -> list[str]`
Return the names of all registered bots.

### `chat(bot_name, message, **kwargs) -> dict`
Route a message to the named bot.  Returns the bot's response dict augmented
with `"bot_name"` and `"timestamp"` keys.

### `get_history(bot_name=None) -> list[dict]`
Return the unified dialogue history, optionally filtered to one bot.

### `clear_history(bot_name=None)`
Clear dialogue history (all bots or just one).

### `describe_bot_tier(bot_name) -> str`
Delegate `describe_tier()` to the named sector bot.

### `event_bus` (property)
Access the shared `EventBus` instance.

---

## EventBus API

```python
from BuddyAI import EventBus

bus = EventBus()

# Subscribe
bus.subscribe("lead_captured", lambda data: print("Lead:", data))

# Publish
bus.publish("lead_captured", {"name": "Alice"})

# Unsubscribe
bus.unsubscribe("lead_captured", handler)
```

### Events published by BuddyBot

| Event | When fired | Payload keys |
|---|---|---|
| `buddy.bot_registered` | A sector bot is registered | `name` |
| `buddy.bot_unregistered` | A sector bot is removed | `name` |
| `buddy.message_received` | Before routing to a sector bot | `bot`, `message` |
| `buddy.message_responded` | After a successful response | `bot`, `response` |

---

## Directory Structure

```
BuddyAI/
├── buddy_bot.py   # Central hub — BuddyBot class + SectorBotProtocol
├── event_bus.py   # Publish/subscribe EventBus
├── __init__.py    # Package exports
└── README.md      # This file
```

---

## Running Tests

```bash
cd Dreamcobots
python -m pytest tests/test_buddy_bot.py -v
```