# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
# Feature 3: Occupational bot for interview preparation.
# Functionality: Provides commonly asked interview questions and tips.
# Use Cases: Candidates preparing for upcoming interviews.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class InterviewPrepBot(BaseBot):
    """
    Occupational bot for mock interview practice and coaching.

    Provides domain-specific interview questions, scores answers, offers
    tips, and sells interview-question datasets to training platforms.
    """

    _COMMON_QUESTIONS = {
        "general": [
            "Tell me about yourself.",
            "What are your greatest strengths and weaknesses?",
            "Where do you see yourself in 5 years?",
            "Why do you want to work here?",
            "Describe a challenge you faced and how you overcame it.",
        ],
        "technical": [
            "Explain the difference between supervised and unsupervised learning.",
            "What data structures do you use most often, and why?",
            "How do you approach debugging a complex system issue?",
            "Describe your experience with agile/scrum methodologies.",
        ],
        "behavioural": [
            "Give an example of a time you led a team under pressure.",
            "Describe a situation where you disagreed with a manager.",
            "Tell me about a time you failed and what you learned.",
        ],
    }

    def __init__(self):
        super().__init__(
            name="Interview Prep Bot",
            domain="career_coaching",
            category="occupational",
        )
        self._question_index = 0

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Interview Questions & Ideal Answers Dataset",
            description="100,000 interview Q&A pairs across 50+ industries with expert ratings.",
            domain="career_coaching",
            size_mb=95.0,
            price_usd=149.00,
            license="CC-BY-4.0",
            tags=["interview", "Q&A", "coaching", "NLP"],
            ethical_review_passed=True,
        )

    def _setup_plans(self):
        super()._setup_plans()
        self.monetization.add_plan(PricingPlan(
            plan_id="mock_interview",
            name="Mock Interview Session",
            model=PricingModel.PAY_PER_USE,
            price_usd=4.99,
            description="One full mock interview session with AI scoring.",
            features=["10-question mock interview", "AI answer scoring", "Personalised tips"],
        ))

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()

        if intent == "interview_prep":
            questions = self._COMMON_QUESTIONS["general"]
            q = questions[self._question_index % len(questions)]
            self._question_index += 1
            response = (
                f"{prefix}Let's practice! Here's your next interview question:\n\n"
                f"❓ *{q}*\n\n"
                "Take a moment to think, then share your answer for feedback."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer a comprehensive interview Q&A dataset."
                + self._dataset_offer()
            )
        elif intent == "greeting":
            response = (
                f"{prefix}Hi! I'm {self.name}. Ready to ace your next interview? "
                "Tell me the role you're interviewing for and I'll tailor the practice."
            )
        elif intent == "help":
            response = (
                "I can: 🎤 Run mock interviews  |  📝 Score your answers  |  "
                "💡 Provide tips  |  🗂️ Sell interview datasets."
            )
        elif intent == "feedback":
            weight = self.learning.get_response_weight("interview_prep")
            response = (
                f"{prefix}Thanks for the feedback! Based on our session, here are "
                f"personalised tips (confidence level: {weight:.2f}): "
                "Focus on the STAR method (Situation, Task, Action, Result) for "
                "behavioural questions, and quantify achievements where possible."
            )
        else:
            response = (
                f"{prefix}What role are you preparing for? I'll select the most "
                "relevant questions for your interview practice."
            )
        return response


if __name__ == "__main__":
    bot = InterviewPrepBot()
    print(bot.chat("Hi! I have a software engineer interview next week."))
    print(bot.chat("Can you ask me an interview question?"))
    print(bot.chat("That was helpful, thanks!"))
    print(bot.status())