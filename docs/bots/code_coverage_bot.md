# Code Coverage Bot

## Overview
Measures and reports Python test coverage, identifies untested modules, and
enforces a configurable minimum coverage threshold to keep the codebase
reliable and trustworthy.

## What It Does
- Runs pytest with `--cov` to collect coverage data
- Saves a JSON coverage report for structured processing
- Lists all modules below the configurable threshold
- Exits with code 1 when overall coverage is insufficient

## Features
- Configurable threshold (default: 60%)
- Per-module breakdowns showing exactly what needs more tests
- Integrates with CI to block merges below minimum coverage
- Compatible with the Testing Bot and Feedback Loop Bot

## Benefits
- Ensures new features are tested before merging
- Identifies dead or unreachable code
- Builds client confidence in system reliability

## Example Use Case
```python
from bots.code_coverage_bot import run_coverage

report = run_coverage(threshold=75)
print(f"Overall: {report['overall_pct']}%")
for m in report["modules_below_threshold"]:
    print(f"  {m['module']}: {m['coverage_pct']}%")
```

## Command Line
```bash
python bots/code_coverage_bot.py
python bots/code_coverage_bot.py --threshold 80
```

## Future Enhancements
- Automatic test generation for uncovered lines using AI
- Coverage trend graphs over time
- GitHub PR comment with coverage delta
