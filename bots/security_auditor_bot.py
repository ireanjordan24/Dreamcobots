"""
Security Auditor Bot — Scans Python code and configs for security vulnerabilities.

Uses ``bandit`` to detect common security issues such as hardcoded secrets,
use of insecure functions, and outdated patterns.

Usage
-----
    python bots/security_auditor_bot.py [<path>]
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_SEVERITY_EXIT_ON = {"HIGH", "MEDIUM"}


def run_bandit(path: str) -> dict:
    """Run bandit on *path* and return a structured report.

    Parameters
    ----------
    path : str
        File or directory to scan.

    Returns
    -------
    dict
        Keys: issues (list), high_count, medium_count, low_count, status.
    """
    cmd = [
        sys.executable,
        "-m",
        "bandit",
        "-r",
        path,
        "-f",
        "json",
        "-ll",  # report medium and higher by default
        "--quiet",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    issues: list[dict] = []
    high_count = medium_count = low_count = 0

    try:
        data = json.loads(result.stdout)
        for issue in data.get("results", []):
            severity = issue.get("issue_severity", "UNDEFINED").upper()
            issues.append(
                {
                    "file": issue.get("filename", ""),
                    "line": issue.get("line_number", 0),
                    "severity": severity,
                    "test_id": issue.get("test_id", ""),
                    "description": issue.get("issue_text", ""),
                }
            )
            if severity == "HIGH":
                high_count += 1
            elif severity == "MEDIUM":
                medium_count += 1
            else:
                low_count += 1
    except (json.JSONDecodeError, KeyError):
        # bandit not installed or no JSON output
        issues = [{"description": result.stderr or result.stdout, "severity": "UNKNOWN"}]

    status = "clean"
    if high_count or medium_count:
        status = "vulnerabilities_found"

    return {
        "scanned_path": path,
        "issues": issues,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
        "status": status,
    }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    context = context or {}
    target = context.get("path", "bots")
    return run_bandit(target)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "bots"
    report = run_bandit(target)
    print(json.dumps(report, indent=2))
    print(
        f"\n🔒 Security scan: {report['high_count']} HIGH  "
        f"{report['medium_count']} MEDIUM  {report['low_count']} LOW"
    )
    if report["status"] == "vulnerabilities_found":
        sys.exit(1)
