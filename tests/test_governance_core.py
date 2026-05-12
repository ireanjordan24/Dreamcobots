from __future__ import annotations

import pytest

from global_learning_system.governance.compliance_engine import (
    ComplianceEngine,
    POLICY_GDPR,
    POLICY_HIPAA,
)
from global_learning_system.governance.security_layer import (
    EncryptedPayload,
    SecurityLayer,
)


class TestSecurityLayer:
    def test_encrypt_decrypt_roundtrip(self):
        sec = SecurityLayer()
        payload = sec.encrypt("hello-governance")
        assert payload.algorithm == "FERNET+HMAC-SHA256"
        assert sec.decrypt(payload) == "hello-governance"

    def test_decrypt_invalid_ciphertext_raises(self):
        sec = SecurityLayer()
        payload = EncryptedPayload(
            ciphertext="not-valid",
            key_id="default",
            algorithm="FERNET+HMAC-SHA256",
        )
        with pytest.raises(ValueError):
            sec.decrypt(payload)


class TestComplianceEngine:
    def test_gdpr_blocks_anonymous_sensitive_access(self):
        engine = ComplianceEngine(active_policies=[POLICY_GDPR])
        assert engine.check("anonymous", "export_records", "customer_pii") is False

    def test_gdpr_allows_named_actor_for_sensitive_access(self):
        engine = ComplianceEngine(active_policies=[POLICY_GDPR])
        assert engine.check("admin", "view", "customer_pii") is True

    def test_hipaa_blocks_non_clinical_actor_for_phi(self):
        engine = ComplianceEngine(active_policies=[POLICY_HIPAA])
        assert engine.check("support_agent", "view", "patient_phi_record") is False

    def test_hipaa_allows_clinician_actor_for_phi(self):
        engine = ComplianceEngine(active_policies=[POLICY_HIPAA])
        assert engine.check("clinician:alice", "view", "patient_phi_record") is True
