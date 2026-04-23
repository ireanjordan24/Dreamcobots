# DreamCo Bot Portfolio

Welcome to the **DreamCobots** bot portfolio — your reference for every AI-powered
automation bot in the DreamCo ecosystem.

## Bot Categories

### 🔵 Core Quality Layer
These bots form the foundation of every CI pipeline run.

| Bot | Purpose |
|-----|---------|
| [Debug Bot](debug_bot.md) | Detects errors and suggests fixes using PR learning |
| [Testing Bot](testing_bot.md) | Runs the full test suite and reports structured results |
| [Validator Bot](bot_validator.md) | Code quality scoring against known bad patterns |
| [Task Execution Controller](task_execution_controller.md) | Orchestrates multi-bot pipelines |
| [Parallel Execution Bot](parallel_execution_bot.md) | Runs bots concurrently for max throughput |
| [Auto Repair Bot](auto_repair_bot.md) | Applies safe automated fixes to common failures |

### 🟢 Intelligence Layer
These bots learn, rank, and distribute knowledge across the system.

| Bot | Purpose |
|-----|---------|
| [Insight Ranker](insight_ranker.md) | Scores and ranks PR insights by confidence |
| [Buddy Bot](buddy_bot.md) | Distributes best practices to all bots |
| [PR Intelligence Bot](pr_intelligence_bot.md) | Extracts patterns from PR history |
| [Feedback Loop Bot](feedback_loop_bot.md) | Converts failures into learning events |
| [Adaptive Learning Bot](adaptive_learning_bot.md) | Auto-adjusts system thresholds |
| [Proactive Task Planner](proactive_task_planner.md) | Generates prioritized sprint plans |
| [Knowledge Sync Bot](knowledge_sync_bot.md) | Keeps knowledge base clean and consistent |
| [Context Pruner Bot](context_pruner_bot.md) | Prevents knowledge base bloat |

### 🟠 Advanced Analytics Layer
These bots measure, optimize, and document the system.

| Bot | Purpose |
|-----|---------|
| [Optimizer Bot](optimizer_bot.md) | Code complexity and maintainability analysis |
| [Security Auditor Bot](security_auditor_bot.md) | Vulnerability scanning with bandit |
| [Deployment Review Bot](deployment_review_bot.md) | Pre-deployment readiness checks |
| [Code Coverage Bot](code_coverage_bot.md) | Test coverage measurement and enforcement |
| [Performance Monitor Bot](performance_monitor_bot.md) | Bot execution speed tracking |

### 🟡 Factory Layer
These bots build and manage the bot ecosystem itself.

| Bot | Purpose |
|-----|---------|
| [Skill Generation Bot](skill_generation_bot.md) | Scaffolds new bot skill modules |
| [Bot Registry](bot_registry.md) | Central catalog of all available bots |

## Running a Bot

Every bot follows the same interface:

```python
# Import and call directly
from bots.debug_bot import run
result = run({"error": "import failed"})
print(result["status"])

# Or run from command line
python bots/debug_bot.py "error description"
```

## CI Pipeline Layers

The `dreamco-bots.yml` workflow runs bots in three staged layers:

```
Layer 1: Core Quality  →  Layer 2: Intelligence  →  Layer 3: Advanced Analytics
```

Each layer only runs if the previous one passes, ensuring fast feedback and
clean failure isolation.
