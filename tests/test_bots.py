"""Unit tests for DreamCobots bot ecosystem."""
import sys
import os
import unittest
import importlib.util

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _ROOT)


def _load_bot_module(bot_dir: str, module_file: str, mod_name: str):
    """Load a bot module from a hyphenated directory using importlib."""
    path = os.path.join(_ROOT, "bots", bot_dir, module_file)
    spec = importlib.util.spec_from_file_location(mod_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestBaseBot(unittest.TestCase):
    """Tests for the BaseBot base class."""

    def setUp(self):
        """Set up a BaseBot-derived test instance."""
        from core.base_bot import BaseBot

        class ConcreteBot(BaseBot):
            def run(self):
                return "running"

        self.bot = ConcreteBot(name="test-bot", description="Test bot", version="1.0.0")

    def test_initial_state(self):
        """Bot should initialize in stopped state."""
        self.assertFalse(self.bot.running)
        self.assertEqual(self.bot._status, "stopped")
        self.assertEqual(self.bot.revenue, 0.0)

    def test_start(self):
        """Bot.start() should set running=True and status=running."""
        self.bot.start()
        self.assertTrue(self.bot.running)
        self.assertEqual(self.bot._status, "running")

    def test_stop(self):
        """Bot.stop() should set running=False and status=stopped."""
        self.bot.start()
        self.bot.stop()
        self.assertFalse(self.bot.running)
        self.assertEqual(self.bot._status, "stopped")

    def test_get_status(self):
        """get_status() should return a dict with expected keys."""
        status = self.bot.get_status()
        self.assertIn("name", status)
        self.assertIn("status", status)
        self.assertIn("revenue", status)
        self.assertEqual(status["name"], "test-bot")

    def test_add_revenue(self):
        """add_revenue() should accumulate correctly."""
        self.bot.add_revenue(100.0)
        self.bot.add_revenue(50.0)
        self.assertEqual(self.bot.revenue, 150.0)

    def test_add_revenue_negative_ignored(self):
        """add_revenue() should ignore negative amounts."""
        self.bot.add_revenue(-50.0)
        self.assertEqual(self.bot.revenue, 0.0)

    def test_log(self):
        """log() should append entries to the log list."""
        self.bot.log("Test event")
        self.assertEqual(len(self.bot._log), 1)
        self.assertIn("Test event", self.bot._log[0]["message"])

    def test_train(self):
        """train() should store training data."""
        self.bot.train({"input": "hello", "output": "world"})
        self.assertEqual(len(self.bot._training_data), 1)

    def test_suggest_improvements(self):
        """suggest_improvements() should return a non-empty list."""
        suggestions = self.bot.suggest_improvements()
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)

    def test_safe_run_handles_exception(self):
        """_safe_run() should catch exceptions and return None."""
        def bad_func():
            raise ValueError("test error")

        result = self.bot._safe_run(bad_func)
        self.assertIsNone(result)


class TestGovernmentBot(unittest.TestCase):
    """Tests for GovernmentContractGrantBot."""

    def setUp(self):
        """Set up government bot instance."""
        mod = _load_bot_module("government-contract-grant-bot",
                               "government_contract_grant_bot.py",
                               "gov_bot")
        self.bot = mod.GovernmentContractGrantBot()

    def test_search_opportunities(self):
        """search_opportunities() should return a non-empty list."""
        results = self.bot.search_opportunities(["technology"])
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn("id", results[0])
        self.assertIn("type", results[0])

    def test_get_funding_recommendations(self):
        """get_funding_recommendations() should return structured recommendations."""
        rec = self.bot.get_funding_recommendations()
        self.assertIn("top_programs", rec)
        self.assertIsInstance(rec["top_programs"], list)
        self.assertGreater(len(rec["top_programs"]), 0)

    def test_apply_for_contract(self):
        """apply_for_contract() should return a submission dict."""
        result = self.bot.apply_for_contract("SAM-2024-001")
        self.assertIn("status", result)
        self.assertEqual(result["status"], "application_submitted")

    def test_apply_for_grant(self):
        """apply_for_grant() should return a submission dict."""
        result = self.bot.apply_for_grant("SBIR-2024-001")
        self.assertIn("status", result)
        self.assertEqual(result["status"], "application_submitted")


class TestHustleBot(unittest.TestCase):
    """Tests for HustleBot."""

    def setUp(self):
        """Set up hustle bot instance."""
        mod = _load_bot_module("hustle-bot", "hustle_bot.py", "hustle_bot")
        self.bot = mod.HustleBot()

    def test_set_goal(self):
        """set_goal() should create a goal entry."""
        goal = self.bot.set_goal("Reach $10K MRR", 10000.0)
        self.assertEqual(goal["goal"], "Reach $10K MRR")
        self.assertEqual(goal["target_revenue"], 10000.0)

    def test_track_progress(self):
        """track_progress() should return progress dict."""
        self.bot.set_goal("Test goal", 1000.0)
        progress = self.bot.track_progress()
        self.assertIn("total_goals", progress)
        self.assertIn("progress", progress)

    def test_suggest_tasks(self):
        """suggest_tasks() should return non-empty task list."""
        tasks = self.bot.suggest_tasks()
        self.assertIsInstance(tasks, list)
        self.assertGreater(len(tasks), 0)
        self.assertIn("task", tasks[0])

    def test_generate_daily_summary(self):
        """generate_daily_summary() should return summary dict."""
        summary = self.bot.generate_daily_summary()
        self.assertIn("date", summary)
        self.assertIn("total_revenue", summary)


class TestReferralBot(unittest.TestCase):
    """Tests for ReferralBot."""

    def setUp(self):
        """Set up referral bot instance."""
        mod = _load_bot_module("referral-bot", "referral_bot.py", "referral_bot")
        self.bot = mod.ReferralBot()

    def test_add_referrer(self):
        """add_referrer() should register a new referrer."""
        result = self.bot.add_referrer("user001", "Alice Smith")
        self.assertIn("id", result)
        self.assertEqual(result["name"], "Alice Smith")

    def test_track_referral(self):
        """track_referral() should log a referral."""
        self.bot.add_referrer("user001", "Alice")
        referral = self.bot.track_referral("user001", "user002")
        self.assertIn("referral_id", referral)
        self.assertEqual(referral["referrer_id"], "user001")

    def test_calculate_earnings(self):
        """calculate_earnings() should return earnings dict."""
        self.bot.add_referrer("user001", "Alice")
        earnings = self.bot.calculate_earnings("user001")
        self.assertIn("commission_rate", earnings)
        self.assertEqual(earnings["commission_rate"], "50%")

    def test_get_leaderboard(self):
        """get_leaderboard() should return a list."""
        leaderboard = self.bot.get_leaderboard()
        self.assertIsInstance(leaderboard, list)
        self.assertGreater(len(leaderboard), 0)

    def test_get_referral_stats(self):
        """get_referral_stats() should return stats dict."""
        stats = self.bot.get_referral_stats()
        self.assertIn("program_name", stats)
        self.assertIn("commission_rate", stats)


class TestEntrepreneurBot(unittest.TestCase):
    """Tests for EntrepreneurBot."""

    def setUp(self):
        """Set up entrepreneur bot instance."""
        mod = _load_bot_module("entrepreneur-bot", "entrepreneur_bot.py", "entrepreneur_bot")
        self.bot = mod.EntrepreneurBot()

    def test_generate_business_plan(self):
        """generate_business_plan() should return structured plan."""
        plan = self.bot.generate_business_plan("AI analytics tool", "technology")
        self.assertIn("executive_summary", plan)
        self.assertIn("financial_projections", plan)

    def test_find_funding(self):
        """find_funding() should return funding sources."""
        funding = self.bot.find_funding("seed", 100000)
        self.assertIn("grants", funding)
        self.assertIn("investors", funding)

    def test_startup_checklist(self):
        """startup_checklist() should return phase-based checklist."""
        checklist = self.bot.startup_checklist()
        self.assertIn("phase_1_validate", checklist)
        self.assertIn("phase_2_build", checklist)
        self.assertIsInstance(checklist["phase_1_validate"], list)

    def test_generate_business_name(self):
        """generate_business_name() should return list of names."""
        names = self.bot.generate_business_name("technology", ["AI", "smart"])
        self.assertIsInstance(names, list)
        self.assertGreater(len(names), 0)


class TestFinanceBot(unittest.TestCase):
    """Tests for FinanceBot."""

    def setUp(self):
        """Set up finance bot instance."""
        mod = _load_bot_module("finance-bot", "finance_bot.py", "finance_bot")
        self.bot = mod.FinanceBot()

    def test_build_budget(self):
        """build_budget() should compute correct surplus."""
        budget = self.bot.build_budget(5000, {"rent": 1500, "food": 500, "utilities": 200})
        self.assertEqual(budget["monthly_income"], 5000)
        self.assertEqual(budget["total_expenses"], 2200)
        self.assertEqual(budget["net_surplus"], 2800.0)

    def test_calculate_roi(self):
        """calculate_roi() should compute correct ROI values."""
        roi = self.bot.calculate_roi(10000, 13000, 1)
        self.assertEqual(roi["net_profit"], 3000)
        self.assertEqual(roi["simple_roi_percent"], 30.0)

    def test_financial_health_score(self):
        """financial_health_score() should return score in 1-100 range."""
        score = self.bot.financial_health_score(100000, 30000, 5000, 3000)
        self.assertGreaterEqual(score["financial_health_score"], 1)
        self.assertLessEqual(score["financial_health_score"], 100)

    def test_forecast_cash_flow(self):
        """forecast_cash_flow() should return correct projection count."""
        forecast = self.bot.forecast_cash_flow(10000, 5000, 3000, 6)
        self.assertEqual(len(forecast["projections"]), 6)
        self.assertEqual(forecast["monthly_net"], 2000)


class TestRealEstateBot(unittest.TestCase):
    """Tests for RealEstateBot."""

    def setUp(self):
        """Set up real estate bot instance."""
        mod = _load_bot_module("real-estate-bot", "real_estate_bot.py", "real_estate_bot")
        self.bot = mod.RealEstateBot()

    def test_analyze_investment(self):
        """analyze_investment() should compute cap rate and cash flow."""
        analysis = self.bot.analyze_investment(200000, 1800, 700)
        self.assertIn("cap_rate_percent", analysis)
        self.assertIn("monthly_cash_flow", analysis)
        self.assertEqual(analysis["monthly_cash_flow"], 1100.0)

    def test_score_deal(self):
        """score_deal() should return score in 1-10 range."""
        score = self.bot.score_deal({
            "price": 150000, "monthly_rent": 1500, "monthly_expenses": 500, "location_score": 75
        })
        self.assertGreaterEqual(score["deal_score"], 1)
        self.assertLessEqual(score["deal_score"], 10)

    def test_flip_vs_rent(self):
        """flip_vs_rent() should return recommendation."""
        result = self.bot.flip_vs_rent(100000, 20000, 180000, 1200)
        self.assertIn("recommendation", result)
        self.assertIn(result["recommendation"], ["Flip", "Rent"])


class TestMarketingBot(unittest.TestCase):
    """Tests for MarketingBot."""

    def setUp(self):
        """Set up marketing bot instance."""
        mod = _load_bot_module("marketing-bot", "marketing_bot.py", "marketing_bot")
        self.bot = mod.MarketingBot()

    def test_research_keywords(self):
        """research_keywords() should return keyword list."""
        keywords = self.bot.research_keywords("real estate", 5)
        self.assertEqual(len(keywords), 5)
        self.assertIn("keyword", keywords[0])
        self.assertIn("monthly_searches", keywords[0])

    def test_track_campaign_roi(self):
        """track_campaign_roi() should compute correct ROI."""
        roi = self.bot.track_campaign_roi(1000, 3000, 500, 30)
        self.assertEqual(roi["roi_percent"], 200.0)
        self.assertEqual(roi["roas"], 3.0)

    def test_generate_social_posts(self):
        """generate_social_posts() should generate posts for each platform."""
        posts = self.bot.generate_social_posts("AI tools", ["LinkedIn", "Twitter"], num_posts=2)
        self.assertIn("LinkedIn", posts["posts"])
        self.assertEqual(len(posts["posts"]["LinkedIn"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
