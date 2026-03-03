# DataForge AI Bot — Documentation

## Overview

DataForge is the data-intelligence engine at the heart of DreamCobots. It automatically
collects structured data from all other bots in the ecosystem, generates synthetic
training datasets, applies regulatory compliance checks, and publishes curated datasets
to leading AI/ML marketplaces (Hugging Face, Kaggle, AWS Data Exchange) and a built-in
user marketplace.

---

## Architecture (text diagram)

```
┌─────────────────────────────────────────────────────────┐
│                    DreamCobots Platform                  │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │FinanceBot│  │ HustleBot│  │ LegalBot │  │  ...   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘  │
│       └──────────────┴─────────────┴─────────────┘       │
│                            │                              │
│                    ┌───────▼────────┐                     │
│                    │  DataForge Bot │                     │
│                    │  ┌──────────┐  │                     │
│                    │  │ Datasets │  │                     │
│                    │  │Generator │  │                     │
│                    │  └────┬─────┘  │                     │
│                    │  ┌────▼──────┐ │                     │
│                    │  │Compliance │ │                     │
│                    │  │  Manager  │ │                     │
│                    │  └────┬──────┘ │                     │
│                    │  ┌────▼──────┐ │                     │
│                    │  │Marketplace│ │                     │
│                    │  │Publishers │ │                     │
│                    │  └───────────┘ │                     │
│                    └────────────────┘                     │
└─────────────────────────────────────────────────────────┘
         │              │              │
   HuggingFace       Kaggle       AWS / Direct
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip dependencies installed: `pip install -r requirements.txt`
- API keys in `.env` (copy `.env.example`)

### Run DataForge standalone

```python
from bots.dataforge.dataforge_bot import DataForgeBot

bot = DataForgeBot()
bot.run()
```

### Generate a dataset

```python
from bots.dataforge.dataset_generators.behavioral_dataset import BehavioralDatasetGenerator

gen = BehavioralDatasetGenerator()
dataset = gen.generate(num_samples=1000)
print(f"Generated {len(dataset)} records")
```

### Publish to Hugging Face

```python
from bots.dataforge.marketplace import HuggingFacePublisher

pub = HuggingFacePublisher(token="hf_...", organization="my-org")
result = pub.publish("my-dataset", dataset)
print(result)
```

---

## API Reference Summary

| Class | Module | Description |
|-------|--------|-------------|
| `DataForgeBot` | `bots.dataforge.dataforge_bot` | Main orchestrating bot |
| `ComplianceManager` | `bots.dataforge.compliance` | GDPR/CCPA/HIPAA validation |
| `HuggingFacePublisher` | `bots.dataforge.marketplace` | Publish to Hugging Face Hub |
| `KagglePublisher` | `bots.dataforge.marketplace` | Publish to Kaggle |
| `AWSPublisher` | `bots.dataforge.marketplace` | Publish to AWS Data Exchange |
| `DirectAPISeller` | `bots.dataforge.marketplace` | Sell via direct API |
| `UserMarketplace` | `bots.dataforge.user_marketplace` | User-facing marketplace |
| `SalesChannelManager` | `bots.dataforge.sales_channels` | Multi-channel sales routing |
| `BehavioralDatasetGenerator` | `bots.dataforge.dataset_generators.behavioral_dataset` | Behavioral data |
| `FacialDatasetGenerator` | `bots.dataforge.dataset_generators.facial_dataset` | Facial/image data |
| `ItemDatasetGenerator` | `bots.dataforge.dataset_generators.item_dataset` | Item/product data |

See [API_GUIDE.md](API_GUIDE.md) for full integration examples.
