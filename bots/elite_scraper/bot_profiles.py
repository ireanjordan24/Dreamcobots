"""
bot_profiles.py — Per-bot Elite Scraper configuration profiles.

Each ``BotProfile`` defines the search queries, knowledge categories,
monetization focus, and client-acquisition targets specific to a single
DreamCo bot.  The EliteScraper reads the matching profile so every bot
gets a scraper team perfectly tuned to make *that* bot the best in its
category.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BotProfile:
    """
    Configuration profile that customises the Elite Scraper for one bot.

    Parameters
    ----------
    bot_name : str
        Canonical bot directory name (e.g. ``"lead_gen_bot"``).
    display_name : str
        Human-readable name shown in reports.
    category : str
        High-level category (e.g. ``"lead-generation"``, ``"crypto"``, …).
    github_queries : list[str]
        GitHub search queries used to find related repos/workflows.
    knowledge_topics : list[str]
        Topic keywords to drive academic / article scraping.
    monetization_keywords : list[str]
        Keywords for monetization-strategy searches.
    client_acquisition_keywords : list[str]
        Keywords used to find potential clients / communities.
    competing_bots_queries : list[str]
        Queries to surface competing or complementary bot solutions.
    self_improvement_topics : list[str]
        Topics for self-improvement / algorithm refinement research.
    description : str
        Short description used in logged reports.
    """

    bot_name: str
    display_name: str
    category: str
    github_queries: list[str]
    knowledge_topics: list[str]
    monetization_keywords: list[str]
    client_acquisition_keywords: list[str]
    competing_bots_queries: list[str]
    self_improvement_topics: list[str]
    description: str = ""
    extra_sources: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Bot profile registry
# ---------------------------------------------------------------------------

BOT_PROFILES: dict[str, BotProfile] = {
    # ------------------------------------------------------------------ #
    # Lead-generation family
    # ------------------------------------------------------------------ #
    "lead_gen_bot": BotProfile(
        bot_name="lead_gen_bot",
        display_name="LeadGenBot",
        category="lead-generation",
        github_queries=[
            "lead generation bot python",
            "real estate lead scraper workflow",
            "small business lead automation",
            "github.com/workflows lead generation",
        ],
        knowledge_topics=["lead generation", "real estate marketing", "small business outreach"],
        monetization_keywords=["pay-per-lead pricing", "lead generation SaaS", "lead selling marketplace"],
        client_acquisition_keywords=["real estate agents looking for leads", "small business marketing budget"],
        competing_bots_queries=["lead generation automation tool", "apollo.io alternative python"],
        self_improvement_topics=["email validation", "phone number enrichment", "lead scoring algorithms"],
        description="Finds and qualifies business leads from multiple online sources.",
    ),
    "multi_source_lead_scraper": BotProfile(
        bot_name="multi_source_lead_scraper",
        display_name="MultiSourceLeadScraper",
        category="lead-generation",
        github_queries=[
            "multi source lead scraper python",
            "google maps business scraper",
            "linkedin scraper python workflow",
        ],
        knowledge_topics=["multi-channel lead generation", "CRM integration", "data enrichment"],
        monetization_keywords=["CRM SaaS pricing", "data enrichment API revenue"],
        client_acquisition_keywords=["B2B companies needing lead data", "marketing agencies"],
        competing_bots_queries=["snov.io alternative", "hunter.io python"],
        self_improvement_topics=["deduplication algorithms", "data quality scoring", "AI lead ranking"],
        description="Aggregates qualified leads from Google, LinkedIn, Twitter, Reddit, and more.",
    ),
    # ------------------------------------------------------------------ #
    # Buddy / AI-learning family
    # ------------------------------------------------------------------ #
    "buddy_bot": BotProfile(
        bot_name="buddy_bot",
        display_name="BuddyBot",
        category="ai-assistant",
        github_queries=[
            "conversational AI bot python",
            "self-improving AI assistant",
            "AI memory system langchain",
            "openai assistant workflow github",
        ],
        knowledge_topics=["conversational AI", "reinforcement learning", "memory systems", "NLP"],
        monetization_keywords=["AI assistant SaaS", "chatbot subscription pricing", "AI API monetization"],
        client_acquisition_keywords=["companies hiring AI assistants", "chatbot platform buyers"],
        competing_bots_queries=["chatgpt alternative python bot", "langchain agent"],
        self_improvement_topics=["self-supervised learning", "conversation context management", "RAG pipeline"],
        description="Intelligent conversational AI assistant with memory and self-improvement.",
    ),
    "buddy_trainer_bot": BotProfile(
        bot_name="buddy_trainer_bot",
        display_name="BuddyTrainerBot",
        category="ai-training",
        github_queries=[
            "AI model training workflow github",
            "bot self improvement pipeline",
            "automated machine learning training",
        ],
        knowledge_topics=["model fine-tuning", "transfer learning", "AutoML", "dataset curation"],
        monetization_keywords=["AI training service pricing", "model-as-a-service revenue"],
        client_acquisition_keywords=["AI startups needing training pipelines", "enterprise ML teams"],
        competing_bots_queries=["huggingface autotrainer", "auto-sklearn workflow"],
        self_improvement_topics=["hyperparameter optimization", "curriculum learning", "knowledge distillation"],
        description="Automates AI model training, fine-tuning, and evaluation pipelines.",
    ),
    # ------------------------------------------------------------------ #
    # Real-estate family
    # ------------------------------------------------------------------ #
    "real_estate_bot": BotProfile(
        bot_name="real_estate_bot",
        display_name="RealEstateBot",
        category="real-estate",
        github_queries=[
            "real estate scraper python",
            "zillow scraper workflow",
            "MLS property listing automation",
            "real estate investment analysis bot",
        ],
        knowledge_topics=["real estate analytics", "property valuation", "rental cashflow analysis"],
        monetization_keywords=["real estate SaaS pricing", "property data API revenue", "MLS data monetization"],
        client_acquisition_keywords=["real estate investors", "property managers", "real estate agents"],
        competing_bots_queries=["zillow API alternative", "redfin data scraper python"],
        self_improvement_topics=["predictive pricing models", "neighborhood scoring", "ROI calculators"],
        description="Finds, analyzes, and tracks real estate deals and investment opportunities.",
    ),
    "home_flipping_analyzer": BotProfile(
        bot_name="home_flipping_analyzer",
        display_name="HomeFlippingAnalyzer",
        category="real-estate",
        github_queries=[
            "house flipping profit calculator python",
            "real estate ARV estimator",
            "property rehab cost estimator",
        ],
        knowledge_topics=["home flipping", "ARV calculation", "rehab cost estimation", "ROI real estate"],
        monetization_keywords=["home flipping SaaS", "real estate analyzer subscription"],
        client_acquisition_keywords=["real estate investors", "house flippers", "fix-and-flip buyers"],
        competing_bots_queries=["dealcheck.io alternative", "rehabvaluator python"],
        self_improvement_topics=["comparable sales analysis", "market trend prediction", "renovation cost AI"],
        description="Analyzes home flipping profitability using ARV, rehab costs, and ROI.",
    ),
    # ------------------------------------------------------------------ #
    # Finance & crypto
    # ------------------------------------------------------------------ #
    "crypto_bot": BotProfile(
        bot_name="crypto_bot",
        display_name="CryptoBot",
        category="crypto-trading",
        github_queries=[
            "crypto trading bot python",
            "DeFi yield farming automation",
            "binance trading bot github",
            "crypto arbitrage bot workflow",
        ],
        knowledge_topics=["algorithmic trading", "DeFi protocols", "crypto arbitrage", "sentiment analysis"],
        monetization_keywords=["crypto trading SaaS", "algo trading subscription", "DeFi yield profit"],
        client_acquisition_keywords=["crypto investors", "DeFi traders", "hedge funds"],
        competing_bots_queries=["freqtrade alternative", "hummingbot python"],
        self_improvement_topics=["backtesting strategies", "risk management", "on-chain data analysis"],
        description="Automates cryptocurrency trading, arbitrage, and DeFi yield strategies.",
    ),
    "stock_trading_bot": BotProfile(
        bot_name="stock_trading_bot",
        display_name="StockTradingBot",
        category="stock-trading",
        github_queries=[
            "stock trading bot python alpaca",
            "automated stock trading workflow",
            "quantitative finance python bot",
        ],
        knowledge_topics=["quantitative finance", "algorithmic trading", "technical analysis"],
        monetization_keywords=["stock trading SaaS", "quant strategy subscription", "trading signals revenue"],
        client_acquisition_keywords=["retail investors", "day traders", "wealth managers"],
        competing_bots_queries=["zipline alternative", "backtrader python workflow"],
        self_improvement_topics=["backtesting frameworks", "factor investing", "ML stock prediction"],
        description="Executes and optimizes stock trades using algorithmic and ML-driven strategies.",
    ),
    # ------------------------------------------------------------------ #
    # Marketing & social
    # ------------------------------------------------------------------ #
    "marketing_bot": BotProfile(
        bot_name="marketing_bot",
        display_name="MarketingBot",
        category="marketing",
        github_queries=[
            "marketing automation bot python",
            "email campaign automation workflow",
            "social media marketing bot github",
        ],
        knowledge_topics=["digital marketing", "content marketing", "email automation", "SEO"],
        monetization_keywords=["marketing SaaS pricing", "email campaign revenue", "ad revenue optimization"],
        client_acquisition_keywords=["SMBs needing marketing", "ecommerce stores", "startup marketing teams"],
        competing_bots_queries=["mailchimp automation alternative", "hubspot workflow python"],
        self_improvement_topics=["A/B testing frameworks", "conversion optimization", "NLP copywriting"],
        description="Automates digital marketing campaigns, email outreach, and social media management.",
    ),
    "social_media_bot": BotProfile(
        bot_name="social_media_bot",
        display_name="SocialMediaBot",
        category="social-media",
        github_queries=[
            "social media automation bot python",
            "twitter bot github",
            "instagram automation workflow",
        ],
        knowledge_topics=["social media growth", "viral content strategies", "influencer marketing"],
        monetization_keywords=["social media SaaS", "social growth subscription", "brand partnership revenue"],
        client_acquisition_keywords=["influencers", "brands", "agencies", "content creators"],
        competing_bots_queries=["buffer alternative python", "hootsuite API bot"],
        self_improvement_topics=["engagement prediction", "sentiment analysis", "hashtag strategy"],
        description="Manages and grows social media accounts using automated content and engagement.",
    ),
    # ------------------------------------------------------------------ #
    # E-commerce & sales
    # ------------------------------------------------------------------ #
    "ecommerce-bot": BotProfile(
        bot_name="ecommerce-bot",
        display_name="EcommerceBot",
        category="ecommerce",
        github_queries=[
            "ecommerce automation bot python",
            "shopify bot workflow github",
            "amazon seller automation",
        ],
        knowledge_topics=["ecommerce optimization", "product listing automation", "price tracking"],
        monetization_keywords=["ecommerce SaaS", "dropshipping automation revenue", "shopify app revenue"],
        client_acquisition_keywords=["shopify store owners", "amazon sellers", "dropshippers"],
        competing_bots_queries=["shopify automation alternative", "amazon repricer python"],
        self_improvement_topics=["dynamic pricing algorithms", "inventory forecasting", "product ranking"],
        description="Automates ecommerce operations including listings, pricing, and order management.",
    ),
    "sales_bot": BotProfile(
        bot_name="sales_bot",
        display_name="SalesBot",
        category="sales",
        github_queries=[
            "sales automation bot python",
            "CRM automation workflow github",
            "cold outreach automation tool",
        ],
        knowledge_topics=["sales automation", "CRM integration", "pipeline management", "cold outreach"],
        monetization_keywords=["sales SaaS pricing", "outreach tool subscription", "CRM integration revenue"],
        client_acquisition_keywords=["sales teams", "B2B companies", "SDR agencies"],
        competing_bots_queries=["salesloft alternative python", "outreach.io bot"],
        self_improvement_topics=["objection handling", "email personalization AI", "deal scoring"],
        description="Automates sales outreach, follow-ups, and CRM updates to close more deals.",
    ),
    # ------------------------------------------------------------------ #
    # Developer tools & DevOps
    # ------------------------------------------------------------------ #
    "devops_bot": BotProfile(
        bot_name="devops_bot",
        display_name="DevOpsBot",
        category="devops",
        github_queries=[
            "devops automation bot python",
            "CI CD pipeline automation github",
            "infrastructure as code workflow",
        ],
        knowledge_topics=["CI/CD pipelines", "Kubernetes automation", "infrastructure as code"],
        monetization_keywords=["DevOps SaaS", "CI/CD tool subscription", "cloud automation revenue"],
        client_acquisition_keywords=["DevOps teams", "engineering departments", "cloud-native startups"],
        competing_bots_queries=["jenkins alternative python", "github actions alternative"],
        self_improvement_topics=["container orchestration", "terraform best practices", "observability"],
        description="Automates DevOps workflows including CI/CD, infrastructure, and deployments.",
    ),
    "coding_assistant_bot": BotProfile(
        bot_name="coding_assistant_bot",
        display_name="CodingAssistantBot",
        category="developer-tools",
        github_queries=[
            "AI coding assistant python",
            "code review automation workflow",
            "code generation AI bot",
        ],
        knowledge_topics=["code generation", "static analysis", "refactoring", "code review"],
        monetization_keywords=["coding assistant SaaS", "code review subscription", "developer tool revenue"],
        client_acquisition_keywords=["software development teams", "engineering leads", "coding bootcamps"],
        competing_bots_queries=["copilot alternative open source", "codewhisperer python"],
        self_improvement_topics=["AST analysis", "code smell detection", "test generation"],
        description="Provides AI-powered code review, generation, and refactoring assistance.",
    ),
    # ------------------------------------------------------------------ #
    # Government / legal
    # ------------------------------------------------------------------ #
    "government_contract_bot": BotProfile(
        bot_name="government_contract_bot",
        display_name="GovernmentContractBot",
        category="government-contracts",
        github_queries=[
            "government contract scraper python",
            "SAM.gov API workflow",
            "federal grant finder automation",
        ],
        knowledge_topics=["government contracts", "federal procurement", "grant writing"],
        monetization_keywords=["government contract SaaS", "grant finder subscription", "procurement consulting"],
        client_acquisition_keywords=["small businesses pursuing government contracts", "nonprofit grant seekers"],
        competing_bots_queries=["sam.gov scraper alternative", "usaspending python"],
        self_improvement_topics=["contract scoring algorithms", "RFP analysis", "compliance checking"],
        description="Finds and tracks government contracts, grants, and procurement opportunities.",
    ),
    # ------------------------------------------------------------------ #
    # Healthcare & biomedical
    # ------------------------------------------------------------------ #
    "biomedical_bot": BotProfile(
        bot_name="biomedical_bot",
        display_name="BiomedicalBot",
        category="biomedical",
        github_queries=[
            "biomedical NLP python",
            "clinical trial data scraper",
            "PubMed paper scraper workflow",
        ],
        knowledge_topics=["biomedical NLP", "clinical trials", "drug discovery", "medical imaging AI"],
        monetization_keywords=["biomedical AI SaaS", "clinical data subscription", "pharma data revenue"],
        client_acquisition_keywords=["pharmaceutical companies", "biotech startups", "research hospitals"],
        competing_bots_queries=["clinical trial tracker alternative", "pubmed automation python"],
        self_improvement_topics=["entity recognition", "drug-disease graphs", "clinical outcome prediction"],
        description="Analyzes biomedical literature, clinical trials, and drug interaction data.",
    ),
    # ------------------------------------------------------------------ #
    # Finance & wealth
    # ------------------------------------------------------------------ #
    "finance_bot": BotProfile(
        bot_name="finance_bot",
        display_name="FinanceBot",
        category="finance",
        github_queries=[
            "personal finance automation python",
            "budget tracker bot github",
            "financial planning AI workflow",
        ],
        knowledge_topics=["personal finance", "budgeting", "wealth building", "investment planning"],
        monetization_keywords=["fintech SaaS pricing", "financial advisor bot subscription", "robo-advisor revenue"],
        client_acquisition_keywords=["millennials managing finances", "small business finance teams"],
        competing_bots_queries=["mint alternative python", "ynab automation bot"],
        self_improvement_topics=["spending pattern recognition", "debt reduction algorithms", "goal tracking"],
        description="Automates personal and business finance tracking, budgeting, and investment planning.",
    ),
    # ------------------------------------------------------------------ #
    # Bot generator / orchestration
    # ------------------------------------------------------------------ #
    "bot_generator_bot": BotProfile(
        bot_name="bot_generator_bot",
        display_name="BotGeneratorBot",
        category="meta-bots",
        github_queries=[
            "bot generator AI python",
            "automated bot creation workflow",
            "low-code bot builder github",
        ],
        knowledge_topics=["bot architecture", "code generation", "template engines", "meta-programming"],
        monetization_keywords=["bot marketplace revenue", "bot generation SaaS", "white-label bot platform"],
        client_acquisition_keywords=["entrepreneurs building bots", "agencies needing custom bots"],
        competing_bots_queries=["botpress alternative", "rasa alternative python generator"],
        self_improvement_topics=["template quality scoring", "bot performance benchmarks", "auto-deploy pipelines"],
        description="Generates fully-featured bots from natural-language descriptions.",
    ),
    # ------------------------------------------------------------------ #
    # Affiliate & monetization
    # ------------------------------------------------------------------ #
    "affiliate_bot": BotProfile(
        bot_name="affiliate_bot",
        display_name="AffiliateBot",
        category="affiliate-marketing",
        github_queries=[
            "affiliate marketing automation python",
            "amazon affiliate bot github",
            "clickbank automation workflow",
        ],
        knowledge_topics=["affiliate marketing", "product promotion", "commission tracking", "SEO content"],
        monetization_keywords=["affiliate SaaS", "commission optimization", "affiliate network revenue"],
        client_acquisition_keywords=["bloggers", "content creators", "affiliate marketers"],
        competing_bots_queries=["impact affiliate alternative", "shareasale automation python"],
        self_improvement_topics=["product matching algorithms", "click-through optimization", "conversion tracking"],
        description="Finds and promotes affiliate products to maximise commission revenue.",
    ),
    # ------------------------------------------------------------------ #
    # Catch-all / generic (used when no specific profile exists)
    # ------------------------------------------------------------------ #
    "_default": BotProfile(
        bot_name="_default",
        display_name="GenericBot",
        category="general",
        github_queries=[
            "automation bot python github",
            "AI agent workflow github actions",
        ],
        knowledge_topics=["automation", "AI agents", "bot frameworks"],
        monetization_keywords=["SaaS monetization", "bot revenue model"],
        client_acquisition_keywords=["businesses needing automation", "startups"],
        competing_bots_queries=["automation tool alternative python"],
        self_improvement_topics=["performance optimization", "error handling"],
        description="Generic Elite Scraper Bot for unregistered bot types.",
    ),
}


def get_profile(bot_name: str) -> BotProfile:
    """
    Return the ``BotProfile`` for *bot_name*, falling back to the default
    profile if no specific profile is registered.

    Parameters
    ----------
    bot_name : str
        Canonical bot directory name.

    Returns
    -------
    BotProfile
    """
    return BOT_PROFILES.get(bot_name, BOT_PROFILES["_default"])
