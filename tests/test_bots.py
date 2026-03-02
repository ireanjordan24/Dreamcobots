"""
Tests for all Dreamcobots bots.

Run:
    python -m pytest tests/
    # or
    python tests/test_bots.py
"""

import sys
import os
import unittest

# ---------------------------------------------------------------------------
# Path setup so bots can be imported without installation
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "bots", "government-contract-grant-bot"))
sys.path.insert(0, os.path.join(_REPO_ROOT, "bots", "referral-bot"))
sys.path.insert(0, os.path.join(_REPO_ROOT, "bots", "hustle-bot"))

from government_contract_grant_bot import GovernmentContractGrantBot
from referral_bot import ReferralBot
from hustle_bot import HustleBot


# ===========================================================================
# Government Contract & Grant Bot
# ===========================================================================

class TestGovernmentContractGrantBot(unittest.TestCase):

    def setUp(self):
        self.bot = GovernmentContractGrantBot()

    def test_start_does_not_raise(self):
        self.bot.start()  # should not raise

    def test_search_contracts_returns_list(self):
        contracts = self.bot.search_contracts()
        self.assertIsInstance(contracts, list)

    def test_search_grants_returns_list(self):
        grants = self.bot.search_grants()
        self.assertIsInstance(grants, list)

    def test_search_contracts_keyword_filter(self):
        contracts = self.bot.search_contracts(keywords=["robotics"])
        for c in contracts:
            self.assertIn("robotics", c["keywords"])

    def test_search_grants_keyword_filter(self):
        grants = self.bot.search_grants(keywords=["innovation"])
        for g in grants:
            self.assertIn("innovation", g["keywords"])

    def test_process_contracts_adds_score(self):
        self.bot.search_contracts()
        self.bot.process_contracts()
        for contract in self.bot.results["contracts_found"]:
            self.assertIn("score", contract)
            self.assertGreaterEqual(contract["score"], 1)
            self.assertLessEqual(contract["score"], 10)

    def test_process_grants_adds_score(self):
        self.bot.search_grants()
        self.bot.process_grants()
        for grant in self.bot.results["grants_found"]:
            self.assertIn("score", grant)

    def test_score_opportunity(self):
        self.assertEqual(self.bot._score_opportunity(2_000_000), 10)
        self.assertEqual(self.bot._score_opportunity(700_000), 8)
        self.assertEqual(self.bot._score_opportunity(200_000), 6)
        self.assertEqual(self.bot._score_opportunity(75_000), 4)
        self.assertEqual(self.bot._score_opportunity(10_000), 2)

    def test_generate_report_structure(self):
        self.bot.run()
        report = self.bot.generate_report()
        self.assertIn("summary", report)
        self.assertIn("contracts", report)
        self.assertIn("grants", report)
        self.assertIn("generated_at", report)

    def test_run_returns_report(self):
        report = self.bot.run()
        self.assertIsNotNone(report)
        self.assertIn("summary", report)

    def test_custom_config_keywords(self):
        bot = GovernmentContractGrantBot(config={
            "contract_keywords": ["robotics"],
            "grant_keywords": ["innovation"],
        })
        contracts = bot.search_contracts()
        grants = bot.search_grants()
        self.assertIsInstance(contracts, list)
        self.assertIsInstance(grants, list)


# ===========================================================================
# Referral Bot
# ===========================================================================

class TestReferralBot(unittest.TestCase):

    def setUp(self):
        self.bot = ReferralBot()

    def test_register_user(self):
        self.bot.register_user("Alice")
        self.assertIn("Alice", self.bot._users)

    def test_register_user_with_referrer(self):
        self.bot.register_user("Alice")
        self.bot.register_user("Bob", referrer_id="Alice")
        self.assertIn("Bob", self.bot._referrers["Alice"]["referrals"])

    def test_register_duplicate_user_is_noop(self):
        self.bot.register_user("Alice")
        self.bot.register_user("Alice")  # should not raise
        self.assertIn("Alice", self.bot._users)

    def test_generate_invite_link(self):
        link = self.bot.generate_invite_link("Alice")
        self.assertIn("Alice", link)
        self.assertTrue(link.startswith("https://"))

    def test_record_revenue_updates_user(self):
        self.bot.register_user("Alice")
        self.bot.record_revenue("Alice", 100)
        self.assertEqual(self.bot._users["Alice"]["revenue"], 100)

    def test_commission_computed_correctly(self):
        bot = ReferralBot(config={"commission_rate": 0.10})
        bot.register_user("Alice")
        bot.register_user("Bob", referrer_id="Alice")
        bot.record_revenue("Bob", 200)
        self.assertAlmostEqual(bot._referrers["Alice"]["total_earnings"], 20.0)

    def test_commission_rate_default(self):
        self.assertEqual(self.bot.commission_rate, ReferralBot.DEFAULT_COMMISSION_RATE)

    def test_record_revenue_unknown_user(self):
        self.bot.record_revenue("Unknown", 100)  # should not raise

    def test_record_revenue_nonpositive(self):
        self.bot.register_user("Alice")
        self.bot.record_revenue("Alice", 0)   # should not change revenue
        self.bot.record_revenue("Alice", -50)
        self.assertEqual(self.bot._users["Alice"]["revenue"], 0)

    def test_get_referrer_dashboard_structure(self):
        self.bot.register_user("Alice")
        self.bot.register_user("Bob", referrer_id="Alice")
        self.bot.record_revenue("Bob", 100)
        dashboard = self.bot.get_referrer_dashboard("Alice")
        self.assertIn("referrer_id", dashboard)
        self.assertIn("total_referrals", dashboard)
        self.assertIn("total_earnings", dashboard)
        self.assertIn("referrals", dashboard)

    def test_get_referrer_dashboard_unknown(self):
        result = self.bot.get_referrer_dashboard("Nobody")
        self.assertIn("error", result)

    def test_identify_underperformers(self):
        self.bot.register_user("Alice")
        self.bot.register_user("Bob", referrer_id="Alice")
        self.bot.register_user("Carol", referrer_id="Alice")
        self.bot.record_revenue("Bob", 200)
        self.bot.record_revenue("Carol", 50)
        underperformers = self.bot.identify_underperformers("Alice", revenue_threshold=100)
        self.assertIn("Carol", underperformers)
        self.assertNotIn("Bob", underperformers)

    def test_notify_hustle_bot(self):
        hustle_bot = HustleBot()
        hustle_bot.configure_goal("Taylor", revenue_goal=500.0)
        self.bot.register_user("Alice")
        self.bot.register_user("Taylor", referrer_id="Alice")
        self.bot.record_revenue("Taylor", 10)
        self.bot.notify_hustle_bot(hustle_bot, "Alice", revenue_threshold=100)
        # Taylor should have received a campaign
        self.assertGreater(len(hustle_bot._users["Taylor"]["campaigns_received"]), 0)

    def test_run_returns_dashboard(self):
        result = self.bot.run()
        self.assertIn("referrer_id", result)


# ===========================================================================
# Hustle Bot
# ===========================================================================

class TestHustleBot(unittest.TestCase):

    def setUp(self):
        self.bot = HustleBot()

    def test_configure_goal(self):
        self.bot.configure_goal("Jordan", 1000.0)
        self.assertEqual(self.bot._users["Jordan"]["goal"], 1000.0)

    def test_configure_goal_invalid(self):
        with self.assertRaises(ValueError):
            self.bot.configure_goal("Jordan", -100)

    def test_configure_goal_update(self):
        self.bot.configure_goal("Jordan", 1000.0)
        self.bot.configure_goal("Jordan", 2000.0)
        self.assertEqual(self.bot._users["Jordan"]["goal"], 2000.0)

    def test_add_task(self):
        self.bot.configure_goal("Jordan", 1000.0)
        self.bot.add_task("Jordan", "Do something")
        self.assertEqual(len(self.bot._users["Jordan"]["tasks"]), 1)

    def test_add_task_unknown_user(self):
        self.bot.add_task("Nobody", "Task")  # should not raise

    def test_complete_task(self):
        self.bot.configure_goal("Jordan", 1000.0)
        self.bot.add_task("Jordan", "Task A")
        self.bot.complete_task("Jordan", 0)
        self.assertTrue(self.bot._users["Jordan"]["tasks"][0]["completed"])

    def test_complete_task_invalid_index(self):
        self.bot.configure_goal("Jordan", 1000.0)
        self.bot.complete_task("Jordan", 99)  # should not raise

    def test_record_revenue(self):
        self.bot.configure_goal("Jordan", 1000.0)
        self.bot.record_revenue("Jordan", 300)
        self.assertEqual(self.bot._users["Jordan"]["current_revenue"], 300)

    def test_record_revenue_nonpositive(self):
        self.bot.configure_goal("Jordan", 1000.0)
        self.bot.record_revenue("Jordan", 0)
        self.bot.record_revenue("Jordan", -50)
        self.assertEqual(self.bot._users["Jordan"]["current_revenue"], 0)

    def test_milestone_detection(self):
        self.bot.configure_goal("Jordan", 1000.0)
        self.bot.record_revenue("Jordan", 250)  # 25%
        self.assertIn("25%", self.bot._users["Jordan"]["milestones"])

    def test_milestone_100_percent(self):
        self.bot.configure_goal("Jordan", 100.0)
        self.bot.record_revenue("Jordan", 100)
        self.assertIn("100%", self.bot._users["Jordan"]["milestones"])

    def test_get_daily_summary_structure(self):
        self.bot.configure_goal("Jordan", 1000.0)
        self.bot.record_revenue("Jordan", 200)
        summary = self.bot.get_daily_summary("Jordan")
        for key in ("user_id", "goal", "current_revenue", "progress_pct", "milestones"):
            self.assertIn(key, summary)

    def test_get_daily_summary_unknown(self):
        result = self.bot.get_daily_summary("Nobody")
        self.assertIn("error", result)

    def test_suggest_tasks_returns_list(self):
        self.bot.configure_goal("Jordan", 1000.0)
        tasks = self.bot.suggest_tasks("Jordan")
        self.assertIsInstance(tasks, list)
        self.assertGreater(len(tasks), 0)

    def test_identify_untapped_markets(self):
        markets = self.bot.identify_untapped_markets()
        self.assertIsInstance(markets, list)
        self.assertGreater(len(markets), 0)
        self.assertIn("name", markets[0])
        self.assertIn("potential_score", markets[0])

    def test_run_motivational_campaign(self):
        self.bot.configure_goal("Taylor", 500.0)
        resource = self.bot.run_motivational_campaign("Taylor")
        self.assertIsInstance(resource, str)
        self.assertIn(resource, self.bot._users["Taylor"]["campaigns_received"])

    def test_run_motivational_campaign_auto_registers(self):
        # User not previously configured – should auto-register
        resource = self.bot.run_motivational_campaign("NewUser")
        self.assertIn("NewUser", self.bot._users)
        self.assertIsInstance(resource, str)

    def test_run_returns_summary(self):
        summary = self.bot.run()
        self.assertIn("user_id", summary)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
