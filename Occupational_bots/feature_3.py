"""
Feature 3: Occupational bot for interview preparation.
Functionality: Provides commonly asked interview questions and tips.
Use Cases: Candidates preparing for upcoming interviews.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import random
from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


_QUESTION_BANK = {
    "general": [
        "Tell me about yourself.",
        "What are your greatest strengths and weaknesses?",
        "Where do you see yourself in 5 years?",
        "Why do you want to work here?",
        "Describe a challenge you faced and how you overcame it.",
    ],
    "technical": [
        "Explain the difference between REST and GraphQL.",
        "What is a race condition and how do you prevent it?",
        "Describe a design pattern you have used recently.",
        "How would you optimise a slow database query?",
        "What is the difference between concurrency and parallelism?",
    ],
    "behavioural": [
        "Give an example of a time you demonstrated leadership.",
        "Describe a situation where you disagreed with a teammate.",
        "Tell me about a time you missed a deadline and what you learned.",
        "How do you prioritise when handling multiple urgent tasks?",
        "Describe your most successful project and your role in it.",
    ],
}

_TIPS = [
    "Research the company thoroughly before your interview.",
    "Use the STAR method (Situation, Task, Action, Result) for behavioural answers.",
    "Prepare 3-5 insightful questions to ask the interviewer.",
    "Practice answers out loud to build confidence.",
    "Arrive (or log in) 10 minutes early.",
    "Send a thank-you email within 24 hours of the interview.",
]


class InterviewPrepBot(BotBase):
    """Prepares candidates for job interviews with curated questions and tips."""

    def __init__(self) -> None:
        super().__init__("InterviewPrepBot", AutonomyLevel.FULLY_AUTONOMOUS, ScalingLevel.CONSERVATIVE)

    def get_questions(self, category: str = "general", count: int = 5) -> dict:
        """Return a random selection of interview questions for a category."""
        if category not in _QUESTION_BANK:
            return {"status": "error", "message": f"Unknown category '{category}'. Choose from {list(_QUESTION_BANK.keys())}"}
        questions = random.sample(_QUESTION_BANK[category], min(count, len(_QUESTION_BANK[category])))
        return {"status": "ok", "category": category, "questions": questions}

    def get_tips(self, count: int = 3) -> dict:
        """Return a random selection of interview tips."""
        tips = random.sample(_TIPS, min(count, len(_TIPS)))
        return {"status": "ok", "tips": tips}

    def mock_interview(self, category: str = "general") -> dict:
        """Simulate a short mock interview session."""
        questions = self.get_questions(category, count=3)["questions"]
        tips = self.get_tips(count=2)["tips"]
        return {"status": "ok", "mock_questions": questions, "preparation_tips": tips}

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "mock_interview":
            return self.mock_interview(task.get("category", "general"))
        return super()._run_task(task)


if __name__ == "__main__":
    bot = InterviewPrepBot()
    bot.start()
    session = bot.mock_interview("technical")
    for q in session["mock_questions"]:
        print(f"Q: {q}")
    print("\nTips:")
    for t in session["preparation_tips"]:
        print(f"  • {t}")
    bot.stop()