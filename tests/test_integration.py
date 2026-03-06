"""
tests/test_integration.py

Integration tests: bot-to-bot communication, DataForge data collection,
and end-to-end data pipeline.
"""

import importlib.util
import os
import sys
import unittest
from typing import Any

from core.orchestrator import BotOrchestrator
from bots.bot_base import BotBase
from framework.base_bot import BaseBot
from framework.nlp_engine import NLPEngine
from framework.adaptive_learning import AdaptiveLearning


def _load_bot(dir_name: str, file_name: str, class_name: str) -> Any:
    bots_dir = os.path.join(os.path.dirname(__file__), "..", "bots")
    path = os.path.join(bots_dir, dir_name, f"{file_name}.py")
    spec = importlib.util.spec_from_file_location(file_name, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[file_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return getattr(mod, class_name)


HustleBot = _load_bot("hustle-bot", "hustle_bot", "HustleBot")
BuddyBot  = _load_bot("buddy-bot",  "buddy_bot",  "BuddyBot")
FinanceBot = _load_bot("finance-bot", "finance_bot", "FinanceBot")
MarketingBot = _load_bot("marketing-bot", "marketing_bot", "MarketingBot")


# ---------------------------------------------------------------------------
# Minimal concrete BotBase
# ---------------------------------------------------------------------------

class _SimpleBotBase(BotBase):
    def run(self) -> None:
        self._set_running(True)

    def stop(self) -> None:
        self._set_running(False)


# ---------------------------------------------------------------------------
# Bot-to-bot communication via Orchestrator
# ---------------------------------------------------------------------------

class TestBotToBotCommunication(unittest.TestCase):
    def setUp(self) -> None:
        self.orch = BotOrchestrator()
        # BotBase(bot_name, bot_id) - orchestrator indexes by bot_id
        self.bot_a = _SimpleBotBase(bot_name="BotA", bot_id="bot-a")
        self.bot_b = _SimpleBotBase(bot_name="BotB", bot_id="bot-b")
        self.orch.register_bot(self.bot_a)
        self.orch.register_bot(self.bot_b)

    def test_send_receive_message(self) -> None:
        self.orch.send_message("bot-a", "bot-b", "greeting", {"text": "hello"})
        msgs = self.orch.receive_messages("bot-b")
        self.assertEqual(1, len(msgs))
        self.assertEqual("greeting", msgs[0]["topic"])
        self.assertEqual("hello", msgs[0]["payload"]["text"])

    def test_bidirectional_messaging(self) -> None:
        self.orch.send_message("bot-a", "bot-b", "request", {"q": "price?"})
        self.orch.send_message("bot-b", "bot-a", "response", {"price": 99.99})
        msgs_b = self.orch.receive_messages("bot-b")
        msgs_a = self.orch.receive_messages("bot-a")
        self.assertEqual(1, len(msgs_b))
        self.assertEqual(1, len(msgs_a))

    def test_message_history_recorded(self) -> None:
        self.orch.send_message("bot-a", "bot-b", "ping")
        history = self.orch.get_message_history()
        topics = [h["topic"] for h in history]
        self.assertIn("ping", topics)

    def test_collect_all_data_from_both_bots(self) -> None:
        data = self.orch.collect_all_data()
        self.assertIn("bot-a", data["bots"])
        self.assertIn("bot-b", data["bots"])
        self.assertEqual(2, data["bot_count"])

    def test_all_statuses(self) -> None:
        statuses = self.orch.get_all_statuses()
        self.assertIn("bot-a", statuses["bots"])
        self.assertIn("bot-b", statuses["bots"])


# ---------------------------------------------------------------------------
# DataForge collecting from multiple bots
# ---------------------------------------------------------------------------

class TestDataForgeCollection(unittest.TestCase):
    def setUp(self) -> None:
        self.orch = BotOrchestrator()
        self.hustle = HustleBot()
        self.buddy = BuddyBot()
        self.finance = FinanceBot()
        self.hustle.run()
        self.buddy.run()
        self.finance.run()
        self.orch.register_bot(self.hustle)
        self.orch.register_bot(self.buddy)
        self.orch.register_bot(self.finance)

    def tearDown(self) -> None:
        self.hustle.stop()
        self.buddy.stop()
        self.finance.stop()

    def test_collect_all_returns_all_bots(self) -> None:
        data = self.orch.collect_all_data()
        self.assertEqual(3, data["bot_count"])
        for bot_id in [self.hustle.bot_id, self.buddy.bot_id, self.finance.bot_id]:
            self.assertIn(bot_id, data["bots"])

    def test_each_bot_exports_activity_log(self) -> None:
        # Generate some activity
        self.hustle.find_opportunities("freelance")
        self.buddy.chat("hello")
        self.finance.analyze_budget(5000.0, {"rent": 1200})
        data = self.orch.collect_all_data()
        for bot_id in [self.hustle.bot_id, self.buddy.bot_id, self.finance.bot_id]:
            bot_data = data["bots"][bot_id]
            self.assertIn("activity_log", bot_data)

    def test_exported_data_has_timestamps(self) -> None:
        data = self.orch.collect_all_data()
        self.assertIn("collected_at", data)
        for bot_id, bot_data in data["bots"].items():
            self.assertIn("exported_at", bot_data)


# ---------------------------------------------------------------------------
# End-to-end data pipeline: NLP → AdaptiveLearning → prediction
# ---------------------------------------------------------------------------

class TestEndToEndPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.nlp = NLPEngine()
        self.al = AdaptiveLearning()

    def test_nlp_to_adaptive_learning(self) -> None:
        training_texts = [
            ("I need help with my finances", "finance"),
            ("What investment should I make", "finance"),
            ("How do I code in Python", "education"),
            ("Teach me machine learning", "education"),
            ("Find marketing opportunities", "marketing"),
            ("Create a social media campaign", "marketing"),
        ]
        for text, label in training_texts:
            intent = self.nlp.extract_intent(text)
            self.al.add_training_sample(text, label)

        result = self.al.train(epochs=10)
        self.assertGreater(len(result["loss_history"]), 0)

        prediction = self.al.predict("investment advice")
        self.assertIn(prediction["match_type"], ("exact", "fuzzy", "no_match"))

    def test_nlp_sentiment_pipeline(self) -> None:
        texts = [
            "I love this product, it's amazing!",
            "This is terrible, worst experience ever.",
            "The weather is cloudy today.",
        ]
        results = [self.nlp.sentiment_analysis(t) for t in texts]
        labels = [r["label"] for r in results]
        self.assertIn("positive", labels)
        self.assertIn("negative", labels)

    def test_nlp_entity_pipeline(self) -> None:
        text = "Contact sales@dreamcobots.ai or visit https://dreamcobots.ai for pricing at $99/month."
        entities = self.nlp.extract_entities(text)
        types = {e["type"] for e in entities}
        self.assertIn("EMAIL", types)
        self.assertIn("URL", types)

    def test_full_bot_lifecycle(self) -> None:
        """Start bots, process messages, collect data, stop bots."""
        orch = BotOrchestrator()
        bots = [HustleBot(), BuddyBot(), FinanceBot(), MarketingBot()]
        for bot in bots:
            bot.run()
            orch.register_bot(bot)

        # Process messages
        bots[0].find_opportunities("ecommerce")
        bots[1].chat("What are you?")
        bots[2].analyze_budget(6000, {"rent": 1800, "food": 500})
        bots[3].generate_campaign("brand awareness", 3000.0)

        # Collect data
        data = orch.collect_all_data()
        self.assertEqual(4, data["bot_count"])

        # Stop all
        for bot in bots:
            bot.stop()

        # Verify they're stopped
        for bot in bots:
            self.assertFalse(bot.is_running)


# ---------------------------------------------------------------------------
# BuddyAI integration test
# ---------------------------------------------------------------------------

class TestBuddyAIIntegration(unittest.TestCase):
    def test_buddy_ai_loads(self) -> None:
        """BuddyAI initialises without raising even if some bots fail to load."""
        try:
            from BuddyAI import BuddyAI
            ai = BuddyAI()
            # Should have at least some bots
            status = ai.get_system_status()
            self.assertIn("total_bots", status)
            self.assertGreaterEqual(status["total_bots"], 0)
        except Exception as exc:
            self.fail(f"BuddyAI raised unexpectedly: {exc}")

    def test_buddy_ai_route_request(self) -> None:
        from BuddyAI import BuddyAI
        ai = BuddyAI()
        response = ai.route_request("user-001", "hello")
        self.assertIsInstance(response, str)

    def test_buddy_ai_collect_all_data(self) -> None:
        from BuddyAI import BuddyAI
        ai = BuddyAI()
        data = ai.collect_all_data()
        self.assertIn("collected_at", data)
        self.assertIn("bots", data)

    def test_buddy_ai_get_best_bot(self) -> None:
        from BuddyAI import BuddyAI
        ai = BuddyAI()
        best = ai.get_best_bot("what investment should I make")
        self.assertIsInstance(best, str)

    def test_buddy_ai_broadcast(self) -> None:
        from BuddyAI import BuddyAI
        ai = BuddyAI()
        responses = ai.broadcast_message("status check")
        self.assertIsInstance(responses, dict)


if __name__ == "__main__":
    unittest.main()
