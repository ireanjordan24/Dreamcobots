# Validator Bot

## Overview
Intelligent code quality gate that scans source code for patterns known to
cause failures, scoring it against the ranked PR insight database.

## What It Does
- Reads ranked insights from `knowledge/ranked_insights.json`
- Scans code for titles that match historically bad patterns
- Computes a quality score (0–100) with graduated penalties
- Returns `"pass"` (score > 60) or `"review"` status

## Features
- Confidence-weighted penalties (high-confidence issues cost more)
- Works on code strings, files, or stdin
- CI-friendly: exits 1 when status is `"review"`
- Integrates with PR learning for continuous improvement

## Benefits
- Prevents previously-seen bugs from re-entering the codebase
- Quantifies code risk as a numeric score
- Improves automatically as the knowledge base grows

## Example Use Case
```python
from bots.bot_validator import validate_code

result = validate_code(open("bots/debug_bot.py").read())
print(result["score"], result["warnings"])
```

## Command Line
```bash
python bots/bot_validator.py bots/debug_bot.py
echo "fix ci workflow" | python bots/bot_validator.py -
```

## Future Enhancements
- Language-agnostic pattern matching (JS, Go, etc.)
- Integration with GitHub PR review API
- Auto-generated inline code comments
