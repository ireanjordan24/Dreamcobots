"""
Testing Bot — Runs the project test suite and reports results.

Executes pytest programmatically, captures results, and returns a
structured report. Exits with code 1 if any tests fail so that CI
pipelines treat failures appropriately.

Usage
-----
    python bots/testing_bot.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

IGNORED_TESTS = [
    "tests/test_backend.py",
    "tests/test_web_dashboard.py",
]


def run_tests(
    test_dir: str = "tests",
    ignore: list[str] | None = None,
    max_fail: int = 5,
) -> dict:
    """Execute pytest and return a structured result dictionary.

    Parameters
    ----------
    test_dir : str
        Directory (relative to repo root) containing the test files.
    ignore : list[str] | None
        Test files to exclude from the run.
    max_fail : int
        Stop after this many failures (passed to ``--maxfail``).

    Returns
    -------
    dict
        Keys: success, returncode, output, errors, passed, failed.
    """
    ignore = ignore or IGNORED_TESTS
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        test_dir,
        f"--maxfail={max_fail}",
        "--disable-warnings",
        "-q",
        "--tb=short",
    ]
    for path in ignore:
        cmd += ["--ignore", path]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        passed = failed = 0
        for line in result.stdout.splitlines():
            if " passed" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0 and parts[i - 1].isdigit():
                        passed = int(parts[i - 1])
                    if part == "failed" and i > 0 and parts[i - 1].isdigit():
                        failed = int(parts[i - 1])

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "output": result.stdout[-4000:],
            "errors": result.stderr[-2000:],
            "passed": passed,
            "failed": failed,
        }
    except Exception as exc:
        return {
            "success": False,
            "returncode": -1,
            "output": "",
            "errors": str(exc),
            "passed": 0,
            "failed": 0,
        }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    context = context or {}
    return run_tests(
        test_dir=context.get("test_dir", "tests"),
        max_fail=context.get("max_fail", 5),
    )


if __name__ == "__main__":
    report = run_tests()
    print(json.dumps(report, indent=2))
    if not report["success"]:
        sys.exit(1)
