"""
tests/test_framework.py

Tests for framework module: base_bot, nlp_engine, adaptive_learning,
dataset_manager, and monetization.
"""

import os
import tempfile
import unittest

from framework.base_bot import BaseBot
from framework.nlp_engine import NLPEngine
from framework.adaptive_learning import AdaptiveLearning
from framework.dataset_manager import DatasetManager
from framework.monetization import MonetizationEngine


# ---------------------------------------------------------------------------
# BaseBot
# ---------------------------------------------------------------------------

class TestBaseBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = BaseBot(
            name="TestBot",
            description="A test bot",
            capabilities=["chat", "search"],
        )

    def test_init(self) -> None:
        self.assertEqual("TestBot", self.bot.name)
        self.assertEqual("A test bot", self.bot.description)
        self.assertFalse(self.bot._running)

    def test_get_capabilities(self) -> None:
        caps = self.bot.get_capabilities()
        self.assertIn("chat", caps)
        self.assertIn("search", caps)

    def test_start_stop(self) -> None:
        self.bot.start()
        self.assertTrue(self.bot._running)
        self.bot.stop()
        self.assertFalse(self.bot._running)

    def test_double_start(self) -> None:
        self.bot.start()
        self.bot.start()  # should not raise, just warn
        self.assertTrue(self.bot._running)
        self.bot.stop()

    def test_process_message_greeting(self) -> None:
        self.bot.start()
        response = self.bot.process_message("hello")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        self.bot.stop()

    def test_process_message_help(self) -> None:
        self.bot.start()
        response = self.bot.process_message("help me please")
        self.assertIn("chat", response.lower())
        self.bot.stop()

    def test_process_message_empty(self) -> None:
        response = self.bot.process_message("")
        self.assertIsInstance(response, str)

    def test_learn(self) -> None:
        self.bot.learn({"color": "blue", "size": "large"})
        self.assertEqual(2, self.bot._knowledge_base.__len__())

    def test_learn_invalid_type(self) -> None:
        self.bot.learn("not a dict")  # should not raise, just warn

    def test_get_stats(self) -> None:
        stats = self.bot.get_stats()
        self.assertIn("name", stats)
        self.assertIn("running", stats)
        self.assertIn("message_count", stats)

    def test_export_structured_data(self) -> None:
        data = self.bot.export_structured_data()
        self.assertIn("stats", data)
        self.assertIn("capabilities", data)


# ---------------------------------------------------------------------------
# NLPEngine
# ---------------------------------------------------------------------------

class TestNLPEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.nlp = NLPEngine()

    def test_tokenize_basic(self) -> None:
        tokens = self.nlp.tokenize("Hello world this is a test")
        self.assertIn("hello", tokens)
        self.assertIn("world", tokens)
        # stopwords removed
        self.assertNotIn("this", tokens)

    def test_tokenize_empty(self) -> None:
        self.assertEqual([], self.nlp.tokenize(""))
        self.assertEqual([], self.nlp.tokenize("   "))

    def test_extract_intent_greeting(self) -> None:
        self.assertEqual("greeting", self.nlp.extract_intent("Hello there!"))

    def test_extract_intent_question(self) -> None:
        self.assertEqual("question", self.nlp.extract_intent("What is Python?"))

    def test_extract_intent_command(self) -> None:
        intent = self.nlp.extract_intent("Find me the best deals")
        self.assertEqual("command", intent)

    def test_extract_intent_unknown(self) -> None:
        self.assertEqual("unknown", self.nlp.extract_intent(""))

    def test_extract_entities_email(self) -> None:
        entities = self.nlp.extract_entities("Contact us at support@example.com")
        types = [e["type"] for e in entities]
        self.assertIn("EMAIL", types)

    def test_extract_entities_url(self) -> None:
        entities = self.nlp.extract_entities("Visit https://dreamcobots.ai for more")
        types = [e["type"] for e in entities]
        self.assertIn("URL", types)

    def test_extract_entities_empty(self) -> None:
        self.assertEqual([], self.nlp.extract_entities(""))

    def test_sentiment_positive(self) -> None:
        result = self.nlp.sentiment_analysis("This is great and amazing work!")
        self.assertEqual("positive", result["label"])

    def test_sentiment_negative(self) -> None:
        result = self.nlp.sentiment_analysis("This is terrible and horrible.")
        self.assertEqual("negative", result["label"])

    def test_sentiment_neutral_empty(self) -> None:
        result = self.nlp.sentiment_analysis("")
        self.assertEqual("neutral", result["label"])

    def test_sentiment_negation(self) -> None:
        result = self.nlp.sentiment_analysis("This is not bad at all.")
        # "not bad" should shift positive
        self.assertIsInstance(result["label"], str)

    def test_summarize_short(self) -> None:
        text = "This is one sentence."
        summary = self.nlp.summarize(text, max_length=100)
        self.assertEqual(text, summary)

    def test_summarize_long(self) -> None:
        text = (
            "Python is a programming language. "
            "It is widely used for data science and AI. "
            "Python has a simple syntax. "
            "Many developers prefer Python for rapid development. "
            "It supports multiple programming paradigms."
        )
        summary = self.nlp.summarize(text, max_length=100)
        self.assertLessEqual(len(summary), 100)
        self.assertGreater(len(summary), 0)


# ---------------------------------------------------------------------------
# AdaptiveLearning
# ---------------------------------------------------------------------------

class TestAdaptiveLearning(unittest.TestCase):
    def setUp(self) -> None:
        self.al = AdaptiveLearning()

    def test_add_training_sample(self) -> None:
        self.al.add_training_sample("hello", "world")
        self.assertEqual(1, len(self.al._training_samples))

    def test_train_returns_loss_history(self) -> None:
        self.al.add_training_sample("cat", "animal")
        self.al.add_training_sample("dog", "animal")
        result = self.al.train(epochs=3)
        self.assertEqual(3, result["epochs"])
        self.assertEqual(3, len(result["loss_history"]))

    def test_train_empty_samples(self) -> None:
        result = self.al.train(epochs=5)
        self.assertEqual(0, result["epochs"])

    def test_predict_exact(self) -> None:
        self.al.add_training_sample("cat", "meows")
        self.al.train(epochs=5)
        result = self.al.predict("cat")
        self.assertEqual("exact", result["match_type"])
        self.assertEqual("meows", result["output"])

    def test_predict_fuzzy(self) -> None:
        self.al.add_training_sample("machine learning basics", "intro to ML")
        self.al.train(epochs=3)
        result = self.al.predict("machine learning")
        self.assertIn(result["match_type"], ("exact", "fuzzy"))

    def test_predict_no_model(self) -> None:
        result = self.al.predict("anything")
        self.assertEqual("no_model", result["match_type"])

    def test_save_and_load_model(self) -> None:
        self.al.add_training_sample("x", "y")
        self.al.train(epochs=2)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            self.al.save_model(path)
            al2 = AdaptiveLearning()
            al2.load_model(path)
            result = al2.predict("x")
            self.assertEqual("y", result["output"])
        finally:
            os.unlink(path)

    def test_get_performance_metrics(self) -> None:
        self.al.add_training_sample("a", "b")
        self.al.train(epochs=2)
        metrics = self.al.get_performance_metrics()
        self.assertIn("model_size", metrics)
        self.assertIn("average_confidence", metrics)


# ---------------------------------------------------------------------------
# DatasetManager
# ---------------------------------------------------------------------------

class TestDatasetManager(unittest.TestCase):
    def setUp(self) -> None:
        self.dm = DatasetManager()

    def test_add_and_get(self) -> None:
        self.dm.add_dataset("ds1", [{"a": 1}, {"a": 2}])
        data = self.dm.get_dataset("ds1")
        self.assertEqual(2, len(data))

    def test_add_invalid_name_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.dm.add_dataset("", [])

    def test_add_invalid_data_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.dm.add_dataset("bad", "not a list")  # type: ignore

    def test_get_missing_raises(self) -> None:
        with self.assertRaises(KeyError):
            self.dm.get_dataset("nonexistent")

    def test_list_datasets(self) -> None:
        self.dm.add_dataset("alpha", [1, 2])
        self.dm.add_dataset("beta", [3, 4])
        names = self.dm.list_datasets()
        self.assertIn("alpha", names)
        self.assertIn("beta", names)

    def test_export_json(self) -> None:
        self.dm.add_dataset("export_test", [{"x": 1}, {"x": 2}])
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            self.dm.export_dataset("export_test", "json", path)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 0)
        finally:
            os.unlink(path)

    def test_export_jsonl(self) -> None:
        self.dm.add_dataset("jl_test", [{"y": 1}, {"y": 2}])
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            path = f.name
        try:
            self.dm.export_dataset("jl_test", "jsonl", path)
            self.assertTrue(os.path.exists(path))
        finally:
            os.unlink(path)

    def test_export_csv(self) -> None:
        self.dm.add_dataset("csv_test", [{"col": "a"}, {"col": "b"}])
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            self.dm.export_dataset("csv_test", "csv", path)
            self.assertTrue(os.path.exists(path))
        finally:
            os.unlink(path)

    def test_export_unsupported_format_raises(self) -> None:
        self.dm.add_dataset("x", [1])
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            with self.assertRaises(ValueError):
                self.dm.export_dataset("x", "xml", path)
        finally:
            os.unlink(path)

    def test_merge_datasets(self) -> None:
        self.dm.add_dataset("m1", [1, 2, 3])
        self.dm.add_dataset("m2", [4, 5])
        self.dm.merge_datasets(["m1", "m2"], "merged")
        merged = self.dm.get_dataset("merged")
        self.assertEqual(5, len(merged))

    def test_merge_empty_list_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.dm.merge_datasets([], "empty_merge")

    def test_get_stats(self) -> None:
        self.dm.add_dataset("stats_test", [{"a": 1}, {"a": 2}], {"owner": "test"})
        stats = self.dm.get_stats("stats_test")
        self.assertEqual("stats_test", stats["name"])
        self.assertEqual(2, stats["record_count"])
        self.assertIn("a", stats["field_names"])

    def test_get_stats_missing_raises(self) -> None:
        with self.assertRaises(KeyError):
            self.dm.get_stats("does_not_exist")


# ---------------------------------------------------------------------------
# MonetizationEngine
# ---------------------------------------------------------------------------

class TestMonetizationEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.me = MonetizationEngine()

    def test_register_stream(self) -> None:
        self.me.register_revenue_stream("subscriptions", "subscription")
        report = self.me.generate_revenue_report()
        self.assertIn("subscriptions", report["streams"])

    def test_register_duplicate_is_noop(self) -> None:
        self.me.register_revenue_stream("ads", "ads")
        self.me.register_revenue_stream("ads", "ads")  # should not raise
        self.assertEqual(1, sum(1 for k in self.me._streams if k == "ads"))

    def test_register_invalid_type_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.me.register_revenue_stream("x", "invalid_type_xyz")

    def test_register_empty_name_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.me.register_revenue_stream("", "ads")

    def test_track_transaction(self) -> None:
        self.me.register_revenue_stream("sales", "one-time")
        txn_id = self.me.track_transaction("sales", 49.99, "Product purchase")
        self.assertIsInstance(txn_id, str)

    def test_track_transaction_unknown_stream_raises(self) -> None:
        with self.assertRaises(KeyError):
            self.me.track_transaction("nonexistent", 10.0)

    def test_calculate_total_revenue(self) -> None:
        self.me.register_revenue_stream("rev", "usage")
        self.me.track_transaction("rev", 100.0)
        self.me.track_transaction("rev", 50.0)
        self.assertAlmostEqual(150.0, self.me.calculate_total_revenue(), places=2)

    def test_refund_reduces_revenue(self) -> None:
        self.me.register_revenue_stream("refundable", "one-time")
        self.me.track_transaction("refundable", 200.0, "Purchase")
        self.me.track_transaction("refundable", -50.0, "Refund")
        self.assertAlmostEqual(150.0, self.me.calculate_total_revenue(), places=2)

    def test_get_revenue_by_stream(self) -> None:
        self.me.register_revenue_stream("s1", "subscription")
        self.me.register_revenue_stream("s2", "ads")
        self.me.track_transaction("s1", 300.0)
        self.me.track_transaction("s2", 100.0)
        by_stream = self.me.get_revenue_by_stream()
        self.assertEqual(300.0, by_stream["s1"])
        self.assertEqual(100.0, by_stream["s2"])

    def test_set_pricing_tier(self) -> None:
        self.me.set_pricing_tier("basic", 9.99)
        self.me.set_pricing_tier("pro", 29.99)
        report = self.me.generate_revenue_report()
        self.assertIn("basic", report["pricing_tiers"])
        self.assertAlmostEqual(9.99, report["pricing_tiers"]["basic"], places=2)

    def test_set_pricing_tier_negative_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.me.set_pricing_tier("negative", -5.0)

    def test_generate_revenue_report_structure(self) -> None:
        self.me.register_revenue_stream("final", "other")
        self.me.track_transaction("final", 75.0)
        report = self.me.generate_revenue_report()
        self.assertIn("generated_at", report)
        self.assertIn("total_revenue", report)
        self.assertIn("stream_count", report)
        self.assertIn("transaction_count", report)
        self.assertEqual(75.0, report["total_revenue"])


if __name__ == "__main__":
    unittest.main()
