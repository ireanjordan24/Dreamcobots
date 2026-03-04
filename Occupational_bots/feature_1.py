"""
Feature 1: Occupational bot that assists with job searches.
Functionality: This bot helps users find job listings based on their skills and preferences.
Use Cases: Recent graduates seeking entry-level positions, professionals looking for career shifts.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uuid
from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class JobSearchBot(BotBase):
    """Finds and curates job listings matching user skills and preferences."""

    def __init__(self) -> None:
        super().__init__("JobSearchBot", AutonomyLevel.FULLY_AUTONOMOUS, ScalingLevel.MODERATE)
        self._job_database: list = []

    def add_job(self, title: str, company: str, location: str, skills: list, salary_range: str) -> dict:
        """Add a job listing to the internal database."""
        job = {
            "job_id": str(uuid.uuid4()), "title": title, "company": company,
            "location": location, "skills": [s.lower() for s in skills],
            "salary_range": salary_range,
        }
        self._job_database.append(job)
        return {"status": "ok", "job_id": job["job_id"]}

    def search(self, skills: list, location: str = None) -> list:
        """Return jobs matching at least one skill; optionally filter by location."""
        user_skills = {s.lower() for s in skills}
        results = [j for j in self._job_database if user_skills & set(j["skills"])]
        if location:
            results = [j for j in results if location.lower() in j["location"].lower()]
        return results

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "search_jobs":
            jobs = self.search(task.get("skills", []), task.get("location"))
            return {"status": "ok", "count": len(jobs), "jobs": jobs}
        return super()._run_task(task)


if __name__ == "__main__":
    bot = JobSearchBot()
    bot.start()
    bot.add_job("Python Developer", "TechCorp", "Remote", ["python", "django"], "$80k-$120k")
    print(bot.search(["python"]))
    bot.stop()