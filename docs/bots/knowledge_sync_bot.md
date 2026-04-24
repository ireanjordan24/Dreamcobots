# Knowledge Sync Bot

## Overview
Keeps all knowledge store files clean, consistent, and de-duplicated by
merging raw and ranked insights, pruning duplicates, and rebuilding the fast
lookup index used by all inference bots.

## What It Does
- Merges `pr_insights.json` and `ranked_insights.json` bidirectionally
- Removes exact duplicate entries (matching title + lesson)
- Enforces storage caps (500 raw, 100 ranked) to prevent bloat
- Rebuilds `knowledge/index.json` for O(1) title-based lookups

## Features
- Idempotent — safe to run multiple times without side effects
- Structured diff report (before/after counts per file)
- Full integration with the Feedback Loop Bot and Insight Ranker
- Zero external dependencies

## Benefits
- Eliminates redundant data that slows inference
- Ensures all bots work from a consistent, authoritative source
- Maintains fast lookup performance regardless of history size

## Command Line
```bash
python bots/knowledge_sync_bot.py
```

## Future Enhancements
- Scheduled automatic sync via cron or GitHub Actions
- Version history for the knowledge store (git-backed)
- Conflict resolution for insights with the same title but different lessons
