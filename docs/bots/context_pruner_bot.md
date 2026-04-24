# Context Pruner Bot

## Overview
Prevents knowledge base bloat by systematically removing stale, zero-confidence,
and outdated entries from all knowledge store files, keeping the system lean
and inference fast.

## What It Does
- Trims `pr_insights.json`, `ranked_insights.json`, `feedback_log.json`,
  and `performance_metrics.json` to their configured size caps
- Removes zero-confidence entries from insight files
- Reports exact before/after counts for full transparency

## Features
- Per-file configurable caps (`_CAPS` dictionary)
- Zero-confidence insight removal for quality-over-quantity storage
- Safe — only removes tail data, never corrupts structure
- Idempotent (no-op when files are already within limits)

## Benefits
- Keeps all knowledge lookups fast as the system scales
- Prevents CI from slowing down due to oversized JSON files
- Maintains high signal-to-noise ratio in the knowledge base

## Command Line
```bash
python bots/context_pruner_bot.py
```

## Future Enhancements
- Age-based pruning (remove insights older than N days)
- Archive pruned data to a separate historical store
- Configurable caps via `knowledge/adaptive_config.json`
