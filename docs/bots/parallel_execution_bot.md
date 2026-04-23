# Parallel Execution Bot

## Overview
Maximizes system throughput by running multiple bots concurrently in a
managed thread pool, collecting results and handling timeouts gracefully —
ideal for the intelligence and analytics pipeline layers.

## What It Does
- Executes a list of bot modules simultaneously using `ThreadPoolExecutor`
- Enforces per-bot timeouts to prevent hung processes from blocking CI
- Collects structured pass/fail/timeout results for each bot
- Reports total elapsed time for the entire parallel batch

## Features
- Configurable `max_workers` (default: 4) and `timeout` (default: 60s)
- Dynamic bot loading — no hardcoded module list required
- Thread-safe result collection
- CI-friendly: exits 1 if any bot fails or times out

## Benefits
- Reduces total CI time by running independent bots simultaneously
- Fault-isolated — one bot's failure doesn't prevent others from running
- Enables aggressive parallelism for the intelligence pipeline

## Example Use Case
```python
from bots.parallel_execution_bot import run_parallel

report = run_parallel(["insight_ranker", "buddy_bot", "knowledge_sync_bot"])
print(f"Completed in {report['elapsed_seconds']}s")
```

## Command Line
```bash
python bots/parallel_execution_bot.py
```

## Future Enhancements
- ProcessPoolExecutor option for CPU-bound bots
- Priority queuing for critical vs. optional bots
- Real-time progress reporting via WebSocket
