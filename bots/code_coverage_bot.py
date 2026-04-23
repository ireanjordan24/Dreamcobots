"""
Code Coverage Bot — Measures test coverage and identifies untested areas.

Runs pytest with coverage enabled, parses the report, and surfaces modules
below the configured coverage threshold.

Usage
-----
    python bots/code_coverage_bot.py [--threshold <pct>]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_DEFAULT_THRESHOLD = 60
_IGNORED_TESTS = [
    "tests/test_backend.py",
    "tests/test_web_dashboard.py",
]


def run_coverage(threshold: int = _DEFAULT_THRESHOLD) -> dict:
    """Execute pytest-cov and return a structured coverage report.

    Parameters
    ----------
    threshold : int
        Minimum acceptable overall coverage percentage.

    Returns
    -------
    dict
        Keys: overall_pct, passed, modules_below_threshold, output, status.
    """
    ignore_args: list[str] = []
    for path in _IGNORED_TESTS:
        ignore_args += ["--ignore", path]

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=json:/tmp/coverage.json",
        "-q",
        "--tb=no",
        "--disable-warnings",
        f"--cov-fail-under={threshold}",
    ] + ignore_args

    result = subprocess.run(cmd, capture_output=True, text=True)

    overall_pct = 0.0
    modules_below: list[dict] = []

    try:
        with open("/tmp/coverage.json") as fh:
            cov_data = json.load(fh)
        totals = cov_data.get("totals", {})
        overall_pct = totals.get("percent_covered", 0.0)
        for module, data in cov_data.get("files", {}).items():
            pct = data.get("summary", {}).get("percent_covered", 0.0)
            if pct < threshold:
                modules_below.append({"module": module, "coverage_pct": round(pct, 1)})
    except (OSError, json.JSONDecodeError, KeyError):
        pass

    passed = result.returncode == 0
    return {
        "overall_pct": round(overall_pct, 1),
        "threshold": threshold,
        "passed": passed,
        "modules_below_threshold": modules_below[:20],
        "output": result.stdout[-3000:],
        "status": "coverage_ok" if passed else "coverage_insufficient",
    }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    context = context or {}
    threshold = context.get("threshold", _DEFAULT_THRESHOLD)
    return run_coverage(threshold=threshold)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Code coverage reporter")
    parser.add_argument(
        "--threshold",
        type=int,
        default=_DEFAULT_THRESHOLD,
        help=f"Minimum coverage %% (default: {_DEFAULT_THRESHOLD})",
    )
    args = parser.parse_args()

    report = run_coverage(threshold=args.threshold)
    print(json.dumps(report, indent=2))
    print(
        f"\n📈 Overall coverage: {report['overall_pct']}%  "
        f"(threshold: {report['threshold']}%)"
    )
    if not report["passed"]:
        sys.exit(1)
