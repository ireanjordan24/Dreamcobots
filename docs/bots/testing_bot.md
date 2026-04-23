# Testing Bot

## Overview
Runs the full project test suite using pytest and returns a structured
pass/fail report. Designed to be the first quality gate in every CI pipeline.

## What It Does
- Executes `pytest tests/` with configurable ignore lists
- Captures stdout/stderr and parses pass/fail counts
- Returns a machine-readable JSON report
- Exits with code 1 on any test failure so CI stops immediately

## Features
- Configurable `max_fail` to stop early on cascading failures
- Automatic exclusion of known slow/broken test files
- Clean JSON output for downstream bots (e.g., Feedback Loop Bot)
- Works standalone or as an imported function

## Benefits
- Prevents broken code from reaching production
- Provides structured data that the Feedback Loop Bot can learn from
- Faster feedback loops than raw `pytest` output

## Example Use Case
```python
from bots.testing_bot import run_tests

result = run_tests(max_fail=3)
if not result["success"]:
    print("Tests failed:", result["errors"])
```

## Command Line
```bash
python bots/testing_bot.py
```

## Future Enhancements
- Per-module test isolation and parallel execution
- Automatic test generation for uncovered paths
- Slack/email notifications on failure
