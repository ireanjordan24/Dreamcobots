# Buddy Bot

## Overview
The system's intelligence distributor. Reads the top-ranked insights and
broadcasts best practices to all registered bots so every component of the
ecosystem benefits from the same accumulated knowledge.

## What It Does
- Reads `knowledge/ranked_insights.json` for high-confidence recommendations
- Filters insights by configurable `min_confidence` threshold
- Returns the top N actionable lessons
- Reports which bots received the distributed recommendations

## Features
- Configurable `min_confidence` (default: 3) and `top_n` (default: 5)
- Works as a standalone script or imported module
- Zero external dependencies
- Human-readable and JSON-structured output

## Benefits
- Ensures all bots operate from the same knowledge baseline
- Prevents individual bots from developing blind spots
- Creates a cohesive intelligence layer across the entire system

## Example Use Case
```python
from bots.buddy_bot import get_top_recommendations

recs = get_top_recommendations(min_confidence=3, top_n=3)
for r in recs:
    print(f"  → {r}")
```

## Command Line
```bash
python bots/buddy_bot.py
```

## Future Enhancements
- Push recommendations to individual bot config files
- Priority routing (urgent fixes reach critical bots first)
- Integration with the Adaptive Learning Bot for threshold auto-tuning
