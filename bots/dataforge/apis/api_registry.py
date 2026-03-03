"""
bots/dataforge/apis/api_registry.py

APIRegistry – maintains the registry of all API connector configurations
for the DataForge module.
"""

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Pre-populated configuration for 100 representative API entries.
# Each entry has: name, category, base_url, auth_type, description.
_BUILTIN_APIS: list[dict[str, Any]] = [
    # AI / ML
    {"name": "openai", "category": "ai_ml", "base_url": "https://api.openai.com/v1", "auth_type": "bearer", "description": "OpenAI GPT models and embeddings"},
    {"name": "anthropic", "category": "ai_ml", "base_url": "https://api.anthropic.com/v1", "auth_type": "x-api-key", "description": "Anthropic Claude models"},
    {"name": "huggingface", "category": "ai_ml", "base_url": "https://api-inference.huggingface.co", "auth_type": "bearer", "description": "HuggingFace model inference"},
    {"name": "cohere", "category": "ai_ml", "base_url": "https://api.cohere.ai/v1", "auth_type": "bearer", "description": "Cohere NLP APIs"},
    {"name": "mistral", "category": "ai_ml", "base_url": "https://api.mistral.ai/v1", "auth_type": "bearer", "description": "Mistral AI models"},
    {"name": "stability_ai", "category": "ai_ml", "base_url": "https://api.stability.ai/v1", "auth_type": "bearer", "description": "Stability AI image generation"},
    {"name": "replicate", "category": "ai_ml", "base_url": "https://api.replicate.com/v1", "auth_type": "bearer", "description": "Replicate model hosting"},
    {"name": "together_ai", "category": "ai_ml", "base_url": "https://api.together.xyz/v1", "auth_type": "bearer", "description": "Together AI LLM hosting"},
    {"name": "groq", "category": "ai_ml", "base_url": "https://api.groq.com/openai/v1", "auth_type": "bearer", "description": "Groq LLM inference"},
    {"name": "perplexity", "category": "ai_ml", "base_url": "https://api.perplexity.ai", "auth_type": "bearer", "description": "Perplexity AI search"},
    # Data / Analytics
    {"name": "kaggle", "category": "data", "base_url": "https://www.kaggle.com/api/v1", "auth_type": "basic", "description": "Kaggle datasets and competitions"},
    {"name": "aws_s3", "category": "cloud", "base_url": "https://s3.amazonaws.com", "auth_type": "aws_sig_v4", "description": "AWS S3 object storage"},
    {"name": "aws_data_exchange", "category": "data", "base_url": "https://dataexchange.us-east-1.amazonaws.com", "auth_type": "aws_sig_v4", "description": "AWS Data Exchange marketplace"},
    {"name": "google_bigquery", "category": "data", "base_url": "https://bigquery.googleapis.com/bigquery/v2", "auth_type": "oauth2", "description": "Google BigQuery analytics"},
    {"name": "snowflake", "category": "data", "base_url": "https://account.snowflakecomputing.com", "auth_type": "jwt", "description": "Snowflake data cloud"},
    {"name": "databricks", "category": "data", "base_url": "https://databricks.example.com/api/2.0", "auth_type": "bearer", "description": "Databricks unified analytics"},
    {"name": "elastic", "category": "data", "base_url": "https://api.elastic.co", "auth_type": "api_key", "description": "Elasticsearch / Elastic Cloud"},
    {"name": "mongodb_atlas", "category": "data", "base_url": "https://cloud.mongodb.com/api/atlas/v2", "auth_type": "digest", "description": "MongoDB Atlas cloud database"},
    {"name": "postgres_supabase", "category": "data", "base_url": "https://api.supabase.co", "auth_type": "api_key", "description": "Supabase Postgres hosting"},
    {"name": "pinecone", "category": "data", "base_url": "https://api.pinecone.io", "auth_type": "api_key", "description": "Pinecone vector database"},
    # Payments
    {"name": "stripe", "category": "payments", "base_url": "https://api.stripe.com/v1", "auth_type": "bearer", "description": "Stripe payment processing"},
    {"name": "paypal", "category": "payments", "base_url": "https://api.paypal.com/v2", "auth_type": "oauth2", "description": "PayPal payment platform"},
    {"name": "square", "category": "payments", "base_url": "https://connect.squareup.com/v2", "auth_type": "bearer", "description": "Square point-of-sale"},
    {"name": "braintree", "category": "payments", "base_url": "https://api.braintreegateway.com", "auth_type": "basic", "description": "Braintree payment gateway"},
    {"name": "adyen", "category": "payments", "base_url": "https://checkout-test.adyen.com/v71", "auth_type": "api_key", "description": "Adyen global payments"},
    # Communications
    {"name": "twilio", "category": "communications", "base_url": "https://api.twilio.com/2010-04-01", "auth_type": "basic", "description": "Twilio SMS and voice"},
    {"name": "sendgrid", "category": "communications", "base_url": "https://api.sendgrid.com/v3", "auth_type": "bearer", "description": "SendGrid transactional email"},
    {"name": "mailchimp", "category": "communications", "base_url": "https://api.mailchimp.com/3.0", "auth_type": "basic", "description": "Mailchimp email marketing"},
    {"name": "vonage", "category": "communications", "base_url": "https://api.nexmo.com", "auth_type": "api_key", "description": "Vonage Communications APIs"},
    {"name": "messagebird", "category": "communications", "base_url": "https://rest.messagebird.com", "auth_type": "api_key", "description": "MessageBird messaging"},
    # CRM / Sales
    {"name": "salesforce", "category": "crm", "base_url": "https://instance.salesforce.com/services/data/v59.0", "auth_type": "oauth2", "description": "Salesforce CRM"},
    {"name": "hubspot", "category": "crm", "base_url": "https://api.hubapi.com", "auth_type": "bearer", "description": "HubSpot CRM and marketing"},
    {"name": "zendesk", "category": "crm", "base_url": "https://subdomain.zendesk.com/api/v2", "auth_type": "basic", "description": "Zendesk customer support"},
    {"name": "pipedrive", "category": "crm", "base_url": "https://api.pipedrive.com/v1", "auth_type": "api_key", "description": "Pipedrive sales CRM"},
    {"name": "freshsales", "category": "crm", "base_url": "https://domain.freshsales.io/api", "auth_type": "api_key", "description": "Freshsales CRM"},
    # Cloud Providers
    {"name": "azure_openai", "category": "cloud", "base_url": "https://resource.openai.azure.com/openai", "auth_type": "api_key", "description": "Azure OpenAI Service"},
    {"name": "gcp_vertex", "category": "cloud", "base_url": "https://us-central1-aiplatform.googleapis.com/v1", "auth_type": "oauth2", "description": "Google Vertex AI"},
    {"name": "aws_bedrock", "category": "cloud", "base_url": "https://bedrock.us-east-1.amazonaws.com", "auth_type": "aws_sig_v4", "description": "AWS Bedrock foundation models"},
    {"name": "cloudflare", "category": "cloud", "base_url": "https://api.cloudflare.com/client/v4", "auth_type": "api_key", "description": "Cloudflare edge platform"},
    {"name": "vercel", "category": "cloud", "base_url": "https://api.vercel.com", "auth_type": "bearer", "description": "Vercel serverless deployment"},
    # Social Media / Data
    {"name": "twitter_x", "category": "social", "base_url": "https://api.twitter.com/2", "auth_type": "oauth2", "description": "Twitter/X API v2"},
    {"name": "reddit", "category": "social", "base_url": "https://oauth.reddit.com/api/v1", "auth_type": "oauth2", "description": "Reddit API"},
    {"name": "linkedin", "category": "social", "base_url": "https://api.linkedin.com/v2", "auth_type": "oauth2", "description": "LinkedIn API"},
    {"name": "youtube_data", "category": "social", "base_url": "https://www.googleapis.com/youtube/v3", "auth_type": "api_key", "description": "YouTube Data API"},
    {"name": "tiktok", "category": "social", "base_url": "https://open-api.tiktok.com/v2", "auth_type": "oauth2", "description": "TikTok for Developers API"},
    # E-Commerce
    {"name": "shopify", "category": "ecommerce", "base_url": "https://store.myshopify.com/admin/api/2024-01", "auth_type": "api_key", "description": "Shopify commerce platform"},
    {"name": "woocommerce", "category": "ecommerce", "base_url": "https://store.example.com/wp-json/wc/v3", "auth_type": "basic", "description": "WooCommerce REST API"},
    {"name": "amazon_mws", "category": "ecommerce", "base_url": "https://sellingpartnerapi-na.amazon.com", "auth_type": "lwa", "description": "Amazon Selling Partner API"},
    {"name": "etsy", "category": "ecommerce", "base_url": "https://openapi.etsy.com/v3", "auth_type": "api_key", "description": "Etsy marketplace API"},
    {"name": "ebay", "category": "ecommerce", "base_url": "https://api.ebay.com/sell/inventory/v1", "auth_type": "oauth2", "description": "eBay Sell APIs"},
    # Maps / Location
    {"name": "google_maps", "category": "location", "base_url": "https://maps.googleapis.com/maps/api", "auth_type": "api_key", "description": "Google Maps Platform"},
    {"name": "mapbox", "category": "location", "base_url": "https://api.mapbox.com", "auth_type": "api_key", "description": "Mapbox mapping and navigation"},
    {"name": "here_maps", "category": "location", "base_url": "https://router.hereapi.com/v8", "auth_type": "api_key", "description": "HERE location services"},
    {"name": "foursquare", "category": "location", "base_url": "https://api.foursquare.com/v3", "auth_type": "api_key", "description": "Foursquare Places API"},
    {"name": "openstreetmap_nominatim", "category": "location", "base_url": "https://nominatim.openstreetmap.org", "auth_type": "none", "description": "OpenStreetMap geocoding"},
    # Weather / Environment
    {"name": "openweathermap", "category": "weather", "base_url": "https://api.openweathermap.org/data/3.0", "auth_type": "api_key", "description": "OpenWeatherMap weather API"},
    {"name": "weatherapi", "category": "weather", "base_url": "https://api.weatherapi.com/v1", "auth_type": "api_key", "description": "WeatherAPI forecast"},
    {"name": "tomorrow_io", "category": "weather", "base_url": "https://api.tomorrow.io/v4", "auth_type": "api_key", "description": "Tomorrow.io climate API"},
    {"name": "noaa", "category": "weather", "base_url": "https://api.weather.gov", "auth_type": "none", "description": "NOAA National Weather Service"},
    {"name": "aqicn", "category": "weather", "base_url": "https://api.waqi.info", "auth_type": "api_key", "description": "World Air Quality Index"},
    # Finance / Market Data
    {"name": "alpha_vantage", "category": "finance", "base_url": "https://www.alphavantage.co/query", "auth_type": "api_key", "description": "Alpha Vantage stock data"},
    {"name": "polygon_io", "category": "finance", "base_url": "https://api.polygon.io/v2", "auth_type": "api_key", "description": "Polygon.io market data"},
    {"name": "coinbase", "category": "finance", "base_url": "https://api.coinbase.com/v2", "auth_type": "api_key", "description": "Coinbase cryptocurrency exchange"},
    {"name": "binance", "category": "finance", "base_url": "https://api.binance.com/api/v3", "auth_type": "api_key", "description": "Binance crypto exchange"},
    {"name": "plaid", "category": "finance", "base_url": "https://production.plaid.com", "auth_type": "api_key", "description": "Plaid banking data"},
    # Health / Medical
    {"name": "fhir_r4", "category": "health", "base_url": "https://server.fire.ly/r4", "auth_type": "oauth2", "description": "HL7 FHIR R4 health data"},
    {"name": "epic_fhir", "category": "health", "base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4", "auth_type": "oauth2", "description": "Epic EHR FHIR API"},
    {"name": "health_gorilla", "category": "health", "base_url": "https://sandbox.healthgorilla.com/fhir/stu3", "auth_type": "oauth2", "description": "Health Gorilla clinical data"},
    {"name": "veeva_vault", "category": "health", "base_url": "https://domain.veevavault.com/api/v24.1", "auth_type": "session", "description": "Veeva Vault life-sciences"},
    {"name": "clinicaltrials_gov", "category": "health", "base_url": "https://clinicaltrials.gov/api/v2", "auth_type": "none", "description": "ClinicalTrials.gov study data"},
    # Identity / Auth
    {"name": "auth0", "category": "identity", "base_url": "https://domain.auth0.com/api/v2", "auth_type": "bearer", "description": "Auth0 identity platform"},
    {"name": "okta", "category": "identity", "base_url": "https://domain.okta.com/api/v1", "auth_type": "ssws", "description": "Okta identity management"},
    {"name": "cognito", "category": "identity", "base_url": "https://cognito-idp.us-east-1.amazonaws.com", "auth_type": "aws_sig_v4", "description": "AWS Cognito user pools"},
    {"name": "firebase_auth", "category": "identity", "base_url": "https://identitytoolkit.googleapis.com/v1", "auth_type": "api_key", "description": "Firebase Authentication"},
    {"name": "microsoft_entra", "category": "identity", "base_url": "https://graph.microsoft.com/v1.0", "auth_type": "oauth2", "description": "Microsoft Entra (Azure AD)"},
    # Developer Tools
    {"name": "github", "category": "devtools", "base_url": "https://api.github.com", "auth_type": "bearer", "description": "GitHub REST API"},
    {"name": "gitlab", "category": "devtools", "base_url": "https://gitlab.com/api/v4", "auth_type": "bearer", "description": "GitLab REST API"},
    {"name": "jira", "category": "devtools", "base_url": "https://domain.atlassian.net/rest/api/3", "auth_type": "basic", "description": "Jira project management"},
    {"name": "pagerduty", "category": "devtools", "base_url": "https://api.pagerduty.com", "auth_type": "api_key", "description": "PagerDuty incident management"},
    {"name": "datadog", "category": "devtools", "base_url": "https://api.datadoghq.com/api/v2", "auth_type": "api_key", "description": "Datadog monitoring"},
    # Media / Content
    {"name": "unsplash", "category": "media", "base_url": "https://api.unsplash.com", "auth_type": "api_key", "description": "Unsplash free photos"},
    {"name": "pexels", "category": "media", "base_url": "https://api.pexels.com/v1", "auth_type": "api_key", "description": "Pexels stock photos"},
    {"name": "spotify", "category": "media", "base_url": "https://api.spotify.com/v1", "auth_type": "oauth2", "description": "Spotify music data"},
    {"name": "soundcloud", "category": "media", "base_url": "https://api.soundcloud.com", "auth_type": "oauth2", "description": "SoundCloud audio streaming"},
    {"name": "cloudinary", "category": "media", "base_url": "https://api.cloudinary.com/v1_1", "auth_type": "basic", "description": "Cloudinary media management"},
    # Search / Knowledge
    {"name": "serp_api", "category": "search", "base_url": "https://serpapi.com/search", "auth_type": "api_key", "description": "SerpAPI SERP results"},
    {"name": "bing_search", "category": "search", "base_url": "https://api.bing.microsoft.com/v7.0", "auth_type": "api_key", "description": "Bing Web Search API"},
    {"name": "wikipedia", "category": "search", "base_url": "https://en.wikipedia.org/api/rest_v1", "auth_type": "none", "description": "Wikipedia REST API"},
    {"name": "wolfram_alpha", "category": "search", "base_url": "https://api.wolframalpha.com/v2", "auth_type": "api_key", "description": "Wolfram Alpha computational knowledge"},
    {"name": "newsapi", "category": "search", "base_url": "https://newsapi.org/v2", "auth_type": "api_key", "description": "NewsAPI current events"},
    # IoT / Robotics
    {"name": "aws_iot", "category": "iot", "base_url": "https://endpoint.iot.us-east-1.amazonaws.com", "auth_type": "aws_sig_v4", "description": "AWS IoT Core"},
    {"name": "azure_iot_hub", "category": "iot", "base_url": "https://iothub.azure-devices.net", "auth_type": "sas", "description": "Azure IoT Hub"},
    {"name": "particle_io", "category": "iot", "base_url": "https://api.particle.io/v1", "auth_type": "bearer", "description": "Particle.io IoT platform"},
    {"name": "influxdb_cloud", "category": "iot", "base_url": "https://us-east-1-1.aws.cloud2.influxdata.com/api/v2", "auth_type": "bearer", "description": "InfluxDB time-series cloud"},
    {"name": "thinspeak", "category": "iot", "base_url": "https://api.thingspeak.com", "auth_type": "api_key", "description": "ThingSpeak IoT analytics"},
    # Additional connectors to reach 100
    {"name": "deepgram", "category": "ai_ml", "base_url": "https://api.deepgram.com/v1", "auth_type": "bearer", "description": "Deepgram speech-to-text API"},
    {"name": "assemblyai", "category": "ai_ml", "base_url": "https://api.assemblyai.com/v2", "auth_type": "api_key", "description": "AssemblyAI audio transcription"},
    {"name": "elevenlabs", "category": "ai_ml", "base_url": "https://api.elevenlabs.io/v1", "auth_type": "api_key", "description": "ElevenLabs text-to-speech"},
    {"name": "roboflow", "category": "ai_ml", "base_url": "https://api.roboflow.com", "auth_type": "api_key", "description": "Roboflow computer vision platform"},
    {"name": "scale_ai", "category": "data", "base_url": "https://api.scale.com/v1", "auth_type": "bearer", "description": "Scale AI data labeling platform"},
]


class APIRegistry:
    """
    Central registry of all API connector configurations for DataForge.

    Provides lookup, categorisation, and listing of up to 100 API entries.
    """

    def __init__(self) -> None:
        """Initialise the registry with the built-in API list."""
        self._registry: dict[str, dict[str, Any]] = {}
        for api in _BUILTIN_APIS:
            self._registry[api["name"]] = dict(api)
        logger.info(
            "APIRegistry initialised with %d entries", len(self._registry)
        )

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def register(self, name: str, config: dict[str, Any]) -> None:
        """
        Register (or update) an API entry in the registry.

        Args:
            name: Unique API name / slug.
            config: Configuration dict containing at minimum ``category``
                    and ``base_url``.
        """
        config = dict(config)
        config["name"] = name
        config.setdefault("registered_at", datetime.now(timezone.utc).isoformat())
        self._registry[name] = config
        logger.debug("Registered API '%s'", name)

    def lookup(self, name: str) -> dict[str, Any]:
        """
        Look up an API entry by name.

        Args:
            name: The API slug to look up.

        Returns:
            A copy of the registry entry dict.

        Raises:
            KeyError: If *name* is not registered.
        """
        if name not in self._registry:
            raise KeyError(f"API '{name}' not found in registry")
        return dict(self._registry[name])

    def list_all(self) -> list[dict[str, Any]]:
        """
        Return a list of all registered API entries.

        Returns:
            A list of registry entry dicts.
        """
        return [dict(v) for v in self._registry.values()]

    def get_by_category(self, category: str) -> list[dict[str, Any]]:
        """
        Return all API entries matching the given category.

        Args:
            category: Category string to filter by (e.g. ``"ai_ml"``,
                      ``"payments"``).

        Returns:
            A list of matching registry entry dicts.
        """
        return [
            dict(v)
            for v in self._registry.values()
            if v.get("category") == category
        ]

    def list_categories(self) -> list[str]:
        """
        Return a sorted list of distinct categories in the registry.

        Returns:
            A sorted list of category strings.
        """
        return sorted({v.get("category", "uncategorised") for v in self._registry.values()})
