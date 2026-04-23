# Deployment Review Bot

## Overview
Validates production readiness by performing a comprehensive pre-deployment
checklist — confirming that all required files, directories, and workflow
configurations are present before code goes live.

## What It Does
- Checks for the existence of `requirements.txt`, CI workflow files, core bot scripts,
  knowledge store files, and essential directories
- Returns a structured pass/fail report with a list of missing resources
- Exits with code 1 if any required resource is missing

## Features
- Configurable checklist (add files/dirs to `REQUIRED_FILES` / `REQUIRED_DIRS`)
- Zero external dependencies
- Fast execution (< 1 second)
- Human-readable summary message alongside JSON output

## Benefits
- Prevents broken deployments caused by missing configuration
- Acts as a final safety net in CI/CD pipelines
- Documents deployment prerequisites in code

## Example Use Case
```python
from bots.deployment_review_bot import review

report = review()
if not report["passed"]:
    print("Deployment blocked:", report["missing"])
```

## Command Line
```bash
python bots/deployment_review_bot.py
```

## Future Enhancements
- Environment variable validation (check required secrets are set)
- Docker image existence checks
- Integration with deployment platforms (Heroku, Railway, etc.)
