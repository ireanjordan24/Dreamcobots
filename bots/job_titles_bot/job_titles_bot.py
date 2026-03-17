"""
DreamCo Job Titles Bot — comprehensive AI workforce platform.

Combines:
* JobTitleDatabase  — searchable directory of all job titles
* JobBotGenerator   — creates AI worker bot specs for any job
* AutonomousTrainer — trains bots on job skills, face/object recognition,
                      and item valuation

Tiers
-----
FREE       — keyword search + 10 titles per industry
PRO        — full database + AI bot generation + hiring marketplace
ENTERPRISE — autonomous training + scalable Buddy Bot upgrades + API

GLOBAL AI SOURCES FLOW: uses GlobalAISourcesFlow pipeline.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from typing import List, Optional, Dict, Any

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.job_titles_bot.tiers import BOT_FEATURES, get_bot_tier_info
from bots.job_titles_bot.job_titles_database import JobTitleDatabase, JobTitle
from bots.job_titles_bot.job_bot_generator import JobBotGenerator, AIWorkerBot
from bots.job_titles_bot.autonomous_trainer import AutonomousTrainer, TrainingSession, ItemValuation
from framework import GlobalAISourcesFlow  # noqa: F401


class JobTitlesBotError(Exception):
    """Raised for general bot errors."""


class JobTitlesBotTierError(JobTitlesBotError):
    """Raised when a feature requires a higher tier."""


class JobTitlesBot:
    """
    DreamCo AI workforce platform — look up any job title, hire humans or AI
    bots, generate AI worker bots, and train them autonomously.
    """

    # Maximum job titles returned per search on the free tier
    FREE_SEARCH_LIMIT = 10

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self._db = JobTitleDatabase()
        self._generator = JobBotGenerator()
        self._trainer = AutonomousTrainer()

    # -----------------------------------------------------------------------
    # Tier helpers
    # -----------------------------------------------------------------------

    def get_tier_info(self) -> dict:
        """Return information about the current subscription tier."""
        return get_bot_tier_info(self.tier)

    def get_upgrade_suggestion(self) -> Optional[dict]:
        """Return the next upgrade tier info, or None if already at Enterprise."""
        next_tier_cfg = get_upgrade_path(self.tier)
        if next_tier_cfg is None:
            return None
        return {
            "upgrade_to": next_tier_cfg.name,
            "price_usd_monthly": next_tier_cfg.price_usd_monthly,
            "unlock_features": BOT_FEATURES[next_tier_cfg.tier.value],
        }

    def _require_tier(self, minimum: Tier) -> None:
        tier_order = list(Tier)
        if tier_order.index(self.tier) < tier_order.index(minimum):
            suggestion = self.get_upgrade_suggestion()
            msg = (
                f"This feature requires the {minimum.value.upper()} tier or higher. "
                f"You are currently on the {self.tier.value.upper()} tier."
            )
            if suggestion:
                msg += (
                    f" Upgrade to {suggestion['upgrade_to']} for "
                    f"${suggestion['price_usd_monthly']}/month to unlock: "
                    + ", ".join(suggestion["unlock_features"][:3]) + " and more."
                )
            raise JobTitlesBotTierError(msg)

    # -----------------------------------------------------------------------
    # Job title lookup (available on all tiers)
    # -----------------------------------------------------------------------

    def search_job_titles(self, keyword: str) -> List[dict]:
        """
        Search job titles by keyword.

        FREE tier  : returns up to 10 results.
        PRO+       : returns all matching results.
        """
        results = self._db.search(keyword)
        if self.tier == Tier.FREE:
            results = results[: self.FREE_SEARCH_LIMIT]
        return [j.to_dict() for j in results]

    def get_job_title(self, title: str) -> Optional[dict]:
        """Return full details for a job title (all tiers)."""
        job = self._db.get_by_title(title)
        return job.to_dict() if job else None

    def browse_industry(self, industry: str) -> List[dict]:
        """
        Browse job titles by industry.

        FREE tier  : up to 10 titles.
        PRO+       : all titles in the industry.
        """
        if self.tier == Tier.FREE:
            results = self._db.top_titles_by_industry(industry, limit=self.FREE_SEARCH_LIMIT)
        else:
            results = self._db.get_by_industry(industry)
        return [j.to_dict() for j in results]

    def list_industries(self) -> List[str]:
        """Return all available industries (all tiers)."""
        return self._db.list_industries()

    def list_all_job_titles(self) -> List[str]:
        """Return every job title in the database (PRO+ only)."""
        self._require_tier(Tier.PRO)
        return self._db.list_all_titles()

    def database_stats(self) -> dict:
        """Return statistics about the job title database (all tiers)."""
        return {
            "total_titles": self._db.count(),
            "industries": len(self._db.list_industries()),
            "automatable_by_ai": len(self._db.get_automatable_jobs()),
        }

    # -----------------------------------------------------------------------
    # AI worker bot generation (PRO+)
    # -----------------------------------------------------------------------

    def generate_ai_worker_bot(self, job_title: str) -> dict:
        """
        Generate an AI worker bot specification for a given job title.

        Returns the bot specification including cost explanation and
        payment options. Requires PRO tier or higher.
        """
        self._require_tier(Tier.PRO)
        job = self._db.get_by_title(job_title)
        if job is None:
            raise JobTitlesBotError(f"Job title '{job_title}' not found in the database.")
        bot = self._generator.generate(job)
        result = bot.to_dict()
        result["cost_explanation"] = bot.explain_cost()
        return result

    def generate_bulk_ai_bots(self, job_titles: List[str]) -> List[dict]:
        """
        Generate AI worker bots for multiple job titles at once.

        Requires ENTERPRISE tier.
        """
        self._require_tier(Tier.ENTERPRISE)
        results = []
        for title in job_titles:
            job = self._db.get_by_title(title)
            if job is None:
                continue
            bot = self._generator.generate(job)
            result = bot.to_dict()
            result["cost_explanation"] = bot.explain_cost()
            results.append(result)
        return results

    # -----------------------------------------------------------------------
    # Hiring marketplace (PRO+)
    # -----------------------------------------------------------------------

    def hire_worker(self, job_title: str, worker_type: str = "ai") -> dict:
        """
        Return a hiring package for a given job title.

        Parameters
        ----------
        job_title : str
            The job title to hire for.
        worker_type : str
            One of 'human', 'ai', or 'robot'.

        Requires PRO tier.
        """
        self._require_tier(Tier.PRO)
        job = self._db.get_by_title(job_title)
        if job is None:
            raise JobTitlesBotError(f"Job title '{job_title}' not found.")

        worker_type = worker_type.lower()
        valid_types = {"human", "ai", "robot"}
        if worker_type not in valid_types:
            raise JobTitlesBotError(f"worker_type must be one of {valid_types}.")

        base = {
            "job_title": job_title,
            "industry": job.industry,
            "worker_type": worker_type,
            "required_skills": job.required_skills,
            "education_required": job.education_required,
        }

        if worker_type == "human":
            base.update({
                "estimated_salary_usd_annual": job.avg_salary_usd_annual,
                "hiring_channels": ["LinkedIn", "Indeed", "Glassdoor", "ZipRecruiter", "DreamCo Marketplace"],
                "onboarding_time": "2-4 weeks",
                "note": "Post to DreamCo Marketplace to reach pre-screened candidates.",
            })
        elif worker_type == "ai":
            bot = self._generator.generate(job)
            base.update({
                "ai_bot_name": bot.name,
                "monthly_cost_usd": bot.estimated_monthly_cost_usd,
                "payment_options": bot.payment_options,
                "capabilities": bot.capabilities,
                "deployment_time": "Immediate",
                "cost_explanation": bot.explain_cost(),
            })
        else:  # robot
            base.update({
                "robot_contract_type": "DreamCo Robot Workforce Contract",
                "contact": "robotcontracts@dreamco.ai",
                "estimated_monthly_cost_usd": (job.avg_salary_usd_annual or 50000) / 12 * 0.6,
                "available_manufacturers": ["Boston Dynamics", "ABB Robotics", "FANUC", "Universal Robots", "Tesla Optimus"],
                "contract_note": "DreamCo negotiates robot manufacturing contracts to deploy physical robots for your workforce.",
            })

        return base

    # -----------------------------------------------------------------------
    # Autonomous training (ENTERPRISE)
    # -----------------------------------------------------------------------

    def train_bot_on_job(
        self,
        bot_name: str,
        job_title: str,
        examples: int = 100,
    ) -> dict:
        """
        Autonomously train a bot on all skills for a given job title.

        Requires ENTERPRISE tier.
        """
        self._require_tier(Tier.ENTERPRISE)
        job = self._db.get_by_title(job_title)
        if job is None:
            raise JobTitlesBotError(f"Job title '{job_title}' not found.")

        sessions = []
        for skill in job.required_skills:
            session = self._trainer.train_job_skill(
                bot_name=bot_name,
                skill_name=skill,
                domain=job.industry,
                examples=examples,
            )
            sessions.append(session.to_dict())

        return {
            "bot_name": bot_name,
            "job_title": job_title,
            "skills_trained": job.required_skills,
            "sessions": sessions,
            "buddy_bot_upgrade": "All registered Buddy Bots have been upgraded with these skills.",
        }

    def train_face_recognition(self, bot_name: str, num_faces: int = 50) -> dict:
        """
        Train a bot to recognize human faces. Requires ENTERPRISE tier.
        """
        self._require_tier(Tier.ENTERPRISE)
        session = self._trainer.train_face_recognition(bot_name, num_faces)
        return session.to_dict()

    def train_object_recognition(
        self,
        bot_name: str,
        object_classes: List[str],
        examples_per_class: int = 100,
    ) -> dict:
        """
        Train a bot to identify objects. Requires ENTERPRISE tier.
        """
        self._require_tier(Tier.ENTERPRISE)
        session = self._trainer.train_object_recognition(bot_name, object_classes, examples_per_class)
        return session.to_dict()

    def valuate_item(self, item_name: str) -> dict:
        """
        Estimate the value of an item (antique, coin, collectible, etc.).

        Available to all tiers — Buddy Bot always knows how to valuate.
        """
        valuation = self._trainer.valuate_item(item_name)
        return valuation.to_dict()

    # -----------------------------------------------------------------------
    # Buddy Bot management (ENTERPRISE)
    # -----------------------------------------------------------------------

    def register_buddy_bot(self, bot_id: str) -> None:
        """Register a Buddy Bot to receive automatic skill upgrades. ENTERPRISE only."""
        self._require_tier(Tier.ENTERPRISE)
        self._trainer.register_buddy_bot(bot_id)

    def list_buddy_bots(self) -> List[str]:
        """List all registered Buddy Bots. ENTERPRISE only."""
        self._require_tier(Tier.ENTERPRISE)
        return self._trainer.list_buddy_bots()

    def get_buddy_bot_skills(self, bot_id: str) -> List[str]:
        """Return all skills a registered Buddy Bot has been trained on. ENTERPRISE only."""
        self._require_tier(Tier.ENTERPRISE)
        return self._trainer.get_bot_skills(bot_id)

    # -----------------------------------------------------------------------
    # Automatable jobs listing (PRO+)
    # -----------------------------------------------------------------------

    def list_automatable_jobs(self) -> List[dict]:
        """
        Return all job titles that can be automated by AI.
        Requires PRO tier.
        """
        self._require_tier(Tier.PRO)
        return [j.to_dict() for j in self._db.get_automatable_jobs()]
