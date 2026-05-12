#!/usr/bin/env python3
"""
AI Fluency Gate for Dreamcobots.

Scores PR/commit changes against repository AI fluency expectations:
  1. Governance evidence
  2. Automation/workflow evidence
  3. Observability/orchestration evidence
  4. Onboarding/enablement evidence

Exit code:
  0 -> gate passed
  1 -> gate failed
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

FLUENCY_SIGNALS = {
    "governance": (
        "global_ai_sources_flow",
        "governance",
        "compliance",
        "security",
        "audit",
    ),
    "automation": (
        ".github/workflows/",
        "workflow_dispatch",
        "dependabot",
        "check_data_integrity",
    ),
    "observability": (
        "orchestrator",
        "heartbeat",
        "status",
        "analytics",
        "actions",
    ),
    "enablement": (
        "onboarding",
        "champion",
        "mentorship",
        "docs",
        "contributing",
    ),
}


def _changed_files() -> list[Path]:
    """
    Return changed files for fluency evaluation.

    Preference order:
      1) HEAD~1..HEAD (CI/push diff)
      2) Working tree changes vs HEAD (local validation)
    """
    primary = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    files: set[str] = set()
    if primary.returncode == 0:
        files = {p.strip() for p in primary.stdout.splitlines() if p.strip()}

    fallback = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if fallback.returncode == 0:
        files.update(p.strip() for p in fallback.stdout.splitlines() if p.strip())

    return [ROOT / p for p in sorted(files)]


def _score_file(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    try:
        text = path.read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        return set()

    matched: set[str] = set()
    rel = str(path.relative_to(ROOT)).lower()
    for area, terms in FLUENCY_SIGNALS.items():
        if any(t in text or t in rel for t in terms):
            matched.add(area)
    return matched


def main() -> int:
    files = _changed_files()
    if not files:
        print("AI fluency check: no changed files detected; skipping with pass.")
        return 0

    coverage: set[str] = set()
    for f in files:
        coverage |= _score_file(f)

    score = len(coverage)
    passed = score >= 2

    print("AI fluency check summary")
    print(f"- Changed files: {len(files)}")
    print(f"- Covered dimensions ({score}/4): {sorted(coverage)}")
    print(f"- Gate result: {'PASS' if passed else 'FAIL'}")

    if not passed:
        print(
            "Expected at least 2 fluency dimensions in changes "
            "(governance/automation/observability/enablement)."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
