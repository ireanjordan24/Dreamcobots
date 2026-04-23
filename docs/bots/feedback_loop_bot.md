# Feedback Loop Bot

## Overview
Closes the intelligence loop by analyzing bot run outcomes, identifying
recurring failures, and automatically injecting new learnings back into the
PR insights knowledge base.

## What It Does
- Reads the feedback log (`knowledge/feedback_log.json`)
- Identifies bots that have failed 2+ times consecutively
- Converts recurring failures into structured PR insights for future reference
- Persists learnings to `knowledge/pr_insights.json`

## Features
- Anti-context rot: log is capped at 1,000 entries
- Deduplication of learnings before insertion
- Configurable failure threshold for triggering insight injection
- JSON output compatible with CI dashboards

## Benefits
- System gets smarter with every failure — not just every success
- Reduces repeat incidents by creating institutional memory
- Enables proactive intervention before failures cascade

## Example Use Case
```python
from bots.feedback_loop_bot import record_run_result, analyze_feedback

record_run_result("testing_bot", "error", "pytest: command not found")
feedback = analyze_feedback()
print(feedback["recurring_failures"])
```

## Command Line
```bash
python bots/feedback_loop_bot.py
```

## Future Enhancements
- Slack notifications when a recurring failure is detected
- Severity scoring for failures (P1 / P2 / P3)
- Cross-bot failure correlation analysis
