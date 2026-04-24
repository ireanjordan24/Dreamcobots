# Optimizer Bot

## Overview
Analyzes Python source code for performance bottlenecks and maintainability
issues using static analysis, surfacing functions that are too complex and
modules that are difficult to maintain.

## What It Does
- Measures cyclomatic complexity of every function and class using `radon`
- Flags functions with complexity ≥ 10 as refactoring candidates
- Computes the Maintainability Index and warns when it drops below 20/100
- Scans entire directories recursively

## Features
- Per-file JSON reports with line numbers for easy navigation
- Directory walk with automatic exclusion of `node_modules`, `__pycache__`, `venv`
- Graceful degradation when `radon` is not installed
- CI-friendly: exits 1 when optimization issues are found

## Benefits
- Keeps codebase lean and fast over time
- Surfaces technical debt early
- Reduces future debugging effort by enforcing simplicity

## Example Use Case
```python
from bots.optimizer_bot import analyze_path

reports = analyze_path("bots/")
for r in reports:
    if r["status"] == "needs_optimization":
        print(r["file"], r["issues"])
```

## Command Line
```bash
python bots/optimizer_bot.py bots/
python bots/optimizer_bot.py core/dreamco_orchestrator.py
```

## Future Enhancements
- Auto-refactoring suggestions using `autopep8`
- Integration with the Adaptive Learning Bot for threshold tuning
- Support for JavaScript via ESLint complexity rules
