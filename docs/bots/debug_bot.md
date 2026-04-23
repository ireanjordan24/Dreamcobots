# Debug Bot

## Overview
AI-powered bot that detects workflow and runtime errors, matches them against
a curated knowledge base of past PR fixes, and suggests actionable resolutions.

## What It Does
- Loads ranked PR insights from `knowledge/ranked_insights.json`
- Matches error descriptions against known failure patterns
- Returns up to three confidence-ranked fix suggestions
- Exits with a non-zero status when no fix is found (CI-friendly)

## Features
- PR-based learning via the insight ranking system
- Configurable confidence threshold (`min_confidence` parameter)
- JSON-structured output for pipeline integration
- Zero external dependencies beyond the standard library

## Benefits
- Reduces mean time to resolution (MTTR) for CI failures
- Continuously improves as new PR fixes are recorded
- Works as a standalone script or imported module

## Example Use Case
```python
from bots.debug_bot import analyze

report = analyze("ModuleNotFoundError: No module named 'requests'")
print(report["suggestions"])
```

## Command Line
```bash
python bots/debug_bot.py "CI workflow failed on step Install dependencies"
```

## Future Enhancements
- Auto-apply safe fixes (e.g., add missing package to requirements.txt)
- Cross-bot learning so fixes discovered by other bots feed back here
- Integration with GitHub PR comments API
