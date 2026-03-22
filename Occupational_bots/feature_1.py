"""
Feature 1: Occupational Job Search Bot
Functionality: Helps users find job listings based on their skills and preferences.
  Searches across multiple job boards and filters by role, location, salary, and type.
Use Cases: Recent graduates seeking entry-level positions, professionals looking
  for career shifts, remote job seekers.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example job listing records
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "title": "Software Engineer",              "company": "TechCorp",       "location": "Austin, TX",       "salary_min": 90000,  "salary_max": 130000, "type": "full_time", "remote": True,  "experience": "mid",    "skills": ["Python","JavaScript","React"],        "platform": "LinkedIn",    "posted_days_ago": 2},
    {"id": 2,  "title": "Data Analyst",                   "company": "Analytics Inc",  "location": "Remote",           "salary_min": 65000,  "salary_max": 90000,  "type": "full_time", "remote": True,  "experience": "entry",  "skills": ["SQL","Tableau","Excel"],              "platform": "Indeed",      "posted_days_ago": 1},
    {"id": 3,  "title": "Product Manager",                "company": "StartupXYZ",     "location": "San Francisco, CA","salary_min": 130000, "salary_max": 180000, "type": "full_time", "remote": False, "experience": "senior", "skills": ["Product Strategy","Agile","Jira"],    "platform": "LinkedIn",    "posted_days_ago": 3},
    {"id": 4,  "title": "Marketing Manager",              "company": "BrandCo",        "location": "New York, NY",     "salary_min": 80000,  "salary_max": 110000, "type": "full_time", "remote": False, "experience": "mid",    "skills": ["SEO","Content Marketing","Analytics"], "platform": "Glassdoor",   "posted_days_ago": 4},
    {"id": 5,  "title": "UX Designer",                    "company": "DesignHub",      "location": "Remote",           "salary_min": 75000,  "salary_max": 105000, "type": "full_time", "remote": True,  "experience": "mid",    "skills": ["Figma","UX Research","Prototyping"],  "platform": "ZipRecruiter","posted_days_ago": 1},
    {"id": 6,  "title": "DevOps Engineer",                "company": "CloudFirst",     "location": "Seattle, WA",      "salary_min": 110000, "salary_max": 150000, "type": "full_time", "remote": True,  "experience": "senior", "skills": ["AWS","Docker","Kubernetes","CI/CD"],   "platform": "Indeed",      "posted_days_ago": 2},
    {"id": 7,  "title": "Sales Representative",           "company": "RevGrowth",      "location": "Dallas, TX",       "salary_min": 50000,  "salary_max": 80000,  "type": "full_time", "remote": False, "experience": "entry",  "skills": ["CRM","Cold Calling","Negotiation"],   "platform": "LinkedIn",    "posted_days_ago": 1},
    {"id": 8,  "title": "Machine Learning Engineer",      "company": "AI Ventures",    "location": "Remote",           "salary_min": 140000, "salary_max": 200000, "type": "full_time", "remote": True,  "experience": "senior", "skills": ["PyTorch","TensorFlow","Python","ML"],  "platform": "LinkedIn",    "posted_days_ago": 5},
    {"id": 9,  "title": "Customer Success Manager",       "company": "SaaS Pro",       "location": "Remote",           "salary_min": 70000,  "salary_max": 95000,  "type": "full_time", "remote": True,  "experience": "mid",    "skills": ["CRM","Communication","SaaS"],          "platform": "Indeed",      "posted_days_ago": 2},
    {"id": 10, "title": "Financial Analyst",              "company": "Finance Co",     "location": "Chicago, IL",      "salary_min": 70000,  "salary_max": 95000,  "type": "full_time", "remote": False, "experience": "entry",  "skills": ["Excel","Financial Modeling","CFA"],     "platform": "Glassdoor",   "posted_days_ago": 3},
    {"id": 11, "title": "Content Writer",                 "company": "ContentPlus",    "location": "Remote",           "salary_min": 45000,  "salary_max": 65000,  "type": "full_time", "remote": True,  "experience": "entry",  "skills": ["Writing","SEO","WordPress","Editing"], "platform": "ZipRecruiter","posted_days_ago": 1},
    {"id": 12, "title": "Cybersecurity Analyst",          "company": "SecureNet",      "location": "Washington, DC",   "salary_min": 85000,  "salary_max": 120000, "type": "full_time", "remote": False, "experience": "mid",    "skills": ["SIEM","Penetration Testing","CISSP"],  "platform": "LinkedIn",    "posted_days_ago": 4},
    {"id": 13, "title": "Project Manager",                "company": "PM Solutions",   "location": "Denver, CO",       "salary_min": 75000,  "salary_max": 100000, "type": "full_time", "remote": True,  "experience": "mid",    "skills": ["PMP","Agile","Scrum","Jira"],          "platform": "Indeed",      "posted_days_ago": 2},
    {"id": 14, "title": "React Developer",                "company": "WebTech",        "location": "Remote",           "salary_min": 85000,  "salary_max": 120000, "type": "full_time", "remote": True,  "experience": "mid",    "skills": ["React","TypeScript","CSS","REST API"], "platform": "LinkedIn",    "posted_days_ago": 1},
    {"id": 15, "title": "HR Business Partner",            "company": "PeopleFirst",    "location": "Atlanta, GA",      "salary_min": 70000,  "salary_max": 95000,  "type": "full_time", "remote": False, "experience": "mid",    "skills": ["HRIS","Employee Relations","Recruiting"],"platform": "Glassdoor",  "posted_days_ago": 3},
    {"id": 16, "title": "Operations Manager",             "company": "LogiCo",         "location": "Houston, TX",      "salary_min": 80000,  "salary_max": 110000, "type": "full_time", "remote": False, "experience": "senior", "skills": ["Operations","Supply Chain","ERP"],     "platform": "LinkedIn",    "posted_days_ago": 5},
    {"id": 17, "title": "Social Media Manager",           "company": "DigitalAgency",  "location": "Remote",           "salary_min": 50000,  "salary_max": 70000,  "type": "full_time", "remote": True,  "experience": "entry",  "skills": ["Social Media","Content","Analytics"],  "platform": "Indeed",      "posted_days_ago": 1},
    {"id": 18, "title": "Backend Developer (Node.js)",    "company": "AppFactory",     "location": "Remote",           "salary_min": 90000,  "salary_max": 125000, "type": "full_time", "remote": True,  "experience": "mid",    "skills": ["Node.js","Express","MongoDB","AWS"],   "platform": "ZipRecruiter","posted_days_ago": 2},
    {"id": 19, "title": "Business Analyst",               "company": "ConsultCo",      "location": "New York, NY",     "salary_min": 75000,  "salary_max": 100000, "type": "full_time", "remote": False, "experience": "mid",    "skills": ["Business Analysis","SQL","Tableau"],   "platform": "LinkedIn",    "posted_days_ago": 4},
    {"id": 20, "title": "Graphic Designer",               "company": "Creative Studio","location": "Remote",           "salary_min": 50000,  "salary_max": 75000,  "type": "full_time", "remote": True,  "experience": "entry",  "skills": ["Photoshop","Illustrator","Figma"],     "platform": "Indeed",      "posted_days_ago": 2},
    {"id": 21, "title": "QA Engineer",                    "company": "QualityTech",    "location": "Remote",           "salary_min": 75000,  "salary_max": 100000, "type": "full_time", "remote": True,  "experience": "mid",    "skills": ["Selenium","Test Automation","Python"],  "platform": "LinkedIn",    "posted_days_ago": 3},
    {"id": 22, "title": "Account Executive",              "company": "SalesForce Co",  "location": "San Francisco, CA","salary_min": 70000,  "salary_max": 120000, "type": "full_time", "remote": False, "experience": "mid",    "skills": ["B2B Sales","Negotiation","CRM"],       "platform": "Glassdoor",   "posted_days_ago": 1},
    {"id": 23, "title": "Data Scientist",                 "company": "DataDriven",     "location": "Remote",           "salary_min": 110000, "salary_max": 160000, "type": "full_time", "remote": True,  "experience": "senior", "skills": ["Python","R","Statistics","ML"],         "platform": "LinkedIn",    "posted_days_ago": 2},
    {"id": 24, "title": "Technical Support Specialist",   "company": "TechHelp",       "location": "Remote",           "salary_min": 45000,  "salary_max": 65000,  "type": "full_time", "remote": True,  "experience": "entry",  "skills": ["Technical Support","Communication"],  "platform": "Indeed",      "posted_days_ago": 1},
    {"id": 25, "title": "iOS Developer (Swift)",          "company": "AppMakers",      "location": "Austin, TX",       "salary_min": 100000, "salary_max": 140000, "type": "full_time", "remote": True,  "experience": "mid",    "skills": ["Swift","iOS","Xcode","UIKit"],         "platform": "LinkedIn",    "posted_days_ago": 3},
    {"id": 26, "title": "Legal Counsel",                  "company": "LawFirm LLC",    "location": "New York, NY",     "salary_min": 120000, "salary_max": 200000, "type": "full_time", "remote": False, "experience": "senior", "skills": ["Contract Law","Corporate Law","JD"],   "platform": "Glassdoor",   "posted_days_ago": 5},
    {"id": 27, "title": "Email Marketing Specialist",     "company": "GrowthAgency",   "location": "Remote",           "salary_min": 55000,  "salary_max": 75000,  "type": "full_time", "remote": True,  "experience": "entry",  "skills": ["Mailchimp","Klaviyo","Email Design"],  "platform": "ZipRecruiter","posted_days_ago": 2},
    {"id": 28, "title": "Scrum Master",                   "company": "AgileTeam",      "location": "Chicago, IL",      "salary_min": 85000,  "salary_max": 115000, "type": "full_time", "remote": True,  "experience": "mid",    "skills": ["Scrum","Agile","Jira","Facilitation"], "platform": "LinkedIn",    "posted_days_ago": 4},
    {"id": 29, "title": "Supply Chain Manager",           "company": "GlobalOps",      "location": "Dallas, TX",       "salary_min": 90000,  "salary_max": 125000, "type": "full_time", "remote": False, "experience": "senior", "skills": ["Supply Chain","SAP","Logistics"],      "platform": "Indeed",      "posted_days_ago": 3},
    {"id": 30, "title": "AI/ML Researcher",               "company": "DeepAI Labs",    "location": "Remote",           "salary_min": 160000, "salary_max": 250000, "type": "full_time", "remote": True,  "experience": "senior", "skills": ["Deep Learning","NLP","Research","PhD"],"platform": "LinkedIn",    "posted_days_ago": 1},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_results": 5,    "job_alerts": False, "ai_matching": False, "application_tracking": False},
    "PRO":        {"price_usd": 19,  "max_results": 50,   "job_alerts": True,  "ai_matching": True,  "application_tracking": True},
    "ENTERPRISE": {"price_usd": 49,  "max_results": None, "job_alerts": True,  "ai_matching": True,  "application_tracking": True},
}


class JobSearchBot:
    """Aggregates and filters job listings from LinkedIn, Indeed, Glassdoor, and more.

    Competes with Handshake and LinkedIn Jobs by combining multi-platform
    aggregation, AI skill matching, and automated job alert notifications.
    Monetization: $19/month PRO or $49/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="JobSearchBot")
        self._applications: list[dict] = []
        self._saved_jobs: list[int] = []

    def _limit_results(self, results: list[dict]) -> list[dict]:
        limit = self._config["max_results"]
        return results[:limit] if limit else results

    def search_jobs(self, *, title: str | None = None, location: str | None = None,
                    remote_only: bool = False, min_salary: float | None = None,
                    experience: str | None = None) -> list[dict]:
        """Search job listings with filters."""
        results = list(EXAMPLES)
        if title:
            results = [j for j in results if title.lower() in j["title"].lower()]
        if location:
            results = [j for j in results if location.lower() in j["location"].lower() or j["remote"]]
        if remote_only:
            results = [j for j in results if j["remote"]]
        if min_salary is not None:
            results = [j for j in results if j["salary_min"] >= min_salary]
        if experience:
            results = [j for j in results if j["experience"] == experience.lower()]
        return self._limit_results(results)

    def get_job(self, job_id: int) -> dict:
        """Get details of a specific job listing."""
        job = next((j for j in EXAMPLES if j["id"] == job_id), None)
        if job is None:
            raise ValueError(f"Job ID {job_id} not found.")
        return dict(job)

    def get_remote_jobs(self) -> list[dict]:
        """Return all remote job listings."""
        return self._limit_results([j for j in EXAMPLES if j["remote"]])

    def get_jobs_by_platform(self, platform: str) -> list[dict]:
        """Return jobs from a specific platform."""
        return self._limit_results([j for j in EXAMPLES if j["platform"].lower() == platform.lower()])

    def get_top_paying_jobs(self, count: int = 5) -> list[dict]:
        """Return the top N highest-paying jobs."""
        return sorted(EXAMPLES, key=lambda j: j["salary_max"], reverse=True)[:count]

    def get_ai_job_matches(self, skills: list[str]) -> list[dict]:
        """Return AI-matched jobs based on user skills (PRO/ENTERPRISE)."""
        if not self._config["ai_matching"]:
            raise PermissionError(
                "AI job matching requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        skills_lower = [s.lower() for s in skills]
        scored = []
        for job in EXAMPLES:
            job_skills_lower = [s.lower() for s in job["skills"]]
            matches = sum(1 for s in skills_lower if any(s in js for js in job_skills_lower))
            if matches > 0:
                scored.append({**job, "match_score": round(matches / len(job["skills"]) * 100, 1)})
        scored.sort(key=lambda j: j["match_score"], reverse=True)
        return self._limit_results(scored)

    def track_application(self, job_id: int, status: str = "applied") -> dict:
        """Track a job application (PRO/ENTERPRISE)."""
        if not self._config["application_tracking"]:
            raise PermissionError(
                "Application tracking requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        job = self.get_job(job_id)
        app = {
            "application_id": f"APP-{len(self._applications) + 1:04d}",
            "job_id": job_id,
            "title": job["title"],
            "company": job["company"],
            "status": status,
        }
        self._applications.append(app)
        return app

    def save_job(self, job_id: int) -> dict:
        """Save a job for later review."""
        job = self.get_job(job_id)
        if job_id not in self._saved_jobs:
            self._saved_jobs.append(job_id)
        return {"saved": True, "job_id": job_id, "title": job["title"]}

    def get_saved_jobs(self) -> list[dict]:
        """Return all saved job listings."""
        return [self.get_job(jid) for jid in self._saved_jobs]

    def get_search_stats(self) -> dict:
        """Return statistics about available job listings."""
        by_platform: dict[str, int] = {}
        by_experience: dict[str, int] = {}
        remote_count = 0
        for j in EXAMPLES:
            by_platform[j["platform"]] = by_platform.get(j["platform"], 0) + 1
            by_experience[j["experience"]] = by_experience.get(j["experience"], 0) + 1
            if j["remote"]:
                remote_count += 1
        salaries = [j["salary_min"] for j in EXAMPLES]
        return {
            "total_listings": len(EXAMPLES),
            "remote_jobs": remote_count,
            "avg_min_salary": round(sum(salaries) / len(salaries), 0),
            "by_platform": by_platform,
            "by_experience": by_experience,
            "tier": self.tier,
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_results"] if cfg["max_results"] else "unlimited"
        lines = [
            f"=== JobSearchBot — {self.tier} Tier ===",
            f"  Monthly price         : ${cfg['price_usd']}/month",
            f"  Max search results    : {limit}",
            f"  Job alerts            : {'enabled' if cfg['job_alerts'] else 'disabled'}",
            f"  AI skill matching     : {'enabled' if cfg['ai_matching'] else 'disabled'}",
            f"  Application tracking  : {'enabled' if cfg['application_tracking'] else 'disabled'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "job_search", "listings_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "stats": self.get_search_stats()}


if __name__ == "__main__":
    bot = JobSearchBot(tier="PRO")
    remote = bot.get_remote_jobs()
    print(f"Remote jobs: {len(remote)}")
    top_paying = bot.get_top_paying_jobs(3)
    print("Top 3 paying jobs:")
    for j in top_paying:
        print(f"  💰 {j['title']} at {j['company']} — ${j['salary_max']:,}/yr")
    matches = bot.get_ai_job_matches(["Python", "Machine Learning", "SQL"])
    print(f"\nAI-matched jobs (Python/ML/SQL): {len(matches)} results")
    print(bot.describe_tier())