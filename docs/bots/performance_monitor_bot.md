# Performance Monitor Bot

## Overview
Instruments bot executions with timing measurements, persists metrics to the
knowledge store, and raises alerts when any bot shows significant performance
degradation across successive runs.

## What It Does
- Records per-bot elapsed time and status for every run
- Computes average and latest timing statistics
- Flags bots exceeding the 30-second slow threshold
- Persists metrics to `knowledge/performance_metrics.json` (capped at 500 entries)

## Features
- Per-bot average and latest timing
- Configurable slow threshold (`_SLOW_THRESHOLD_SECONDS`)
- Anti-context rot: metrics file capped automatically
- CI-friendly: exits 1 when slow bots are detected

## Benefits
- Catches performance regressions before they impact production
- Provides data for capacity planning and optimization priorities
- Creates a historical record of system performance

## Example Use Case
```python
from bots.performance_monitor_bot import record, report

record("testing_bot", elapsed_seconds=12.5, status="ok")
r = report()
print(r["slow_bots"])  # [] if all bots are healthy
```

## Command Line
```bash
python bots/performance_monitor_bot.py
```

## Future Enhancements
- Memory and CPU usage tracking via `psutil`
- Performance trend graphs using matplotlib
- Automated alerts via Slack or email when degradation is detected
