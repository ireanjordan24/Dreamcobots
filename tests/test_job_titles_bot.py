"""Tests for bots/job_titles_bot/ — JobTitlesBot, JobTitleDatabase, JobBotGenerator, AutonomousTrainer."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.job_titles_bot.job_titles_bot import JobTitlesBot, JobTitlesBotError, JobTitlesBotTierError
from bots.job_titles_bot.job_titles_database import JobTitleDatabase, JobTitle
from bots.job_titles_bot.job_bot_generator import JobBotGenerator, AIWorkerBot
from bots.job_titles_bot.autonomous_trainer import AutonomousTrainer, TrainingSession, ItemValuation
from bots.job_titles_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ===========================================================================
# Tiers
# ===========================================================================

class TestJobTitlesBotTiers:
    def test_free_tier_info(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0
        assert "search job titles by keyword" in info["features"]

    def test_pro_tier_info(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] == 49.0
        assert "generate AI worker bot for any job" in info["features"]

    def test_enterprise_tier_info(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["tier"] == "enterprise"
        assert "autonomous AI worker training" in info["features"]

    def test_bot_features_all_tiers_defined(self):
        for tier in Tier:
            assert tier.value in BOT_FEATURES
            assert len(BOT_FEATURES[tier.value]) > 0


# ===========================================================================
# JobTitleDatabase
# ===========================================================================

class TestJobTitleDatabase:
    def setup_method(self):
        self.db = JobTitleDatabase()

    def test_database_has_many_titles(self):
        assert self.db.count() >= 50

    def test_list_all_titles_returns_sorted_list(self):
        titles = self.db.list_all_titles()
        assert isinstance(titles, list)
        assert len(titles) >= 50
        assert titles == sorted(titles)

    def test_list_industries_returns_sorted_nonempty(self):
        industries = self.db.list_industries()
        assert len(industries) >= 10
        assert industries == sorted(industries)

    def test_list_categories_returns_sorted_nonempty(self):
        categories = self.db.list_categories()
        assert len(categories) >= 10
        assert categories == sorted(categories)

    def test_search_by_keyword_engineer(self):
        results = self.db.search("engineer")
        assert len(results) >= 3
        for j in results:
            assert isinstance(j, JobTitle)

    def test_search_by_keyword_returns_relevant(self):
        results = self.db.search("software")
        titles = [j.title.lower() for j in results]
        assert any("software" in t for t in titles)

    def test_search_by_skill(self):
        results = self.db.search("Python")
        assert len(results) >= 2

    def test_search_case_insensitive(self):
        results_lower = self.db.search("engineer")
        results_upper = self.db.search("ENGINEER")
        assert len(results_lower) == len(results_upper)

    def test_search_no_results(self):
        results = self.db.search("zzz_nonexistent_job_xyzxyz")
        assert results == []

    def test_get_by_title_exact(self):
        job = self.db.get_by_title("Software Engineer")
        assert job is not None
        assert job.title == "Software Engineer"
        assert job.industry == "Technology"

    def test_get_by_title_case_insensitive(self):
        job = self.db.get_by_title("software engineer")
        assert job is not None

    def test_get_by_title_not_found(self):
        job = self.db.get_by_title("Quantum Pizza Chef")
        assert job is None

    def test_get_by_industry_technology(self):
        jobs = self.db.get_by_industry("Technology")
        assert len(jobs) >= 5
        for j in jobs:
            assert j.industry == "Technology"

    def test_get_by_industry_case_insensitive(self):
        jobs_lower = self.db.get_by_industry("technology")
        jobs_title = self.db.get_by_industry("Technology")
        assert len(jobs_lower) == len(jobs_title)

    def test_get_by_industry_not_found(self):
        jobs = self.db.get_by_industry("MadeUpIndustry9999")
        assert jobs == []

    def test_get_automatable_jobs(self):
        jobs = self.db.get_automatable_jobs()
        assert len(jobs) >= 10
        for j in jobs:
            assert j.automatable_by_ai is True

    def test_top_titles_by_industry_limit(self):
        jobs = self.db.top_titles_by_industry("Technology", limit=3)
        assert len(jobs) <= 3

    def test_top_titles_by_industry_default_limit(self):
        jobs = self.db.top_titles_by_industry("Technology")
        assert len(jobs) <= 10

    def test_job_title_has_all_fields(self):
        job = self.db.get_by_title("Software Engineer")
        assert isinstance(job.title, str) and job.title
        assert isinstance(job.industry, str) and job.industry
        assert isinstance(job.category, str) and job.category
        assert isinstance(job.responsibilities, list) and len(job.responsibilities) > 0
        assert isinstance(job.required_skills, list) and len(job.required_skills) > 0
        assert isinstance(job.education_required, str) and job.education_required
        assert isinstance(job.description, str) and job.description
        assert isinstance(job.automatable_by_ai, bool)

    def test_job_to_dict(self):
        job = self.db.get_by_title("Software Engineer")
        d = job.to_dict()
        assert isinstance(d, dict)
        for key in ("title", "industry", "category", "responsibilities",
                    "required_skills", "education_required", "avg_salary_usd_annual",
                    "automatable_by_ai", "description"):
            assert key in d

    def test_multiple_industries_covered(self):
        industries = self.db.list_industries()
        for ind in ["Technology", "Healthcare", "Finance", "Education", "Legal",
                    "Engineering", "Business", "Manufacturing"]:
            assert ind in industries, f"Expected industry '{ind}' in database"


# ===========================================================================
# JobBotGenerator
# ===========================================================================

class TestJobBotGenerator:
    def setup_method(self):
        self.db = JobTitleDatabase()
        self.gen = JobBotGenerator()

    def _get_job(self, title: str) -> JobTitle:
        job = self.db.get_by_title(title)
        assert job is not None, f"Job '{title}' must be in the database"
        return job

    def test_generate_returns_ai_worker_bot(self):
        job = self._get_job("Software Engineer")
        bot = self.gen.generate(job)
        assert isinstance(bot, AIWorkerBot)

    def test_generated_bot_has_name(self):
        job = self._get_job("Software Engineer")
        bot = self.gen.generate(job)
        assert isinstance(bot.name, str) and len(bot.name) > 0

    def test_generated_bot_has_job_title(self):
        job = self._get_job("Software Engineer")
        bot = self.gen.generate(job)
        assert bot.job_title == "Software Engineer"

    def test_generated_bot_has_industry(self):
        job = self._get_job("Software Engineer")
        bot = self.gen.generate(job)
        assert bot.industry == "Technology"

    def test_generated_bot_has_ai_models(self):
        job = self._get_job("Software Engineer")
        bot = self.gen.generate(job)
        assert isinstance(bot.ai_models_required, list)
        assert len(bot.ai_models_required) > 0

    def test_generated_bot_has_monthly_cost(self):
        job = self._get_job("Software Engineer")
        bot = self.gen.generate(job)
        assert bot.estimated_monthly_cost_usd > 0

    def test_generated_bot_has_payment_options(self):
        job = self._get_job("Software Engineer")
        bot = self.gen.generate(job)
        assert "Free Tier" in bot.payment_options
        assert "Tokens" in bot.payment_options
        assert "Monthly Subscription" in bot.payment_options
        assert "Yearly Subscription" in bot.payment_options

    def test_generated_bot_has_capabilities(self):
        job = self._get_job("Software Engineer")
        bot = self.gen.generate(job)
        assert isinstance(bot.capabilities, list)
        assert len(bot.capabilities) > 0

    def test_generated_bot_has_automation_tasks(self):
        job = self._get_job("Software Engineer")
        bot = self.gen.generate(job)
        assert isinstance(bot.automation_tasks, list)
        assert len(bot.automation_tasks) == len(job.responsibilities)

    def test_generated_bot_is_scalable(self):
        job = self._get_job("Software Engineer")
        bot = self.gen.generate(job)
        assert bot.scalable is True

    def test_explain_cost_returns_string(self):
        job = self._get_job("Accountant")
        bot = self.gen.generate(job)
        explanation = bot.explain_cost()
        assert isinstance(explanation, str)
        assert "cost" in explanation.lower() or "$" in explanation
        assert "payment" in explanation.lower()

    def test_explain_cost_mentions_payment_options(self):
        job = self._get_job("Accountant")
        bot = self.gen.generate(job)
        explanation = bot.explain_cost()
        assert "Free Tier" in explanation or "Tokens" in explanation

    def test_bot_to_dict(self):
        job = self._get_job("Data Scientist")
        bot = self.gen.generate(job)
        d = bot.to_dict()
        assert isinstance(d, dict)
        for key in ("name", "job_title", "industry", "category", "automation_tasks",
                    "ai_models_required", "estimated_monthly_cost_usd", "payment_options",
                    "capabilities", "training_datasets", "scalable"):
            assert key in d

    def test_generate_bulk(self):
        jobs = [self.db.get_by_title(t) for t in ["Software Engineer", "Accountant", "Nurse"]]
        jobs = [j for j in jobs if j is not None]
        bots = self.gen.generate_bulk(jobs)
        assert len(bots) == len(jobs)
        for bot in bots:
            assert isinstance(bot, AIWorkerBot)

    def test_generate_different_jobs_different_bots(self):
        job1 = self._get_job("Software Engineer")
        job2 = self._get_job("Accountant")
        bot1 = self.gen.generate(job1)
        bot2 = self.gen.generate(job2)
        assert bot1.job_title != bot2.job_title
        assert bot1.name != bot2.name


# ===========================================================================
# AutonomousTrainer
# ===========================================================================

class TestAutonomousTrainer:
    def setup_method(self):
        self.trainer = AutonomousTrainer()

    # --- Job skill training ---

    def test_train_job_skill_returns_session(self):
        session = self.trainer.train_job_skill("MyBot", "customer service", "Retail")
        assert isinstance(session, TrainingSession)

    def test_training_session_is_complete(self):
        session = self.trainer.train_job_skill("MyBot", "invoicing", "Finance")
        assert session.status == "complete"

    def test_training_session_has_accuracy(self):
        session = self.trainer.train_job_skill("MyBot", "data entry", "Admin", examples=200)
        assert 0 < session.accuracy_pct <= 100

    def test_training_session_id_unique(self):
        s1 = self.trainer.train_job_skill("BotA", "skill1", "Domain")
        s2 = self.trainer.train_job_skill("BotA", "skill2", "Domain")
        assert s1.session_id != s2.session_id

    def test_get_bot_skills_after_training(self):
        self.trainer.train_job_skill("BotX", "Python", "Technology")
        self.trainer.train_job_skill("BotX", "SQL", "Technology")
        skills = self.trainer.get_bot_skills("BotX")
        assert "Python" in skills
        assert "SQL" in skills

    def test_get_bot_skills_empty_for_unknown_bot(self):
        skills = self.trainer.get_bot_skills("UnknownBot")
        assert skills == []

    def test_list_sessions(self):
        self.trainer.train_job_skill("BotA", "skill1", "Domain")
        self.trainer.train_job_skill("BotA", "skill2", "Domain")
        sessions = self.trainer.list_sessions()
        assert len(sessions) >= 2

    def test_session_to_dict(self):
        session = self.trainer.train_job_skill("BotA", "research", "Science")
        d = session.to_dict()
        assert isinstance(d, dict)
        for key in ("session_id", "skill_name", "domain", "examples_used", "accuracy_pct", "status"):
            assert key in d

    # --- Face recognition training ---

    def test_train_face_recognition(self):
        session = self.trainer.train_face_recognition("BuddyBot1", num_faces=100)
        assert isinstance(session, TrainingSession)
        assert "face_recognition" in session.skill_name

    def test_face_recognition_skill_registered(self):
        self.trainer.train_face_recognition("BuddyBot2", num_faces=50)
        skills = self.trainer.get_bot_skills("BuddyBot2")
        assert "face_recognition" in skills

    # --- Object recognition training ---

    def test_train_object_recognition(self):
        session = self.trainer.train_object_recognition("BotV", ["coin", "antique", "painting"])
        assert isinstance(session, TrainingSession)
        assert "coin" in session.skill_name

    def test_object_recognition_examples_count(self):
        session = self.trainer.train_object_recognition("BotW", ["coin", "stamp"], examples_per_class=200)
        assert session.examples_used == 400

    # --- Buddy Bot propagation ---

    def test_register_buddy_bot(self):
        self.trainer.register_buddy_bot("Buddy_1")
        assert "Buddy_1" in self.trainer.list_buddy_bots()

    def test_register_buddy_bot_deduplication(self):
        self.trainer.register_buddy_bot("Buddy_2")
        self.trainer.register_buddy_bot("Buddy_2")
        bots = self.trainer.list_buddy_bots()
        assert bots.count("Buddy_2") == 1

    def test_skill_propagates_to_buddy_bots(self):
        self.trainer.register_buddy_bot("Buddy_A")
        self.trainer.register_buddy_bot("Buddy_B")
        self.trainer.train_job_skill("MainBot", "negotiation", "Sales")
        assert "negotiation" in self.trainer.get_bot_skills("Buddy_A")
        assert "negotiation" in self.trainer.get_bot_skills("Buddy_B")

    def test_multiple_skills_propagate(self):
        self.trainer.register_buddy_bot("Buddy_C")
        self.trainer.train_job_skill("MainBot", "accounting", "Finance")
        self.trainer.train_job_skill("MainBot", "tax law", "Finance")
        skills = self.trainer.get_bot_skills("Buddy_C")
        assert "accounting" in skills
        assert "tax law" in skills

    # --- Item valuation ---

    def test_valuate_penny(self):
        val = self.trainer.valuate_item("penny")
        assert isinstance(val, ItemValuation)
        assert val.item_type == "coin"
        assert val.estimated_value_usd_low > 0
        assert val.estimated_value_usd_high >= val.estimated_value_usd_low

    def test_valuate_antique_clock(self):
        val = self.trainer.valuate_item("antique clock")
        assert val.item_type == "antique"
        assert len(val.value_factors) > 0
        assert isinstance(val.recommended_action, str) and len(val.recommended_action) > 0

    def test_valuate_vintage_painting(self):
        val = self.trainer.valuate_item("vintage painting")
        assert val.item_type == "art"

    def test_valuate_sports_card(self):
        val = self.trainer.valuate_item("sports card")
        assert val.item_type == "collectible"

    def test_valuate_unknown_item_returns_fallback(self):
        val = self.trainer.valuate_item("alien artifact xyz123")
        assert val.item_type == "unknown"
        assert val.estimated_value_usd_high > 0
        assert "appraiser" in val.recommended_action.lower()

    def test_valuate_item_to_dict(self):
        val = self.trainer.valuate_item("penny")
        d = val.to_dict()
        assert isinstance(d, dict)
        for key in ("item_name", "item_type", "estimated_value_usd_low",
                    "estimated_value_usd_high", "confidence_pct", "value_factors",
                    "recommended_action"):
            assert key in d

    def test_valuate_case_insensitive(self):
        val_lower = self.trainer.valuate_item("penny")
        val_upper = self.trainer.valuate_item("PENNY")
        assert val_lower.item_type == val_upper.item_type

    def test_list_valuatable_items(self):
        items = self.trainer.list_valuatable_items()
        assert isinstance(items, list)
        assert len(items) >= 10
        assert "penny" in items


# ===========================================================================
# JobTitlesBot — Free Tier
# ===========================================================================

class TestJobTitlesBotFree:
    def setup_method(self):
        self.bot = JobTitlesBot(tier=Tier.FREE)

    def test_default_tier_is_free(self):
        bot = JobTitlesBot()
        assert bot.tier == Tier.FREE

    def test_get_tier_info(self):
        info = self.bot.get_tier_info()
        assert info["tier"] == "free"

    def test_get_upgrade_suggestion(self):
        suggestion = self.bot.get_upgrade_suggestion()
        assert suggestion is not None
        assert "upgrade_to" in suggestion
        assert "unlock_features" in suggestion

    def test_search_job_titles_returns_list(self):
        results = self.bot.search_job_titles("engineer")
        assert isinstance(results, list)

    def test_search_job_titles_limited_to_10(self):
        results = self.bot.search_job_titles("e")  # broad search
        assert len(results) <= 10

    def test_search_job_titles_returns_dicts(self):
        results = self.bot.search_job_titles("engineer")
        for r in results:
            assert isinstance(r, dict)
            assert "title" in r

    def test_get_job_title_found(self):
        result = self.bot.get_job_title("Software Engineer")
        assert result is not None
        assert result["title"] == "Software Engineer"

    def test_get_job_title_not_found(self):
        result = self.bot.get_job_title("Unicorn Wrangler")
        assert result is None

    def test_browse_industry_limited_to_10(self):
        results = self.bot.browse_industry("Technology")
        assert len(results) <= 10

    def test_list_industries(self):
        industries = self.bot.list_industries()
        assert len(industries) >= 10

    def test_database_stats(self):
        stats = self.bot.database_stats()
        assert "total_titles" in stats
        assert stats["total_titles"] >= 50
        assert "industries" in stats
        assert "automatable_by_ai" in stats

    def test_valuate_item_available_on_free(self):
        result = self.bot.valuate_item("penny")
        assert result is not None
        assert "item_type" in result

    def test_list_all_job_titles_requires_pro(self):
        with pytest.raises(JobTitlesBotTierError):
            self.bot.list_all_job_titles()

    def test_generate_ai_worker_bot_requires_pro(self):
        with pytest.raises(JobTitlesBotTierError):
            self.bot.generate_ai_worker_bot("Software Engineer")

    def test_hire_worker_requires_pro(self):
        with pytest.raises(JobTitlesBotTierError):
            self.bot.hire_worker("Software Engineer")

    def test_train_bot_on_job_requires_enterprise(self):
        with pytest.raises(JobTitlesBotTierError):
            self.bot.train_bot_on_job("MyBot", "Software Engineer")

    def test_register_buddy_bot_requires_enterprise(self):
        with pytest.raises(JobTitlesBotTierError):
            self.bot.register_buddy_bot("Buddy_1")


# ===========================================================================
# JobTitlesBot — Pro Tier
# ===========================================================================

class TestJobTitlesBotPro:
    def setup_method(self):
        self.bot = JobTitlesBot(tier=Tier.PRO)

    def test_pro_tier_set(self):
        assert self.bot.tier == Tier.PRO

    def test_list_all_job_titles(self):
        titles = self.bot.list_all_job_titles()
        assert len(titles) >= 50
        assert titles == sorted(titles)

    def test_browse_industry_full(self):
        results = self.bot.browse_industry("Technology")
        assert len(results) >= 5  # not limited to 10 max

    def test_search_returns_more_than_10_if_available(self):
        # Pro tier should not cap at 10
        results = self.bot.search_job_titles("e")
        assert len(results) > 10 or len(results) == len(
            JobTitleDatabase().search("e")
        )

    def test_generate_ai_worker_bot_returns_dict(self):
        result = self.bot.generate_ai_worker_bot("Software Engineer")
        assert isinstance(result, dict)
        assert "name" in result
        assert "cost_explanation" in result

    def test_generate_ai_worker_bot_includes_payment_options(self):
        result = self.bot.generate_ai_worker_bot("Accountant")
        assert "payment_options" in result
        assert "Free Tier" in result["payment_options"]

    def test_generate_ai_worker_bot_not_found(self):
        with pytest.raises(JobTitlesBotError):
            self.bot.generate_ai_worker_bot("Dinosaur Tamer")

    def test_list_automatable_jobs(self):
        jobs = self.bot.list_automatable_jobs()
        assert len(jobs) >= 10
        for j in jobs:
            assert j["automatable_by_ai"] is True

    def test_hire_human_worker(self):
        result = self.bot.hire_worker("Software Engineer", worker_type="human")
        assert result["worker_type"] == "human"
        assert "hiring_channels" in result
        assert "estimated_salary_usd_annual" in result

    def test_hire_ai_worker(self):
        result = self.bot.hire_worker("Accountant", worker_type="ai")
        assert result["worker_type"] == "ai"
        assert "ai_bot_name" in result
        assert "monthly_cost_usd" in result
        assert "cost_explanation" in result

    def test_hire_robot_worker(self):
        result = self.bot.hire_worker("CNC Machinist", worker_type="robot")
        assert result["worker_type"] == "robot"
        assert "robot_contract_type" in result
        assert "available_manufacturers" in result

    def test_hire_invalid_worker_type(self):
        with pytest.raises(JobTitlesBotError):
            self.bot.hire_worker("Accountant", worker_type="dragon")

    def test_hire_worker_not_found(self):
        with pytest.raises(JobTitlesBotError):
            self.bot.hire_worker("Pizza Delivery Robot XYZ")

    def test_generate_bulk_ai_bots_requires_enterprise(self):
        with pytest.raises(JobTitlesBotTierError):
            self.bot.generate_bulk_ai_bots(["Software Engineer", "Accountant"])

    def test_train_bot_on_job_requires_enterprise(self):
        with pytest.raises(JobTitlesBotTierError):
            self.bot.train_bot_on_job("MyBot", "Software Engineer")

    def test_register_buddy_bot_requires_enterprise(self):
        with pytest.raises(JobTitlesBotTierError):
            self.bot.register_buddy_bot("Buddy_1")


# ===========================================================================
# JobTitlesBot — Enterprise Tier
# ===========================================================================

class TestJobTitlesBotEnterprise:
    def setup_method(self):
        self.bot = JobTitlesBot(tier=Tier.ENTERPRISE)

    def test_enterprise_tier_set(self):
        assert self.bot.tier == Tier.ENTERPRISE

    def test_get_upgrade_suggestion_returns_none(self):
        assert self.bot.get_upgrade_suggestion() is None

    def test_generate_bulk_ai_bots(self):
        result = self.bot.generate_bulk_ai_bots(["Software Engineer", "Accountant"])
        assert len(result) == 2
        for item in result:
            assert isinstance(item, dict)
            assert "name" in item

    def test_generate_bulk_ai_bots_skips_unknown(self):
        result = self.bot.generate_bulk_ai_bots(["Software Engineer", "Unicorn Tamer"])
        assert len(result) == 1

    def test_train_bot_on_job(self):
        result = self.bot.train_bot_on_job("EnterpriseBot", "Software Engineer")
        assert isinstance(result, dict)
        assert result["bot_name"] == "EnterpriseBot"
        assert "sessions" in result
        assert len(result["sessions"]) > 0
        assert "buddy_bot_upgrade" in result

    def test_train_bot_on_job_not_found(self):
        with pytest.raises(JobTitlesBotError):
            self.bot.train_bot_on_job("Bot", "Imaginary Job 9999")

    def test_train_face_recognition(self):
        result = self.bot.train_face_recognition("SecurityBot", num_faces=200)
        assert isinstance(result, dict)
        assert "face_recognition" in result["skill_name"]
        assert result["status"] == "complete"

    def test_train_object_recognition(self):
        result = self.bot.train_object_recognition("VisionBot", ["coin", "stamp"], examples_per_class=50)
        assert isinstance(result, dict)
        assert result["status"] == "complete"

    def test_register_buddy_bot(self):
        self.bot.register_buddy_bot("BuddyX")
        bots = self.bot.list_buddy_bots()
        assert "BuddyX" in bots

    def test_list_buddy_bots(self):
        self.bot.register_buddy_bot("BuddyY")
        bots = self.bot.list_buddy_bots()
        assert isinstance(bots, list)

    def test_buddy_bot_skill_propagation_via_training(self):
        self.bot.register_buddy_bot("BuddyProp1")
        self.bot.train_bot_on_job("MainBot", "Accountant")
        skills = self.bot.get_buddy_bot_skills("BuddyProp1")
        assert len(skills) > 0

    def test_buddy_bot_upgrade_propagation_note_present(self):
        result = self.bot.train_bot_on_job("Bot99", "Accountant")
        assert "buddy" in result["buddy_bot_upgrade"].lower()

    def test_get_buddy_bot_skills(self):
        self.bot.register_buddy_bot("SkillBot")
        self.bot.train_bot_on_job("Trainer", "Data Scientist")
        skills = self.bot.get_buddy_bot_skills("SkillBot")
        assert isinstance(skills, list)
        assert len(skills) > 0

    def test_valuate_coin_on_enterprise(self):
        result = self.bot.valuate_item("gold coin")
        assert result["item_type"] == "coin"
        assert result["estimated_value_usd_low"] > 0

    def test_valuate_antique_furniture(self):
        result = self.bot.valuate_item("antique furniture")
        assert result["item_type"] == "antique"

    def test_valuate_vintage_watch(self):
        result = self.bot.valuate_item("vintage watch")
        assert result["item_type"] == "collectible"


# ===========================================================================
# Framework compliance — GLOBAL AI SOURCES FLOW
# ===========================================================================

class TestFrameworkCompliance:
    def test_job_titles_bot_imports_global_ai_sources_flow(self):
        import importlib
        bot_module = importlib.import_module("bots.job_titles_bot.job_titles_bot")
        assert hasattr(bot_module, "GlobalAISourcesFlow")

    def test_database_imports_global_ai_sources_flow(self):
        import importlib
        db_module = importlib.import_module("bots.job_titles_bot.job_titles_database")
        assert hasattr(db_module, "GlobalAISourcesFlow")

    def test_generator_imports_global_ai_sources_flow(self):
        import importlib
        gen_module = importlib.import_module("bots.job_titles_bot.job_bot_generator")
        assert hasattr(gen_module, "GlobalAISourcesFlow")

    def test_trainer_imports_global_ai_sources_flow(self):
        import importlib
        trainer_module = importlib.import_module("bots.job_titles_bot.autonomous_trainer")
        assert hasattr(trainer_module, "GlobalAISourcesFlow")
