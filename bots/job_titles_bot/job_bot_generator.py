"""
DreamCo Job Bot Generator — creates AI worker bot specifications for any job title.

Given a job title from the database, generates a fully-specified AI worker bot
that can automate the core tasks of that role.

GLOBAL AI SOURCES FLOW: participates via job_titles_bot.py pipeline.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from framework import GlobalAISourcesFlow  # noqa: F401
from bots.job_titles_bot.job_titles_database import JobTitle


@dataclass
class AIWorkerBot:
    """Specification for an AI worker bot generated for a specific job title."""
    name: str
    job_title: str
    industry: str
    category: str
    automation_tasks: List[str]
    ai_models_required: List[str]
    estimated_monthly_cost_usd: float
    cost_justification: str
    payment_options: Dict[str, Any]
    capabilities: List[str]
    training_datasets: List[str]
    scalable: bool = True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "job_title": self.job_title,
            "industry": self.industry,
            "category": self.category,
            "automation_tasks": self.automation_tasks,
            "ai_models_required": self.ai_models_required,
            "estimated_monthly_cost_usd": self.estimated_monthly_cost_usd,
            "cost_justification": self.cost_justification,
            "payment_options": self.payment_options,
            "capabilities": self.capabilities,
            "training_datasets": self.training_datasets,
            "scalable": self.scalable,
        }

    def explain_cost(self) -> str:
        """Return a human-friendly explanation of costs and why they are worth it."""
        lines = [
            f"💰 Estimated monthly cost: ${self.estimated_monthly_cost_usd:.2f}",
            f"✅ Why it's worth it: {self.cost_justification}",
            "",
            "💳 Payment options:",
        ]
        for method, detail in self.payment_options.items():
            lines.append(f"  • {method}: {detail}")
        lines += [
            "",
            "🤖 This AI worker bot can:",
        ]
        for cap in self.capabilities:
            lines.append(f"  • {cap}")
        return "\n".join(lines)


# Default payment options available to all clients
_DEFAULT_PAYMENT_OPTIONS: Dict[str, str] = {
    "Free Tier": "Access via token credits — limited capacity, no charge",
    "Tokens": "Pay-as-you-go: purchase token bundles starting at $5",
    "Monthly Subscription": "Flat monthly rate for unlimited access ($49–$299/mo)",
    "Yearly Subscription": "Save 20% with an annual plan ($470–$2870/yr)",
}

# AI model recommendations by task type
_TASK_MODEL_MAP: Dict[str, List[str]] = {
    "natural language processing": ["GPT-4", "Claude 3", "Gemini Pro"],
    "document processing": ["GPT-4", "Document AI", "Textract"],
    "data analysis": ["GPT-4 Code Interpreter", "AutoML", "XGBoost"],
    "image recognition": ["GPT-4 Vision", "CLIP", "YOLOv8"],
    "face recognition": ["DeepFace", "AWS Rekognition", "Azure Face API"],
    "object recognition": ["YOLOv8", "CLIP", "GPT-4 Vision"],
    "voice/audio processing": ["Whisper", "ElevenLabs", "AssemblyAI"],
    "automation": ["GPT-4 Agents", "LangChain", "AutoGPT"],
    "code generation": ["GitHub Copilot", "GPT-4", "Codex"],
    "scheduling": ["GPT-4", "LangChain Agents", "Zapier AI"],
    "customer interaction": ["GPT-4", "Claude 3", "Dialogflow"],
    "financial modelling": ["GPT-4 Code Interpreter", "FinGPT", "AutoML"],
}


def _infer_ai_models(responsibilities: List[str], required_skills: List[str]) -> List[str]:
    """Infer the best AI models for a given set of responsibilities and skills."""
    text = " ".join(responsibilities + required_skills).lower()
    models: set = set()
    for task_type, model_list in _TASK_MODEL_MAP.items():
        # Match any word from the task type key
        if any(word in text for word in task_type.split("/")):
            models.update(model_list)
    if not models:
        # Default to general-purpose LLM for any remaining job
        models = {"GPT-4", "Claude 3"}
    return sorted(models)


def _estimate_cost(num_tasks: int, avg_salary: Optional[int]) -> float:
    """Estimate monthly running cost for an AI worker bot."""
    base_cost = 49.0  # base platform fee
    per_task_cost = num_tasks * 2.0  # $2 per task type per month
    return round(base_cost + per_task_cost, 2)


def _build_cost_justification(job: JobTitle, monthly_cost: float) -> str:
    annual_savings = (job.avg_salary_usd_annual or 50000) - (monthly_cost * 12)
    if annual_savings > 0:
        return (
            f"Replacing or augmenting a human {job.title} (avg ${job.avg_salary_usd_annual:,}/yr) "
            f"with this AI bot saves approximately ${annual_savings:,.0f} per year in labor costs "
            f"while operating 24/7 without breaks or benefits."
        )
    return (
        f"Augmenting human {job.title} work with AI reduces error rates, "
        f"increases throughput, and frees humans for higher-value creative tasks."
    )


class JobBotGeneratorError(Exception):
    """Raised when bot generation fails."""


class JobBotGenerator:
    """Generates AI worker bot specifications for any job title."""

    def generate(self, job: JobTitle) -> AIWorkerBot:
        """Generate an AI worker bot specification for the given job title."""
        ai_models = _infer_ai_models(job.responsibilities, job.required_skills)
        monthly_cost = _estimate_cost(len(job.responsibilities), job.avg_salary_usd_annual)
        cost_justification = _build_cost_justification(job, monthly_cost)

        # Build automation tasks from responsibilities
        automation_tasks = [f"Automate: {r}" for r in job.responsibilities]

        # Build capabilities list
        capabilities = [
            f"Perform '{r}' autonomously" for r in job.responsibilities
        ] + [
            f"Apply skill: {s}" for s in job.required_skills
        ]

        # Training datasets needed
        training_datasets = [
            f"{job.industry} industry documents and workflows",
            f"{job.title} task examples and outcomes",
            f"{job.category} domain knowledge corpus",
        ]

        bot_name = f"{job.title.title().replace(' ', '')}AIBot"

        return AIWorkerBot(
            name=bot_name,
            job_title=job.title,
            industry=job.industry,
            category=job.category,
            automation_tasks=automation_tasks,
            ai_models_required=ai_models,
            estimated_monthly_cost_usd=monthly_cost,
            cost_justification=cost_justification,
            payment_options=dict(_DEFAULT_PAYMENT_OPTIONS),
            capabilities=capabilities,
            training_datasets=training_datasets,
            scalable=True,
        )

    def generate_bulk(self, jobs: List[JobTitle]) -> List[AIWorkerBot]:
        """Generate AI worker bots for multiple job titles at once."""
        return [self.generate(job) for job in jobs]
