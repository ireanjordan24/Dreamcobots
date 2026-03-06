"""
bots/marketing-bot/marketing_bot.py

MarketingBot — campaign creation, content generation, audience analysis, and metrics tracking.
"""

from __future__ import annotations

import random
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

_CONTENT_TEMPLATES: dict[str, dict[str, str]] = {
    "twitter": {
        "template": "🚀 {hook} — {value_prop}. {cta} #{tag1} #{tag2}",
        "max_chars": 280,
    },
    "linkedin": {
        "template": (
            "{hook}\n\n"
            "Here's what we've learned about {topic}:\n\n"
            "→ {point1}\n"
            "→ {point2}\n"
            "→ {point3}\n\n"
            "{cta}\n\n"
            "#{tag1} #{tag2} #{tag3}"
        ),
        "max_chars": 3000,
    },
    "instagram": {
        "template": "✨ {hook} ✨\n\n{value_prop}\n\n{cta}\n\n#{tag1} #{tag2} #{tag3} #{tag4}",
        "max_chars": 2200,
    },
    "email": {
        "template": (
            "Subject: {hook}\n\n"
            "Hi {first_name},\n\n"
            "{value_prop}\n\n"
            "{point1}\n"
            "{point2}\n\n"
            "{cta}\n\n"
            "Best regards,\nThe DreamCobots Team"
        ),
        "max_chars": 5000,
    },
}


class MarketingBot(BotBase):
    """
    Marketing automation bot for campaign management, content creation, and analytics.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="MarketingBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._campaigns: dict[str, dict[str, Any]] = {}
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("MarketingBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("MarketingBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def generate_campaign(self, goal: str, budget: float) -> dict[str, Any]:
        """
        Generate a marketing campaign plan.

        Args:
            goal: Campaign goal (e.g. ``"brand awareness"``, ``"lead gen"``).
            budget: Total campaign budget.

        Returns:
            Campaign plan dict with ID, channels, and allocation.
        """
        campaign_id = str(uuid.uuid4())
        channels = {
            "social_media": round(budget * 0.35, 2),
            "paid_search": round(budget * 0.30, 2),
            "email": round(budget * 0.15, 2),
            "content": round(budget * 0.10, 2),
            "influencer": round(budget * 0.10, 2),
        }
        campaign = {
            "id": campaign_id,
            "goal": goal,
            "budget": budget,
            "channel_allocation": channels,
            "duration_weeks": 4,
            "kpis": self._get_kpis_for_goal(goal),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "draft",
        }
        with self._lock_extra:
            self._campaigns[campaign_id] = campaign
        self.log_activity(f"Campaign created: id={campaign_id}, goal='{goal}'.")
        return campaign

    def create_content(self, topic: str, platform: str) -> str:
        """
        Generate platform-specific marketing content for *topic*.

        Args:
            topic: Content topic.
            platform: Target platform (``twitter``, ``linkedin``, ``instagram``, ``email``).

        Returns:
            Generated content string.
        """
        tmpl_cfg = _CONTENT_TEMPLATES.get(platform.lower(), _CONTENT_TEMPLATES["twitter"])
        tag = topic.lower().replace(" ", "")
        content = tmpl_cfg["template"].format(
            hook=f"Discover the future of {topic}",
            value_prop=f"We're transforming how businesses handle {topic}",
            cta="Learn more at dreamcobots.ai",
            topic=topic,
            point1=f"✅ Increased efficiency in {topic} by 40%",
            point2=f"✅ Reduced costs associated with {topic} by 25%",
            point3=f"✅ Improved {topic} outcomes in 90% of use cases",
            first_name="there",
            tag1=tag,
            tag2="DreamCobots",
            tag3="AI",
            tag4="Innovation",
        )[:tmpl_cfg["max_chars"]]
        self.log_activity(f"Content created for topic='{topic}', platform='{platform}'.")
        return content

    def analyze_audience(self, demographics: dict[str, Any]) -> dict[str, Any]:
        """
        Analyse audience demographics and recommend targeting strategy.

        Args:
            demographics: Dict with optional keys ``age_range``, ``gender``,
                          ``interests``, ``location``.

        Returns:
            Audience analysis and targeting recommendations.
        """
        age_range = demographics.get("age_range", "25-44")
        interests = demographics.get("interests", [])
        location = demographics.get("location", "US")

        recommended_channels = []
        if "18-24" in age_range or "Gen Z" in str(interests):
            recommended_channels.extend(["TikTok", "Instagram Reels", "YouTube Shorts"])
        if "25-44" in age_range:
            recommended_channels.extend(["LinkedIn", "Facebook", "Instagram"])
        if "45+" in age_range:
            recommended_channels.extend(["Facebook", "Email", "YouTube"])
        if not recommended_channels:
            recommended_channels = ["Facebook", "Google Ads", "Email"]

        self.log_activity("Audience analysed.")
        return {
            "demographics": demographics,
            "estimated_reach": random.randint(10_000, 500_000),
            "recommended_channels": list(set(recommended_channels)),
            "peak_engagement_time": "Tuesday–Thursday, 9am–11am or 6pm–8pm",
            "content_format_preference": random.choice(["video", "carousel", "infographic", "long-form"]),
            "avg_cpc": f"${random.uniform(0.5, 5.0):.2f}",
        }

    def track_campaign_metrics(self, campaign_id: str) -> dict[str, Any]:
        """
        Return simulated performance metrics for a campaign.

        Args:
            campaign_id: The campaign's ID.

        Returns:
            Metrics dict with impressions, clicks, conversions, and ROAS.

        Raises:
            KeyError: If *campaign_id* is not found.
        """
        with self._lock_extra:
            campaign = self._campaigns.get(campaign_id)
        if campaign is None:
            raise KeyError(f"Campaign '{campaign_id}' not found.")

        impressions = random.randint(10_000, 500_000)
        clicks = random.randint(100, impressions // 10)
        conversions = random.randint(1, clicks // 5)
        revenue = conversions * random.uniform(20, 200)
        spend = campaign["budget"]

        self.log_activity(f"Metrics tracked for campaign '{campaign_id}'.")
        return {
            "campaign_id": campaign_id,
            "impressions": impressions,
            "clicks": clicks,
            "ctr_pct": round(clicks / impressions * 100, 3),
            "conversions": conversions,
            "conversion_rate_pct": round(conversions / clicks * 100, 2) if clicks > 0 else 0,
            "revenue": round(revenue, 2),
            "spend": spend,
            "roas": round(revenue / spend, 2) if spend > 0 else 0,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_kpis_for_goal(goal: str) -> list[str]:
        gl = goal.lower()
        if "awareness" in gl:
            return ["Impressions", "Reach", "Brand Recall Lift"]
        if "lead" in gl or "acquisition" in gl:
            return ["Cost Per Lead", "Lead Volume", "MQL Rate"]
        if "sales" in gl or "revenue" in gl:
            return ["ROAS", "Conversion Rate", "Revenue Generated"]
        return ["CTR", "Engagement Rate", "Conversions"]
