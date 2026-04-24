# Proactive Task Planner

## Overview
Continuously scans the repository for gaps — missing bots, undocumented
skills, incomplete workflows — and generates a prioritized action plan so
the team always knows what to work on next.

## What It Does
- Checks for the existence of every priority bot and its documentation
- Verifies knowledge store files and CI workflow configuration
- Produces a time-stamped, sorted task list with effort estimates
- Returns up to 20 immediate action items

## Features
- Zero-config — works by inspecting the file system
- Priority-sorted output (highest-impact items first)
- Effort estimates (`low` / `medium` / `high`) for sprint planning
- Machine-readable JSON output for dashboard integration

## Benefits
- Eliminates the "what should I work on?" question
- Keeps the system self-documenting and gap-free
- Aligns development effort with the highest-leverage improvements

## Example Use Case
```python
from bots.proactive_task_planner import generate_plan

plan = generate_plan()
for task in plan["tasks"][:5]:
    print(f"[{task['effort'].upper()}] {task['task']}")
```

## Command Line
```bash
python bots/proactive_task_planner.py
```

## Future Enhancements
- Integration with GitHub Issues API to create tasks automatically
- Sprint velocity tracking and workload balancing
- Dependency-aware task ordering
