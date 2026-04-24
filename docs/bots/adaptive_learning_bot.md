# Adaptive Learning Bot

## Overview
Dynamically adjusts system-wide bot configuration thresholds based on the
quality and quantity of available ranked insights, ensuring the whole
ecosystem becomes more accurate as the knowledge base grows.

## What It Does
- Reads `knowledge/ranked_insights.json` to assess data richness
- Computes optimal `min_confidence` and penalty values
- Saves updated configuration to `knowledge/adaptive_config.json`
- Other bots read this config to apply up-to-date thresholds

## Features
- Automatic threshold raising when high-confidence data is abundant
- Threshold relaxation when the knowledge base is sparse or new
- Timestamp tracking for every configuration update
- No manual tuning required

## Benefits
- Prevents false positives when the knowledge base is immature
- Increases precision as the system matures
- Makes the entire bot ecosystem self-calibrating

## Example Use Case
```python
from bots.adaptive_learning_bot import adapt, _load_ranked, _load_config

insights = _load_ranked()
config = _load_config()
updated = adapt(insights, config)
print(f"New min_confidence: {updated['min_confidence']}")
```

## Command Line
```bash
python bots/adaptive_learning_bot.py
```

## Future Enhancements
- Reinforcement learning integration for dynamic policy optimization
- Per-bot threshold tuning (not just global)
- A/B testing framework for competing threshold strategies
