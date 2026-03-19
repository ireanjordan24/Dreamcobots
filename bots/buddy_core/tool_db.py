"""
Tool Database for the Buddy Core System.

Pre-built catalogue of 15+ API/library tools that can be auto-injected
into generated bots based on industry and purpose.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ToolDBError(Exception):
    """Raised when a ToolDB operation fails."""


class ToolCategory(Enum):
    API = "api"
    LIBRARY = "library"
    WEBHOOK = "webhook"
    PAYMENT = "payment"
    SCRAPER = "scraper"
    CRM = "crm"
    ANALYTICS = "analytics"


@dataclass
class Tool:
    """Represents a single integration tool."""

    tool_id: str
    name: str
    category: ToolCategory
    description: str
    industry_tags: list
    api_endpoint: Optional[str]
    is_free: bool
    monthly_cost_usd: float


# ---------------------------------------------------------------------------
# Pre-built catalogue
# ---------------------------------------------------------------------------

_CATALOGUE: list[Tool] = [
    Tool(
        tool_id="zillow_api",
        name="Zillow API",
        category=ToolCategory.API,
        description="Real-estate listing data, home values, and market trends.",
        industry_tags=["real_estate"],
        api_endpoint="https://api.zillow.com/v2",
        is_free=False,
        monthly_cost_usd=49.0,
    ),
    Tool(
        tool_id="trulia",
        name="Trulia",
        category=ToolCategory.SCRAPER,
        description="Property listings and neighbourhood insights scraper.",
        industry_tags=["real_estate"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="google_maps",
        name="Google Maps API",
        category=ToolCategory.API,
        description="Geocoding, routing, and place search.",
        industry_tags=["real_estate", "logistics", "general"],
        api_endpoint="https://maps.googleapis.com/maps/api",
        is_free=False,
        monthly_cost_usd=0.0,  # pay-per-use
    ),
    Tool(
        tool_id="stripe",
        name="Stripe",
        category=ToolCategory.PAYMENT,
        description="Online payment processing and subscription billing.",
        industry_tags=["finance", "general", "freelance", "marketing"],
        api_endpoint="https://api.stripe.com/v1",
        is_free=False,
        monthly_cost_usd=0.0,  # per-transaction fees
    ),
    Tool(
        tool_id="plaid",
        name="Plaid",
        category=ToolCategory.PAYMENT,
        description="Bank account linking and financial data aggregation.",
        industry_tags=["finance"],
        api_endpoint="https://production.plaid.com",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="fiverr_api",
        name="Fiverr API",
        category=ToolCategory.API,
        description="Access Fiverr gig marketplace data and automation.",
        industry_tags=["freelance"],
        api_endpoint="https://api.fiverr.com/v1",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="upwork_api",
        name="Upwork API",
        category=ToolCategory.API,
        description="Freelancer and job listing data from Upwork.",
        industry_tags=["freelance"],
        api_endpoint="https://www.upwork.com/api",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="hubspot_crm",
        name="HubSpot CRM",
        category=ToolCategory.CRM,
        description="Contact management, pipelines, and email sequences.",
        industry_tags=["marketing", "general", "freelance"],
        api_endpoint="https://api.hubapi.com",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="salesforce",
        name="Salesforce",
        category=ToolCategory.CRM,
        description="Enterprise CRM with advanced reporting.",
        industry_tags=["marketing", "finance", "general"],
        api_endpoint="https://login.salesforce.com/services/oauth2",
        is_free=False,
        monthly_cost_usd=75.0,
    ),
    Tool(
        tool_id="linkedin_scraper",
        name="LinkedIn Scraper",
        category=ToolCategory.SCRAPER,
        description="Extract professional profiles and company data.",
        industry_tags=["marketing", "freelance", "general"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="twitter_api",
        name="Twitter/X API",
        category=ToolCategory.API,
        description="Tweets, user data, and trend monitoring.",
        industry_tags=["marketing", "general"],
        api_endpoint="https://api.twitter.com/2",
        is_free=False,
        monthly_cost_usd=100.0,
    ),
    Tool(
        tool_id="mailchimp",
        name="Mailchimp",
        category=ToolCategory.ANALYTICS,
        description="Email marketing, automation, and audience analytics.",
        industry_tags=["marketing", "general"],
        api_endpoint="https://api.mailchimp.com/3.0",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="openai_api",
        name="OpenAI API",
        category=ToolCategory.API,
        description="GPT models for text generation, embeddings, and chat.",
        industry_tags=["general", "marketing", "health", "finance"],
        api_endpoint="https://api.openai.com/v1",
        is_free=False,
        monthly_cost_usd=20.0,
    ),
    Tool(
        tool_id="twilio",
        name="Twilio",
        category=ToolCategory.WEBHOOK,
        description="SMS, voice, and WhatsApp messaging platform.",
        industry_tags=["general", "marketing", "health"],
        api_endpoint="https://api.twilio.com/2010-04-01",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="sendgrid",
        name="SendGrid",
        category=ToolCategory.WEBHOOK,
        description="Transactional and marketing email delivery.",
        industry_tags=["general", "marketing"],
        api_endpoint="https://api.sendgrid.com/v3",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
]

_CATALOGUE_MAP: dict[str, Tool] = {t.tool_id: t for t in _CATALOGUE}


class ToolDB:
    """In-memory tool catalogue with search and injection helpers."""

    def search(self, query: str, industry: str = "") -> list[Tool]:
        """Search tools by keywords and optional industry filter."""
        lower = query.lower()
        results: list[Tool] = []
        for tool in _CATALOGUE:
            text = (
                tool.name.lower()
                + " "
                + tool.description.lower()
                + " "
                + " ".join(tool.industry_tags)
            )
            if lower in text:
                if not industry or industry.lower() in tool.industry_tags:
                    results.append(tool)
        return results

    def get_tools_for_industry(self, industry: str) -> list[Tool]:
        """Return all tools tagged for the given industry."""
        lower = industry.lower()
        return [t for t in _CATALOGUE if lower in t.industry_tags or "general" in t.industry_tags]

    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """Return a tool by its ID, or None."""
        return _CATALOGUE_MAP.get(tool_id)

    def inject_tools(self, bot_name: str, industry: str) -> list[Tool]:
        """Auto-select the best tools for a bot given its industry."""
        lower = industry.lower()
        # Prefer industry-specific tools; add general ones as fill
        specific = [t for t in _CATALOGUE if lower in t.industry_tags]
        general = [t for t in _CATALOGUE if "general" in t.industry_tags and t not in specific]
        combined = specific + general
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[Tool] = []
        for t in combined:
            if t.tool_id not in seen:
                seen.add(t.tool_id)
                unique.append(t)
        return unique[:6]  # cap at 6 injected tools

    def list_all(self) -> list[Tool]:
        """Return the full catalogue."""
        return list(_CATALOGUE)
