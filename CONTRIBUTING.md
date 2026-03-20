# Contributing to DreamCObots

Thank you for your interest in contributing to the DreamCObots project! To
keep the codebase consistent and production-ready, all contributors — human or
automated — **must** follow the guidelines below.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [GLOBAL AI SOURCES FLOW — Mandatory Architecture](#global-ai-sources-flow--mandatory-architecture)
3. [How to Add a New Bot](#how-to-add-a-new-bot)
4. [Required Framework Integration Checklist](#required-framework-integration-checklist)
5. [Testing Requirements](#testing-requirements)
6. [Static Analysis](#static-analysis)
7. [Pull Request Process](#pull-request-process)

---

## Code of Conduct

All participants are expected to be respectful and constructive. Harassment or
exclusionary behaviour will not be tolerated.

---

## GLOBAL AI SOURCES FLOW — Mandatory Architecture

Every bot added to this repository **must** follow the eight-stage
**GLOBAL AI SOURCES FLOW** pipeline.  The pipeline is implemented in
`framework/global_ai_sources_flow.py` and must be imported and used by every
bot.

```
GLOBAL AI SOURCES
┌─────────────────────────────────────────────┐
│ Research Papers │ GitHub │ Kaggle │ AI Labs │
│ US │ China │ India │ EU │ Global Labs        │
└─────────────────────────────────────────────┘
                      │
                      ▼
          ┌─────────────────────────┐
          │ DATA INGESTION LAYER    │
          │ Scrapers + Parsers      │
          │ Dataset normalization   │
          │ Language translation    │
          └────────────┬────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │ LEARNING METHOD CLASSIFIER  │
        │ Supervised                  │
        │ Unsupervised                │
        │ Reinforcement               │
        │ Self-Supervised             │
        │ Multi-Modal                 │
        │ Transfer Learning           │
        │ Federated Learning          │
        └────────────┬────────────────┘
                     │
                     ▼
         ┌──────────────────────────┐
         │ SANDBOX TEST LAB         │
         │ Containerized AI tests   │
         │ Model vs model battles   │
         │ A/B experiments          │
         │ Stress & adversarial     │
         └────────────┬─────────────┘
                      │
                      ▼
       ┌─────────────────────────────┐
       │ PERFORMANCE ANALYTICS       │
       │ Accuracy metrics            │
       │ Cost metrics                │
       │ Convergence speed           │
       │ Global Learning Matrix      │
       └────────────┬────────────────┘
                    │
                    ▼
      ┌──────────────────────────────┐
      │ HYBRID EVOLUTION ENGINE      │
      │ Genetic algorithms           │
      │ Reinforcement optimization   │
      │ Hybrid model creation        │
      └────────────┬─────────────────┘
                   │
                   ▼
      ┌──────────────────────────────┐
      │ DEPLOYMENT ENGINE            │
      │ Updates DreamCo bots         │
      │ Pushes best strategies       │
      │ Continuous retraining        │
      └────────────┬─────────────────┘
                   │
                   ▼
      ┌──────────────────────────────┐
      │ PROFIT & MARKET INTELLIGENCE │
      │ Real estate bots             │
      │ Car flipping bots            │
      │ Trading bots                 │
      │ Lead generation bots         │
      └────────────┬─────────────────┘
                   │
                   ▼
      ┌──────────────────────────────┐
      │ GOVERNANCE + SECURITY        │
      │ Encryption                   │
      │ Audit logs                   │
      │ Compliance checks            │
      │ AI safety controls           │
      └──────────────────────────────┘
```

### Why this matters

The pipeline ensures that:

- All data is sourced from traceable global AI inputs.
- Learning methods are explicitly classified.
- Every model is battle-tested in a sandbox before deployment.
- Performance is measured consistently across all bots.
- Models evolve using hybrid genetic and reinforcement-learning techniques.
- Deployment is always accompanied by continuous retraining.
- All activity feeds into profit-generating market verticals.
- Governance and security controls are never bypassed.

---

## How to Add a New Bot

1. **Create a directory** under `bots/<your-bot-name>/`.
2. **Add the main bot module** `bots/<your-bot-name>/<your_bot_name>.py`.
3. **Import and instantiate `GlobalAISourcesFlow`** in your bot's `__init__`:

   ```python
   from framework import GlobalAISourcesFlow

   class MyBot:
       def __init__(self):
           self.flow = GlobalAISourcesFlow(bot_name="MyBot")
   ```

4. **Call `run_pipeline()`** when your bot processes a request, passing the
   domain-specific payload as `raw_data`:

   ```python
   result = self.flow.run_pipeline(
       raw_data={"domain": "my_domain", "input": payload},
       learning_method="supervised",   # or another supported method
   )
   ```

5. **Add a `README.md`** inside your bot directory documenting:
   - Purpose and use cases
   - How to run the bot
   - Which `learning_method` the bot uses

6. **Add unit tests** in `tests/test_<your_bot_name>.py` (see
   [Testing Requirements](#testing-requirements)).

7. **Run the static analysis checker** before opening a PR:

   ```bash
   python tools/check_bot_framework.py
   ```

---

## Required Framework Integration Checklist

Before submitting a PR for a new or modified bot, verify all of the following:

- [ ] `from framework import GlobalAISourcesFlow` is present in the bot's main
  module.
- [ ] `self.flow = GlobalAISourcesFlow(bot_name="<YourBotName>")` is
  instantiated in `__init__`.
- [ ] `self.flow.run_pipeline(...)` is called during bot operation.
- [ ] `self.flow.validate()` passes without raising `FrameworkViolationError`.
- [ ] All eight `REQUIRED_STAGES` are present (verified automatically by
  `validate()`).
- [ ] `GovernanceSecurityLayer` has `encryption_enabled=True`,
  `audit_logs_enabled=True`, and `ai_safety_controls_enabled=True` (these are
  the defaults and must not be overridden to `False`).

---

## Testing Requirements

- All new bots **must** include a test file at `tests/test_<bot_name>.py`.
- Tests must cover at minimum:
  - Bot instantiation creates a `GlobalAISourcesFlow` attribute (`self.flow`).
  - `self.flow.validate()` returns `True` without errors.
  - `self.flow.run_pipeline()` completes and returns
    `{"pipeline_complete": True, ...}`.
- Run the full test suite before opening a PR:

  ```bash
  python -m pytest tests/ -v
  ```

---

## Static Analysis

A static analysis script is provided to catch bots that do not reference the
framework:

```bash
python tools/check_bot_framework.py
```

The checker will scan all Python files under `bots/`, `Business_bots/`,
`App_bots/`, `Marketing_bots/`, `Occupational_bots/`, `Real_Estate_bots/`,
and `Fiverr_bots/` and report any file that lacks a reference to
`GlobalAISourcesFlow` or the framework adherence comment.

> **PRs that introduce new bot files failing the static analysis check will
> not be merged.**

---

## Pull Request Process

1. Fork the repository and create a feature branch.
2. Follow the [How to Add a New Bot](#how-to-add-a-new-bot) steps.
3. Ensure the static analysis checker passes: `python tools/check_bot_framework.py`
4. Ensure all tests pass: `python -m pytest tests/ -v`
5. Open a PR against the `main` branch with a clear description of the bot's
   purpose and how it implements the GLOBAL AI SOURCES FLOW.
6. A maintainer will review the PR for framework compliance before merging.

---

## Auto-Recovery Mechanism

The CI pipeline includes an **auto-recovery step** that runs automatically
whenever tests fail.  It is implemented in `tools/auto_recovery.py`.

### What it does

| Check | Auto-fix? | On failure |
|---|---|---|
| Python version ≥ 3.8 | No | Logs manual action required |
| Dependency health (`pip check`) | **Yes** — re-runs `pip install -r requirements.txt` | Logs failure if pip install also fails |
| Bot framework compliance | No | Lists non-compliant files and links to CONTRIBUTING.md |
| Uncommitted changes | No | Warning only (not a blocking failure) |

### How it integrates with CI

The `.github/workflows/ci.yml` workflow adds three steps after the normal
test run, each guarded by `if: failure()`:

1. **Auto-recovery** — runs `tools/auto_recovery.py` to diagnose and fix what
   it can.
2. **Upload recovery log** — attaches `ci_recovery.log` as a workflow artifact
   so every recovery attempt is auditable.
3. **Re-run tests** — re-runs the full pytest suite after recovery to confirm
   whether the automatic fix resolved the failures.

### Running locally

```bash
# Diagnose and attempt automatic fixes
python tools/auto_recovery.py

# Point at a non-default requirements file
python tools/auto_recovery.py --requirements path/to/requirements.txt

# Send results to a webhook (e.g. Slack incoming webhook)
python tools/auto_recovery.py --webhook-url https://hooks.slack.com/services/...

# Write the recovery log to a custom path
python tools/auto_recovery.py --log-file /tmp/my_recovery.log
```

### Recovery log format

Each run appends one JSON line to `ci_recovery.log`:

```json
{
  "timestamp": "2024-01-01T12:00:00+00:00",
  "python": "3.10.12",
  "results": [
    {
      "check": "dependencies",
      "status": "ok",
      "detail": "Dependency issues detected and resolved via pip install -r requirements.txt.",
      "fix_applied": true,
      "manual_action": null
    }
  ]
}
```

`ci_recovery.log` is listed in `.gitignore` and is never committed to the
repository; it is only uploaded as a CI artifact.
