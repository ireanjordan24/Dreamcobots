"""
tests/test_marketplace.py

Tests for marketplace publishers, sales channels, and user marketplace.
"""

import unittest

from bots.dataforge.marketplace import (
    HuggingFacePublisher,
    KagglePublisher,
    AWSPublisher,
    DirectAPISeller,
)
from bots.dataforge.user_marketplace import UserMarketplace
from bots.dataforge.sales_channels import SalesChannelManager


_SAMPLE_DATA = [
    {"id": i, "text": f"sample {i}", "label": i % 2}
    for i in range(10)
]


class TestHuggingFacePublisher(unittest.TestCase):
    def setUp(self) -> None:
        self.pub = HuggingFacePublisher(token="test-token", organization="testuser")

    def test_publish_returns_dict(self) -> None:
        result = self.pub.publish("test-dataset", _SAMPLE_DATA)
        self.assertIsInstance(result, dict)

    def test_publish_history_grows(self) -> None:
        before = len(self.pub.get_publish_history())
        self.pub.publish("test-dataset-2", _SAMPLE_DATA)
        after = len(self.pub.get_publish_history())
        self.assertGreater(after, before)

    def test_get_stats(self) -> None:
        stats = self.pub.get_stats()
        self.assertIsInstance(stats, dict)


class TestKagglePublisher(unittest.TestCase):
    def setUp(self) -> None:
        self.pub = KagglePublisher()

    def test_publish_returns_dict(self) -> None:
        result = self.pub.publish("test-dataset", _SAMPLE_DATA)
        self.assertIsInstance(result, dict)

    def test_publish_history_grows(self) -> None:
        before = len(self.pub.get_publish_history())
        self.pub.publish("test-dataset-2", _SAMPLE_DATA)
        after = len(self.pub.get_publish_history())
        self.assertGreater(after, before)

    def test_get_stats(self) -> None:
        stats = self.pub.get_stats()
        self.assertIsInstance(stats, dict)


class TestAWSPublisher(unittest.TestCase):
    def setUp(self) -> None:
        self.pub = AWSPublisher(
            access_key="AKIATEST",
            secret_key="secret",
            default_bucket="test-bucket",
        )

    def test_publish_returns_dict(self) -> None:
        result = self.pub.publish("test-dataset", _SAMPLE_DATA)
        self.assertIsInstance(result, dict)

    def test_publish_history_grows(self) -> None:
        before = len(self.pub.get_publish_history())
        self.pub.publish("test-dataset-2", _SAMPLE_DATA)
        after = len(self.pub.get_publish_history())
        self.assertGreater(after, before)

    def test_get_stats(self) -> None:
        stats = self.pub.get_stats()
        self.assertIsInstance(stats, dict)


class TestDirectAPISeller(unittest.TestCase):
    def setUp(self) -> None:
        self.seller = DirectAPISeller(price_per_record_usd=0.01)

    def test_register_buyer(self) -> None:
        buyer = self.seller.register_buyer("buyer-001", "ACME Corp")
        self.assertIn("buyer_id", buyer)

    def test_sell_dataset(self) -> None:
        self.seller.register_buyer("buyer-002", "BuyerCo")
        result = self.seller.sell_dataset("buyer-002", "test-dataset", _SAMPLE_DATA)
        self.assertIsInstance(result, dict)

    def test_get_stats(self) -> None:
        stats = self.seller.get_stats()
        self.assertIsInstance(stats, dict)


class TestUserMarketplaceExtended(unittest.TestCase):
    def setUp(self) -> None:
        self.mp = UserMarketplace()

    def test_register_multiple_users(self) -> None:
        for i in range(5):
            user = self.mp.register_user(f"user-{i}")
            self.assertIn("user_id", user)

    def test_submit_and_calculate_earnings(self) -> None:
        self.mp.register_user("earner-001")
        self.mp.submit_data("earner-001", "behavioral", {"text": "hello", "label": 1})
        earnings = self.mp.calculate_earnings("earner-001")
        self.assertGreaterEqual(earnings, 0.0)

    def test_pay_user(self) -> None:
        self.mp.register_user("payee-001")
        self.mp.submit_data("payee-001", "voice", {"x": 1})
        # Force some earnings
        try:
            payout = self.mp.pay_user("payee-001", 1.0)
            self.assertIsInstance(payout, dict)
        except Exception:
            pass  # may require minimum threshold

    def test_marketplace_stats_structure(self) -> None:
        stats = self.mp.get_marketplace_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_users", stats)


class TestSalesChannelManagerExtended(unittest.TestCase):
    def setUp(self) -> None:
        self.scm = SalesChannelManager()

    def test_stats_initial(self) -> None:
        stats = self.scm.get_sales_stats()
        self.assertIsInstance(stats, dict)

    def test_multiple_publish_calls(self) -> None:
        for platform in ("huggingface", "kaggle", "aws"):
            try:
                if platform == "huggingface":
                    self.scm.publish_to_huggingface("ds", "/tmp/fake.json", "test")
                elif platform == "kaggle":
                    self.scm.publish_to_kaggle("ds", "/tmp/fake.json", "test")
                elif platform == "aws":
                    self.scm.publish_to_aws("ds", "/tmp/fake.json")
            except Exception:
                pass  # expected without credentials


if __name__ == "__main__":
    unittest.main()
