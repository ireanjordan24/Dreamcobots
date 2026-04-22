# GitHub Analyzer Bot

## Overview

The **GitHub Analyzer Bot** autonomously discovers, analyses, and learns from
top-of-the-line bot systems published on GitHub, then feeds those insights back
into the DreamCo ecosystem.

---

## Responsibilities

| # | Responsibility | Description |
|---|----------------|-------------|
| 1 | **Autonomous Discovery** | Searches public GitHub repositories for trending bot systems across any category using the GitHub Search API. |
| 2 | **Data Extraction** | Fetches and parses `workflows.json`, bot metadata, and automation schemas from each discovered repository. |
| 3 | **DreamCo Integration** | Generates new DreamCo-compatible bot configuration stubs from extracted patterns and best practices. |
| 4 | **AI-Powered Learning** | Categorises repositories using keyword-based AI scoring, ranks them by relevance, and surfaces actionable recommendations. |

---

## Quick Start

```python
from bots.github_analyzer_bot import GitHubAnalyzerBot

bot = GitHubAnalyzerBot(github_token="ghp_...", max_results_per_query=10)

# 1 — Discover repositories
repos = bot.discover_repositories()

# 2 — Analyse and score them
insights = bot.analyze_all()

# 3 — Generate DreamCo bot configs from the insights
configs = bot.generate_all_configs()

# 4 — Summarise category trends
summary = bot.get_trend_summary()
print(summary)
```

---

## Key Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `discover_repositories(queries?)` | `list[dict]` | Search GitHub for bot repos. |
| `extract_workflows(repo_full_name)` | `dict` | Fetch `workflows.json` from a repo. |
| `analyze_repository(repo)` | `dict` | Analyse a single repo and produce an insight record. |
| `analyze_all()` | `list[dict]` | Analyse all discovered repos, sorted by relevance score. |
| `generate_bot_config(insight)` | `dict` | Create a DreamCo-compatible bot config stub. |
| `generate_all_configs()` | `list[dict]` | Generate configs for every insight. |
| `get_top_insights(n=5)` | `list[dict]` | Return the top *n* insights. |
| `get_trend_summary()` | `dict` | Summarise category trends across all analysed repos. |

---

## Bot Categories

The built-in AI categoriser maps repositories to one of 15 categories:

`automation` · `chatbot` · `ci_cd` · `crypto_trading` · `customer_support` ·
`data_pipeline` · `ecommerce` · `finance` · `lead_generation` · `marketing` ·
`real_estate` · `security` · `social_media` · `web_scraping` ·
`workflow_orchestration`

---

## Relevance Score

Repositories are scored on a **0–100** scale:

- **Stars** — logarithmic, up to 60 points
- **Forks** — logarithmic, up to 20 points
- **Metadata quality** (description + topics) — up to 20 points

---

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `github_token` | `None` | Personal-access token (raises rate limit from 60 → 5,000 req/hr). |
| `max_results_per_query` | `10` | Repos returned per search query (max 100). |
