"""
bots/dataforge/compliance.py

ComplianceManager implementing GDPR, CCPA, and HIPAA validation,
reporting, and audit logging for DataForge datasets.
"""

import logging
import threading
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class ComplianceManager:
    """
    Validates datasets against GDPR, CCPA, and HIPAA requirements.

    Maintains an immutable audit log of every compliance check performed
    so that the results can be reviewed at any time.
    """

    # Fields whose presence in a dataset requires explicit consent.
    consent_required: list[str] = [
        "name",
        "email",
        "phone",
        "address",
        "ip_address",
        "device_id",
        "location",
        "biometric",
        "health_data",
        "financial_data",
        "social_security_number",
        "date_of_birth",
        "gender",
        "race",
        "religion",
        "political_opinion",
    ]

    # HIPAA Protected Health Information field names.
    _hipaa_phi_fields: list[str] = [
        "patient_id",
        "medical_record_number",
        "health_plan_number",
        "diagnosis",
        "treatment",
        "prescription",
        "health_data",
        "biometric",
        "date_of_birth",
        "social_security_number",
    ]

    def __init__(self) -> None:
        """Initialise ComplianceManager with an empty audit log."""
        self._audit_log: list[dict[str, Any]] = []
        self._lock = threading.Lock()
        logger.info("ComplianceManager initialised")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _record_audit(
        self,
        regulation: str,
        passed: bool,
        details: dict[str, Any],
    ) -> None:
        """Append an entry to the audit log (thread-safe)."""
        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "regulation": regulation,
            "passed": passed,
            "details": details,
        }
        with self._lock:
            self._audit_log.append(entry)

    def _collect_sensitive_fields(self, data: dict) -> list[str]:
        """Return which consent-required fields are present in *data*."""
        return [f for f in self.consent_required if f in data]

    # ------------------------------------------------------------------
    # Public validation methods
    # ------------------------------------------------------------------

    def validate_gdpr_compliance(self, data: dict) -> bool:
        """
        Validate that *data* satisfies GDPR requirements.

        Rules checked:
        - ``data_subject_id`` must be present.
        - ``consent_given`` must be ``True``.
        - ``purpose_of_processing`` must be declared.
        - No sensitive field may be present without consent.

        Args:
            data: The dataset record to validate.

        Returns:
            ``True`` if the record is GDPR-compliant, otherwise ``False``.
        """
        violations: list[str] = []

        if not data.get("data_subject_id"):
            violations.append("Missing data_subject_id")
        if not data.get("consent_given"):
            violations.append("consent_given is False or missing")
        if not data.get("purpose_of_processing"):
            violations.append("Missing purpose_of_processing")

        sensitive = self._collect_sensitive_fields(data)
        if sensitive and not data.get("consent_given"):
            violations.append(
                f"Sensitive fields present without consent: {sensitive}"
            )

        passed = len(violations) == 0
        self._record_audit(
            "GDPR",
            passed,
            {"violations": violations, "sensitive_fields_found": sensitive},
        )
        if not passed:
            logger.warning("GDPR validation failed: %s", violations)
        else:
            logger.debug("GDPR validation passed")
        return passed

    def validate_ccpa_compliance(self, data: dict) -> bool:
        """
        Validate that *data* satisfies CCPA requirements.

        Rules checked:
        - ``consumer_id`` must be present.
        - ``opt_out_of_sale`` must not be ``True`` (user opted out).
        - ``data_category`` must be declared.
        - ``collection_source`` must be declared.

        Args:
            data: The dataset record to validate.

        Returns:
            ``True`` if the record is CCPA-compliant, otherwise ``False``.
        """
        violations: list[str] = []

        if not data.get("consumer_id"):
            violations.append("Missing consumer_id")
        if data.get("opt_out_of_sale") is True:
            violations.append("Consumer has opted out of data sale")
        if not data.get("data_category"):
            violations.append("Missing data_category")
        if not data.get("collection_source"):
            violations.append("Missing collection_source")

        passed = len(violations) == 0
        self._record_audit("CCPA", passed, {"violations": violations})
        if not passed:
            logger.warning("CCPA validation failed: %s", violations)
        else:
            logger.debug("CCPA validation passed")
        return passed

    def validate_hipaa_compliance(self, data: dict) -> bool:
        """
        Validate that *data* satisfies HIPAA requirements.

        Rules checked:
        - PHI fields must not be present unless ``hipaa_authorization`` is ``True``.
        - ``data_encryption`` must be ``True``.
        - ``covered_entity`` must be declared.

        Args:
            data: The dataset record to validate.

        Returns:
            ``True`` if the record is HIPAA-compliant, otherwise ``False``.
        """
        violations: list[str] = []

        phi_found = [f for f in self._hipaa_phi_fields if f in data]
        authorized = data.get("hipaa_authorization") is True
        if phi_found and not authorized:
            violations.append(
                f"PHI fields present without hipaa_authorization: {phi_found}"
            )
        if not data.get("data_encryption"):
            violations.append("data_encryption is False or missing")
        if not data.get("covered_entity"):
            violations.append("Missing covered_entity")

        passed = len(violations) == 0
        self._record_audit(
            "HIPAA",
            passed,
            {"violations": violations, "phi_fields_found": phi_found},
        )
        if not passed:
            logger.warning("HIPAA validation failed: %s", violations)
        else:
            logger.debug("HIPAA validation passed")
        return passed

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def generate_compliance_report(self, data: dict) -> dict[str, Any]:
        """
        Run all three compliance checks against *data* and return a report.

        Args:
            data: The dataset record to evaluate.

        Returns:
            A dict containing per-regulation results and an overall status.
        """
        gdpr = self.validate_gdpr_compliance(data)
        ccpa = self.validate_ccpa_compliance(data)
        hipaa = self.validate_hipaa_compliance(data)
        overall = gdpr and ccpa and hipaa

        report: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_compliant": overall,
            "gdpr": {"compliant": gdpr},
            "ccpa": {"compliant": ccpa},
            "hipaa": {"compliant": hipaa},
            "sensitive_fields_detected": self._collect_sensitive_fields(data),
            "recommendation": (
                "Dataset is fully compliant."
                if overall
                else "Review and remediate violations before publishing."
            ),
        }
        logger.info(
            "Compliance report generated – overall_compliant=%s", overall
        )
        return report

    # ------------------------------------------------------------------
    # Audit log
    # ------------------------------------------------------------------

    def audit_log(self) -> list[dict[str, Any]]:
        """
        Return the full audit log of all compliance checks performed.

        Returns:
            A list of audit-log entry dicts ordered by insertion time.
        """
        with self._lock:
            return list(self._audit_log)
