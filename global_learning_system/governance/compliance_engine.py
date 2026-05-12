"""
compliance_engine.py — Enforces compliance and logging processes.

Manages audit logging, policy enforcement, and regulatory compliance
(e.g. GDPR, HIPAA) for operations performed within the DreamCo platform.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Supported compliance standards
# ---------------------------------------------------------------------------

POLICY_GDPR = "GDPR"
POLICY_HIPAA = "HIPAA"
POLICY_SOC2 = "SOC2"
POLICY_ISO27001 = "ISO27001"

ALL_POLICIES = [POLICY_GDPR, POLICY_HIPAA, POLICY_SOC2, POLICY_ISO27001]


@dataclass
class AuditEntry:
    """A single immutable audit log entry."""

    event_id: str
    actor: str
    action: str
    resource: str
    outcome: str  # "success" | "denied" | "error"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComplianceEngine:
    """
    Enforces governance policies and maintains an immutable audit log.

    Parameters
    ----------
    active_policies : list[str]
        Compliance standards to enforce. Any action not permitted under all
        active policies is blocked.
    """

    def __init__(self, active_policies: Optional[List[str]] = None):
        self.active_policies: List[str] = active_policies or [POLICY_GDPR]
        self._audit_log: List[AuditEntry] = []
        self._event_counter: int = 0

        for policy in self.active_policies:
            if policy not in ALL_POLICIES:
                raise ValueError(
                    f"Unknown policy '{policy}'. Valid: {ALL_POLICIES}"
                )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def check(self, actor: str, action: str, resource: str) -> bool:
        """
        Check whether *actor* is permitted to perform *action* on *resource*.

        The default implementation allows all actions; override or extend
        for production rule-based checks.

        Returns
        -------
        bool
            ``True`` if the action is permitted.
        """
        permitted = self._evaluate_policies(actor, action, resource)
        outcome = "success" if permitted else "denied"
        self._log(actor=actor, action=action, resource=resource, outcome=outcome)
        return permitted

    def enforce(self, actor: str, action: str, resource: str) -> None:
        """
        Enforce policy; raise ``PermissionError`` if the action is denied.

        Parameters
        ----------
        actor : str
        action : str
        resource : str

        Raises
        ------
        PermissionError
            If the action is not permitted.
        """
        if not self.check(actor, action, resource):
            raise PermissionError(
                f"Actor '{actor}' is not permitted to '{action}' on '{resource}'."
            )

    def get_audit_log(
        self,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> List[AuditEntry]:
        """
        Retrieve audit log entries with optional filters.

        Parameters
        ----------
        actor : str | None
        action : str | None
        outcome : str | None
        """
        entries = self._audit_log
        if actor is not None:
            entries = [e for e in entries if e.actor == actor]
        if action is not None:
            entries = [e for e in entries if e.action == action]
        if outcome is not None:
            entries = [e for e in entries if e.outcome == outcome]
        return list(entries)

    def enable_policy(self, policy: str) -> None:
        """Enable an additional compliance policy."""
        if policy not in ALL_POLICIES:
            raise ValueError(f"Unknown policy '{policy}'. Valid: {ALL_POLICIES}")
        if policy not in self.active_policies:
            self.active_policies.append(policy)

    def disable_policy(self, policy: str) -> None:
        """Disable a compliance policy."""
        if policy in self.active_policies:
            self.active_policies.remove(policy)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evaluate_policies(self, actor: str, action: str, resource: str) -> bool:
        """
        Apply each active policy rule.

        Each active policy contributes a rule-based decision.
        All active policies must pass for an action to be permitted.
        """
        actor_norm = (actor or "").strip().lower()
        action_norm = (action or "").strip().lower()
        resource_norm = (resource or "").strip().lower()

        for policy in self.active_policies:
            if not self._policy_allows(policy, actor_norm, action_norm, resource_norm):
                return False
        return True

    def _policy_allows(
        self,
        policy: str,
        actor: str,
        action: str,
        resource: str,
    ) -> bool:
        """Evaluate one policy against the request tuple."""
        if policy == POLICY_GDPR:
            # Block anonymous access to sensitive personal data.
            if self._is_sensitive_resource(resource) and actor in {"", "anonymous", "unknown"}:
                return False
            # Block bulk export actions on personal data without identified actor.
            if "export" in action and self._is_sensitive_resource(resource) and actor.startswith("svc_"):
                return False
            return True

        if policy == POLICY_HIPAA:
            # PHI operations must be done by explicit clinical/compliance/admin actors.
            if self._is_phi_resource(resource):
                allowed_prefixes = ("clinician:", "compliance:", "admin")
                return actor.startswith(allowed_prefixes)
            return True

        if policy == POLICY_SOC2:
            # Only admins can mutate governance-critical assets.
            guarded_resources = ("audit_log", "governance", "security_config", "compliance_config")
            if any(gr in resource for gr in guarded_resources):
                return actor.startswith("admin")
            return True

        if policy == POLICY_ISO27001:
            # Explicitly block security bypass actions.
            denied_tokens = ("disable_security", "bypass", "disable_audit", "disable_encryption")
            if any(t in action for t in denied_tokens):
                return False
            return True

        return True

    @staticmethod
    def _is_sensitive_resource(resource: str) -> bool:
        tokens = ("pii", "personal_data", "customer_data", "identity", "email", "phone", "ssn")
        return any(t in resource for t in tokens)

    @staticmethod
    def _is_phi_resource(resource: str) -> bool:
        tokens = ("phi", "patient", "medical_record", "diagnosis", "treatment")
        return any(t in resource for t in tokens)

    def _log(self, actor: str, action: str, resource: str, outcome: str, metadata: Optional[Dict[str, Any]] = None) -> AuditEntry:
        self._event_counter += 1
        entry = AuditEntry(
            event_id=f"evt_{self._event_counter:06d}",
            actor=actor,
            action=action,
            resource=resource,
            outcome=outcome,
            metadata=metadata or {},
        )
        self._audit_log.append(entry)
        return entry
