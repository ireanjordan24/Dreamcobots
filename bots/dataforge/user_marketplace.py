"""
bots/dataforge/user_marketplace.py

UserMarketplace – a data-selling cooperative where users earn revenue
from contributing their consented data to DataForge datasets.
"""

import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Simulated earnings rate per data submission (USD).
_EARNINGS_PER_SUBMISSION: dict[str, float] = {
    "voice": 0.05,
    "facial": 0.08,
    "behavioral": 0.03,
    "emotion": 0.04,
    "item": 0.02,
    "default": 0.01,
}


class UserMarketplace:
    """
    Manages user registration, data submissions, earnings, and payouts
    for the DataForge data-selling cooperative.

    All monetary values are expressed in USD.
    """

    def __init__(self) -> None:
        """Initialise the marketplace with empty user and transaction stores."""
        self._users: dict[str, dict[str, Any]] = {}
        self._submissions: list[dict[str, Any]] = []
        self._transactions: list[dict[str, Any]] = []
        self._lock = threading.RLock()
        logger.info("UserMarketplace initialised")

    # ------------------------------------------------------------------
    # User management
    # ------------------------------------------------------------------

    def register_user(
        self, user_id: str, consent_level: str = "standard"
    ) -> dict[str, Any]:
        """
        Register a new user with the marketplace.

        Args:
            user_id: Unique identifier for the user.
            consent_level: One of ``"minimal"``, ``"standard"``, or ``"full"``.

        Returns:
            The newly created user profile dict.

        Raises:
            ValueError: If *user_id* is already registered.
        """
        valid_levels = {"minimal", "standard", "full"}
        if consent_level not in valid_levels:
            consent_level = "standard"

        with self._lock:
            if user_id in self._users:
                raise ValueError(f"User '{user_id}' is already registered")
            profile: dict[str, Any] = {
                "user_id": user_id,
                "consent_level": consent_level,
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "balance_usd": 0.0,
                "total_earned_usd": 0.0,
                "total_paid_usd": 0.0,
                "submission_count": 0,
                "active": True,
            }
            self._users[user_id] = profile
        logger.info("Registered user '%s' with consent_level='%s'", user_id, consent_level)
        return profile

    def _require_user(self, user_id: str) -> dict[str, Any]:
        """Return the user profile or raise ``KeyError`` if not found."""
        user = self._users.get(user_id)
        if user is None:
            raise KeyError(f"User '{user_id}' not found in marketplace")
        return user

    # ------------------------------------------------------------------
    # Data submission
    # ------------------------------------------------------------------

    def submit_data(
        self,
        user_id: str,
        data_type: str,
        data: dict,
    ) -> dict[str, Any]:
        """
        Record a data submission and credit earnings to the user.

        Args:
            user_id: Identifier of the submitting user.
            data_type: Category of data (e.g. ``"voice"``, ``"behavioral"``).
            data: The actual data payload (stored by reference).

        Returns:
            A submission receipt dict including the credited amount.
        """
        with self._lock:
            user = self._require_user(user_id)
            rate = _EARNINGS_PER_SUBMISSION.get(
                data_type, _EARNINGS_PER_SUBMISSION["default"]
            )
            submission_id = str(uuid.uuid4())
            receipt: dict[str, Any] = {
                "submission_id": submission_id,
                "user_id": user_id,
                "data_type": data_type,
                "data_keys": list(data.keys()),
                "credited_usd": rate,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._submissions.append(receipt)
            user["balance_usd"] = round(user["balance_usd"] + rate, 4)
            user["total_earned_usd"] = round(user["total_earned_usd"] + rate, 4)
            user["submission_count"] += 1

        logger.debug(
            "Submission %s from user '%s' (type=%s, +$%.4f)",
            submission_id,
            user_id,
            data_type,
            rate,
        )
        return receipt

    # ------------------------------------------------------------------
    # Earnings & payouts
    # ------------------------------------------------------------------

    def calculate_earnings(self, user_id: str) -> float:
        """
        Return the current unpaid balance for *user_id*.

        Args:
            user_id: Identifier of the user.

        Returns:
            Current balance in USD as a float.
        """
        with self._lock:
            return self._require_user(user_id)["balance_usd"]

    def pay_user(self, user_id: str, amount: float) -> dict[str, Any]:
        """
        Simulate a payout to *user_id*.

        The balance is reduced by *amount*; if *amount* exceeds the current
        balance the entire balance is paid out.

        Args:
            user_id: Identifier of the user to pay.
            amount: Amount to pay in USD.

        Returns:
            A transaction receipt dict.

        Raises:
            ValueError: If *amount* is not positive.
        """
        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        with self._lock:
            user = self._require_user(user_id)
            actual = min(amount, user["balance_usd"])
            user["balance_usd"] = round(user["balance_usd"] - actual, 4)
            user["total_paid_usd"] = round(user["total_paid_usd"] + actual, 4)
            tx: dict[str, Any] = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": user_id,
                "requested_usd": amount,
                "paid_usd": actual,
                "remaining_balance_usd": user["balance_usd"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "simulated_success",
            }
            self._transactions.append(tx)

        logger.info("Paid $%.4f to user '%s'", actual, user_id)
        return tx

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_marketplace_stats(self) -> dict[str, Any]:
        """
        Return aggregate statistics for the marketplace.

        Returns:
            A dict with user counts, submission totals, and financial totals.
        """
        with self._lock:
            total_users = len(self._users)
            active_users = sum(1 for u in self._users.values() if u["active"])
            total_submissions = len(self._submissions)
            total_earned = sum(u["total_earned_usd"] for u in self._users.values())
            total_paid = sum(u["total_paid_usd"] for u in self._users.values())

            by_type: dict[str, int] = {}
            for sub in self._submissions:
                dt = sub["data_type"]
                by_type[dt] = by_type.get(dt, 0) + 1

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_users": total_users,
            "active_users": active_users,
            "total_submissions": total_submissions,
            "submissions_by_type": by_type,
            "total_earned_usd": round(total_earned, 4),
            "total_paid_usd": round(total_paid, 4),
            "total_outstanding_usd": round(total_earned - total_paid, 4),
            "total_transactions": len(self._transactions),
        }
