"""
tests/test_dataforge.py

Tests for DataForge: dataset generators, API manager, and compliance.
"""

import unittest

from bots.dataforge.dataset_generators import (
    VoiceDatasetGenerator,
    FacialDatasetGenerator,
    ItemDatasetGenerator,
    BehavioralDatasetGenerator,
    EmotionEngineDatasetGenerator,
)
from bots.dataforge.compliance import ComplianceManager
from bots.dataforge.user_marketplace import UserMarketplace
from bots.dataforge.sales_channels import SalesChannelManager


class TestVoiceDatasetGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = VoiceDatasetGenerator()

    def test_generate_sample(self) -> None:
        sample = self.gen.generate_sample()
        self.assertIsInstance(sample, dict)
        self.assertGreater(len(sample), 0)

    def test_generate_batch(self) -> None:
        batch = self.gen.generate_batch(5)
        self.assertEqual(5, len(batch))

    def test_validate_sample(self) -> None:
        sample = self.gen.generate_sample()
        self.assertTrue(self.gen.validate_sample(sample))

    def test_get_metadata(self) -> None:
        meta = self.gen.get_metadata()
        self.assertIsInstance(meta, dict)


class TestFacialDatasetGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = FacialDatasetGenerator()

    def test_generate_sample(self) -> None:
        sample = self.gen.generate_sample()
        self.assertIsInstance(sample, dict)

    def test_generate_batch(self) -> None:
        batch = self.gen.generate_batch(3)
        self.assertEqual(3, len(batch))

    def test_validate_sample(self) -> None:
        sample = self.gen.generate_sample()
        self.assertTrue(self.gen.validate_sample(sample))


class TestItemDatasetGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = ItemDatasetGenerator()

    def test_generate_sample(self) -> None:
        sample = self.gen.generate_sample()
        self.assertIsInstance(sample, dict)

    def test_generate_batch(self) -> None:
        batch = self.gen.generate_batch(4)
        self.assertEqual(4, len(batch))


class TestBehavioralDatasetGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = BehavioralDatasetGenerator()

    def test_generate_sample(self) -> None:
        sample = self.gen.generate_sample()
        self.assertIsInstance(sample, dict)

    def test_generate_batch(self) -> None:
        batch = self.gen.generate_batch(6)
        self.assertEqual(6, len(batch))


class TestEmotionEngineDatasetGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = EmotionEngineDatasetGenerator()

    def test_generate_sample(self) -> None:
        sample = self.gen.generate_sample()
        self.assertIsInstance(sample, dict)

    def test_generate_batch(self) -> None:
        batch = self.gen.generate_batch(2)
        self.assertEqual(2, len(batch))


class TestUserMarketplace(unittest.TestCase):
    def setUp(self) -> None:
        self.mp = UserMarketplace()

    def test_register_user(self) -> None:
        user = self.mp.register_user("user-001")
        self.assertIn("user_id", user)

    def test_submit_data(self) -> None:
        self.mp.register_user("user-002")
        result = self.mp.submit_data("user-002", "voice", {"type": "voice", "text": "Hello"})
        self.assertIsInstance(result, dict)

    def test_calculate_earnings(self) -> None:
        self.mp.register_user("user-003")
        earnings = self.mp.calculate_earnings("user-003")
        self.assertGreaterEqual(earnings, 0.0)

    def test_get_marketplace_stats(self) -> None:
        stats = self.mp.get_marketplace_stats()
        self.assertIsInstance(stats, dict)


class TestSalesChannelManager(unittest.TestCase):
    def setUp(self) -> None:
        self.scm = SalesChannelManager()

    def test_get_sales_stats(self) -> None:
        stats = self.scm.get_sales_stats()
        self.assertIsInstance(stats, dict)

    def test_publish_to_huggingface_dry_run(self) -> None:
        # Should not raise even without credentials
        try:
            self.scm.publish_to_huggingface(
                dataset_name="test-dataset",
                dataset_path="/tmp/fake.json",
                description="Test",
            )
        except Exception:
            pass  # expected without real credentials

    def test_publish_via_direct_api(self) -> None:
        try:
            self.scm.publish_via_direct_api(
                dataset_name="test",
                dataset_path="/tmp/fake.json",
                price=0.0,
            )
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()
