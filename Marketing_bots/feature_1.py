# Feature 1: Marketing bot for social media posting.
# Functionality: Automates posting updates to social media channels.
# Use Cases: Businesses maintaining an active online presence.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class SocialMediaBot(BaseBot):
    """
    Marketing bot that automates social media content creation and posting.

    Uses NLP to craft audience-appropriate messages and sells social-media
    performance datasets to marketing analytics firms.
    """

    _PLATFORM_TIPS = {
        "twitter":   "Keep it under 280 characters; use 1-2 relevant hashtags.",
        "instagram": "Lead with a compelling visual description; use up to 10 hashtags.",
        "linkedin":  "Professional tone; share insights or stats; tag relevant companies.",
        "facebook":  "Conversational tone; ask a question to drive engagement.",
    }

    def __init__(self):
        super().__init__(
            name="Social Media Bot",
            domain="digital_marketing",
            category="marketing",
        )
        self._posts_scheduled = 0

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Social Media Engagement Dataset",
            description="5M posts with engagement metrics (likes, shares, reach) across 4 platforms.",
            domain="digital_marketing",
            size_mb=560.0,
            price_usd=399.00,
            license="CC-BY-4.0",
            tags=["social media", "engagement", "marketing", "NLP"],
            ethical_review_passed=True,
        )

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        tokens = set(nlp_result.get("tokens", []))
        prefix = self._emotion_prefix()

        platform_hint = ""
        for platform, tip in self._PLATFORM_TIPS.items():
            if platform in tokens:
                platform_hint = f" Tip for {platform.title()}: {tip}"
                break

        if intent == "greeting":
            response = (
                f"{prefix}Hi! I'm {self.name}. Let's grow your social presence! "
                "Which platform are you targeting today?"
            )
        elif intent == "help":
            platforms = ", ".join(self._PLATFORM_TIPS.keys())
            response = (
                f"I can: ✍️ Draft posts  |  📅 Schedule content  |  "
                f"📊 Analyse engagement  |  Platforms: {platforms}."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer social media engagement datasets for marketing research."
                + self._dataset_offer()
            )
        else:
            self._posts_scheduled += 1
            response = (
                f"{prefix}I'll craft a post for you!{platform_hint} "
                f"(Scheduled posts: {self._posts_scheduled}) "
                "Share your message/topic and target audience."
            )
        return response


if __name__ == "__main__":
    bot = SocialMediaBot()
    print(bot.chat("Hi! I need to post about our new product launch on LinkedIn."))
    print(bot.chat("The product is an AI-powered scheduling tool for teams."))
    print(bot.status())