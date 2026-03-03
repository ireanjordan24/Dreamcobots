"""DreamCobots Marketplace - browse, purchase, and manage AI bots."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from marketplace.pricing import ALL_TIERS, REVENUE_SHARE


BOT_CATALOG = [
    {"name": "government-contract-grant-bot", "category": "government", "description": "Finds and applies for federal contracts and grants.", "base_price": 49, "revenue_potential": "High"},
    {"name": "hustle-bot", "category": "revenue", "description": "Tracks revenue goals and optimizes income streams.", "base_price": 49, "revenue_potential": "Very High"},
    {"name": "referral-bot", "category": "marketing", "description": "Manages 50% commission referral programs.", "base_price": 49, "revenue_potential": "Very High"},
    {"name": "buddy-bot", "category": "general", "description": "Central AI assistant coordinating all bots.", "base_price": 99, "revenue_potential": "High"},
    {"name": "entrepreneur-bot", "category": "business", "description": "Business plans, market research, and startup guidance.", "base_price": 49, "revenue_potential": "High"},
    {"name": "medical-bot", "category": "medical", "description": "Health information with HIPAA compliance.", "base_price": 149, "revenue_potential": "Very High"},
    {"name": "legal-bot", "category": "legal", "description": "Contract generation and legal document drafting.", "base_price": 149, "revenue_potential": "Very High"},
    {"name": "finance-bot", "category": "financial", "description": "Budgeting, portfolio analysis, and tax optimization.", "base_price": 99, "revenue_potential": "High"},
    {"name": "real-estate-bot", "category": "real_estate", "description": "Property valuation and investment analysis.", "base_price": 99, "revenue_potential": "High"},
    {"name": "ecommerce-bot", "category": "ecommerce", "description": "Listing optimization and sales forecasting.", "base_price": 49, "revenue_potential": "High"},
    {"name": "marketing-bot", "category": "marketing", "description": "SEO, content creation, and campaign management.", "base_price": 49, "revenue_potential": "High"},
    {"name": "education-bot", "category": "education", "description": "Personalized learning plans and quizzes.", "base_price": 49, "revenue_potential": "Medium"},
    {"name": "cybersecurity-bot", "category": "cybersecurity", "description": "Security audits and compliance guidance.", "base_price": 149, "revenue_potential": "Very High"},
    {"name": "hr-bot", "category": "hr", "description": "Job descriptions, resume screening, and HR compliance.", "base_price": 49, "revenue_potential": "Medium"},
    {"name": "farewell-bot", "category": "funeral", "description": "Compassionate funeral planning and memorial services.", "base_price": 149, "revenue_potential": "High"},
]


class Marketplace:
    """DreamCobots Marketplace for browsing, purchasing, and managing AI bots."""

    def __init__(self):
        """Initialize the marketplace."""
        self._purchases = []

    def list_bots(self) -> list:
        """Return all available bots with descriptions and pricing."""
        return [
            {
                **bot,
                "pricing": self.get_pricing(bot["name"]),
                "revenue_share": "50%",
            }
            for bot in BOT_CATALOG
        ]

    def purchase_bot(self, bot_name: str, tier: str) -> dict:
        """Simulate purchasing a bot at a given tier."""
        bot = next((b for b in BOT_CATALOG if b["name"] == bot_name), None)
        if not bot:
            return {"error": f"Bot '{bot_name}' not found in marketplace"}
        tier_info = next((t for t in ALL_TIERS if t["name"].lower() == tier.lower()), None)
        if not tier_info:
            return {"error": f"Tier '{tier}' not found. Available: Starter, Professional, Enterprise, Master"}
        purchase = {
            "purchase_id": f"DC-{len(self._purchases) + 1:06d}",
            "bot_name": bot_name,
            "tier": tier,
            "price_monthly": tier_info["price_monthly"],
            "purchased_at": datetime.utcnow().isoformat(),
            "status": "active",
            "revenue_share": "50%",
            "download_kit": f"https://dreamcobots.com/download/{bot_name}",
        }
        self._purchases.append(purchase)
        return purchase

    def get_pricing(self, bot_name: str) -> dict:
        """Get pricing tiers for a specific bot."""
        bot = next((b for b in BOT_CATALOG if b["name"] == bot_name), None)
        if not bot:
            return {}
        base = bot.get("base_price", 49)
        return {
            "Starter": f"${base}/month",
            "Professional": f"${base * 3}/month",
            "Enterprise": f"${base * 10}/month",
            "Master": f"${base * 20}/month",
        }

    def get_revenue_share(self) -> dict:
        """Return the platform revenue share information."""
        return REVENUE_SHARE

    def browse_by_category(self, category: str) -> list:
        """Filter bots by category."""
        category_lower = category.lower()
        return [b for b in BOT_CATALOG if b["category"].lower() == category_lower]

    def download_kit(self, bot_name: str) -> dict:
        """Simulate downloading a bot kit."""
        bot = next((b for b in BOT_CATALOG if b["name"] == bot_name), None)
        if not bot:
            return {"error": f"Bot '{bot_name}' not found"}
        return {
            "bot_name": bot_name,
            "download_url": f"https://dreamcobots.com/download/{bot_name}.zip",
            "kit_contents": [
                f"{bot_name}.py",
                "requirements.txt",
                "README.md",
                "config.example.json",
                "compliance_checklist.pdf",
            ],
            "version": "2.0.0",
            "downloaded_at": datetime.utcnow().isoformat(),
        }

    def get_categories(self) -> list:
        """Return all unique bot categories."""
        return list(set(b["category"] for b in BOT_CATALOG))
