# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
# Feature 2: Occupational bot for resume building.
# Functionality: Assists in creating and formatting resumes using user-provided information.
# Use Cases: Job seekers wanting a polished resume.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class ResumeBuildingBot(BaseBot):
    """
    Occupational bot that guides users through resume creation and formatting.

    Offers industry-specific templates, keyword optimisation advice, and
    sells a dataset of successful resume patterns to HR-tech companies.
    """

    _RESUME_SECTIONS = [
        "Contact Information",
        "Professional Summary",
        "Work Experience",
        "Education",
        "Skills",
        "Certifications",
        "Projects",
        "References",
    ]

    def __init__(self):
        super().__init__(
            name="Resume Builder Bot",
            domain="career_services",
            category="occupational",
        )
        self._current_section_index = 0

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="High-Performance Resume Patterns Dataset",
            description="50,000 anonymised resumes with hiring outcomes for ML training.",
            domain="career_services",
            size_mb=180.0,
            price_usd=199.00,
            license="Proprietary",
            tags=["resumes", "HR", "NLP", "hiring"],
            ethical_review_passed=True,
        )

    def _setup_plans(self):
        super()._setup_plans()
        self.monetization.add_plan(PricingPlan(
            plan_id="resume_pack",
            name="Resume Pack",
            model=PricingModel.ONE_TIME,
            price_usd=9.99,
            description="One-time purchase: 10 industry-specific resume templates.",
            features=["10 templates", "ATS-friendly formats", "Keyword suggestions"],
        ))

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()

        if intent == "resume_help":
            section = self._RESUME_SECTIONS[self._current_section_index % len(self._RESUME_SECTIONS)]
            self._current_section_index += 1
            response = (
                f"{prefix}Let's build your resume step by step. "
                f"Next section: **{section}**. "
                "Please share the relevant details and I'll format them for you."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer a dataset of high-performing resume patterns."
                + self._dataset_offer()
            )
        elif intent == "greeting":
            response = (
                f"{prefix}Hi! I'm {self.name}. I'll help you craft a standout resume. "
                "Tell me about your background and target role."
            )
        elif intent == "help":
            response = (
                "I can: ✏️ Guide resume sections  |  🎨 Suggest ATS-friendly formats  |"
                "  🔑 Recommend power keywords  |  💾 Sell resume datasets."
            )
        else:
            response = (
                f"{prefix}Tell me more about your experience so I can tailor your resume. "
                "What industry are you targeting?"
            )
        return response


if __name__ == "__main__":
    bot = ResumeBuildingBot()
    print(bot.chat("Hi, I need help building my resume for a data science role."))
    print(bot.chat("I have 3 years of Python and machine learning experience."))
    print(bot.status())