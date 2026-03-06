"""
tests/test_bots.py

Tests for all 14 bot implementations.
"""

import importlib.util
import os
import sys
import unittest
from typing import Any


def _load_bot(dir_name: str, file_name: str, class_name: str) -> Any:
    bots_dir = os.path.join(os.path.dirname(__file__), "..", "bots")
    path = os.path.join(bots_dir, dir_name, f"{file_name}.py")
    spec = importlib.util.spec_from_file_location(file_name, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[file_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return getattr(mod, class_name)


# Load all bot classes
HustleBot        = _load_bot("hustle-bot",        "hustle_bot",        "HustleBot")
ReferralBot      = _load_bot("referral-bot",      "referral_bot",      "ReferralBot")
BuddyBot         = _load_bot("buddy-bot",         "buddy_bot",         "BuddyBot")
EntrepreneurBot  = _load_bot("entrepreneur-bot",  "entrepreneur_bot",  "EntrepreneurBot")
MedicalBot       = _load_bot("medical-bot",       "medical_bot",       "MedicalBot")
LegalBot         = _load_bot("legal-bot",         "legal_bot",         "LegalBot")
FinanceBot       = _load_bot("finance-bot",       "finance_bot",       "FinanceBot")
RealEstateBot    = _load_bot("real-estate-bot",   "real_estate_bot",   "RealEstateBot")
EcommerceBot     = _load_bot("ecommerce-bot",     "ecommerce_bot",     "EcommerceBot")
MarketingBot     = _load_bot("marketing-bot",     "marketing_bot",     "MarketingBot")
EducationBot     = _load_bot("education-bot",     "education_bot",     "EducationBot")
CybersecurityBot = _load_bot("cybersecurity-bot", "cybersecurity_bot", "CybersecurityBot")
HRBot            = _load_bot("hr-bot",            "hr_bot",            "HRBot")
FarewellBot      = _load_bot("farewell-bot",      "farewell_bot",      "FarewellBot")


class TestHustleBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = HustleBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_init(self) -> None:
        self.assertEqual("HustleBot", self.bot.bot_name)
        self.assertTrue(self.bot.is_running)

    def test_find_opportunities(self) -> None:
        opps = self.bot.find_opportunities("freelance")
        self.assertIsInstance(opps, list)
        self.assertGreater(len(opps), 0)

    def test_find_opportunities_all(self) -> None:
        opps = self.bot.find_opportunities("all")
        self.assertGreater(len(opps), 3)

    def test_set_goal_and_track(self) -> None:
        goal_id = self.bot.set_goal("Save $1000", 1000.0)
        progress = self.bot.track_progress(goal_id)
        self.assertEqual(goal_id, progress["id"])
        self.assertEqual(0.0, progress["progress_pct"])

    def test_generate_action_plan(self) -> None:
        goal_id = self.bot.set_goal("Side income", 500.0)
        plan = self.bot.generate_action_plan(goal_id)
        self.assertIsInstance(plan, list)
        self.assertGreater(len(plan), 0)

    def test_record_earning(self) -> None:
        goal_id = self.bot.set_goal("Save", 100.0)
        self.bot.record_earning(goal_id, 50.0, "Freelance work")
        progress = self.bot.track_progress(goal_id)
        self.assertEqual(50.0, progress["current_amount"])

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestReferralBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = ReferralBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_create_referral_link(self) -> None:
        link = self.bot.create_referral_link("user-1")
        self.assertIn("ref=", link)

    def test_create_referral_link_idempotent(self) -> None:
        link1 = self.bot.create_referral_link("user-2")
        link2 = self.bot.create_referral_link("user-2")
        self.assertEqual(link1, link2)  # Same URL both times

    def test_track_referral(self) -> None:
        self.bot.create_referral_link("user-3")
        code = self.bot._referral_links["user-3"]
        self.bot.track_referral(code, "new-user-1")
        earnings = self.bot.calculate_earnings("user-3")
        self.assertGreater(earnings, 0)

    def test_get_referral_tree(self) -> None:
        self.bot.create_referral_link("user-4")
        tree = self.bot.get_referral_tree("user-4")
        self.assertEqual("user-4", tree["user_id"])

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestBuddyBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = BuddyBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_chat_greeting(self) -> None:
        response = self.bot.chat("Hello!")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_remember_recall(self) -> None:
        self.bot.remember("favorite_color", "blue")
        self.assertEqual("blue", self.bot.recall("favorite_color"))

    def test_recall_missing(self) -> None:
        result = self.bot.recall("nonexistent_key")
        self.assertIn("don't remember", result.lower())

    def test_get_mood(self) -> None:
        mood = self.bot.get_mood()
        self.assertIsInstance(mood, str)
        self.assertGreater(len(mood), 0)

    def test_customize_personality(self) -> None:
        self.bot.customize_personality({"tone": "formal", "emoji": False})
        self.assertEqual("formal", self.bot._personality["tone"])

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestEntrepreneurBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = EntrepreneurBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_generate_business_idea(self) -> None:
        result = self.bot.generate_business_idea("tech")
        self.assertIn("idea", result)
        self.assertIn("industry", result)

    def test_analyze_market(self) -> None:
        result = self.bot.analyze_market("fintech")
        self.assertIn("niche", result)
        self.assertIn("market_size", result)

    def test_create_business_plan(self) -> None:
        idea = self.bot.generate_business_idea("health")
        plan = self.bot.create_business_plan(idea)
        self.assertIn("business_name", plan)
        self.assertIn("revenue_model", plan)

    def test_estimate_revenue(self) -> None:
        revenue = self.bot.estimate_revenue({"customers": 200, "avg_revenue": 50.0})
        self.assertGreater(revenue, 0)

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestMedicalBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = MedicalBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_search_condition_known(self) -> None:
        result = self.bot.search_condition("diabetes")
        self.assertIn("disclaimer", result)
        self.assertIn("symptoms", result)

    def test_search_condition_unknown(self) -> None:
        result = self.bot.search_condition("unknowndisease123")
        self.assertIn("disclaimer", result)

    def test_get_medication_info(self) -> None:
        result = self.bot.get_medication_info("metformin")
        self.assertIn("disclaimer", result)
        self.assertIn("uses", result)

    def test_find_providers(self) -> None:
        providers = self.bot.find_providers("New York", "cardiologist")
        self.assertIsInstance(providers, list)
        self.assertGreater(len(providers), 0)
        self.assertIn("disclaimer", providers[0])

    def test_generate_health_report(self) -> None:
        report = self.bot.generate_health_report({
            "blood_pressure": "120/80", "heart_rate": 72,
            "temperature": 98.6, "bmi": 22.5,
        })
        self.assertIn("disclaimer", report)
        self.assertIn("observations", report)

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestLegalBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = LegalBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_search_law(self) -> None:
        result = self.bot.search_law("gdpr")
        self.assertIn("disclaimer", result)
        self.assertIn("summary", result)

    def test_analyze_contract(self) -> None:
        text = "This agreement includes an indemnification clause and arbitration provisions."
        result = self.bot.analyze_contract(text)
        self.assertIn("findings", result)
        self.assertIn("disclaimer", result)
        self.assertGreater(len(result["findings"]), 0)

    def test_find_attorney(self) -> None:
        attorneys = self.bot.find_attorney("Chicago", "employment law")
        self.assertIsInstance(attorneys, list)
        self.assertGreater(len(attorneys), 0)

    def test_generate_legal_document_nda(self) -> None:
        doc = self.bot.generate_legal_document("nda", {"party_a": "Alice", "party_b": "Bob"})
        self.assertIn("NON-DISCLOSURE", doc)
        self.assertIn("LEGAL DISCLAIMER", doc)

    def test_generate_legal_document_unknown(self) -> None:
        with self.assertRaises(ValueError):
            self.bot.generate_legal_document("unknown_template", {})

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestFinanceBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = FinanceBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_analyze_budget(self) -> None:
        result = self.bot.analyze_budget(5000.0, {"housing": 1500, "food": 400})
        self.assertIn("surplus", result)
        self.assertIn("savings_rate_pct", result)

    def test_calculate_investment_returns(self) -> None:
        fv = self.bot.calculate_investment_returns(10000.0, 0.07, 10)
        self.assertAlmostEqual(fv, 19671.51, places=0)

    def test_find_investment_opportunities(self) -> None:
        opts = self.bot.find_investment_opportunities("low")
        self.assertIsInstance(opts, list)
        self.assertGreater(len(opts), 0)

    def test_generate_financial_plan(self) -> None:
        plan = self.bot.generate_financial_plan(["retirement", "emergency fund"])
        self.assertIn("strategies", plan)
        self.assertIn("goals", plan)

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestRealEstateBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = RealEstateBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_search_properties(self) -> None:
        listings = self.bot.search_properties("Austin, TX", 400_000.0)
        self.assertIsInstance(listings, list)
        self.assertGreater(len(listings), 0)

    def test_analyze_property(self) -> None:
        result = self.bot.analyze_property("123 Main St, Austin TX")
        self.assertIn("estimated_value", result)
        self.assertIn("cap_rate_pct", result)

    def test_calculate_mortgage(self) -> None:
        result = self.bot.calculate_mortgage(300_000, 60_000, 0.065, 30)
        self.assertIn("monthly_payment", result)
        self.assertGreater(result["monthly_payment"], 0)

    def test_get_market_trends(self) -> None:
        trends = self.bot.get_market_trends("Denver, CO")
        self.assertIn("median_home_price", trends)
        self.assertIn("market_type", trends)

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestEcommerceBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = EcommerceBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_search_products(self) -> None:
        products = self.bot.search_products("wireless headphones", "amazon")
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)

    def test_analyze_competition(self) -> None:
        analysis = self.bot.analyze_competition("pet supplies")
        self.assertIn("competition_level", analysis)
        self.assertIn("market_opportunity", analysis)

    def test_generate_product_listing(self) -> None:
        listing = self.bot.generate_product_listing({
            "name": "Ergonomic Chair",
            "features": ["Lumbar support", "Adjustable height"],
            "price": 299.99,
            "category": "Furniture",
        })
        self.assertIn("title", listing)
        self.assertIn("bullet_points", listing)

    def test_calculate_profit_margin(self) -> None:
        margin = self.bot.calculate_profit_margin(15.0, 40.0, 6.0)
        self.assertAlmostEqual(margin, 47.5, places=1)

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestMarketingBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = MarketingBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_generate_campaign(self) -> None:
        campaign = self.bot.generate_campaign("brand awareness", 5000.0)
        self.assertIn("id", campaign)
        self.assertIn("channel_allocation", campaign)

    def test_create_content(self) -> None:
        content = self.bot.create_content("AI tools", "twitter")
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 0)

    def test_analyze_audience(self) -> None:
        result = self.bot.analyze_audience({"age_range": "25-44", "interests": ["tech"]})
        self.assertIn("recommended_channels", result)

    def test_track_campaign_metrics(self) -> None:
        campaign = self.bot.generate_campaign("lead gen", 2000.0)
        metrics = self.bot.track_campaign_metrics(campaign["id"])
        self.assertIn("impressions", metrics)
        self.assertIn("roas", metrics)

    def test_track_unknown_campaign_raises(self) -> None:
        with self.assertRaises(KeyError):
            self.bot.track_campaign_metrics("nonexistent-campaign-id")

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestEducationBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = EducationBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_create_lesson_plan(self) -> None:
        plan = self.bot.create_lesson_plan("Python", "beginner")
        self.assertIn("modules", plan)
        self.assertGreater(plan["total_weeks"], 0)

    def test_generate_quiz(self) -> None:
        questions = self.bot.generate_quiz("Python basics", 5)
        self.assertEqual(5, len(questions))
        self.assertIn("options", questions[0])

    def test_track_progress_new_student(self) -> None:
        progress = self.bot.track_progress("student-001")
        self.assertEqual("student-001", progress["student_id"])

    def test_recommend_resources(self) -> None:
        resources = self.bot.recommend_resources("python")
        self.assertIsInstance(resources, list)
        self.assertGreater(len(resources), 0)

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestCybersecurityBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = CybersecurityBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_scan_vulnerabilities(self) -> None:
        findings = self.bot.scan_vulnerabilities("example.com")
        self.assertIsInstance(findings, list)
        self.assertGreater(len(findings), 0)

    def test_generate_security_report(self) -> None:
        findings = self.bot.scan_vulnerabilities("test-app")
        report = self.bot.generate_security_report(findings)
        self.assertIn("overall_risk_level", report)
        self.assertIn("total_vulnerabilities", report)

    def test_recommend_patches(self) -> None:
        findings = self.bot.scan_vulnerabilities("test-app")
        patches = self.bot.recommend_patches(findings)
        self.assertIsInstance(patches, list)
        self.assertGreater(len(patches), 0)

    def test_check_password_strength_weak(self) -> None:
        result = self.bot.check_password_strength("password")
        self.assertEqual(0, result["score"])
        self.assertEqual("Very Weak", result["strength"])

    def test_check_password_strength_strong(self) -> None:
        result = self.bot.check_password_strength("Tr0ub4dor&3Secure!")
        self.assertGreater(result["score"], 60)

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestHRBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = HRBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_post_job(self) -> None:
        posting = self.bot.post_job(
            "Senior Python Developer",
            "Build scalable AI systems.",
            ["5+ years Python", "AWS experience"],
        )
        self.assertIn("id", posting)
        self.assertEqual("Senior Python Developer", posting["title"])

    def test_screen_resume(self) -> None:
        resume = "Python developer with 5 years experience. Bachelor's degree in CS. AWS certified."
        result = self.bot.screen_resume(resume)
        self.assertIn("screening_score", result)
        self.assertIn("matched_skills", result)
        self.assertGreater(result["skill_count"], 0)

    def test_schedule_interview(self) -> None:
        interview = self.bot.schedule_interview(
            "cand-001", "interviewer-001", "2025-01-15 14:00 UTC"
        )
        self.assertIn("id", interview)
        self.assertEqual("scheduled", interview["status"])

    def test_generate_offer_letter(self) -> None:
        letter = self.bot.generate_offer_letter(
            {"name": "Jane Doe", "email": "jane@example.com"},
            {"title": "Engineer", "department": "Engineering", "salary": 95000,
             "start_date": "Feb 1, 2025", "location": "Remote", "employment_type": "Full-Time"},
        )
        self.assertIn("Jane Doe", letter)
        self.assertIn("Engineer", letter)

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


class TestFarewellBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = FarewellBot()
        self.bot.run()

    def tearDown(self) -> None:
        self.bot.stop()

    def test_initiate_offboarding(self) -> None:
        record = self.bot.initiate_offboarding("user-999")
        self.assertIn("checklist", record)
        self.assertEqual("in_progress", record["status"])

    def test_collect_feedback(self) -> None:
        survey = self.bot.collect_feedback("user-999")
        self.assertIn("questions", survey)
        self.assertGreater(len(survey["questions"]), 0)

    def test_generate_farewell_message_resignation(self) -> None:
        msg = self.bot.generate_farewell_message("user-999", "resignation")
        self.assertIn("user-999", msg.lower() or msg)
        self.assertIsInstance(msg, str)

    def test_generate_farewell_message_retirement(self) -> None:
        msg = self.bot.generate_farewell_message("user-888", "retirement")
        self.assertIn("retirement", msg.lower())

    def test_archive_user_data(self) -> None:
        self.bot.initiate_offboarding("user-777")
        result = self.bot.archive_user_data("user-777")
        self.assertTrue(result)

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("bot_id", data)


if __name__ == "__main__":
    unittest.main()
