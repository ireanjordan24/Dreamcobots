# Auto Repair Bot

## Overview
Monitors the feedback log for recurring failures and automatically applies
safe, reversible repairs — such as creating missing `__init__.py` files and
verifying `sys.path` configuration — without requiring human intervention.

## What It Does
- Reads `knowledge/feedback_log.json` for recent error entries
- Matches error text against a library of safe repair patterns
- Applies repairs (e.g., creates missing `__init__.py`) automatically
- Persists repair history to `knowledge/repair_log.json`

## Features
- Safe-only repairs (no code deletion or destructive changes)
- Pattern-matched triggers (configurable via `_SAFE_REPAIRS`)
- Idempotent — checks before creating to avoid duplication
- Structured repair log for auditing

## Benefits
- Reduces developer toil for common, repetitive fixes
- Keeps CI pipelines green with minimal intervention
- Creates an audit trail of every automated repair

## Command Line
```bash
python bots/auto_repair_bot.py
```

## Future Enhancements
- Expand the repair library with more patterns (e.g., fixing common import errors)
- Dry-run mode that reports what would be repaired without applying changes
- Integration with GitHub PR creation for non-trivial repairs
