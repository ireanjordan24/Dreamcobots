"""
Deployment Review Bot — Validates production readiness of workflows and bots.

Checks that all required resources (workflow YAML files, requirements.txt,
bot entry points) are present before a deployment attempt, reducing the
chance of broken production pushes.

Usage
-----
    python bots/deployment_review_bot.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

REQUIRED_FILES = [
    "requirements.txt",
    ".github/workflows/ci.yml",
    "bots/debug_bot.py",
    "bots/testing_bot.py",
    "bots/bot_validator.py",
    "knowledge/pr_insights.json",
    "knowledge/ranked_insights.json",
]

REQUIRED_DIRS = [
    "bots",
    "tests",
    "docs",
    ".github/workflows",
    "knowledge",
]


def check_file_exists(path: str) -> dict:
    full = os.path.join(_ROOT, path)
    exists = os.path.isfile(full)
    return {"path": path, "exists": exists, "type": "file"}


def check_dir_exists(path: str) -> dict:
    full = os.path.join(_ROOT, path)
    exists = os.path.isdir(full)
    return {"path": path, "exists": exists, "type": "directory"}


def review() -> dict:
    """Run all pre-deployment checks and return a status report."""
    results: list[dict] = []
    missing: list[str] = []

    for fpath in REQUIRED_FILES:
        check = check_file_exists(fpath)
        results.append(check)
        if not check["exists"]:
            missing.append(fpath)

    for dpath in REQUIRED_DIRS:
        check = check_dir_exists(dpath)
        results.append(check)
        if not check["exists"]:
            missing.append(dpath)

    passed = len(missing) == 0
    return {
        "passed": passed,
        "missing": missing,
        "checks": results,
        "status": "ready_to_deploy" if passed else "deployment_blocked",
        "summary": (
            "✅ All deployment checks passed!"
            if passed
            else f"❌ {len(missing)} required resource(s) missing."
        ),
    }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    return review()


if __name__ == "__main__":
    report = review()
    print(json.dumps(report, indent=2))
    print(f"\n{report['summary']}")
    if not report["passed"]:
        sys.exit(1)
