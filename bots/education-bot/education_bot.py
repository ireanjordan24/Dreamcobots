"""
bots/education-bot/education_bot.py

EducationBot — lesson planning, quiz generation, progress tracking, and resource recommendations.
"""

from __future__ import annotations

import random
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

_RESOURCE_DB: dict[str, list[dict[str, str]]] = {
    "python": [
        {"title": "Python.org Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "documentation"},
        {"title": "Automate the Boring Stuff with Python", "url": "https://automatetheboringstuff.com", "type": "book"},
        {"title": "Real Python", "url": "https://realpython.com", "type": "tutorial"},
    ],
    "machine learning": [
        {"title": "fast.ai Practical Deep Learning", "url": "https://course.fast.ai", "type": "course"},
        {"title": "Scikit-learn User Guide", "url": "https://scikit-learn.org/stable/user_guide.html", "type": "documentation"},
        {"title": "Hands-On ML with Scikit-Learn & TensorFlow", "url": "https://oreilly.com/library/view/hands-on-machine-learning", "type": "book"},
    ],
    "mathematics": [
        {"title": "Khan Academy Math", "url": "https://khanacademy.org/math", "type": "course"},
        {"title": "MIT OpenCourseWare Mathematics", "url": "https://ocw.mit.edu/courses/mathematics/", "type": "course"},
        {"title": "Paul's Online Math Notes", "url": "https://tutorial.math.lamar.edu", "type": "tutorial"},
    ],
    "english": [
        {"title": "Grammarly Blog", "url": "https://grammarly.com/blog", "type": "blog"},
        {"title": "Purdue OWL", "url": "https://owl.purdue.edu", "type": "reference"},
        {"title": "Coursera English Composition", "url": "https://coursera.org", "type": "course"},
    ],
}


class EducationBot(BotBase):
    """
    Education and learning assistant for lesson planning, quizzes, and progress tracking.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="EducationBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._student_progress: dict[str, dict[str, Any]] = {}
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("EducationBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("EducationBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def create_lesson_plan(self, subject: str, level: str) -> dict[str, Any]:
        """
        Create a structured lesson plan.

        Args:
            subject: Subject area.
            level: Proficiency level (``beginner``, ``intermediate``, ``advanced``).

        Returns:
            Lesson plan dict with modules, objectives, and duration.
        """
        level_lower = level.lower()
        weeks = {"beginner": 8, "intermediate": 6, "advanced": 4}.get(level_lower, 6)
        modules = []
        for i in range(1, weeks + 1):
            modules.append({
                "week": i,
                "title": f"Module {i}: {subject} — Week {i} Content",
                "objectives": [
                    f"Understand core concept {i} in {subject}",
                    f"Apply {subject} techniques to practical problems",
                    f"Complete exercises and assessments",
                ],
                "duration_hours": 3,
                "assessment": f"Quiz {i}" if i % 2 == 0 else "Practice exercises",
            })
        self.log_activity(f"Lesson plan created: subject='{subject}', level='{level}'.")
        return {
            "subject": subject,
            "level": level,
            "total_weeks": weeks,
            "total_hours": weeks * 3,
            "modules": modules,
            "prerequisites": f"Basic knowledge of {subject}" if level_lower != "beginner" else "None",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def generate_quiz(self, topic: str, num_questions: int) -> list[dict[str, Any]]:
        """
        Generate a multiple-choice quiz for *topic*.

        Args:
            topic: Quiz topic.
            num_questions: Number of questions to generate.

        Returns:
            List of question dicts with options and correct answer.
        """
        num_questions = max(1, min(num_questions, 20))
        questions = []
        for i in range(1, num_questions + 1):
            correct = random.randint(0, 3)
            options = [
                f"Option A for Q{i}",
                f"Option B for Q{i}",
                f"Option C for Q{i}",
                f"Option D for Q{i}",
            ]
            options[correct] = f"Correct answer for {topic} Q{i}"
            questions.append({
                "question_id": i,
                "question": f"Question {i}: Which of the following best describes {topic} concept {i}?",
                "options": options,
                "correct_index": correct,
                "points": 1,
            })
        self.log_activity(f"Quiz generated: topic='{topic}', {num_questions} questions.")
        return questions

    def track_progress(self, student_id: str) -> dict[str, Any]:
        """
        Return learning progress for *student_id*.

        Args:
            student_id: Student identifier.

        Returns:
            Progress dict with completed modules, scores, and next steps.
        """
        with self._lock_extra:
            progress = self._student_progress.get(student_id)
            if progress is None:
                # Initialise new student record
                progress = {
                    "student_id": student_id,
                    "enrolled_at": datetime.now(timezone.utc).isoformat(),
                    "completed_modules": [],
                    "quiz_scores": {},
                    "total_hours": 0.0,
                    "badges": [],
                    "next_module": "Module 1",
                }
                self._student_progress[student_id] = progress
        return dict(progress)

    def record_module_completion(
        self, student_id: str, module: str, score: float, hours: float
    ) -> None:
        """
        Record that a student has completed a module.

        Args:
            student_id: Student identifier.
            module: Module name or number.
            score: Assessment score (0-100).
            hours: Time spent on the module.
        """
        with self._lock_extra:
            progress = self._student_progress.setdefault(student_id, {
                "student_id": student_id,
                "enrolled_at": datetime.now(timezone.utc).isoformat(),
                "completed_modules": [],
                "quiz_scores": {},
                "total_hours": 0.0,
                "badges": [],
                "next_module": "Module 1",
            })
            if module not in progress["completed_modules"]:
                progress["completed_modules"].append(module)
            progress["quiz_scores"][module] = score
            progress["total_hours"] = round(progress["total_hours"] + hours, 1)
            if score >= 90:
                progress["badges"].append(f"Excellence in {module}")
        self.log_activity(f"Module '{module}' completed by student '{student_id}' (score={score}).")

    def recommend_resources(self, topic: str) -> list[dict[str, str]]:
        """
        Recommend learning resources for *topic*.

        Args:
            topic: Learning topic.

        Returns:
            List of resource dicts with title, URL, and type.
        """
        topic_lower = topic.lower()
        resources = next(
            (v for k, v in _RESOURCE_DB.items() if k in topic_lower or topic_lower in k),
            [
                {"title": f"Search '{topic}' on Coursera", "url": "https://coursera.org", "type": "course"},
                {"title": f"Search '{topic}' on Khan Academy", "url": "https://khanacademy.org", "type": "course"},
                {"title": f"'{topic}' on Wikipedia", "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}", "type": "reference"},
            ],
        )
        self.log_activity(f"Resources recommended for topic='{topic}'.")
        return list(resources)
