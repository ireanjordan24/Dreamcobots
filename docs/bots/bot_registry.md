# Bot Registry

## Overview
The central catalog for the entire DreamCobots ecosystem. Scans the `bots/`
directory, checks each bot for a `run()` function and companion documentation,
and produces a machine-readable registry for dashboards, CI pipelines, and
other bots to query.

## What It Does
- Discovers all `.py` bot files in `bots/`
- Dynamically loads each module to detect `run()` availability
- Categorizes bots (`core` / `intelligence` / `analytics` / `factory` / `custom`)
- Saves the catalog to `knowledge/bot_registry.json`
- Renders a formatted terminal table or JSON output

## Features
- Zero-config auto-discovery
- Category-based grouping aligned with CI pipeline layers
- Documentation health check (marks bots missing `docs/bots/` pages)
- Persisted registry for use by other bots without re-scanning

## Benefits
- Single source of truth for all available bots
- Makes onboarding new developers instant — one command shows everything
- Enables automated compliance checks (all bots must have docs)

## Command Line
```bash
python bots/bot_registry.py         # formatted table
python bots/bot_registry.py --json  # machine-readable JSON
```

## Future Enhancements
- Web UI rendering of the registry (Bot Management Platform)
- Run-button integration with GitHub Actions workflow_dispatch API
- Health check polling with live status badges
