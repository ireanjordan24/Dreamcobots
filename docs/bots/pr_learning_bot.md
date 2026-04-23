# PR Learning Bot

## Overview
Foundation bot that learns from pull request data and adapts behavior based
on historical patterns. Acts as the base intelligence layer for the PR
insights knowledge pipeline.

## What It Does
- Records PR-level learning events
- Provides a `learn_from_pr(pr_data)` API for integration
- Generates structured responses to PR data inputs

## Features
- Clean `PullRequestLearningBot` class interface
- Ready for extension with real GitHub API integration
- `run()` entry point compatible with the Task Execution Controller

## Benefits
- Establishes the foundation for all PR-based intelligence
- Simple interface makes integration straightforward
- Designed for extension without breaking changes

## Example Use Case
```python
from bots.pr_learning_bot import PullRequestLearningBot

bot = PullRequestLearningBot()
bot.learn_from_pr({"title": "fix: resolve import error", "type": "bug_fix"})
```

## Future Enhancements
- GitHub API integration to auto-pull merged PR metadata
- Pattern clustering for recurring issue types
- Direct feed into `knowledge/pr_insights.json`
