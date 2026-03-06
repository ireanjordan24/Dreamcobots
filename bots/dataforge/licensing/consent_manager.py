"""
bots/dataforge/licensing/consent_manager.py

ConsentManager – manages user consent tokens for DataForge data collection.
"""

import hashlib
import logging
import secrets
import threading
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

# How long a consent token remains valid (days).
_TOKEN_VALIDITY_DAYS = 365


class ConsentManager:
    """
    Issues, verifies, and revokes consent tokens for DataForge users.

    Tokens are cryptographically random strings tied to a user ID and
    a list of consented data types, with a configurable expiry period.
    """

    def __init__(self, token_validity_days: int = _TOKEN_VALIDITY_DAYS) -> None:
        """
        Initialise the consent manager.

        Args:
            token_validity_days: Number of days a token is valid after issuance.
        """
        self._token_validity_days = token_validity_days
        self._consent_store: dict[str, dict[str, Any]] = {}   # token -> record
        self._user_tokens: dict[str, list[str]] = {}           # user_id -> [tokens]
        self._lock = threading.Lock()
        logger.info(
            "ConsentManager initialised (validity=%d days)", token_validity_days
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def request_consent(
        self, user_id: str, data_types: list[str]
    ) -> str:
        """
        Issue a new consent token for the given user and data types.

        Any existing active tokens for the same user remain valid until
        they expire or are explicitly revoked.

        Args:
            user_id: Identifier of the consenting user.
            data_types: List of data categories the user consents to share
                        (e.g. ``["voice", "behavioral"]``).

        Returns:
            A URL-safe consent token string.
        """
        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        record: dict[str, Any] = {
            "token": token,
            "user_id": user_id,
            "data_types": list(data_types),
            "issued_at": now.isoformat(),
            "expires_at": (
                now + timedelta(days=self._token_validity_days)
            ).isoformat(),
            "revoked": False,
        }
        with self._lock:
            self._consent_store[token] = record
            self._user_tokens.setdefault(user_id, []).append(token)

        logger.info(
            "Consent token issued for user '%s' covering: %s", user_id, data_types
        )
        return token

    def verify_consent(self, consent_token: str) -> bool:
        """
        Check whether a consent token is valid (exists, not revoked, not expired).

        Args:
            consent_token: The token to verify.

        Returns:
            ``True`` if the token is valid and active, otherwise ``False``.
        """
        with self._lock:
            record = self._consent_store.get(consent_token)

        if record is None:
            logger.debug("Consent token not found")
            return False
        if record["revoked"]:
            logger.debug("Consent token has been revoked")
            return False

        expires_at = datetime.fromisoformat(record["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            logger.debug("Consent token has expired")
            return False

        return True

    def revoke_consent(self, user_id: str) -> int:
        """
        Revoke all active consent tokens for a user.

        Args:
            user_id: Identifier of the user whose consent is being withdrawn.

        Returns:
            The number of tokens revoked.
        """
        revoked_count = 0
        with self._lock:
            for token in self._user_tokens.get(user_id, []):
                record = self._consent_store.get(token)
                if record and not record["revoked"]:
                    record["revoked"] = True
                    revoked_count += 1

        logger.info(
            "Revoked %d consent token(s) for user '%s'", revoked_count, user_id
        )
        return revoked_count

    def get_consent_status(self, user_id: str) -> dict[str, Any]:
        """
        Return a summary of consent status for a user.

        Args:
            user_id: Identifier of the user.

        Returns:
            A dict with counts of active, expired, and revoked tokens plus
            the list of consented data types from active tokens.
        """
        now = datetime.now(timezone.utc)
        active: list[dict] = []
        expired_count = 0
        revoked_count = 0
        consented_types: set[str] = set()

        with self._lock:
            tokens = self._user_tokens.get(user_id, [])
            for token in tokens:
                record = self._consent_store.get(token, {})
                if record.get("revoked"):
                    revoked_count += 1
                elif datetime.fromisoformat(record["expires_at"]) <= now:
                    expired_count += 1
                else:
                    active.append(record)
                    consented_types.update(record.get("data_types", []))

        return {
            "user_id": user_id,
            "active_tokens": len(active),
            "expired_tokens": expired_count,
            "revoked_tokens": revoked_count,
            "consented_data_types": sorted(consented_types),
            "has_active_consent": len(active) > 0,
        }
