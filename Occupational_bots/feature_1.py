# Feature 1: Occupational bot that assists with job searches.
# Functionality: This bot helps users find job listings based on their skills and preferences.
# Use Cases: Recent graduates seeking entry-level positions, professionals looking for career shifts.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot, DatasetManager
from framework.monetization import PricingPlan, PricingModel


class JobSearchBot(BaseBot):
    """
    Occupational bot for job searching (Occupational Outlook Handbook aligned).

    Helps users discover job listings, explore career paths, and understand
    labour-market trends.  Sells curated job-market datasets to recruiters
    and HR professionals.
    """

    def __init__(self):
        super().__init__(
            name="JobSearch Bot",
            domain="employment",
            category="occupational",
        )

    # ------------------------------------------------------------------
    # Dataset registration
    # ------------------------------------------------------------------

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="US Job Listings Corpus 2024",
            description="1M anonymised job postings with salary ranges, skills, and locations.",
            domain="employment",
            size_mb=420.0,
            price_usd=299.00,
            license="CC-BY-4.0",
            tags=["jobs", "salaries", "skills", "NLP"],
            ethical_review_passed=True,
        )
        self.datasets.create_dataset(
            name="Occupational Outlook Handbook Structured Data",
            description="Structured extracts from the BLS Occupational Outlook Handbook.",
            domain="employment",
            size_mb=15.0,
            price_usd=49.00,
            license="Public Domain",
            tags=["BLS", "OOH", "careers", "labour-market"],
            ethical_review_passed=True,
        )

    # ------------------------------------------------------------------
    # Response builder
    # ------------------------------------------------------------------

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()

        if intent == "job_search":
            response = (
                f"{prefix}I can help you find job listings! "
                "Tell me your skills, preferred location, and desired salary range, "
                "and I'll match you with the best opportunities."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I have curated job-market datasets available for purchase. "
                + self._dataset_offer()
            )
        elif intent == "greeting":
            response = (
                f"{prefix}Hello! I'm {self.name}. I specialise in job searches and "
                "career guidance. How can I help you today?"
            )
        elif intent == "help":
            response = (
                "I can: 🔍 Search jobs by skill/location  |  📊 Provide labour-market "
                "insights  |  💾 Sell job-market datasets  |  💰 Show salary ranges."
            )
        else:
            context = nlp_result.get("context_summary", "")
            response = (
                f"{prefix}I'm here to assist with your job search. "
                f"{context}  What skills or roles are you exploring?"
            )

        return response


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    bot = JobSearchBot()
    print(bot.chat("Hello! I'm looking for software engineering jobs in New York."))
    print(bot.chat("Do you have any datasets I can purchase?"))
    print(bot.status())