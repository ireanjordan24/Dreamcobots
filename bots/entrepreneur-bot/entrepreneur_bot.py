"""
bots/entrepreneur-bot/entrepreneur_bot.py

EntrepreneurBot — business idea generation, market analysis, and planning.
"""

from __future__ import annotations

import random
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

_INDUSTRY_IDEAS: dict[str, list[str]] = {
    "tech": [
        "AI-powered customer support chatbot",
        "No-code website builder for small businesses",
        "Cybersecurity audit SaaS for SMEs",
        "API monitoring and alerting platform",
    ],
    "health": [
        "Remote patient monitoring wearables",
        "Mental health journaling app with AI insights",
        "Telehealth platform for rural communities",
        "Personalised nutrition planning service",
    ],
    "education": [
        "Gamified coding curriculum for kids",
        "AI tutoring platform for STEM subjects",
        "Corporate microlearning mobile app",
        "Language exchange social network",
    ],
    "finance": [
        "Automated invoice factoring for freelancers",
        "Micro-investment app for Gen Z",
        "Crypto portfolio tax-reporting tool",
        "Peer-to-peer lending marketplace",
    ],
    "ecommerce": [
        "Sustainable product marketplace",
        "Subscription box for niche hobbies",
        "B2B wholesale platform for artisans",
        "Live-commerce SaaS for brands",
    ],
}

_MARKET_SIZES: dict[str, str] = {
    "tech": "$5T global market",
    "health": "$8.9T global market",
    "education": "$7.3T global market",
    "finance": "$22.5T global market",
    "ecommerce": "$6.3T global market",
}


class EntrepreneurBot(BotBase):
    """
    Helps entrepreneurs generate ideas, analyse markets, and create plans.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="EntrepreneurBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("EntrepreneurBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("EntrepreneurBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def generate_business_idea(self, industry: str) -> dict[str, Any]:
        """
        Generate a business idea for the given industry.

        Args:
            industry: e.g. ``tech``, ``health``, ``education``, ``finance``, ``ecommerce``.

        Returns:
            Dict with ``idea``, ``industry``, ``potential``, and ``next_steps``.
        """
        ind = industry.lower().strip()
        ideas = _INDUSTRY_IDEAS.get(ind, _INDUSTRY_IDEAS["tech"])
        idea = random.choice(ideas)
        self.log_activity(f"Generated business idea for '{ind}'.")
        return {
            "idea": idea,
            "industry": ind,
            "potential": "High" if ind in ("tech", "health", "finance") else "Medium",
            "next_steps": [
                "Validate with 10 potential customers",
                "Build a minimal viable product (MVP)",
                "Launch on Product Hunt or App Store",
                "Seek seed funding or bootstrap",
            ],
        }

    def analyze_market(self, niche: str) -> dict[str, Any]:
        """
        Produce a market analysis for *niche*.

        Args:
            niche: Market niche or industry keyword.

        Returns:
            Dict with market size, trends, competition level, and entry barriers.
        """
        niche_lower = niche.lower()
        market_size = next(
            (v for k, v in _MARKET_SIZES.items() if k in niche_lower),
            "$1T+ addressable market",
        )
        self.log_activity(f"Market analysis for '{niche}'.")
        return {
            "niche": niche,
            "market_size": market_size,
            "growth_rate": f"{random.randint(5, 25)}% CAGR",
            "competition_level": random.choice(["Low", "Medium", "High"]),
            "entry_barriers": random.choice(["Low", "Medium", "High"]),
            "key_trends": [
                "AI and automation adoption",
                "Mobile-first consumer behaviour",
                "Sustainability and ESG compliance",
                "Remote work acceleration",
            ],
            "target_demographics": ["18-35 tech-savvy professionals", "SME owners", "Remote workers"],
        }

    def create_business_plan(self, idea: dict[str, Any]) -> dict[str, Any]:
        """
        Create a basic business plan for *idea*.

        Args:
            idea: Output of :meth:`generate_business_idea`.

        Returns:
            Structured business plan dict.
        """
        idea_name = idea.get("idea", "New Business")
        self.log_activity(f"Business plan created for '{idea_name}'.")
        return {
            "business_name": f"{idea_name} Inc.",
            "executive_summary": f"A startup focused on '{idea_name}' targeting an underserved market.",
            "value_proposition": "Solving a real pain point with a scalable, tech-driven solution.",
            "revenue_model": "SaaS subscription + usage-based pricing",
            "go_to_market": [
                "Content marketing and SEO",
                "Partner with industry influencers",
                "Launch freemium tier to drive adoption",
            ],
            "financial_projections": {
                "year_1_revenue": "$120,000",
                "year_2_revenue": "$500,000",
                "year_3_revenue": "$1,500,000",
            },
            "team_requirements": ["Founder/CEO", "CTO", "Head of Marketing", "Sales Lead"],
            "risks": ["Market saturation", "Regulatory changes", "Funding shortfall"],
        }

    def estimate_revenue(self, model: dict[str, Any]) -> float:
        """
        Estimate annual revenue from a simplified revenue model.

        Args:
            model: Dict with optional keys ``customers``, ``avg_revenue``,
                   ``churn_rate`` (0-1), ``growth_rate`` (0-1).

        Returns:
            Estimated annual revenue as a float.
        """
        customers = float(model.get("customers", 100))
        avg_revenue = float(model.get("avg_revenue", 99.0))
        churn_rate = float(model.get("churn_rate", 0.05))
        growth_rate = float(model.get("growth_rate", 0.10))

        retained = customers * (1 - churn_rate)
        end_of_year = retained * (1 + growth_rate)
        avg_customers = (customers + end_of_year) / 2
        revenue = round(avg_customers * avg_revenue * 12, 2)
        self.log_activity(f"Revenue estimated: ${revenue}")
        return revenue
