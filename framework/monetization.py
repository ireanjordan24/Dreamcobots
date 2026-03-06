"""
framework/monetization.py

MonetizationEngine for tracking revenue streams, transactions, pricing tiers,
and generating revenue reports.
"""

from __future__ import annotations

import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class MonetizationEngine:
    """
    Tracks multiple revenue streams, individual transactions, and pricing tiers.
    Provides revenue calculations and structured report generation.
    """

    _VALID_TYPES: frozenset[str] = frozenset(
        {"subscription", "one-time", "usage", "referral", "affiliate", "ads", "other"}
    )

    def __init__(self) -> None:
        self._lock: threading.RLock = threading.RLock()
        # { stream_name: {"type": str, "created_at": str} }
        self._streams: dict[str, dict[str, Any]] = {}
        # { stream_name: [ {id, amount, description, timestamp}, ... ] }
        self._transactions: dict[str, list[dict[str, Any]]] = {}
        # { tier_name: price_float }
        self._pricing_tiers: dict[str, float] = {}
        self.logger = logging.getLogger("MonetizationEngine")

    # ------------------------------------------------------------------
    # Revenue streams
    # ------------------------------------------------------------------

    def register_revenue_stream(self, name: str, type: str) -> None:
        """
        Register a new revenue stream.

        Args:
            name: Unique stream name (e.g. ``"saas_subscriptions"``).
            type: Stream type — one of ``subscription``, ``one-time``,
                  ``usage``, ``referral``, ``affiliate``, ``ads``, ``other``.

        Raises:
            ValueError: If *name* is empty or *type* is not supported.
        """
        if not name or not name.strip():
            raise ValueError("Stream name must be a non-empty string.")
        stream_type = type.lower().strip()
        if stream_type not in self._VALID_TYPES:
            raise ValueError(
                f"Unsupported stream type '{type}'. "
                f"Valid types: {sorted(self._VALID_TYPES)}"
            )
        with self._lock:
            if name in self._streams:
                self.logger.warning("Stream '%s' already registered. Skipping.", name)
                return
            self._streams[name] = {
                "type": stream_type,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._transactions[name] = []
        self.logger.info("Revenue stream registered: '%s' (%s).", name, stream_type)

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------

    def track_transaction(
        self,
        stream_name: str,
        amount: float,
        description: str = "",
    ) -> str:
        """
        Record a transaction against a registered revenue stream.

        Args:
            stream_name: The target stream's name.
            amount: Transaction amount in the base currency (may be negative for refunds).
            description: Human-readable transaction note.

        Returns:
            The generated transaction ID.

        Raises:
            KeyError: If *stream_name* is not registered.
        """
        with self._lock:
            if stream_name not in self._streams:
                raise KeyError(
                    f"Revenue stream '{stream_name}' is not registered."
                )
            txn_id = str(uuid.uuid4())
            txn: dict[str, Any] = {
                "id": txn_id,
                "amount": float(amount),
                "description": description,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._transactions[stream_name].append(txn)
        self.logger.debug(
            "Transaction %s: stream='%s', amount=%.2f", txn_id, stream_name, amount
        )
        return txn_id

    # ------------------------------------------------------------------
    # Revenue calculations
    # ------------------------------------------------------------------

    def calculate_total_revenue(self) -> float:
        """
        Sum all transaction amounts across all streams.

        Returns:
            Total revenue as a float.
        """
        with self._lock:
            total = sum(
                txn["amount"]
                for txns in self._transactions.values()
                for txn in txns
            )
        return round(total, 2)

    def get_revenue_by_stream(self) -> dict[str, float]:
        """
        Return a dict mapping each stream name to its total revenue.

        Returns:
            ``{ stream_name: total_amount }``
        """
        with self._lock:
            return {
                stream: round(sum(t["amount"] for t in txns), 2)
                for stream, txns in self._transactions.items()
            }

    # ------------------------------------------------------------------
    # Pricing tiers
    # ------------------------------------------------------------------

    def set_pricing_tier(self, tier: str, price: float) -> None:
        """
        Define or update a pricing tier.

        Args:
            tier: Tier name (e.g. ``"basic"``, ``"pro"``, ``"enterprise"``).
            price: Price for the tier (must be >= 0).

        Raises:
            ValueError: If *price* is negative.
        """
        if price < 0:
            raise ValueError(f"Price must be >= 0, got {price}.")
        with self._lock:
            self._pricing_tiers[tier] = float(price)
        self.logger.info("Pricing tier '%s' set to %.2f.", tier, price)

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def generate_revenue_report(self) -> dict[str, Any]:
        """
        Generate a comprehensive revenue report.

        Returns:
            Dict with ``generated_at``, ``total_revenue``, ``stream_count``,
            ``transaction_count``, ``revenue_by_stream``, ``pricing_tiers``,
            and ``streams`` detail.
        """
        with self._lock:
            revenue_by_stream = {
                stream: round(sum(t["amount"] for t in txns), 2)
                for stream, txns in self._transactions.items()
            }
            total_revenue = round(sum(revenue_by_stream.values()), 2)
            transaction_count = sum(
                len(txns) for txns in self._transactions.values()
            )
            streams_detail: dict[str, Any] = {
                name: {
                    **info,
                    "transaction_count": len(self._transactions.get(name, [])),
                    "total_revenue": revenue_by_stream.get(name, 0.0),
                }
                for name, info in self._streams.items()
            }
            pricing_tiers = dict(self._pricing_tiers)

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_revenue": total_revenue,
            "stream_count": len(self._streams),
            "transaction_count": transaction_count,
            "revenue_by_stream": revenue_by_stream,
            "pricing_tiers": pricing_tiers,
            "streams": streams_detail,
        }
