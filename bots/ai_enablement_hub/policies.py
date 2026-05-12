"""
Pillar 2 — Clear Policies & Guardrails.

Explicitly documents and enforces vetted AI tool guidelines and acceptable
usage policies for all DreamCo bots.  PRO+ tiers can add custom policies.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

@dataclass
class AIPolicy:
    """A documented AI usage policy or guardrail."""

    policy_id: str
    name: str
    description: str
    category: str        # "tool_usage" | "data_privacy" | "security" | "ethics" | "compliance"
    severity: str        # "low" | "medium" | "high" | "critical"
    enabled: bool = True
    is_custom: bool = False
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "enabled": self.enabled,
            "is_custom": self.is_custom,
            "created_at": self.created_at,
        }


@dataclass
class PolicyViolation:
    """Records a detected policy violation."""

    violation_id: str
    policy_id: str
    actor: str
    detail: str
    severity: str
    resolved: bool = False
    recorded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "violation_id": self.violation_id,
            "policy_id": self.policy_id,
            "actor": self.actor,
            "detail": self.detail,
            "severity": self.severity,
            "resolved": self.resolved,
            "recorded_at": self.recorded_at,
        }


# ---------------------------------------------------------------------------
# Default vetted policy catalogue
# ---------------------------------------------------------------------------

VALID_CATEGORIES = {"tool_usage", "data_privacy", "security", "ethics", "compliance"}
VALID_SEVERITIES = {"low", "medium", "high", "critical"}

_DEFAULT_POLICIES: list[AIPolicy] = [
    AIPolicy(
        "pol-001", "Vetted AI Tool Registry",
        "Only AI tools listed in the approved registry may be integrated.",
        "tool_usage", "critical",
    ),
    AIPolicy(
        "pol-002", "Data Privacy Protection",
        "PII must be anonymized before any AI model training or inference.",
        "data_privacy", "critical",
    ),
    AIPolicy(
        "pol-003", "Model Output Review",
        "AI-generated content in high-stakes domains must be human-reviewed.",
        "ethics", "high",
    ),
    AIPolicy(
        "pol-004", "Acceptable Use Boundaries",
        "Bots must not autonomously take irreversible financial actions above $500.",
        "tool_usage", "high",
    ),
    AIPolicy(
        "pol-005", "Security Scanning",
        "All AI model artifacts must pass an adversarial-vulnerability scan.",
        "security", "high",
    ),
    AIPolicy(
        "pol-006", "GDPR/CCPA Compliance",
        "AI outputs must comply with applicable data-protection regulations.",
        "compliance", "critical",
    ),
    AIPolicy(
        "pol-007", "Bias & Fairness Auditing",
        "Models must undergo quarterly fairness audits before production use.",
        "ethics", "high",
    ),
    AIPolicy(
        "pol-008", "Audit Logging",
        "All AI inference requests must be captured in immutable audit logs.",
        "security", "medium",
    ),
    AIPolicy(
        "pol-009", "Rate Limiting & Quota Management",
        "Enforce per-bot token/request quotas to prevent abuse.",
        "tool_usage", "medium",
    ),
    AIPolicy(
        "pol-010", "Explainability Requirement",
        "Production models in regulated domains must expose feature attribution.",
        "compliance", "medium",
    ),
]


# ---------------------------------------------------------------------------
# Policies & Guardrails engine
# ---------------------------------------------------------------------------

class PoliciesGuardrails:
    """
    Manages AI usage policies and detects guardrail violations.

    The default catalogue of 10 vetted policies is loaded at construction.
    PRO/ENTERPRISE tiers can add custom policies via ``add_custom_policy()``.
    """

    def __init__(self, allow_custom: bool = False) -> None:
        self._allow_custom = allow_custom
        self._policies: dict[str, AIPolicy] = {
            p.policy_id: p for p in _DEFAULT_POLICIES
        }
        self._violations: list[PolicyViolation] = []

    # ------------------------------------------------------------------
    # Policy management
    # ------------------------------------------------------------------

    def get_policy(self, policy_id: str) -> AIPolicy:
        """Return a policy by ID."""
        if policy_id not in self._policies:
            raise KeyError(f"Policy '{policy_id}' not found.")
        return self._policies[policy_id]

    def list_policies(
        self,
        category: Optional[str] = None,
        enabled_only: bool = False,
    ) -> list[dict]:
        """Return all policies, optionally filtered."""
        policies = self._policies.values()
        if category is not None:
            policies = [p for p in policies if p.category == category]
        if enabled_only:
            policies = [p for p in policies if p.enabled]
        return [p.to_dict() for p in policies]

    def enable_policy(self, policy_id: str) -> None:
        """Enable a policy."""
        self.get_policy(policy_id).enabled = True

    def disable_policy(self, policy_id: str) -> None:
        """Disable a policy (use with caution)."""
        self.get_policy(policy_id).enabled = False

    def add_custom_policy(
        self,
        name: str,
        description: str,
        category: str,
        severity: str,
    ) -> AIPolicy:
        """
        Add a custom policy (requires PRO+ tier).

        Raises
        ------
        PermissionError
            If custom policies are not allowed on the current tier.
        ValueError
            If category or severity values are invalid.
        """
        if not self._allow_custom:
            raise PermissionError(
                "Custom policies require PRO or ENTERPRISE tier."
            )
        if category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Valid: {sorted(VALID_CATEGORIES)}")
        if severity not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity '{severity}'. Valid: {sorted(VALID_SEVERITIES)}")

        policy_id = f"custom-{uuid.uuid4().hex[:8]}"
        policy = AIPolicy(
            policy_id=policy_id,
            name=name,
            description=description,
            category=category,
            severity=severity,
            is_custom=True,
        )
        self._policies[policy_id] = policy
        return policy

    # ------------------------------------------------------------------
    # Violation recording
    # ------------------------------------------------------------------

    def record_violation(
        self,
        policy_id: str,
        actor: str,
        detail: str,
    ) -> PolicyViolation:
        """Record a policy violation."""
        policy = self.get_policy(policy_id)
        violation = PolicyViolation(
            violation_id=f"vio-{uuid.uuid4().hex[:8]}",
            policy_id=policy_id,
            actor=actor,
            detail=detail,
            severity=policy.severity,
        )
        self._violations.append(violation)
        return violation

    def resolve_violation(self, violation_id: str) -> None:
        """Mark a violation as resolved."""
        for v in self._violations:
            if v.violation_id == violation_id:
                v.resolved = True
                return
        raise KeyError(f"Violation '{violation_id}' not found.")

    def list_violations(self, resolved: Optional[bool] = None) -> list[dict]:
        """Return violations, optionally filtered by resolved status."""
        violations = self._violations
        if resolved is not None:
            violations = [v for v in violations if v.resolved == resolved]
        return [v.to_dict() for v in violations]

    # ------------------------------------------------------------------
    # Compliance score
    # ------------------------------------------------------------------

    def compliance_score(self) -> float:
        """
        Return a 0–100 compliance score.

        Score decreases for each unresolved critical/high violation and each
        disabled critical policy.
        """
        score = 100.0
        for policy in self._policies.values():
            if not policy.enabled and policy.severity == "critical":
                score -= 15.0
        for violation in self._violations:
            if not violation.resolved:
                score -= {"critical": 10.0, "high": 5.0, "medium": 2.0, "low": 1.0}.get(
                    violation.severity, 1.0
                )
        return max(0.0, round(score, 2))

    def guardrails_report(self) -> dict:
        """Return a summary of policy status and compliance."""
        active = sum(1 for p in self._policies.values() if p.enabled)
        unresolved = sum(1 for v in self._violations if not v.resolved)
        return {
            "total_policies": len(self._policies),
            "active_policies": active,
            "total_violations": len(self._violations),
            "unresolved_violations": unresolved,
            "compliance_score": self.compliance_score(),
        }
