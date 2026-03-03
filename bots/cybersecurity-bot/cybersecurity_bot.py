"""
bots/cybersecurity-bot/cybersecurity_bot.py

CybersecurityBot — vulnerability scanning (simulated), security reporting, and password analysis.
"""

from __future__ import annotations

import hashlib
import random
import re
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

_VULN_CATALOG: list[dict[str, Any]] = [
    {"id": "CVE-2023-001", "name": "SQL Injection", "severity": "Critical", "cvss": 9.8,
     "description": "Unsanitised user input passed directly to SQL queries.",
     "patch": "Use parameterised queries and prepared statements."},
    {"id": "CVE-2023-002", "name": "Cross-Site Scripting (XSS)", "severity": "High", "cvss": 7.2,
     "description": "Unescaped user input rendered in HTML context.",
     "patch": "Encode all output; use Content-Security-Policy header."},
    {"id": "CVE-2023-003", "name": "Insecure Direct Object Reference", "severity": "High", "cvss": 7.5,
     "description": "Object references exposed in URLs without authorisation checks.",
     "patch": "Implement proper authorisation on all resource access."},
    {"id": "CVE-2023-004", "name": "Security Misconfiguration", "severity": "Medium", "cvss": 5.3,
     "description": "Default credentials or unnecessary features left enabled.",
     "patch": "Harden server configuration; disable debug mode in production."},
    {"id": "CVE-2023-005", "name": "Outdated Dependencies", "severity": "Medium", "cvss": 6.1,
     "description": "Third-party libraries with known vulnerabilities in use.",
     "patch": "Update all dependencies; run `pip audit` or `npm audit` regularly."},
    {"id": "CVE-2023-006", "name": "Missing Rate Limiting", "severity": "Low", "cvss": 4.0,
     "description": "API endpoints lack rate limiting, enabling brute-force attacks.",
     "patch": "Implement rate limiting with exponential back-off."},
]

_PASSWORD_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"[a-z]"), "lowercase"),
    (re.compile(r"[A-Z]"), "uppercase"),
    (re.compile(r"\d"), "digit"),
    (re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]"), "special"),
]

_COMMON_PASSWORDS: frozenset[str] = frozenset(
    {"password", "123456", "password123", "admin", "qwerty", "letmein",
     "welcome", "monkey", "dragon", "master", "1234567890", "iloveyou"}
)


class CybersecurityBot(BotBase):
    """
    Cybersecurity assistant providing simulated vulnerability scans,
    security reports, patch recommendations, and password strength analysis.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="CybersecurityBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("CybersecurityBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("CybersecurityBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def scan_vulnerabilities(self, target: str) -> list[dict[str, Any]]:
        """
        Simulate a vulnerability scan of *target*.

        Args:
            target: Hostname, IP, or application name (simulation only).

        Returns:
            List of vulnerability finding dicts.
        """
        scan_id = uuid.uuid4().hex[:8].upper()
        num_found = random.randint(1, len(_VULN_CATALOG))
        findings = random.sample(_VULN_CATALOG, num_found)
        result = [
            {**v, "target": target, "scan_id": scan_id,
             "discovered_at": datetime.now(timezone.utc).isoformat()}
            for v in findings
        ]
        self.log_activity(f"Vulnerability scan: target='{target}', found {len(result)} issues.")
        return result

    def generate_security_report(self, findings: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Generate a structured security report from scan findings.

        Args:
            findings: List of vulnerability dicts (output of :meth:`scan_vulnerabilities`).

        Returns:
            Security report dict with risk summary and remediation plan.
        """
        severity_counts: dict[str, int] = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for f in findings:
            sev = f.get("severity", "Low")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        risk_score = (
            severity_counts["Critical"] * 10
            + severity_counts["High"] * 7
            + severity_counts["Medium"] * 4
            + severity_counts["Low"] * 1
        )
        risk_level = (
            "Critical" if risk_score >= 20
            else "High" if risk_score >= 10
            else "Medium" if risk_score >= 5
            else "Low"
        )
        self.log_activity("Security report generated.")
        return {
            "report_id": uuid.uuid4().hex[:12].upper(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_vulnerabilities": len(findings),
            "severity_breakdown": severity_counts,
            "overall_risk_score": risk_score,
            "overall_risk_level": risk_level,
            "findings": findings,
            "executive_summary": (
                f"Scan identified {len(findings)} vulnerabilities: "
                f"{severity_counts['Critical']} Critical, {severity_counts['High']} High, "
                f"{severity_counts['Medium']} Medium, {severity_counts['Low']} Low."
            ),
        }

    def recommend_patches(self, vulnerabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Generate patch recommendations for a list of vulnerabilities.

        Args:
            vulnerabilities: List of vulnerability dicts.

        Returns:
            Ordered list of patch recommendation dicts (highest severity first).
        """
        recommendations = []
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        sorted_vulns = sorted(
            vulnerabilities,
            key=lambda v: severity_order.get(v.get("severity", "Low"), 3),
        )
        for vuln in sorted_vulns:
            recommendations.append({
                "vulnerability_id": vuln.get("id", "N/A"),
                "name": vuln.get("name", "Unknown"),
                "severity": vuln.get("severity", "Unknown"),
                "patch": vuln.get("patch", "Consult vendor documentation."),
                "priority": severity_order.get(vuln.get("severity", "Low"), 3) + 1,
                "estimated_effort": {
                    "Critical": "1-2 days",
                    "High": "2-5 days",
                    "Medium": "1 week",
                    "Low": "2 weeks",
                }.get(vuln.get("severity", "Low"), "1 week"),
            })
        self.log_activity(f"Patch recommendations generated for {len(vulnerabilities)} vulnerabilities.")
        return recommendations

    def check_password_strength(self, password: str) -> dict[str, Any]:
        """
        Analyse the strength of *password*.

        Args:
            password: The password string to evaluate.

        Returns:
            Dict with ``score`` (0-100), ``strength`` label, ``issues``, and ``suggestions``.

        Note:
            The password is hashed immediately and never stored or logged.
        """
        # Never log or store the actual password
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()[:16]

        issues: list[str] = []
        suggestions: list[str] = []
        score = 0

        # Common password check
        if password.lower() in _COMMON_PASSWORDS:
            issues.append("Password is on the common password list.")
            return {
                "score": 0,
                "strength": "Very Weak",
                "issues": issues,
                "suggestions": ["Choose a unique, unpredictable password."],
                "hash_preview": pwd_hash,
            }

        # Length
        length = len(password)
        if length >= 16:
            score += 30
        elif length >= 12:
            score += 20
        elif length >= 8:
            score += 10
        else:
            issues.append("Password is shorter than 8 characters.")
            suggestions.append("Use at least 12 characters.")

        # Complexity checks
        found_types: list[str] = []
        for pattern, type_name in _PASSWORD_PATTERNS:
            if pattern.search(password):
                score += 15
                found_types.append(type_name)
            else:
                issues.append(f"Missing {type_name} characters.")
                suggestions.append(f"Add {type_name} characters.")

        # Bonus for mixing
        if len(found_types) == 4:
            score += 10

        score = min(score, 100)
        strength = (
            "Very Weak" if score < 20
            else "Weak" if score < 40
            else "Moderate" if score < 60
            else "Strong" if score < 80
            else "Very Strong"
        )

        return {
            "score": score,
            "strength": strength,
            "character_types_found": found_types,
            "length": length,
            "issues": issues,
            "suggestions": suggestions if suggestions else ["Password looks good!"],
            "hash_preview": pwd_hash,
        }
