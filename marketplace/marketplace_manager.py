"""
marketplace/marketplace_manager.py

High-level marketplace management: dataset listings, purchases, publishing,
statistics, and payment processing.
"""

import uuid
from datetime import datetime, timezone
from typing import Any


class MarketplaceManager:
    """Manages dataset listings, transactions, and market statistics."""

    def __init__(self) -> None:
        self._listings: list[dict[str, Any]] = []
        self._transactions: list[dict[str, Any]] = []

    def list_datasets(self, filters: dict | None = None) -> list:
        """
        Return available dataset listings, optionally filtered.

        Args:
            filters: Optional dict of key/value pairs to filter by (equality match).

        Returns:
            List of matching dataset listing dicts.
        """
        results = list(self._listings)
        if filters:
            for key, value in filters.items():
                results = [d for d in results if d.get(key) == value]
        return results

    def purchase_dataset(self, dataset_id: str, buyer_id: str) -> dict:
        """
        Record a dataset purchase and return a transaction receipt.

        Args:
            dataset_id: The ID of the dataset to purchase.
            buyer_id: The ID of the purchasing user.

        Returns:
            Transaction receipt dict with transaction_id, status, and timestamp.
        """
        listing = next((d for d in self._listings if d.get("dataset_id") == dataset_id), None)
        status = "completed" if listing else "dataset_not_found"
        receipt: dict[str, Any] = {
            "transaction_id": str(uuid.uuid4()),
            "dataset_id": dataset_id,
            "buyer_id": buyer_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._transactions.append(receipt)
        return receipt

    def publish_dataset(self, dataset: dict, seller_id: str) -> dict:
        """
        Publish a new dataset listing to the marketplace.

        Args:
            dataset: Dataset metadata dict (must include at least a ``name`` key).
            seller_id: The ID of the seller.

        Returns:
            Published listing dict including a generated ``dataset_id``.
        """
        listing = {
            "dataset_id": str(uuid.uuid4()),
            "seller_id": seller_id,
            "published_at": datetime.now(timezone.utc).isoformat(),
            **dataset,
        }
        self._listings.append(listing)
        return listing

    def get_market_stats(self) -> dict:
        """
        Return high-level marketplace statistics.

        Returns:
            dict with total_listings, total_transactions, and revenue_usd.
        """
        revenue = sum(
            t.get("amount", 0.0)
            for t in self._transactions
            if t.get("status") == "completed"
        )
        return {
            "total_listings": len(self._listings),
            "total_transactions": len(self._transactions),
            "revenue_usd": revenue,
        }

    def process_payment(self, buyer_id: str, amount: float) -> bool:
        """
        Simulate payment processing for a buyer.

        Args:
            buyer_id: The ID of the buyer.
            amount: Amount in USD to charge (must be > 0).

        Returns:
            ``True`` if payment succeeded, ``False`` otherwise.
        """
        if amount <= 0:
            return False
        self._transactions.append({
            "transaction_id": str(uuid.uuid4()),
            "buyer_id": buyer_id,
            "amount": amount,
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return True
