# PR Intelligence Bot

## Overview
Extracts actionable intelligence from pull request history, identifies
recurring failure patterns, and keeps the knowledge base populated with
high-signal data for all other bots to learn from.

## What It Does
- Analyzes `pr_insights.json` / `ranked_insights.json` for statistical patterns
- Counts issue types, affected components, and top-confidence fixes
- Provides an `ingest_pr()` API to record new insights from live PRs
- Outputs pattern summaries for human-readable reporting

## Features
- Component-level attribution of failures
- High-confidence fix extraction (confidence ≥ 3)
- Automatic deduplication and size capping (max 500 raw insights)
- Seamless integration with the Insight Ranker and Buddy Bot

## Benefits
- Turns every merged PR into a learning event for the entire system
- Reduces repeat failures by surfacing known patterns
- Gives team members data-driven code review suggestions

## Example Use Case
```python
from bots.pr_intelligence_bot import ingest_pr, analyze_pr_patterns

ingest_pr({
    "title": "fix missing requirements import",
    "type": "bug_fix",
    "lesson": "Always verify requirements.txt before merging dependency changes."
})
```

## Command Line
```bash
python bots/pr_intelligence_bot.py
```

## Future Enhancements
- GitHub API integration to automatically pull merged PR data
- NLP-based clustering of similar failure patterns
- Weekly digest email report generation
