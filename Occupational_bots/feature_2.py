"""
Feature 2: Occupational bot for resume building.
Functionality: Assists in creating and formatting resumes using user-provided information.
Use Cases: Job seekers wanting a polished resume.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class ResumeBuilderBot(BotBase):
    """Generates polished resumes from user-provided information."""

    SECTIONS = ["contact", "summary", "experience", "education", "skills", "certifications"]

    def __init__(self) -> None:
        super().__init__("ResumeBuilderBot", AutonomyLevel.SEMI_AUTONOMOUS, ScalingLevel.MODERATE)

    def build_resume(self, data: dict) -> dict:
        """
        Generate a structured resume from *data*.

        Expected keys: name, email, phone, summary, experience (list),
        education (list), skills (list), certifications (list, optional).
        """
        missing = [s for s in ["name", "email", "summary", "experience", "education", "skills"] if s not in data]
        if missing:
            return {"status": "error", "message": f"Missing required fields: {missing}"}

        resume = {
            "name": data["name"],
            "contact": {"email": data["email"], "phone": data.get("phone", "")},
            "summary": data["summary"],
            "experience": data["experience"],
            "education": data["education"],
            "skills": data["skills"],
            "certifications": data.get("certifications", []),
        }
        return {"status": "ok", "resume": resume}

    def format_as_text(self, resume: dict) -> str:
        """Format a resume dict as plain text."""
        lines = [
            resume["name"],
            f"Email: {resume['contact']['email']} | Phone: {resume['contact']['phone']}",
            "", "SUMMARY", resume["summary"], "",
            "EXPERIENCE",
            *[f"  - {e}" for e in resume["experience"]], "",
            "EDUCATION",
            *[f"  - {e}" for e in resume["education"]], "",
            "SKILLS", ", ".join(resume["skills"]),
        ]
        if resume.get("certifications"):
            lines += ["", "CERTIFICATIONS", *[f"  - {c}" for c in resume["certifications"]]]
        return "\n".join(lines)

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "build_resume":
            return self.build_resume(task.get("data", {}))
        return super()._run_task(task)


if __name__ == "__main__":
    bot = ResumeBuilderBot()
    bot.start()
    result = bot.build_resume({
        "name": "Jane Doe", "email": "jane@example.com", "phone": "555-1234",
        "summary": "Experienced software engineer.", "experience": ["TechCorp 2022-2025"],
        "education": ["BSc Computer Science, MIT 2022"], "skills": ["Python", "AI", "Bots"],
    })
    if result["status"] == "ok":
        print(bot.format_as_text(result["resume"]))
    bot.stop()