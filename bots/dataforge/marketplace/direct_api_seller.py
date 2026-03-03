"""
bots/dataforge/marketplace/direct_api_seller.py

DirectAPISeller – manages direct API data sales to enterprise buyers.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class DirectAPISeller:
    """
    Manages direct API-based data sales to enterprise buyers.

    Buyers register with an API key and purchase dataset access; all
    transactions are simulated and recorded for audit purposes.
    """

    def __init__(self, price_per_record_usd: float = 0.001) -> None:
        """
        Initialise the seller.

        Args:
            price_per_record_usd: Default price charged per dataset record.
        """
        self.price_per_record_usd = price_per_record_usd
        self._buyers: dict[str, dict[str, Any]] = {}
        self._transactions: list[dict[str, Any]] = []
        logger.info(
            "DirectAPISeller initialised (price_per_record=$%.4f)",
            price_per_record_usd,
        )

    # ------------------------------------------------------------------
    # Buyer management
    # ------------------------------------------------------------------

    def register_buyer(
        self, buyer_id: str, company: str = "Unknown Corp"
    ) -> dict[str, Any]:
        """
        Register a new enterprise buyer.

        Args:
            buyer_id: Unique identifier for the buyer.
            company: Buyer's company name.

        Returns:
            The buyer profile dict including their API key.

        Raises:
            ValueError: If *buyer_id* is already registered.
        """
        if buyer_id in self._buyers:
            raise ValueError(f"Buyer '{buyer_id}' is already registered")

        api_key = f"dfk_{uuid.uuid4().hex}"
        profile: dict[str, Any] = {
            "buyer_id": buyer_id,
            "company": company,
            "api_key": api_key,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "total_spent_usd": 0.0,
            "total_records_purchased": 0,
            "active": True,
        }
        self._buyers[buyer_id] = profile
        logger.info("Registered buyer '%s' (%s)", buyer_id, company)
        return profile

    # ------------------------------------------------------------------
    # Data sales
    # ------------------------------------------------------------------

    def sell_dataset(
        self,
        buyer_id: str,
        dataset_name: str,
        data: list[dict[str, Any]],
        price_per_record: float | None = None,
    ) -> dict[str, Any]:
        """
        Simulate selling a dataset to a registered buyer.

        Args:
            buyer_id: Identifier of the purchasing buyer.
            dataset_name: Name / label for the dataset being sold.
            data: List of dataset sample records.
            price_per_record: Override per-record price (uses default if ``None``).

        Returns:
            A transaction receipt dict.

        Raises:
            KeyError: If *buyer_id* is not registered.
        """
        buyer = self._buyers.get(buyer_id)
        if buyer is None:
            raise KeyError(f"Buyer '{buyer_id}' not registered")

        rate = price_per_record if price_per_record is not None else self.price_per_record_usd
        total_cost = round(len(data) * rate, 4)

        tx: dict[str, Any] = {
            "transaction_id": str(uuid.uuid4()),
            "buyer_id": buyer_id,
            "dataset_name": dataset_name,
            "num_records": len(data),
            "price_per_record_usd": rate,
            "total_cost_usd": total_cost,
            "access_token": uuid.uuid4().hex,
            "download_url": f"https://api.dreamcobots.ai/datasets/{uuid.uuid4().hex[:8]}",
            "expires_at": None,  # perpetual access for purchased datasets
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }
        self._transactions.append(tx)
        buyer["total_spent_usd"] = round(buyer["total_spent_usd"] + total_cost, 4)
        buyer["total_records_purchased"] += len(data)

        logger.info(
            "[DirectAPI] Sold '%s' to buyer '%s' (%d records, $%.4f)",
            dataset_name,
            buyer_id,
            len(data),
            total_cost,
        )
        return tx

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_stats(self) -> dict[str, Any]:
        """Return aggregate sales statistics."""
        total_revenue = sum(tx["total_cost_usd"] for tx in self._transactions)
        total_records = sum(tx["num_records"] for tx in self._transactions)
        return {
            "publisher": "DirectAPISeller",
            "registered_buyers": len(self._buyers),
            "total_transactions": len(self._transactions),
            "total_records_sold": total_records,
            "total_revenue_usd": round(total_revenue, 4),
            "price_per_record_usd": self.price_per_record_usd,
        }
