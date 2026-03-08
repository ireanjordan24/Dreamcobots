# Dreamcobots Mining Bot

An adaptive, AI-enhanced cryptocurrency mining bot for the Dreamcobots platform.

---

## Features

### Core Enhancements
| Feature | FREE | PRO | ENTERPRISE |
|---------|------|-----|------------|
| Pool mining | ✓ | ✓ | ✓ |
| Solo mining | — | ✓ | ✓ |
| Merged mining | — | ✓ | ✓ |
| Adaptive strategy switching | — | ✓ | ✓ |
| Basic profitability analytics | ✓ | ✓ | ✓ |
| Advanced analytics (energy + ROI) | — | ✓ | ✓ |
| Full analytics (trends + efficiency) | — | — | ✓ |
| Smart alerts (downtime, anomalies) | — | ✓ | ✓ |
| AI-driven optimisation | — | — | ✓ |
| Reinforcement learning fine-tuning | — | — | ✓ |

### Additional Functionalities
| Feature | FREE | PRO | ENTERPRISE |
|---------|------|-----|------------|
| Fraud detection | — | ✓ | ✓ |
| Honeypot detection | — | ✓ | ✓ |
| Contract verification | — | ✓ | ✓ |
| Multi-exchange execution | — | ✓ | ✓ |
| DEX routing | — | — | ✓ |
| Hardware wallet support | — | — | ✓ |
| Strategy backtesting | — | ✓ | ✓ |

---

## Pricing

| Tier | Price | Monitored Coins | Analytics |
|------|-------|-----------------|-----------|
| Free | $0/mo | 2 | Basic |
| Pro | $49/mo | 10 | Advanced |
| Enterprise | $299/mo | Unlimited | Full |

---

## Quick Start

```python
from bots.mining_bot.mining_bot import MiningBot
from bots.mining_bot.tiers import Tier
from bots.mining_bot.strategy import CoinProfile

# Create a PRO bot
bot = MiningBot(
    tier=Tier.PRO,
    hashrate_ths=100.0,
    power_kw=3.5,
    electricity_rate=0.06,
)

# Define coins to mine
btc = CoinProfile(
    symbol="BTC",
    algorithm="SHA-256",
    network_difficulty=5e13,
    block_reward=3.125,
    coin_price_usd=65000.0,
    network_hashrate=5e20,
    pool_fee_pct=1.0,
)

# Get adaptive strategy recommendation
rec = bot.recommend_strategy([btc])
print(rec["reasoning"])

# Check fraud before mining
result = bot.check_pool("stratum+tcp://pool.example.com:3333")
print(result.passed, result.risk_level)

# Compare exchanges for coin conversion
report = bot.compare_exchanges("BTC", 0.01)
print(f"Best exchange: {report['best_exchange']}")

# Review analytics
bot.describe_tier()
```

---

## Module Structure

```
bots/mining_bot/
├── mining_bot.py        # Main MiningBot class
├── tiers.py             # Tier config (FREE / PRO / ENTERPRISE)
├── strategy.py          # StrategyEngine + AdaptiveStrategyEngine
├── analytics.py         # ProfitabilityAnalytics
├── monitor.py           # MiningMonitor (smart alerts)
├── fraud_detection.py   # FraudDetector (honeypot + contract checks)
├── exchange.py          # MultiExchangeRouter
├── __init__.py
└── README.md
```

---

## Running Tests

```bash
python -m pytest tests/test_mining_bot.py -v
```

---

## Security Notes

- Wallet credentials should be stored in environment variables, **never** hard-coded.
- Hardware wallet support (ENTERPRISE) integrates via standard HID interfaces.
- All contract addresses are verified locally; no secrets are transmitted externally.
- Pool URLs are validated against a known-scam registry before connections are made.
