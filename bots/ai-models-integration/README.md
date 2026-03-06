# AI Models Integration Bot

A modular, scalable integration of the world's major AI models into the Dreamcobots framework.
Follows the same structure as the `government-contract-grant-bot` for consistency.

---

## Supported AI Model Categories

| Category | Models |
|---|---|
| **NLP** | OpenAI GPT-4, Google PaLM 2, Anthropic Claude, Meta LLaMA, HuggingFace Transformers |
| **Computer Vision** | OpenAI GPT-4 Vision, Google Cloud Vision, AWS Rekognition, Meta DINO/SAM, Azure Computer Vision |
| **Generative AI** | OpenAI DALL-E 3, Stability AI Stable Diffusion, Google Gemini, Midjourney, Runway ML |
| **Data Analytics** | Google Vertex AI AutoML, AWS SageMaker, Azure Machine Learning, Databricks, IBM Watson Studio |

---

## Directory Structure

```
bots/ai-models-integration/
├── ai_models_integration.py      # Main orchestrator bot
├── config.json                   # API keys and configuration
├── README.md                     # This file
├── nlp/
│   └── nlp_models_bot.py         # NLP models (GPT-4, PaLM 2, Claude, LLaMA, HuggingFace)
├── computer_vision/
│   └── cv_models_bot.py          # CV models (GPT-4 Vision, Google Vision, Rekognition, SAM, Azure)
├── generative_ai/
│   └── generative_ai_bot.py      # Generative models (DALL-E 3, Stable Diffusion, Gemini, Midjourney, Runway)
└── data_analytics/
    └── data_analytics_bot.py     # Analytics platforms (Vertex AI, SageMaker, Azure ML, Databricks, Watson)
```

---

## Installation

1. Navigate to the bot directory:
   ```bash
   cd bots/ai-models-integration
   ```

2. Install dependencies:
   ```bash
   pip install -r ../../requirements.txt
   ```

3. Configure API keys in `config.json`:
   ```json
   {
     "nlp": {
       "OPENAI_API_KEY": "sk-...",
       "ANTHROPIC_API_KEY": "sk-ant-..."
     }
   }
   ```

---

## How to Run

### Run the full integration (all categories):
```bash
python ai_models_integration.py
```

### Run a specific category bot:
```bash
# NLP only
python nlp/nlp_models_bot.py

# Computer Vision only
python computer_vision/cv_models_bot.py

# Generative AI only
python generative_ai/generative_ai_bot.py

# Data Analytics only
python data_analytics/data_analytics_bot.py
```

### Use as a Python module:
```python
import sys
sys.path.insert(0, "bots/ai-models-integration")
from ai_models_integration import AIModelsIntegrationBot

bot = AIModelsIntegrationBot(config={...})

# NLP: Summarize text with OpenAI GPT-4
bot.process_nlp(
    "Summarize the quarterly earnings report.",
    model="openai-gpt4",
    task="summarize"
)

# Computer Vision: Detect objects in an image
bot.process_computer_vision(
    "https://example.com/factory-floor.jpg",
    model="aws-rekognition",
    task="detect-labels"
)

# Generative AI: Generate a product image
bot.process_generative_ai(
    "A futuristic Dreamcobot assembling electronics",
    model="openai-dalle3",
    size="1792x1024",
    quality="hd"
)

# Data Analytics: Train a model on SageMaker
bot.process_data_analytics(
    platform="aws-sagemaker",
    s3_data_uri="s3://my-bucket/train/",
    algorithm="xgboost",
    job_name="dreamcobots-revenue-model"
)
```

---

## Sample Usage Scenarios

### Scenario 1: Customer Support Automation (NLP)
**Goal**: Automatically classify and respond to customer support tickets.

```python
from nlp.nlp_models_bot import NLPModelsBot

bot = NLPModelsBot()
# Classify ticket severity using HuggingFace
result = bot.run_huggingface(
    "My order has not arrived after 3 weeks and I'm extremely frustrated.",
    pipeline="text-classification",
    model_id="distilbert-base-uncased-finetuned-sst-2-english"
)
# Draft a response using Claude
response = bot.run_anthropic_claude(
    "Write a professional, empathetic response to a late delivery complaint.",
    max_tokens=512
)
```

### Scenario 2: Product Quality Inspection (Computer Vision)
**Goal**: Automatically detect defects on a manufacturing production line.

```python
from computer_vision.cv_models_bot import ComputerVisionModelsBot

bot = ComputerVisionModelsBot()
# Detect anomalies with AWS Rekognition
defects = bot.run_aws_rekognition(
    "s3://dreamcobots-factory/product_images/item_4821.jpg",
    analysis_type="detect-labels"
)
# Segment the defective region with Meta SAM
region = bot.run_meta_dino_sam(
    "s3://dreamcobots-factory/product_images/item_4821.jpg",
    task="segment"
)
```

### Scenario 3: Marketing Content Generation (Generative AI)
**Goal**: Generate product images and video ads for a new robot launch.

```python
from generative_ai.generative_ai_bot import GenerativeAIModelsBot

bot = GenerativeAIModelsBot()
# Generate hero image
image_url = bot.run_openai_dalle3(
    "A sleek silver Dreamcobot standing in a modern office, professional photography",
    size="1792x1024",
    quality="hd"
)
# Generate a 10-second product video
video_url = bot.run_runwayml(
    "A Dreamcobot navigating a warehouse, picking and sorting packages efficiently.",
    mode="text-to-video",
    duration_seconds=10
)
```

### Scenario 4: Revenue Forecasting (Data Analytics)
**Goal**: Predict quarterly revenue using historical sales data.

```python
from data_analytics.data_analytics_bot import DataAnalyticsModelsBot

bot = DataAnalyticsModelsBot()
# Train an AutoML forecasting model on Vertex AI
job_id = bot.run_google_vertex_automl(
    dataset_uri="gs://dreamcobots-data/revenue_history.csv",
    target_column="quarterly_revenue",
    task_type="forecasting",
    budget_hours=3  # Increase for larger datasets; 8–24 hours is typical for production
)
# Explore results with Databricks
run_id = bot.run_databricks(
    notebook_path="/Shared/dreamcobots/revenue_forecast_analysis",
    parameters={"model_id": job_id, "quarters_ahead": 4},
    job_name="dreamcobots-q4-forecast"
)
```

---

## API Integration Points

### NLP Models

| Model | API Endpoint | Auth Header |
|---|---|---|
| OpenAI GPT-4 | `POST https://api.openai.com/v1/chat/completions` | `Authorization: Bearer <OPENAI_API_KEY>` |
| Google PaLM 2 | `POST https://us-central1-aiplatform.googleapis.com/v1/...` | `Authorization: Bearer <GOOGLE_API_KEY>` |
| Anthropic Claude | `POST https://api.anthropic.com/v1/messages` | `x-api-key: <ANTHROPIC_API_KEY>` |
| Meta LLaMA | `POST <META_LLAMA_ENDPOINT>/generate` | Custom bearer token |
| HuggingFace | `POST https://api-inference.huggingface.co/models/<id>` | `Authorization: Bearer <HUGGINGFACE_TOKEN>` |

### Computer Vision Models

| Model | API Endpoint | Auth Header |
|---|---|---|
| OpenAI GPT-4 Vision | `POST https://api.openai.com/v1/chat/completions` | `Authorization: Bearer <OPENAI_API_KEY>` |
| Google Cloud Vision | `POST https://vision.googleapis.com/v1/images:annotate` | `Authorization: Bearer <GOOGLE_CLOUD_API_KEY>` |
| AWS Rekognition | `POST https://rekognition.<region>.amazonaws.com/` | AWS Signature V4 |
| Meta DINO/SAM | `POST <META_SAM_ENDPOINT>/predict` | Custom bearer token |
| Azure Computer Vision | `POST <AZURE_CV_ENDPOINT>/vision/v3.2/analyze` | `Ocp-Apim-Subscription-Key: <AZURE_CV_KEY>` |

### Generative AI Models

| Model | API Endpoint | Auth Header |
|---|---|---|
| OpenAI DALL-E 3 | `POST https://api.openai.com/v1/images/generations` | `Authorization: Bearer <OPENAI_API_KEY>` |
| Stability AI | `POST https://api.stability.ai/v1/generation/<engine>/text-to-image` | `Authorization: Bearer <STABILITY_API_KEY>` |
| Google Gemini | `POST https://generativelanguage.googleapis.com/v1beta/models/<model>:generateContent` | `x-goog-api-key: <GOOGLE_API_KEY>` |
| Midjourney | `POST https://api.midjourney.com/v1/imagine` | `Authorization: Bearer <MIDJOURNEY_API_KEY>` |
| Runway ML | `POST https://api.runwayml.com/v1/generate` | `Authorization: Bearer <RUNWAYML_API_KEY>` |

### Data Analytics Platforms

| Platform | API Endpoint | Auth Header |
|---|---|---|
| Google Vertex AI | `POST https://us-central1-aiplatform.googleapis.com/v1/...` | `Authorization: Bearer <GOOGLE_CLOUD_TOKEN>` |
| AWS SageMaker | `POST https://sagemaker.<region>.amazonaws.com/CreateTrainingJob` | AWS Signature V4 |
| Azure ML | `POST https://management.azure.com/subscriptions/...` | `Authorization: Bearer <AZURE_TOKEN>` |
| Databricks | `POST https://<DATABRICKS_HOST>/api/2.1/jobs/runs/submit` | `Authorization: Bearer <DATABRICKS_TOKEN>` |
| IBM Watson Studio | `POST https://us-south.ml.cloud.ibm.com/ml/v4/trainings` | `Authorization: Bearer <IBM_WATSON_APIKEY>` |

---

## Scalability and Deployment

- **Modular**: Each category bot (`NLPModelsBot`, `ComputerVisionModelsBot`, etc.) can be
  deployed independently or together via the `AIModelsIntegrationBot` orchestrator.
- **Scalable**: Add new models by extending the `SUPPORTED_MODELS` list and adding a
  corresponding method following the existing pattern.
- **Configurable**: All API keys are externalized to `config.json` — never hard-code secrets.
- **Framework-compatible**: Each bot follows the same `__init__ / start / run` pattern as the
  `GovernmentContractGrantBot` for seamless integration into the Dreamcobots ecosystem.

---

## Adding a New Model

1. Choose the appropriate category directory (`nlp/`, `computer_vision/`, etc.).
2. Add the model name to `SUPPORTED_MODELS` in the corresponding bot class.
3. Add a new method following the docstring pattern:
   ```python
   def run_my_new_model(self, prompt, **kwargs):
       """
       Brief description.

       Args: ...
       Returns: ...
       Sample Usage: ...
       API Endpoint: ...
       """
       print(f"[My New Model] Prompt: {prompt}")
       return f"[My New Model Response] ..."
   ```
4. Add the API key to `config.json`.
5. Call the new method in the `run()` demo method.
