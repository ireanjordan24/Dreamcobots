# DreamCObots Repository

Welcome to the DreamCObots project! This repository outlines our groundbreaking mission to develop and deploy 3000 collaborative robots (cobots) designed for transforming industries worldwide. Explore our documentation, system details, and user guides to understand every aspect of this ambitious endeavor.

---
## Installation Instructions
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/ireanjordan24/Dreamcobots.git
   ```
2. Navigate to the directory:
   ```bash
   cd Dreamcobots
   ```
3. Install dependencies (if any bot scripts depend on a specific package manager, such as `pip` for Python):
   ```bash
   pip install -r requirements.txt
   ```

---
## Deployment Steps
To deploy bots or static content:
1. Push changes to the `deployment-setup` branch.
2. Enable **GitHub Pages** in repository settings for frontend hosting.
3. Add and customize workflows to automate bot tasks (see GitHub Actions).

---
## AI Model Editions — Free & Paid Tiers

All AI model integrations support three subscription tiers:

| Tier       | Price/month | Requests/month | Models | Support            |
|------------|-------------|----------------|--------|--------------------|
| **Free**   | $0.00       | 500            | 9      | Community          |
| **Pro**    | $49.00      | 10,000         | 18     | Email (48 h SLA)   |
| **Enterprise** | $299.00 | Unlimited      | 20     | Dedicated 24/7     |

### Free Edition
- GPT-3.5 Turbo, BERT Base, T5 Small *(NLP)*
- YOLOv5, ResNet-50 *(Computer Vision)*
- DALL-E 2, Stable Diffusion 1.4 *(Generative AI)*
- Prophet, XGBoost *(Data Analytics)*

### Pro Edition ($49/month)
Everything in Free, **plus**:
- GPT-4, BERT Large, T5-XL *(NLP)*
- YOLOv8, ResNet-152 *(Computer Vision)*
- DALL-E 3, Stable Diffusion XL *(Generative AI)*
- AutoML, LightGBM *(Data Analytics)*
- Batch processing, fine-tuning, analytics dashboard

### Enterprise Edition ($299/month)
Everything in Pro, **plus**:
- CLIP, GPT-4 Vision *(multimodal)*
- Custom models, SLA guarantee, dedicated support, white-label

To switch tiers, set `DREAMCOBOTS_TIER=FREE|PRO|ENTERPRISE` in your environment
or pass `tier=Tier.PRO` when constructing `AIModelsIntegration` / `Chatbot`.

See full documentation in:
- [`bots/ai-models-integration/README.md`](bots/ai-models-integration/README.md)
- [`bots/ai_chatbot/README.md`](bots/ai_chatbot/README.md)

---
## Folder Explanation
### `bots`
- Contains all bot scripts such as the `government-contract-grant-bot`.
- `bots/ai-models-integration/` — tiered AI model integration (free/pro/enterprise).
- `bots/ai_chatbot/` — tier-aware AI chatbot built on top of the model integration.
- `config.json` needs to be configured with required API keys and bot settings.

### `examples`
- Contains example use cases for different bots like `Referral Bot` and `Hustle Bot`.

---
## How to Run Bots Locally
1. Navigate to the bot directory. For example:
   ```bash
   cd bots/government-contract-grant-bot
   ```
2. Run the bot script. For example:
   ```bash
   python bot.py
   ```
3. Make sure necessary APIs and configurations are set before running.

---
## GitHub Pages Instructions
1. Navigate to **Settings > Pages**.
2. Select the `deployment-setup` branch and root directory as the publishing source.
3. Save your settings to host the frontend.

---