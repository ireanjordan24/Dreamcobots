"""
bots/dataforge/licensing/anonymizer.py

DataAnonymizer – anonymises personally identifiable information (PII)
and applies differential privacy to numeric datasets.
"""

import hashlib
import logging
import math
import random
import re
import secrets
from typing import Any

logger = logging.getLogger(__name__)

# Regex patterns for common PII formats.
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"\+?[\d\s\-().]{7,20}")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

# Fields considered PII in a dict record.
_PII_FIELD_NAMES: set[str] = {
    "name", "full_name", "first_name", "last_name",
    "email", "email_address",
    "phone", "phone_number", "mobile",
    "address", "street_address", "postal_code", "zip_code",
    "social_security_number", "ssn",
    "date_of_birth", "dob",
    "ip_address",
}

_LOCATION_FIELD_NAMES: set[str] = {
    "location", "gps", "latitude", "longitude", "lat", "lon",
    "address", "city", "country", "region", "postcode", "zip_code",
}

# Granularity to apply when rounding GPS coordinates (degrees).
_GPS_GRANULARITY = 0.1


class DataAnonymizer:
    """
    Anonymises PII in dataset records and applies statistical noise for
    differential privacy.

    All methods return *new* dicts/lists; the originals are never mutated.
    """

    def __init__(self, hash_salt: str | None = None) -> None:
        """
        Initialise the anonymizer.

        Args:
            hash_salt: Optional salt string used when hashing identifiers.
                       A random salt is generated if not provided.
        """
        self._salt = hash_salt or secrets.token_hex(16)
        logger.info("DataAnonymizer initialised")

    # ------------------------------------------------------------------
    # PII anonymisation
    # ------------------------------------------------------------------

    def _mask_string(self, value: str) -> str:
        """Replace a PII string with a masked placeholder."""
        if not value:
            return value
        return "[REDACTED]"

    def _scrub_text(self, text: str) -> str:
        """Remove inline PII patterns from free text."""
        text = _EMAIL_RE.sub("[EMAIL_REDACTED]", text)
        text = _SSN_RE.sub("[SSN_REDACTED]", text)
        return text

    def anonymize_pii(self, data: dict) -> dict:
        """
        Replace PII fields in *data* with redacted placeholders.

        String values in known PII fields are replaced with ``"[REDACTED]"``.
        String values in non-PII fields are scanned for embedded email and
        SSN patterns which are also redacted.

        Args:
            data: Input record dict.

        Returns:
            A new dict with PII fields anonymised.
        """
        result: dict[str, Any] = {}
        for key, value in data.items():
            lower_key = key.lower()
            if lower_key in _PII_FIELD_NAMES:
                result[key] = self._mask_string(str(value)) if value else value
            elif isinstance(value, str):
                result[key] = self._scrub_text(value)
            elif isinstance(value, dict):
                result[key] = self.anonymize_pii(value)
            elif isinstance(value, list):
                result[key] = [
                    self.anonymize_pii(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        logger.debug("PII anonymisation applied to record with keys: %s", list(data.keys()))
        return result

    # ------------------------------------------------------------------
    # Location anonymisation
    # ------------------------------------------------------------------

    def anonymize_location(self, data: dict) -> dict:
        """
        Anonymise location fields in *data* by rounding coordinates and
        removing precise address strings.

        Args:
            data: Input record dict.

        Returns:
            A new dict with location data coarsened or removed.
        """
        result: dict[str, Any] = {}
        for key, value in data.items():
            lower_key = key.lower()
            if lower_key in {"latitude", "lat"} and isinstance(value, (int, float)):
                result[key] = round(value / _GPS_GRANULARITY) * _GPS_GRANULARITY
            elif lower_key in {"longitude", "lon"} and isinstance(value, (int, float)):
                result[key] = round(value / _GPS_GRANULARITY) * _GPS_GRANULARITY
            elif lower_key in {"address", "street_address", "postcode", "zip_code"}:
                result[key] = "[LOCATION_REDACTED]"
            elif isinstance(value, dict):
                result[key] = self.anonymize_location(value)
            else:
                result[key] = value
        logger.debug("Location anonymisation applied")
        return result

    # ------------------------------------------------------------------
    # Identifier hashing
    # ------------------------------------------------------------------

    def hash_identifier(self, identifier: str) -> str:
        """
        Return a salted SHA-256 hex digest of *identifier*.

        The same input always produces the same output for a given salt,
        allowing records to be joined without exposing the raw value.

        Args:
            identifier: The identifier string to hash (e.g. a user ID).

        Returns:
            A 64-character hex string.
        """
        raw = f"{self._salt}:{identifier}".encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        logger.debug("Hashed identifier (len=%d)", len(identifier))
        return digest

    # ------------------------------------------------------------------
    # Differential privacy
    # ------------------------------------------------------------------

    def differential_privacy(
        self,
        data: list[float],
        epsilon: float = 1.0,
    ) -> list[float]:
        """
        Apply the Laplace mechanism to a list of numeric values.

        Each value receives additive Laplace noise calibrated to provide
        ``epsilon``-differential privacy with a global sensitivity of 1.

        Args:
            data: List of numeric values to perturb.
            epsilon: Privacy budget parameter.  Smaller values → more noise
                     → stronger privacy guarantee.

        Returns:
            A new list with Laplace noise added to each element.

        Raises:
            ValueError: If *epsilon* is not positive.
        """
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")

        scale = 1.0 / epsilon

        def _laplace_noise(scale: float) -> float:
            """Sample from Laplace(0, scale) distribution."""
            u = random.uniform(-0.5, 0.5)
            return -scale * math.copysign(1, u) * math.log(1 - 2 * abs(u))

        result = [v + _laplace_noise(scale) for v in data]
        logger.debug(
            "Applied differential privacy (epsilon=%.4f) to %d values", epsilon, len(data)
        )
        return result
