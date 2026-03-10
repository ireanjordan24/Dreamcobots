# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
# Feature 2: Business bot for project management.
# Functionality: Helps track project progress and deadlines.
# Use Cases: Managers overseeing multiple projects.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class ProjectManagementBot(BaseBot):
    """
    Business bot for tracking project milestones, deadlines, and team tasks.

    Provides status summaries, flags at-risk tasks, and sells project
    analytics datasets to PMO and agile-tooling companies.
    """

    def __init__(self):
        super().__init__(
            name="Project Manager Bot",
            domain="project_management",
            category="business",
        )
        self._projects = {}

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Agile Project Metrics Dataset",
            description="Sprint velocity, burndown charts, and delivery metrics from 1,000 teams.",
            domain="project_management",
            size_mb=85.0,
            price_usd=179.00,
            license="CC-BY-4.0",
            tags=["agile", "scrum", "metrics", "velocity"],
            ethical_review_passed=True,
        )

    def _setup_plans(self):
        super()._setup_plans()
        self.monetization.add_plan(PricingPlan(
            plan_id="team_plan",
            name="Team Plan",
            model=PricingModel.SUBSCRIPTION,
            price_usd=49.99,
            description="Full project management for teams up to 25 members.",
            features=["Unlimited projects", "Gantt charts", "Risk alerts", "Dataset access"],
        ))

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()

        if intent == "schedule":
            response = (
                f"{prefix}I'll add that deadline to your project timeline. "
                "Please share the project name, milestone, and due date."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer agile project metrics datasets."
                + self._dataset_offer()
            )
        elif intent == "greeting":
            response = (
                f"{prefix}Hello! I'm {self.name}. I help keep projects on track. "
                "Which project would you like to review today?"
            )
        elif intent == "help":
            response = (
                "I can: 📋 Track tasks & milestones  |  ⚠️ Flag at-risk items  |  "
                "📈 Generate progress reports  |  💾 Sell project metrics datasets."
            )
        else:
            response = (
                f"{prefix}Share your project details and I'll help you stay on schedule. "
                "What's the project name and current status?"
            )
        return response


if __name__ == "__main__":
    bot = ProjectManagementBot()
    print(bot.chat("Hi! I need to track our Q1 product launch milestones."))
    print(bot.chat("The deadline for feature freeze is March 15th."))
    print(bot.status())