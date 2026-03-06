"""
bots/referral-bot/referral_bot.py

ReferralBot — manages referral programs, link creation, and earnings.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

logger = logging.getLogger(__name__)

_COMMISSION_RATE: float = 0.10  # 10% per referral


class ReferralBot(BotBase):
    """
    Manages a referral programme: link creation, tracking, earnings,
    and referral-tree visualisation.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="ReferralBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._referral_links: dict[str, str] = {}          # user_id -> code
        self._referrals: dict[str, list[str]] = {}         # code -> [new_user_ids]
        self._earnings: dict[str, float] = {}              # user_id -> total earned
        self._user_parent: dict[str, str] = {}             # new_user_id -> referrer_user_id
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("ReferralBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("ReferralBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def create_referral_link(self, user_id: str) -> str:
        """
        Generate a unique referral link/code for *user_id*.

        Args:
            user_id: The referring user's ID.

        Returns:
            A URL-safe referral link string.
        """
        with self._lock_extra:
            if user_id in self._referral_links:
                code = self._referral_links[user_id]
                return f"https://dreamcobots.ai/join?ref={code}"
            code = hashlib.sha1(
                f"{user_id}{uuid.uuid4()}".encode()
            ).hexdigest()[:12].upper()
            self._referral_links[user_id] = code
            self._referrals[code] = []
            self._earnings.setdefault(user_id, 0.0)
        link = f"https://dreamcobots.ai/join?ref={code}"
        self.log_activity(f"Referral link created for user '{user_id}': {link}")
        return link

    def track_referral(self, referral_code: str, new_user_id: str) -> None:
        """
        Record a successful referral conversion.

        Args:
            referral_code: The referral code used by the new user.
            new_user_id: ID of the newly registered user.

        Raises:
            KeyError: If *referral_code* is not registered.
        """
        with self._lock_extra:
            if referral_code not in self._referrals:
                raise KeyError(f"Referral code '{referral_code}' is not registered.")
            if new_user_id in self._user_parent:
                self.logger.warning(
                    "User '%s' already has a referral source.", new_user_id
                )
                return
            self._referrals[referral_code].append(new_user_id)
            # Find referrer
            referrer = next(
                (uid for uid, code in self._referral_links.items() if code == referral_code),
                None,
            )
            if referrer:
                self._user_parent[new_user_id] = referrer
                commission = 10.0  # flat $10 per referral
                self._earnings[referrer] = round(self._earnings.get(referrer, 0.0) + commission, 2)
        self.log_activity(
            f"Referral tracked: code={referral_code}, new_user={new_user_id}."
        )

    def calculate_earnings(self, user_id: str) -> float:
        """
        Return total referral earnings for *user_id*.

        Args:
            user_id: The user's ID.

        Returns:
            Total earnings as a float.
        """
        with self._lock_extra:
            earnings = self._earnings.get(user_id, 0.0)
        self.log_activity(f"Earnings calculated for user '{user_id}': ${earnings}")
        return earnings

    def get_referral_tree(self, user_id: str) -> dict[str, Any]:
        """
        Return the referral sub-tree rooted at *user_id*.

        Args:
            user_id: Root user ID.

        Returns:
            Dict with ``user_id``, ``referral_code``, ``direct_referrals``,
            ``total_earnings``, and ``sub_trees`` (recursive dicts).
        """
        with self._lock_extra:
            code = self._referral_links.get(user_id, "N/A")
            direct_ids = list(self._referrals.get(code, []))
            earnings = self._earnings.get(user_id, 0.0)

        sub_trees = [self.get_referral_tree(child) for child in direct_ids]
        return {
            "user_id": user_id,
            "referral_code": code,
            "direct_referrals": len(direct_ids),
            "total_earnings": earnings,
            "sub_trees": sub_trees,
        }
