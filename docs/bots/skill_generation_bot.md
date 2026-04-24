# Skill Generation Bot

## Overview
Automatically scaffolds new bot skill modules and their companion portfolio
documentation pages so the team never has to write boilerplate from scratch.

## What It Does
- Detects existing bot skills to avoid duplicates
- Generates a fully-structured `bots/<skill_name>.py` with a `run()` stub
- Creates a matching `docs/bots/<skill_name>.md` portfolio page
- Returns structured JSON status for CI integration

## Features
- Template-driven generation (consistent interface across all bots)
- Idempotent — skips if the skill already exists
- Instantly makes new skills available to the Task Execution Controller
- Compatible with the Bot Registry for automatic catalog updates

## Benefits
- Reduces new bot development time from hours to minutes
- Enforces structural standards automatically
- Enables rapid prototyping without breaking the system

## Example Use Case
```python
from bots.skill_generation_bot import generate_skill

result = generate_skill("weather_forecast_bot")
print(result["skill_path"])  # bots/weather_forecast_bot.py
print(result["doc_path"])    # docs/bots/weather_forecast_bot.md
```

## Command Line
```bash
python bots/skill_generation_bot.py weather_forecast_bot
python bots/skill_generation_bot.py  # lists existing skills
```

## Future Enhancements
- AI-generated skill logic based on a natural language description
- Auto-registration in the Bot Registry on creation
- Test file generation alongside the skill
