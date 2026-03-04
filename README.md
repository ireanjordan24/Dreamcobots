# DreamCObots Repository

Welcome to the DreamCObots project! This repository outlines our groundbreaking mission to develop and deploy 3000 collaborative robots (cobots) designed for transforming industries worldwide. Explore our documentation, system details, and user guides to understand every aspect of this ambitious endeavor.

---

## Repository Structure (Alphabetical)

```
Dreamcobots/
├── App_bots/           # App-focused bot features (onboarding, support, updates)
├── BuddyAI/            # Central AI hub: commands, orchestration
│   ├── buddy_ai.py     # BuddyAI orchestrator class
│   └── commands.py     # Slash-command handler
├── Business_bots/      # Business-focused bot features
├── communications/     # Device communication modules
│   ├── bluetooth_handler.py       # Bluetooth discovery, pairing, data transfer
│   └── http_websocket_handler.py  # HTTP server & WebSocket handler
├── content/            # Content display modules
│   ├── chat_content.py  # Jokes and fun chat responses
│   ├── movie_info.py    # Movie information and search
│   └── random_facts.py  # Random general and tech facts
├── cross_platform/     # Cross-platform rendering
│   └── renderer.py     # Adapts content for TV, PC, phone, tablet
├── Examples/           # Example use cases
├── Fiverr_bots/        # Fiverr-focused bot features
├── Marketing_bots/     # Marketing-focused bot features
├── Occupational_bots/  # Occupational bot features
├── Real_Estate_bots/   # Real-estate bot features
├── bots/               # Core bot scripts and configuration
│   ├── config.json     # API keys and server settings
│   └── government-contract-grant-bot/
├── examples/           # Additional examples
└── tests/
    └── test_commands.py  # Unit tests (58 tests covering all modules)
```

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
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. *(Optional)* For real Bluetooth hardware support, install PyBluez or Bleak:
   ```bash
   pip install pybluez   # classic Bluetooth
   pip install bleak     # BLE (Bluetooth Low Energy)
   ```

---

## Bot Commands

The `BuddyAI/commands.py` module implements the following slash commands through the `CommandHandler` class:

| Command | Description |
|---|---|
| `/run-bot <bot_id>` | Start or resume a bot by ID |
| `/pause-bot <bot_id>` | Pause a running bot |
| `/bot-status [bot_id]` | Get the status of one or all bots |
| `/broadcast-message <msg>` | Broadcast a message to all or selected bots |
| `/analytics` | Return uptime, bot counts, and usage statistics |
| `/device-register <id> <type>` | Register a new device with the bot network |

### Quick example

```python
from BuddyAI.commands import CommandHandler

handler = CommandHandler()
handler.run_bot("my-bot")
handler.broadcast_message("System check!", target_bots=["my-bot"])
print(handler.get_analytics())
```

---

## Device Communication

### HTTP / WebSocket (`communications/http_websocket_handler.py`)

```python
from communications.http_websocket_handler import (
    HTTPCommunicationHandler,
    WebSocketCommunicationHandler,
)

# Start a lightweight HTTP server
http = HTTPCommunicationHandler(host="0.0.0.0", port=8080)
http.start()

# Simulate WebSocket communication
ws = WebSocketCommunicationHandler()
ws.connect_client("device-01")
ws.send("device-01", {"status": "online"})
ws.broadcast("Ping all devices")
```

### Bluetooth (`communications/bluetooth_handler.py`)

```python
from communications.bluetooth_handler import BluetoothHandler

bt = BluetoothHandler(simulate=True)   # set simulate=False for real hardware

devices = bt.discover()                 # scan for nearby devices
bt.pair(devices[0]["address"])          # pair with first found device
bt.connect(devices[0]["address"])       # open connection
bt.send_data(devices[0]["address"], "Hello!")  # send data
print(bt.get_data_log())               # inspect transfer log
```

Set `simulate=False` and ensure PyBluez is installed to use real Bluetooth hardware.
The module supports smart TVs, computers, phones, tablets, and other electronics.

---

## Content Modules

### Movie Information (`content/movie_info.py`)

```python
from content.movie_info import MovieInfo

movies = MovieInfo()
print(movies.display(movies.get_random()))
print(movies.search_by_genre("Sci-Fi"))
print(movies.get_top_rated(3))
```

### Chat & Funny Content (`content/chat_content.py`)

```python
from content.chat_content import ChatContent

chat = ChatContent()
print(chat.format_joke())
print(chat.chat("tell me a joke"))
print(chat.get_greeting())
```

### Random Facts (`content/random_facts.py`)

```python
from content.random_facts import RandomFacts

facts = RandomFacts()
print(facts.display())            # random fact with formatting
print(facts.get_tech_fact())     # technology-specific fact
print(facts.get_multiple(5))     # 5 unique facts
```

---

## Cross-Platform Rendering

The `cross_platform/renderer.py` module adapts content for different device types:

| Platform | Max Width | Emoji | Layout |
|---|---|---|---|
| `smart_tv` | 80 chars | ✅ | landscape |
| `computer` | 120 chars | ✅ | landscape |
| `phone` | 40 chars | ✅ | portrait |
| `tablet` | 60 chars | ✅ | portrait |
| `other` | 60 chars | ❌ | landscape |

```python
from cross_platform.renderer import CrossPlatformRenderer

renderer = CrossPlatformRenderer("phone")   # or "smart_tv", "computer", "tablet"
print(renderer.render("Hello from Dreamcobots!"))
print(renderer.render(movie_dict, content_type="movie"))
```

---

## Running Tests

```bash
python -m unittest tests/test_commands.py -v
```

All 58 unit tests cover:
- All slash commands (`/run-bot`, `/pause-bot`, `/bot-status`, `/broadcast-message`, `/analytics`, `/device-register`)
- Bluetooth discovery, pairing, connection, and data transfer
- HTTP/WebSocket client management and messaging
- Movie search, random facts, and chat content
- Cross-platform rendering for all supported device types

---

## Configuration (`bots/config.json`)

```json
{
  "api_keys": { "movie_db": "", "weather": "" },
  "http_server": { "host": "0.0.0.0", "port": 8080 },
  "websocket_server": { "host": "0.0.0.0", "port": 8765 },
  "bluetooth": { "simulate": true, "discovery_duration_seconds": 5 },
  "bots": { "default_status": "paused", "auto_register": true }
}
```

---

## Deployment Steps

To deploy bots or static content:
1. Push changes to the `deployment-setup` branch.
2. Enable **GitHub Pages** in repository settings for frontend hosting.
3. Add and customize workflows to automate bot tasks (see GitHub Actions).

---

## GitHub Pages Instructions

1. Navigate to **Settings > Pages**.
2. Select the `deployment-setup` branch and root directory as the publishing source.
3. Save your settings to host the frontend.

---

## Integrating Additional Devices

1. **Register the device** using `/device-register`:
   ```python
   handler.device_register("my-device-id", "smart_tv", {"brand": "Samsung", "model": "QN90"})
   ```
2. **Connect via Bluetooth** (if applicable):
   ```python
   bt.discover()
   bt.pair("<device-address>")
   bt.connect("<device-address>")
   ```
3. **Or connect via HTTP/WebSocket**:
   ```python
   ws.connect_client("my-device-id")
   ws.send("my-device-id", {"command": "wake"})
   ```
4. **Render content for the device**:
   ```python
   renderer = CrossPlatformRenderer("smart_tv")
   print(renderer.render(content, content_type="movie"))
   ```

---