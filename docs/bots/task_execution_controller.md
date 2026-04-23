# Task Execution Controller

## Overview
The central pipeline orchestrator that sequences bot tasks, resolves
execution order, and collects structured results — making multi-bot
workflows reliable and reproducible.

## What It Does
- Accepts a prioritized list of bot tasks with dependency metadata
- Loads each bot's `run()` function dynamically at runtime
- Executes tasks in order, halting the pipeline on critical failures
- Returns a full execution report with per-task status and timing

## Features
- `critical` flag per task: halt pipeline on failure when set to True
- Dynamic bot loading — no hardcoded imports required
- Default pipeline covers the five most important quality gates
- JSON output compatible with CI log parsers

## Benefits
- Single command to run the entire quality pipeline
- Clear audit trail of what ran, what passed, and what failed
- Enables reproducible multi-stage bot workflows

## Example Use Case
```python
from bots.task_execution_controller import TaskExecutionController

pipeline = TaskExecutionController(tasks=[
    {"name": "Test", "bot": "testing_bot", "critical": True, "context": {}},
    {"name": "Audit", "bot": "security_auditor_bot", "critical": False, "context": {}},
])
report = pipeline.run()
print(report["status"])
```

## Command Line
```bash
python bots/task_execution_controller.py
```

## Future Enhancements
- DAG-based dependency resolution for parallel stage execution
- Retry logic for transient failures
- Integration with GitHub Actions artifacts for log persistence
