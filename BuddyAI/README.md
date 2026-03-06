# BuddyAI

This directory contains the central AI code to manage and communicate with all bots.

## Overview

**Buddy** is a cutting-edge SaaS bot that understands and executes user commands
dynamically—via text or voice—eliminating the need for specialized apps.

## Architecture

```
BuddyAI/
├── __init__.py           # Package entry point
├── buddy_bot.py          # Main BuddyBot class (start here)
├── task_engine.py        # Core task dispatcher with modular capability registry
├── text_handler.py       # Text-to-task command parsing (intent detection)
├── speech_handler.py     # Speech-to-task voice recognition
├── library_manager.py    # Dynamic library fetching, testing, and loading
├── scheduler.py          # Lightweight background task scheduler
├── benchmarks.py         # Performance benchmarking and auto-optimization
├── event_bus.py          # Event-driven pub/sub architecture
└── plugins/
    ├── __init__.py
    ├── productivity.py   # Todo list, reminders, workflow queue (app replacement)
    ├── data_entry.py     # In-memory record store with CSV import/export
    └── api_integrator.py # Public API compatibility (HTTP GET/POST + caching)
```

## Key Features

| Feature | Module | Description |
|---|---|---|
| **Task Automation** | `task_engine.py` + `plugins/` | Modular capability registry; new handlers plug in with one call |
| **Self-Learning** | `library_manager.py` | Downloads, smoke-tests, and loads new PyPI packages at runtime |
| **App Replacement** | `plugins/productivity.py` | Todo/calendar/workflow mimicking common productivity apps |
| **Text-to-Task** | `text_handler.py` | Regex-based intent detection for free-form commands |
| **Speech-to-Task** | `speech_handler.py` | Microphone capture via `SpeechRecognition`; offline fallback |
| **Efficiency Optimization** | `benchmarks.py` | Measure, compare, and surface optimization opportunities |
| **API Compatibility** | `plugins/api_integrator.py` | Fetch/post any public HTTP API; TTL caching built in |
| **Event-Driven** | `event_bus.py` | Decoupled pub/sub keeps modules independent |

## Quick Start

```python
from BuddyAI import BuddyBot

buddy = BuddyBot()
buddy.start()

# Text commands
print(buddy.chat("Add todo buy groceries")["message"])
print(buddy.chat("List my todos")["message"])
print(buddy.chat("Complete buy groceries")["message"])
print(buddy.chat("Schedule meeting at 3pm")["message"])
print(buddy.chat("Fetch https://api.example.com/data")["message"])

# Voice command (requires: pip install SpeechRecognition pyaudio)
# response = buddy.listen_and_respond()

# Install a new library to extend capabilities
buddy.chat("Install library schedule")

# Benchmark a command
result = buddy.benchmark_task("help", iterations=10)
print(result["message"])

buddy.stop()
```

## Interactive CLI

```bash
python -m BuddyAI.buddy_bot
```

## Installation

```bash
pip install -r requirements.txt
# For voice support:
pip install SpeechRecognition pyaudio
```

## Running Tests

```bash
pytest tests/ -v
```

## Adding New Capabilities

Register any callable as a new capability:

```python
from BuddyAI import BuddyBot

buddy = BuddyBot()
buddy.start()

def handle_weather(params):
    city = params.get("city", "")
    return {"success": True, "message": f"Weather for {city}: sunny 72°F"}

buddy.task_engine.register_capability("weather", handle_weather)
result = buddy.task_engine.execute("weather", {"city": "New York"})
```
