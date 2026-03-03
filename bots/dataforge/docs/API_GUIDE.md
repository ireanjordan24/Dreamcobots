# DataForge API Integration Guide

## Overview

DataForge connects to 100+ external APIs across AI/ML platforms, data marketplaces,
cloud providers, communication services, and financial rails. This guide covers how to
use the API manager and lists all supported integrations.

---

## Using the API Manager

```python
from bots.dataforge.apis import APIManager   # illustrative import

mgr = APIManager()

# Authenticate
mgr.authenticate("huggingface", token="hf_...")
mgr.authenticate("kaggle", username="alice", key="abc123")

# Publish dataset
result = mgr.publish("huggingface", dataset_name="my-dataset", data=records)
print(result)
```

---

## Supported APIs by Category

### AI / ML Platforms (25+)
| API | Purpose |
|-----|---------|
| Hugging Face Hub | Upload & download model/dataset cards |
| Kaggle Datasets | Host public/private competitions datasets |
| OpenAI | GPT-4 fine-tuning data upload |
| Anthropic Claude | RLHF dataset submission |
| Google Vertex AI | AutoML training data |
| AWS SageMaker | Training job data input |
| Azure ML | Dataset registration |
| Cohere | Fine-tuning corpus upload |
| AI21 Labs | Jurassic fine-tune data |
| Replicate | Model deployment data |
| Together AI | Dataset submission |
| Mistral AI | Fine-tuning data |
| Stability AI | Image training sets |
| Midjourney | Style dataset |
| Runway ML | Video training data |
| ElevenLabs | Voice dataset |
| AssemblyAI | Audio transcription corpus |
| Whisper | Speech recognition data |
| DALL·E | Image annotation data |
| LangChain Hub | Chain prompt datasets |
| LlamaIndex | RAG corpus |
| Pinecone | Vector embedding data |
| Weaviate | Knowledge graph data |
| Qdrant | Dense vector sets |
| Chroma | Embedding collections |

### Data Marketplaces (20+)
| API | Purpose |
|-----|---------|
| AWS Data Exchange | Premium dataset listing |
| Snowflake Marketplace | SQL-queryable datasets |
| Databricks Delta Sharing | Open data sharing |
| Google Cloud Analytics Hub | BigQuery dataset sharing |
| Azure Data Marketplace | Azure-hosted datasets |
| Narrative.io | Data collaboration |
| Lotame | Audience data |
| Oracle Data Cloud | Third-party data |
| Nielsen | Consumer data |
| Acxiom | Identity data |
| LiveRamp | Data connectivity |
| Dun & Bradstreet | B2B data |
| Refinitiv (LSEG) | Financial data |
| FactSet | Investment research data |
| Bloomberg Terminal API | Market data |
| Quandl / Nasdaq Data Link | Financial time series |
| World Bank Open Data | Economic indicators |
| UN Comtrade | Trade statistics |
| Eurostat | European statistics |
| Data.gov | US government data |

### Cloud Storage & Infrastructure (15+)
| API | Purpose |
|-----|---------|
| AWS S3 | Object storage |
| AWS Glacier | Archival storage |
| Google Cloud Storage | Bucket storage |
| Azure Blob Storage | Binary large object storage |
| Cloudflare R2 | S3-compatible edge storage |
| Backblaze B2 | Cost-efficient storage |
| DigitalOcean Spaces | Developer object storage |
| Linode Object Storage | Akamai cloud storage |
| MinIO | Self-hosted S3 |
| Wasabi | Hot cloud storage |
| Storj | Decentralised storage |
| IPFS / Filecoin | Web3 storage |
| Arweave | Permanent storage |
| Sia | Blockchain storage |
| MongoDB Atlas | Document database |

### Communication & Notification (15+)
| API | Purpose |
|-----|---------|
| Twilio SMS | SMS notifications |
| Twilio Voice | Voice calls |
| SendGrid | Transactional email |
| Mailgun | Email API |
| Postmark | Developer email |
| AWS SES | Bulk email |
| Slack | Team notifications |
| Discord | Community alerts |
| Telegram Bot | Messaging bot |
| WhatsApp Business | Customer messaging |
| PagerDuty | Incident alerts |
| OpsGenie | On-call management |
| Pushover | Mobile push |
| Vonage (Nexmo) | Programmable communications |
| MessageBird | Omnichannel messaging |

### Payments & Financial (15+)
| API | Purpose |
|-----|---------|
| Stripe | Card payments |
| PayPal | Wallet & card payments |
| Square | POS & online payments |
| Braintree | Gateway & vaulting |
| Adyen | Enterprise payments |
| Razorpay | India market payments |
| Plaid | Bank account linking |
| Dwolla | ACH transfers |
| Wise (TransferWise) | International transfers |
| Coinbase Commerce | Crypto payments |
| BitPay | Bitcoin payments |
| Binance Pay | Crypto checkout |
| OpenNode | Lightning Network |
| Chargebee | Subscription billing |
| Recurly | Revenue management |

### Other / Utilities (10+)
| API | Purpose |
|-----|---------|
| GitHub | Source code integration |
| GitLab | CI/CD data |
| Jira | Project tracking |
| Notion | Knowledge base |
| Airtable | Spreadsheet-DB hybrid |
| Zapier | Workflow automation |
| Make (Integromat) | No-code automation |
| Salesforce | CRM data |
| HubSpot | Marketing data |
| Segment | Customer data platform |

---

## Code Examples

### Publish to Kaggle

```python
from bots.dataforge.marketplace import KagglePublisher

pub = KagglePublisher()
result = pub.publish("behavioral-v1", records)
print(result["status"])  # "published"
```

### Direct API sale

```python
from bots.dataforge.marketplace import DirectAPISeller

seller = DirectAPISeller(api_key="sk-...", endpoint="https://api.example.com/datasets")
result = seller.publish("sentiment-corpus", records)
```

### Compliance check before publishing

```python
from bots.dataforge.compliance import ComplianceManager

cm = ComplianceManager()
assert cm.validate_gdpr_compliance({"consent_given": True, "purpose_of_processing": "ml"})
assert cm.validate_ccpa_compliance({"ccpa_notice_provided": True})
```
