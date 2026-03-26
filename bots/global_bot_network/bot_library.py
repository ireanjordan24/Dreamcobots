"""
Bot Library — DreamCo Global Bot Communication Network.

Catalogs and registers all preexisting DreamCo bots so they can be
discovered, configured, and operated through the GBN.

Each entry in the library describes a bot's identity, capabilities,
category, tier support, and how to instantiate it.  The library acts
as the single source of truth for "which bots exist in DreamCo."
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BotCategory(Enum):
    FINANCE = "finance"
    REAL_ESTATE = "real_estate"
    CRYPTO = "crypto"
    AUTOMATION = "automation"
    AI = "ai"
    MARKETPLACE = "marketplace"
    FREELANCE = "freelance"
    LEAD_GEN = "lead_gen"
    EDUCATION = "education"
    GOVERNMENT = "government"
    JOB = "job"
    MINING = "mining"
    PAYMENTS = "payments"
    DEVELOPER_TOOLS = "developer_tools"
    BUSINESS = "business"
    MARKETING = "marketing"
    APP = "app"
    OCCUPATIONAL = "occupational"
    SYSTEM = "system"
    OTHER = "other"


class BotStatus(Enum):
    ACTIVE = "active"
    BETA = "beta"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"


# ---------------------------------------------------------------------------
# Bot entry
# ---------------------------------------------------------------------------

@dataclass
class BotEntry:
    """
    Metadata record for a single DreamCo bot in the library.

    Attributes
    ----------
    bot_id : str
        Unique identifier (snake_case, e.g. ``"financial_literacy_bot"``).
    display_name : str
        Human-readable name.
    description : str
        Short description of the bot's purpose.
    category : BotCategory
        Functional category.
    module_path : str
        Module filesystem path relative to the repo root, using dots as
        separators (e.g. ``"bots.financial_literacy_bot.financial_literacy_bot"``).
        Note: paths containing hyphens or leading digits are filesystem
        references and cannot be imported directly via ``importlib``; use
        ``importlib.util.spec_from_file_location`` with the resolved path.
    class_name : str
        Class name inside the module.
    version : str
        Current version string.
    tiers_supported : list[str]
        Tiers available (``["free", "pro", "enterprise"]``).
    status : BotStatus
        Operational status.
    capabilities : list[str]
        Key feature tags.
    owner_id : str
        Default owner / team.
    registered_at : str
        ISO-8601 UTC registration timestamp.
    """

    bot_id: str
    display_name: str
    description: str
    category: BotCategory
    module_path: str
    class_name: str
    version: str = "1.0.0"
    tiers_supported: list = field(default_factory=lambda: ["free", "pro", "enterprise"])
    status: BotStatus = BotStatus.ACTIVE
    capabilities: list = field(default_factory=list)
    owner_id: str = "dreamco"
    registered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "bot_id": self.bot_id,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category.value,
            "module_path": self.module_path,
            "class_name": self.class_name,
            "version": self.version,
            "tiers_supported": list(self.tiers_supported),
            "status": self.status.value,
            "capabilities": list(self.capabilities),
            "owner_id": self.owner_id,
            "registered_at": self.registered_at,
        }


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class BotLibraryError(Exception):
    """Base exception for BotLibrary errors."""


class BotAlreadyRegistered(BotLibraryError):
    """Raised when a bot_id is already in the library."""


class BotNotFound(BotLibraryError):
    """Raised when a bot_id is not found in the library."""


# ---------------------------------------------------------------------------
# Bot Library
# ---------------------------------------------------------------------------

class BotLibrary:
    """
    Registry and catalogue of all DreamCo bots.

    Usage::

        library = BotLibrary()
        library.populate_dreamco_bots()   # registers all built-in bots
        entries = library.list_bots()
        entry   = library.get_bot("financial_literacy_bot")
    """

    def __init__(self) -> None:
        self._bots: dict[str, BotEntry] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, entry: BotEntry, *, overwrite: bool = False) -> BotEntry:
        """
        Add a bot to the library.

        Parameters
        ----------
        entry : BotEntry
            The bot to register.
        overwrite : bool
            When *True*, silently replace an existing entry with the same ID.

        Raises
        ------
        BotAlreadyRegistered
            If *overwrite* is False and the bot_id already exists.
        """
        if entry.bot_id in self._bots and not overwrite:
            raise BotAlreadyRegistered(
                f"Bot '{entry.bot_id}' is already registered. "
                "Use overwrite=True to replace it."
            )
        self._bots[entry.bot_id] = entry
        return entry

    def unregister(self, bot_id: str) -> None:
        """Remove a bot from the library."""
        self._bots.pop(bot_id, None)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_bot(self, bot_id: str) -> BotEntry:
        """
        Return the BotEntry for *bot_id*.

        Raises
        ------
        BotNotFound
        """
        if bot_id not in self._bots:
            raise BotNotFound(f"Bot '{bot_id}' not found in the library.")
        return self._bots[bot_id]

    def list_bots(
        self,
        category: Optional[BotCategory] = None,
        status: Optional[BotStatus] = None,
    ) -> list[dict]:
        """
        Return all bots, optionally filtered by category and/or status.
        """
        entries = self._bots.values()
        if category is not None:
            entries = [e for e in entries if e.category == category]
        if status is not None:
            entries = [e for e in entries if e.status == status]
        return [e.to_dict() for e in entries]

    def search(self, query: str) -> list[dict]:
        """
        Full-text search across bot_id, display_name, description, and capabilities.
        """
        q = query.lower()
        results = []
        for entry in self._bots.values():
            haystack = " ".join([
                entry.bot_id,
                entry.display_name,
                entry.description,
                " ".join(entry.capabilities),
            ]).lower()
            if q in haystack:
                results.append(entry.to_dict())
        return results

    def count(self) -> int:
        """Return total number of registered bots."""
        return len(self._bots)

    def get_stats(self) -> dict:
        """Return library statistics."""
        by_category: dict[str, int] = {}
        by_status: dict[str, int] = {}
        for entry in self._bots.values():
            by_category[entry.category.value] = by_category.get(entry.category.value, 0) + 1
            by_status[entry.status.value] = by_status.get(entry.status.value, 0) + 1
        return {
            "total_bots": len(self._bots),
            "by_category": by_category,
            "by_status": by_status,
        }

    # ------------------------------------------------------------------
    # Bulk load of all DreamCo bots
    # ------------------------------------------------------------------

    def populate_dreamco_bots(self) -> None:
        """Register all preexisting DreamCo bots in the library."""
        for entry in _DREAMCO_BOTS:
            self.register(entry, overwrite=True)


# ---------------------------------------------------------------------------
# Prebuilt catalogue — all DreamCo bots
# ---------------------------------------------------------------------------

_DREAMCO_BOTS: list[BotEntry] = [
    BotEntry(
        bot_id="resource_eligibility_bot",
        display_name="211 Resource Eligibility Bot",
        description="Matches users with local social services and resource programs.",
        category=BotCategory.GOVERNMENT,
        module_path="bots.211-resource-eligibility-bot.bot",
        class_name="ResourceEligibilityBot",
        capabilities=["resource_lookup", "eligibility_check", "referral"],
    ),
    BotEntry(
        bot_id="affiliate_bot",
        display_name="Affiliate Bot",
        description="Manages affiliate marketing programs, tracking, and payouts.",
        category=BotCategory.MARKETING,
        module_path="bots.affiliate_bot.affiliate_bot",
        class_name="AffiliateBot",
        capabilities=["affiliate_tracking", "commission", "link_generation"],
    ),
    BotEntry(
        bot_id="ai_models_integration",
        display_name="AI Models Integration Bot",
        description="Connects DreamCo bots with external AI models and APIs.",
        category=BotCategory.AI,
        module_path="bots.ai-models-integration.ai_models_integration",
        class_name="AIModelsIntegration",
        capabilities=["openai", "model_routing", "inference"],
    ),
    BotEntry(
        bot_id="ai_side_hustle_bot",
        display_name="AI Side Hustle Bot",
        description="Generates and manages AI-powered income streams.",
        category=BotCategory.BUSINESS,
        module_path="bots.ai-side-hustle-bots.bot",
        class_name="AISideHustleBot",
        capabilities=["income_generation", "gig_economy", "automation"],
    ),
    BotEntry(
        bot_id="ai_chatbot",
        display_name="AI Chatbot",
        description="General-purpose conversational AI for DreamCo users.",
        category=BotCategory.AI,
        module_path="bots.ai_chatbot.chatbot",
        class_name="AIchatbot",
        capabilities=["conversation", "nlp", "intent_detection"],
    ),
    BotEntry(
        bot_id="ai_learning_system",
        display_name="AI Learning System",
        description="Adaptive learning engine that evolves bot capabilities over time.",
        category=BotCategory.EDUCATION,
        module_path="bots.ai_learning_system.ai_learning_system",
        class_name="AILearningSystem",
        capabilities=["adaptive_learning", "analytics", "classifier"],
    ),
    BotEntry(
        bot_id="ai_level_up_bot",
        display_name="AI Level-Up Bot",
        description="Helps users learn AI skills through structured courses and challenges.",
        category=BotCategory.EDUCATION,
        module_path="bots.ai_level_up_bot.ai_level_up_bot",
        class_name="AILevelUpBot",
        capabilities=["skill_tree", "courses", "token_marketplace", "ai_agents"],
    ),
    BotEntry(
        bot_id="app_builder_bot",
        display_name="App Builder Bot",
        description="Generates and scaffolds full-stack applications on demand.",
        category=BotCategory.DEVELOPER_TOOLS,
        module_path="bots.app_builder_bot.app_builder_bot",
        class_name="AppBuilderBot",
        capabilities=["code_generation", "scaffolding", "deployment"],
    ),
    BotEntry(
        bot_id="big_bro_ai",
        display_name="Big Bro AI",
        description="Central AI mentor, coach, and bot factory for the DreamCo ecosystem.",
        category=BotCategory.AI,
        module_path="bots.big_bro_ai.big_bro_ai",
        class_name="BigBroAI",
        capabilities=[
            "mentorship", "bot_factory", "personality_engine",
            "courses", "memory_system", "sales_monetization",
        ],
    ),
    BotEntry(
        bot_id="bot_generator",
        display_name="Bot Generator",
        description="Generates new bots from specs using code generation and templates.",
        category=BotCategory.DEVELOPER_TOOLS,
        module_path="bots.bot_generator.code_generator",
        class_name="CodeGenerator",
        capabilities=["code_generation", "benchmarking", "revenue_tracking"],
    ),
    BotEntry(
        bot_id="bot_generator_bot",
        display_name="Bot Generator Bot",
        description="High-level bot that orchestrates bot creation workflows.",
        category=BotCategory.DEVELOPER_TOOLS,
        module_path="bots.bot_generator_bot.bot_generator_bot",
        class_name="BotGeneratorBot",
        capabilities=["bot_creation", "template_engine", "deployment"],
    ),
    BotEntry(
        bot_id="buddy_os",
        display_name="Buddy OS",
        description="Mobile-first OS framework for managing DreamCo bots on-device.",
        category=BotCategory.SYSTEM,
        module_path="bots.buddy_os.buddy_os",
        class_name="BuddyOS",
        capabilities=["device_manager", "bluetooth", "cast_engine", "app_framework"],
    ),
    BotEntry(
        bot_id="car_flipping_bot",
        display_name="Car Flipping Bot",
        description="Automates car research, valuation, and flipping workflows.",
        category=BotCategory.BUSINESS,
        module_path="bots.car_flipping_bot.car_flipping_bot",
        class_name="CarFlippingBot",
        capabilities=["valuation", "listing", "deal_analysis"],
    ),
    BotEntry(
        bot_id="ci_auto_fix_bot",
        display_name="CI Auto-Fix Bot",
        description="Automatically detects and fixes CI pipeline failures.",
        category=BotCategory.DEVELOPER_TOOLS,
        module_path="bots.ci_auto_fix_bot.ci_auto_fix_bot",
        class_name="CIAutoFixBot",
        capabilities=["ci_monitoring", "auto_fix", "github_integration"],
    ),
    BotEntry(
        bot_id="control_center",
        display_name="Control Center",
        description="Central hub for monitoring, deploying, and managing all DreamCo bots.",
        category=BotCategory.SYSTEM,
        module_path="bots.control_center.control_center",
        class_name="ControlCenter",
        capabilities=["bot_registry", "heartbeat", "github_integration", "dashboard"],
    ),
    BotEntry(
        bot_id="crypto_bot",
        display_name="Crypto Bot",
        description="Crypto trading, portfolio management, and mining automation.",
        category=BotCategory.CRYPTO,
        module_path="bots.crypto_bot.crypto_bot",
        class_name="CryptoBot",
        capabilities=["trading", "portfolio", "mining", "price_feed", "dashboard"],
    ),
    BotEntry(
        bot_id="deal_finder_bot",
        display_name="Deal Finder Bot",
        description="Scouts deals across multiple platforms and alerts on opportunities.",
        category=BotCategory.BUSINESS,
        module_path="bots.deal_finder_bot.deal_finder_bot",
        class_name="DealFinderBot",
        capabilities=["deal_scouting", "alerts", "comparison"],
    ),
    BotEntry(
        bot_id="dreamco_empire_os",
        display_name="DreamCo Empire OS",
        description="Master operating system for running the full DreamCo business empire.",
        category=BotCategory.SYSTEM,
        module_path="bots.dreamco_empire_os.empire_os",
        class_name="EmpireOS",
        capabilities=[
            "ai_leaders", "bot_fleet", "marketplace", "deal_analyzer",
            "revenue_tracker", "cost_tracking", "orchestration",
        ],
    ),
    BotEntry(
        bot_id="dreamco_payments",
        display_name="DreamCo Payments",
        description="Unified payment processing, account management, and reporting.",
        category=BotCategory.PAYMENTS,
        module_path="bots.dreamco_payments.dreamco_payments",
        class_name="DreamcoPayments",
        capabilities=["stripe", "account_manager", "payment_processor", "reporting"],
    ),
    BotEntry(
        bot_id="financial_literacy_bot",
        display_name="Financial Literacy Bot",
        description="Educates users on credit building, OPM strategies, and investing.",
        category=BotCategory.FINANCE,
        module_path="bots.financial_literacy_bot.financial_literacy_bot",
        class_name="FinancialLiteracyBot",
        capabilities=[
            "credit_tips", "credit_alerts", "investment_calculator",
            "opm_strategies", "education_paths", "community",
        ],
    ),
    BotEntry(
        bot_id="fiverr_bot",
        display_name="Fiverr Bot",
        description="Full freelance marketplace: gigs, proposals, milestones, payments.",
        category=BotCategory.FREELANCE,
        module_path="bots.fiverr_bot.fiverr_bot",
        class_name="FiverrBot",
        capabilities=[
            "freelancer_registration", "gig_posting", "proposals",
            "milestones", "stripe_payments", "admin_dashboard",
        ],
    ),
    BotEntry(
        bot_id="government_contract_grant_bot",
        display_name="Government Contract & Grant Bot",
        description="Identifies, applies for, and tracks government contracts and grants.",
        category=BotCategory.GOVERNMENT,
        module_path="bots.government-contract-grant-bot.government_contract_grant_bot",
        class_name="GovernmentContractGrantBot",
        capabilities=["contract_search", "grant_search", "application_tracking"],
    ),
    BotEntry(
        bot_id="job_titles_bot",
        display_name="Job Titles Bot",
        description="AI job-role database, generator, and cost-justification engine.",
        category=BotCategory.JOB,
        module_path="bots.job_titles_bot.job_titles_bot",
        class_name="JobTitlesBot",
        capabilities=["job_database", "role_generation", "cost_justification", "trainer"],
    ),
    BotEntry(
        bot_id="mining_bot",
        display_name="Mining Bot",
        description="Automates resource and crypto mining workflows.",
        category=BotCategory.MINING,
        module_path="bots.mining_bot.mining_bot",
        class_name="MiningBot",
        capabilities=["crypto_mining", "resource_tracking", "profit_analysis"],
    ),
    BotEntry(
        bot_id="money_finder_bot",
        display_name="Money Finder Bot",
        description="Discovers income opportunities, grants, and financial resources.",
        category=BotCategory.FINANCE,
        module_path="bots.money_finder_bot.money_finder_bot",
        class_name="MoneyFinderBot",
        capabilities=["opportunity_discovery", "grants", "income_streams"],
    ),
    BotEntry(
        bot_id="multi_source_lead_scraper",
        display_name="Multi-Source Lead Scraper",
        description="Aggregates leads from multiple sources with scoring and CRM export.",
        category=BotCategory.LEAD_GEN,
        module_path="bots.multi_source_lead_scraper.lead_scraper",
        class_name="MultiSourceLeadScraper",
        capabilities=["lead_scraping", "lead_scoring", "crm_export"],
    ),
    BotEntry(
        bot_id="open_claw_bot",
        display_name="OpenClaw Bot",
        description="AI-powered strategy engine for trading, clients, and market intel.",
        category=BotCategory.AI,
        module_path="bots.open_claw_bot.open_claw_bot",
        class_name="OpenClawBot",
        capabilities=[
            "strategy_engine", "ai_models", "client_manager",
            "data_analysis", "ml_ensemble", "realtime_signals",
        ],
    ),
    BotEntry(
        bot_id="real_estate_bot",
        display_name="Real Estate Bot",
        description="Property search, valuation, deal analysis, and rental management.",
        category=BotCategory.REAL_ESTATE,
        module_path="bots.real_estate_bot.real_estate_bot",
        class_name="RealEstateBot",
        capabilities=["property_search", "valuation", "deal_analysis", "rental"],
    ),
    BotEntry(
        bot_id="selenium_job_application_bot",
        display_name="Selenium Job Application Bot",
        description="Automates job applications across multiple platforms.",
        category=BotCategory.JOB,
        module_path="bots.selenium-job-application-bot.bot",
        class_name="SeleniumJobApplicationBot",
        capabilities=["job_search", "auto_apply", "form_filling"],
    ),
    BotEntry(
        bot_id="software_bot",
        display_name="Software Bot",
        description="Builds, tests, and deploys software projects end-to-end.",
        category=BotCategory.DEVELOPER_TOOLS,
        module_path="bots.software_bot.software_bot",
        class_name="SoftwareBot",
        capabilities=["code_generation", "testing", "deployment", "devops"],
    ),
    # -- Category bots --
    BotEntry(
        bot_id="app_bots_category",
        display_name="App Bots (Category)",
        description="Collection of app-building and mobile development bots.",
        category=BotCategory.APP,
        module_path="App_bots.feature_1",
        class_name="AppBotFeature",
        capabilities=["app_development", "mobile", "scaffolding"],
    ),
    BotEntry(
        bot_id="business_bots_category",
        display_name="Business Bots (Category)",
        description="Bots for automating business operations and workflows.",
        category=BotCategory.BUSINESS,
        module_path="Business_bots.feature_1",
        class_name="BusinessBotFeature",
        capabilities=["business_automation", "workflows", "reporting"],
    ),
    BotEntry(
        bot_id="fiverr_bots_category",
        display_name="Fiverr Bots (Category)",
        description="Freelance-focused bots for Fiverr-style platforms.",
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.feature_1",
        class_name="FiverrBotFeature",
        capabilities=["freelancing", "gig_management", "proposals"],
    ),
    BotEntry(
        bot_id="marketing_bots_category",
        display_name="Marketing Bots (Category)",
        description="Bots for campaign management, lead gen, and brand growth.",
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.feature_1",
        class_name="MarketingBotFeature",
        capabilities=["campaigns", "lead_gen", "seo", "social_media"],
    ),
    BotEntry(
        bot_id="occupational_bots_category",
        display_name="Occupational Bots (Category)",
        description="Career and occupation-specific automation bots.",
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.feature_1",
        class_name="OccupationalBotFeature",
        capabilities=["career", "job_market", "skills"],
    ),
    BotEntry(
        bot_id="real_estate_bots_category",
        display_name="Real Estate Bots (Category)",
        description="Real estate analysis and management bots collection.",
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.feature_1",
        class_name="RealEstateBotFeature",
        capabilities=["property_analysis", "market_data", "rental"],
    ),
]
