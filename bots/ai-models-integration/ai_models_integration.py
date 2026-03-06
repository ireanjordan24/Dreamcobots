# AI Models Integration Bot
# Main orchestrator that integrates all major AI model categories:
#   - NLP Models (OpenAI GPT-4, Google PaLM 2, Anthropic Claude, Meta LLaMA, HuggingFace)
#   - Computer Vision Models (GPT-4 Vision, Google Vision, AWS Rekognition, Meta DINO/SAM, Azure CV)
#   - Generative AI Models (DALL-E 3, Stable Diffusion, Google Gemini, Midjourney, Runway ML)
#   - Data Analytics AI (Google Vertex AI, AWS SageMaker, Azure ML, Databricks, IBM Watson Studio)
#
# Follow the same structure as the Government Contract & Grant Bot for consistency.

import sys
import os

# Allow imports from subdirectories when running directly
sys.path.insert(0, os.path.dirname(__file__))

from nlp.nlp_models_bot import NLPModelsBot
from computer_vision.cv_models_bot import ComputerVisionModelsBot
from generative_ai.generative_ai_bot import GenerativeAIModelsBot
from data_analytics.data_analytics_bot import DataAnalyticsModelsBot


class AIModelsIntegrationBot:
    """
    Central orchestrator for all major AI model integrations in the Dreamcobots framework.

    This bot coordinates NLP, Computer Vision, Generative AI, and Data Analytics models
    in a modular, scalable manner. Each sub-bot can be used independently or together
    through this unified interface.

    Architecture:
        AIModelsIntegrationBot
        ├── NLPModelsBot            (nlp/nlp_models_bot.py)
        ├── ComputerVisionModelsBot (computer_vision/cv_models_bot.py)
        ├── GenerativeAIModelsBot   (generative_ai/generative_ai_bot.py)
        └── DataAnalyticsModelsBot  (data_analytics/data_analytics_bot.py)

    Configuration:
        Set API keys in bots/ai-models-integration/config.json before running.
        See README.md for detailed setup instructions.
    """

    def __init__(self, config=None):
        self.config = config or {}
        self.nlp_bot = NLPModelsBot(config=self.config.get("nlp", {}))
        self.cv_bot = ComputerVisionModelsBot(config=self.config.get("computer_vision", {}))
        self.generative_bot = GenerativeAIModelsBot(config=self.config.get("generative_ai", {}))
        self.analytics_bot = DataAnalyticsModelsBot(config=self.config.get("data_analytics", {}))

    def start(self):
        print("=" * 60)
        print("AI Models Integration Bot is starting...")
        print("Integrating: NLP | Computer Vision | Generative AI | Data Analytics")
        print("=" * 60)

    def process_nlp(self, prompt=None, model=None, task="chat"):
        """
        Run an NLP task using the specified model.

        Args:
            prompt (str): Text input for the NLP model.
            model (str): Model name from NLPModelsBot.SUPPORTED_MODELS.
                         If None, runs the full NLP demo.
            task (str): Task type for the selected model.

        Returns:
            str: Model response.

        Sample Usage:
            bot.process_nlp("Summarize the quarterly earnings report.",
                            model="openai-gpt4", task="summarize")
        """
        print("\n--- NLP Processing ---")
        if model and prompt:
            self.nlp_bot.select_model(model)
            dispatch = {
                "openai-gpt4": lambda: self.nlp_bot.run_openai_gpt4(prompt, task=task),
                "google-palm2": lambda: self.nlp_bot.run_google_palm2(prompt, task=task),
                "anthropic-claude": lambda: self.nlp_bot.run_anthropic_claude(prompt),
                "meta-llama": lambda: self.nlp_bot.run_meta_llama(prompt),
                "huggingface-transformers": lambda: self.nlp_bot.run_huggingface(prompt),
            }
            fn = dispatch.get(model)
            return fn() if fn else self.nlp_bot.run()
        return self.nlp_bot.run()

    def process_computer_vision(self, image_url=None, model=None, task=None):
        """
        Run a computer vision task using the specified model.

        Args:
            image_url (str): URL or path to the image.
            model (str): Model name from ComputerVisionModelsBot.SUPPORTED_MODELS.
                         If None, runs the full CV demo.
            task (str): Task type or feature list for the selected model.

        Returns:
            str: Model response.

        Sample Usage:
            bot.process_computer_vision("https://example.com/product.jpg",
                                        model="google-cloud-vision",
                                        task="LABEL_DETECTION")
        """
        print("\n--- Computer Vision Processing ---")
        if model and image_url:
            self.cv_bot.select_model(model)
            dispatch = {
                "openai-gpt4-vision": lambda: self.cv_bot.run_openai_gpt4_vision(
                    image_url, task or "Describe this image."
                ),
                "google-cloud-vision": lambda: self.cv_bot.run_google_cloud_vision(
                    image_url, features=[task] if task else None
                ),
                "aws-rekognition": lambda: self.cv_bot.run_aws_rekognition(
                    image_url, analysis_type=task or "detect-labels"
                ),
                "meta-dino-sam": lambda: self.cv_bot.run_meta_dino_sam(
                    image_url, task=task or "segment"
                ),
                "azure-computer-vision": lambda: self.cv_bot.run_azure_computer_vision(
                    image_url, visual_features=[task] if task else None
                ),
            }
            fn = dispatch.get(model)
            return fn() if fn else self.cv_bot.run()
        return self.cv_bot.run()

    def process_generative_ai(self, prompt=None, model=None, **kwargs):
        """
        Run a generative AI task using the specified model.

        Args:
            prompt (str): Text prompt for generation.
            model (str): Model name from GenerativeAIModelsBot.SUPPORTED_MODELS.
                         If None, runs the full generative AI demo.
            **kwargs: Additional model-specific parameters (size, quality, steps, etc.).

        Returns:
            str: Generated content URL or response.

        Sample Usage:
            bot.process_generative_ai(
                "A futuristic Dreamcobot on Mars",
                model="openai-dalle3", size="1792x1024", quality="hd"
            )
        """
        print("\n--- Generative AI Processing ---")
        if model and prompt:
            self.generative_bot.select_model(model)
            dispatch = {
                "openai-dalle3": lambda: self.generative_bot.run_openai_dalle3(
                    prompt, **{k: v for k, v in kwargs.items() if k in ("size", "quality")}
                ),
                "stability-ai-stable-diffusion": lambda: self.generative_bot.run_stable_diffusion(
                    prompt, **{k: v for k, v in kwargs.items()
                               if k in ("negative_prompt", "steps", "cfg_scale", "engine")}
                ),
                "google-gemini": lambda: self.generative_bot.run_google_gemini(
                    prompt, **{k: v for k, v in kwargs.items()
                               if k in ("modality", "image_url", "model")}
                ),
                "midjourney": lambda: self.generative_bot.run_midjourney(
                    prompt, **{k: v for k, v in kwargs.items()
                               if k in ("aspect_ratio", "version")}
                ),
                "runwayml": lambda: self.generative_bot.run_runwayml(
                    prompt, **{k: v for k, v in kwargs.items()
                               if k in ("mode", "duration_seconds")}
                ),
            }
            fn = dispatch.get(model)
            return fn() if fn else self.generative_bot.run()
        return self.generative_bot.run()

    def process_data_analytics(self, platform=None, **kwargs):
        """
        Run a data analytics task on the specified platform.

        Args:
            platform (str): Platform name from DataAnalyticsModelsBot.SUPPORTED_PLATFORMS.
                            If None, runs the full analytics demo.
            **kwargs: Platform-specific parameters (dataset_uri, target_column, etc.).

        Returns:
            str: Job or run ID.

        Sample Usage:
            bot.process_data_analytics(
                platform="aws-sagemaker",
                s3_data_uri="s3://my-bucket/train/",
                algorithm="xgboost",
                job_name="dreamcobots-revenue-model"
            )
        """
        print("\n--- Data Analytics Processing ---")
        if platform:
            self.analytics_bot.select_platform(platform)
            dispatch = {
                "google-vertex-ai": lambda: self.analytics_bot.run_google_vertex_automl(**kwargs),
                "aws-sagemaker": lambda: self.analytics_bot.run_aws_sagemaker(**kwargs),
                "azure-ml": lambda: self.analytics_bot.run_azure_ml(**kwargs),
                "databricks": lambda: self.analytics_bot.run_databricks(**kwargs),
                "ibm-watson-studio": lambda: self.analytics_bot.run_ibm_watson_studio(**kwargs),
            }
            fn = dispatch.get(platform)
            return fn() if fn else self.analytics_bot.run()
        return self.analytics_bot.run()

    def run(self):
        self.start()
        self.process_nlp()
        self.process_computer_vision()
        self.process_generative_ai()
        self.process_data_analytics()
        print("\n" + "=" * 60)
        print("AI Models Integration Bot finished successfully.")
        print("=" * 60)


# If this module is run directly, start the bot
if __name__ == "__main__":
    bot = AIModelsIntegrationBot()
    bot.run()
