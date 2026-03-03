"""
compliance/compliance_checker.py

Top-level compliance checking and auditing for DreamCobots bots and data.
"""

from datetime import datetime, timezone
from typing import Any


class ComplianceChecker:
    """Audits bots and data payloads for regulatory compliance."""

    _GDPR_SENSITIVE = {"email", "biometric", "health", "location", "ip_address"}
    _CCPA_SENSITIVE = {"personal_information", "sale_opt_out"}
    _HIPAA_SENSITIVE = {"medical_record", "health", "diagnosis", "prescription", "ssn"}

    def check_all_compliance(self, data: dict) -> dict:
        """
        Run GDPR, CCPA, and HIPAA checks on *data*.

        Args:
            data: Arbitrary data dict to check.

        Returns:
            dict with keys: gdpr, ccpa, hipaa (each True/False) and
            overall_compliant (bool).
        """
        gdpr = self._check_gdpr(data)
        ccpa = self._check_ccpa(data)
        hipaa = self._check_hipaa(data)
        return {
            "gdpr": gdpr,
            "ccpa": ccpa,
            "hipaa": hipaa,
            "overall_compliant": gdpr and ccpa and hipaa,
        }

    def generate_compliance_report(self, data: dict) -> dict:
        """
        Generate a detailed compliance report for *data*.

        Args:
            data: Data dict to evaluate.

        Returns:
            dict with check results, violations, score, and timestamp.
        """
        checks = self.check_all_compliance(data)
        violations = self.flag_violations(data)
        score = self.get_compliance_score(data)
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
            "violations": violations,
            "score": score,
            "pass": score >= 0.8,
        }

    def flag_violations(self, data: dict) -> list:
        """
        Return a list of violation description strings for *data*.

        Args:
            data: Data dict to inspect.

        Returns:
            List of human-readable violation strings (empty if compliant).
        """
        violations: list[str] = []
        keys = {k.lower() for k in data}

        # GDPR
        for field in self._GDPR_SENSITIVE:
            if field in keys and not data.get("consent_given"):
                violations.append(f"GDPR: sensitive field '{field}' present without consent")

        # CCPA
        if "personal_information" in keys and not data.get("ccpa_notice_provided"):
            violations.append("CCPA: personal_information present without ccpa_notice_provided")

        # HIPAA
        for field in self._HIPAA_SENSITIVE:
            if field in keys and not data.get("hipaa_authorization"):
                violations.append(f"HIPAA: PHI field '{field}' present without authorization")

        return violations

    def get_compliance_score(self, data: dict) -> float:
        """
        Return a compliance score between 0.0 and 1.0 for *data*.

        Args:
            data: Data dict to score.

        Returns:
            Float score where 1.0 = fully compliant.
        """
        checks = self.check_all_compliance(data)
        passed = sum(1 for v in [checks["gdpr"], checks["ccpa"], checks["hipaa"]] if v)
        return passed / 3.0

    def audit_bot(self, bot_instance: Any) -> dict:
        """
        Audit a bot instance for compliance-related properties.

        Args:
            bot_instance: Any DreamCobots bot object.

        Returns:
            dict with bot identity, compliance checks on exported data, and
            audit timestamp.
        """
        exported: dict[str, Any] = {}
        if hasattr(bot_instance, "export_structured_data"):
            exported = bot_instance.export_structured_data()

        checks = self.check_all_compliance(exported)
        return {
            "bot_id": getattr(bot_instance, "bot_id", "unknown"),
            "bot_name": getattr(bot_instance, "bot_name", "unknown"),
            "audited_at": datetime.now(timezone.utc).isoformat(),
            "compliance": checks,
            "score": self.get_compliance_score(exported),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_gdpr(self, data: dict) -> bool:
        keys = {k.lower() for k in data}
        for field in self._GDPR_SENSITIVE:
            if field in keys and not data.get("consent_given"):
                return False
        return True

    def _check_ccpa(self, data: dict) -> bool:
        if "personal_information" in {k.lower() for k in data}:
            return bool(data.get("ccpa_notice_provided"))
        return True

    def _check_hipaa(self, data: dict) -> bool:
        keys = {k.lower() for k in data}
        for field in self._HIPAA_SENSITIVE:
            if field in keys and not data.get("hipaa_authorization"):
                return False
        return True
