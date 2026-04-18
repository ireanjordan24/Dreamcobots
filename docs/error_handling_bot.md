# DreamCo Error Handling Bot — Developer Documentation

## Overview

The **Error Handling Bot** is a beginner-friendly system that automatically
detects, categorizes, and suggests fixes for common runtime errors encountered
by DreamCo bot developers. Every message is written in plain English so that
anyone — even on their first day — can understand what went wrong and how to
fix it.

---

## Features

| Feature | Description |
|---------|-------------|
| **Dynamic Error Detection** | Inspects live Python exceptions and raw log text to identify errors as they happen |
| **Error Categorization** | Buckets every error into one of five simple categories (see below) |
| **Beginner-Friendly Messages** | Explains each error in plain language — no jargon |
| **Fix Suggestions** | Step-by-step remediation advice with copy-paste shell commands |
| **Learning Mode** | Optional mini-tutorials that explain *why* the error happened and where to learn more |
| **Sandbox Simulation** | Replays a catalogue of common errors without a live failing system |
| **GitHub Actions Integration** | Fully automated CI health checks and post-merge validation |

---

## Error Categories

```
Syntax      — Python grammar mistakes (SyntaxError, IndentationError, …)
Dependency  — Missing packages (ModuleNotFoundError, ImportError, …)
Environment — Missing config / API keys (KeyError, EnvironmentError, …)
IO          — File system problems (FileNotFoundError, PermissionError, …)
HTTP        — Web request failures (HTTPError, ConnectionError, status 4xx/5xx)
Unknown     — Anything that does not match the above
```

---

## Quick Start

### 1. Import and create the bot

```python
from bots.error_handling_bot import ErrorHandlingBot

bot = ErrorHandlingBot(learning_mode=True)
bot.start()
```

### 2. Capture a live exception

```python
try:
    import openai  # this might not be installed
except Exception as exc:
    record = bot.capture_exception(exc, context="load_openai()")
    print(record.user_message)      # plain-English description
    print(record.full_report())     # full beginner-friendly report
    if record.tutorial:
        print(record.tutorial)      # mini-tutorial (learning mode only)
```

### 3. Parse raw CI log text

```python
with open("ci-failure.log") as f:
    log_text = f.read()

record = bot.capture_log(log_text, context="GitHub Actions run #42")
print(record.full_report())
```

### 4. Get a summary report

```python
# After capturing several errors:
print(bot.get_report())

# Counts by category:
summary = bot.get_summary()
# → {"Syntax": 2, "Dependency": 1, "Environment": 0, ...}
```

### 5. Run the sandbox simulation

The sandbox exercises every error category without a live failing system:

```python
records = bot.simulate_bot_run()
print(bot.get_report())
```

Or from the command line:

```bash
python bots/error_handling_bot/sandbox_simulation.py
# With tutorials hidden:
python bots/error_handling_bot/sandbox_simulation.py --no-learning
```

---

## Learning Mode

When `learning_mode=True` (the default), every `ErrorRecord` includes a
`tutorial` field — a short explanation of *why* the error category exists and
links to beginner-friendly resources.

```python
# ON  — tutorials included (recommended for development)
bot = ErrorHandlingBot(learning_mode=True)

# OFF — compact output (recommended for production logs)
bot = ErrorHandlingBot(learning_mode=False)
```

---

## GitHub Actions Integration

The bot ships with two pre-configured workflows:

### `.github/workflows/error-handling-bot.yml`

Triggered on:
- Every push / PR touching `bots/error_handling_bot/` or its tests
- Daily at 06:00 UTC (post-merge health check)
- Manual dispatch (`workflow_dispatch`)

Jobs:
1. **Unit Tests** — runs `tests/test_error_handling_bot.py`
2. **Sandbox Simulation** — replays all error categories end-to-end
3. **Post-Merge Health Check** — runs the full test suite after every merge to `main`

### `.github/workflows/health_monitor.yml` (Heartbeat Bot)

Runs daily at midnight UTC and:
- Checks bot framework compliance
- Runs the Python test suite
- Reports branch activity
- Runs the Error Handling Bot simulation as a self-check

---

## API Reference

### `ErrorHandlingBot`

```python
class ErrorHandlingBot:
    def __init__(self, learning_mode: bool = True, log_dir: str = "logs/error-handling-bot")
    def start() -> None
    def stop() -> None
    def is_running -> bool

    def categorize(error_text: str) -> ErrorCategory
    def capture_exception(exc: BaseException, context: str = "") -> ErrorRecord
    def capture_log(log_text: str, context: str = "") -> ErrorRecord

    def get_records() -> List[ErrorRecord]
    def get_report() -> str
    def get_summary() -> Dict[str, int]
    def clear() -> None
    def log_record(record: ErrorRecord) -> str  # returns log file path
    def simulate_bot_run() -> List[ErrorRecord]
```

### `ErrorRecord`

```python
@dataclass
class ErrorRecord:
    error_id: str           # e.g. "ERR-0001"
    category: ErrorCategory
    error_type: str         # Python exception class name
    raw_message: str        # original exception message
    user_message: str       # beginner-friendly explanation
    suggestions: List[FixSuggestion]
    context: str            # where the error occurred
    traceback_text: str     # full Python traceback
    tutorial: str           # mini-tutorial (empty when learning_mode=False)
    timestamp: str          # ISO 8601 UTC

    def summary() -> str    # one-line summary
    def full_report() -> str  # complete formatted report
```

### `FixSuggestion`

```python
@dataclass
class FixSuggestion:
    step: int
    instruction: str    # plain-English instruction
    command: Optional[str]  # shell command (copy-paste ready)
```

### `ErrorCategory`

```python
class ErrorCategory(str, Enum):
    SYNTAX = "Syntax"
    DEPENDENCY = "Dependency"
    ENVIRONMENT = "Environment"
    IO = "IO"
    HTTP = "HTTP"
    UNKNOWN = "Unknown"
```

---

## Extending the Bot

### Adding a new error category

1. Add a new value to `ErrorCategory`.
2. Write a tutorial string (see `_SYNTAX_TUTORIAL` for an example).
3. Add a `_Rule` entry to the `_RULES` list with:
   - `pattern` — a compiled regex matching the new error
   - `category` — the new `ErrorCategory` value
   - `user_message_template` — plain-English description
   - `suggestions` — list of `FixSuggestion` objects
   - `tutorial` — mini-tutorial string
4. Add the new category to the sandbox simulation in `simulate_bot_run()`.
5. Write tests in `tests/test_error_handling_bot.py`.

### Adding a new fix suggestion to an existing category

Find the relevant `_Rule` in `_RULES` and append a new `FixSuggestion` to its
`suggestions` list.

---

## Docker / Codespace Integration

The bot runs inside the standard DreamCo Docker container.  No extra
dependencies are required — everything it needs is already in
`requirements.txt`.

The `.devcontainer/devcontainer.json` has been updated to:
- Use proper JSON format (was previously a Markdown wrapper)
- Point to the root `Dockerfile` correctly
- Include the GitHub Actions extension for editing workflows
- Add the GitHub CLI feature for interacting with the Actions API

---

## Logs

Errors captured by the bot are written to `logs/error-handling-bot/errors.log`
(one line per error).  In GitHub Actions the log directory is ephemeral; use
workflow artifacts to persist logs across runs if needed.

---

## Running Tests

```bash
# Error Handling Bot tests only (fast):
python -m pytest tests/test_error_handling_bot.py -v

# Full test suite:
python -m pytest tests/ --ignore=tests/test_backend.py -q
```
