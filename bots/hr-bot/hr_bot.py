"""
bots/hr-bot/hr_bot.py

HRBot — job posting, resume screening, interview scheduling, and offer letter generation.
"""

from __future__ import annotations

import re
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

_SKILL_KEYWORDS: list[str] = [
    "python", "java", "javascript", "typescript", "sql", "aws", "docker",
    "kubernetes", "machine learning", "data analysis", "react", "node.js",
    "communication", "leadership", "agile", "scrum", "project management",
    "problem solving", "teamwork", "excel", "tableau", "power bi",
]

_OFFER_TEMPLATE = """\
OFFER LETTER

Date: {date}

{candidate_name}
{candidate_email}

Dear {candidate_first_name},

We are pleased to offer you the position of {position_title} at {company_name}.

POSITION DETAILS:
  Title:         {position_title}
  Department:    {department}
  Start Date:    {start_date}
  Compensation:  {salary} per year
  Location:      {location}
  Employment:    {employment_type}

BENEFITS:
  • Health, Dental, and Vision Insurance
  • 401(k) with company match up to 4%
  • {pto_days} days Paid Time Off per year
  • Remote work flexibility

This offer is contingent upon successful completion of a background check.
Please sign and return this letter by {acceptance_deadline}.

Sincerely,

{hr_name}
Human Resources
{company_name}
"""


class HRBot(BotBase):
    """
    Human Resources assistant for recruiting and employee lifecycle management.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="HRBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._job_postings: dict[str, dict[str, Any]] = {}
        self._interviews: dict[str, dict[str, Any]] = {}
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("HRBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("HRBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def post_job(
        self,
        title: str,
        description: str,
        requirements: list[str],
    ) -> dict[str, Any]:
        """
        Create a job posting.

        Args:
            title: Job title.
            description: Full job description.
            requirements: List of requirement strings.

        Returns:
            Job posting dict with generated ID and metadata.
        """
        job_id = str(uuid.uuid4())
        posting: dict[str, Any] = {
            "id": job_id,
            "title": title,
            "description": description,
            "requirements": requirements,
            "status": "active",
            "applications": [],
            "posted_at": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock_extra:
            self._job_postings[job_id] = posting
        self.log_activity(f"Job posted: '{title}' (id={job_id}).")
        return dict(posting)

    def screen_resume(self, resume_text: str) -> dict[str, Any]:
        """
        Screen a resume text for relevant skills and keywords.

        Args:
            resume_text: Plain-text resume content.

        Returns:
            Screening result with matched skills, score, and recommendation.
        """
        text_lower = resume_text.lower()
        matched_skills = [skill for skill in _SKILL_KEYWORDS if skill in text_lower]

        # Heuristic score
        base_score = len(matched_skills) * 5
        if re.search(r"\b\d+\s*(?:years?|yrs?)\s*(?:of\s+)?experience\b", text_lower):
            base_score += 15
        if re.search(r"\b(?:bachelor|master|phd|degree|university|college)\b", text_lower):
            base_score += 10
        score = min(base_score, 100)

        recommendation = (
            "Strong Candidate" if score >= 70
            else "Potential Candidate" if score >= 40
            else "Not a Match"
        )
        self.log_activity(f"Resume screened: score={score}, recommendation='{recommendation}'.")
        return {
            "matched_skills": matched_skills,
            "skill_count": len(matched_skills),
            "screening_score": score,
            "recommendation": recommendation,
            "word_count": len(resume_text.split()),
        }

    def schedule_interview(
        self,
        candidate_id: str,
        interviewer_id: str,
        time: str,
    ) -> dict[str, Any]:
        """
        Schedule an interview between a candidate and interviewer.

        Args:
            candidate_id: Candidate's ID.
            interviewer_id: Interviewer's ID.
            time: Interview date/time string.

        Returns:
            Interview schedule dict with confirmation ID.
        """
        interview_id = str(uuid.uuid4())
        interview: dict[str, Any] = {
            "id": interview_id,
            "candidate_id": candidate_id,
            "interviewer_id": interviewer_id,
            "scheduled_time": time,
            "status": "scheduled",
            "location": "Video Call (Teams/Zoom)",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "calendar_invite_sent": True,
            "reminder_sent": False,
        }
        with self._lock_extra:
            self._interviews[interview_id] = interview
        self.log_activity(
            f"Interview scheduled: candidate={candidate_id}, interviewer={interviewer_id}, time={time}."
        )
        return dict(interview)

    def generate_offer_letter(
        self,
        candidate: dict[str, Any],
        position: dict[str, Any],
    ) -> str:
        """
        Generate a formatted offer letter.

        Args:
            candidate: Dict with ``name``, ``email``.
            position: Dict with ``title``, ``department``, ``salary``,
                      ``start_date``, ``location``, ``employment_type``.

        Returns:
            Filled offer letter as a string.
        """
        name = candidate.get("name", "Candidate")
        first_name = name.split()[0] if name else "Candidate"
        today = datetime.now(timezone.utc)
        deadline = today.strftime("%B %d, %Y")

        letter = _OFFER_TEMPLATE.format(
            date=today.strftime("%B %d, %Y"),
            candidate_name=name,
            candidate_email=candidate.get("email", ""),
            candidate_first_name=first_name,
            position_title=position.get("title", "Position"),
            company_name=position.get("company", "DreamCobots Inc."),
            department=position.get("department", "Engineering"),
            start_date=position.get("start_date", "To be determined"),
            salary=f"${position.get('salary', 80_000):,.0f}",
            location=position.get("location", "Remote"),
            employment_type=position.get("employment_type", "Full-Time"),
            pto_days=position.get("pto_days", 20),
            acceptance_deadline=deadline,
            hr_name="HR Department",
        )
        self.log_activity(f"Offer letter generated for '{name}'.")
        return letter
