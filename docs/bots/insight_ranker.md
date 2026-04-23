# Insight Ranker

## Overview
Scores every raw PR insight using a heuristic confidence model, sorts them
from most to least trustworthy, and saves the top 100 to
`knowledge/ranked_insights.json` — powering every bot that learns from
historical data.

## What It Does
- Reads `knowledge/pr_insights.json`
- Assigns a confidence score based on issue type, title keywords, and context
- Sorts insights by score (descending)
- Saves top 100 to `knowledge/ranked_insights.json`

## Features
- Configurable boost terms and weights (`_BOOST_TERMS`)
- Hard cap of 100 ranked entries to prevent memory creep
- Idempotent — safe to run on every PR merge
- Feeds Debug Bot, Validator Bot, and Buddy Bot

## Benefits
- Ensures bots act on trustworthy data, not noise
- Continuously improves accuracy as more PRs are recorded
- Simple, transparent scoring that the team can audit and adjust

## Command Line
```bash
python bots/insight_ranker.py
```

## Future Enhancements
- ML-based scoring to replace the heuristic model
- Automated ranking triggered on every PR merge via GitHub Actions
- Human-in-the-loop review for low-confidence but high-impact insights
