"""
Optimizer Bot — Analyzes Python code quality and suggests performance improvements.

Uses the ``radon`` library to measure cyclomatic complexity and raw metrics,
then reports functions or classes that exceed maintainability thresholds.

Usage
-----
    python bots/optimizer_bot.py [<python_file_or_dir>]
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from radon.complexity import cc_visit, ComplexityVisitor  # type: ignore
    from radon.metrics import mi_visit  # type: ignore
    _RADON_AVAILABLE = True
except ImportError:
    _RADON_AVAILABLE = False

_COMPLEXITY_THRESHOLD = 10
_MI_WARNING_THRESHOLD = 20
_EXCLUDED_DIRS = frozenset({"node_modules", "__pycache__", "venv", ".venv"})


def analyze_file(path: str) -> dict:
    """Return complexity and maintainability report for a single Python file."""
    report: dict = {"file": path, "issues": [], "status": "ok"}

    if not _RADON_AVAILABLE:
        report["issues"].append("radon library not installed — run: pip install radon")
        report["status"] = "unavailable"
        return report

    try:
        with open(path) as fh:
            source = fh.read()
    except OSError as exc:
        report["issues"].append(f"Cannot read file: {exc}")
        report["status"] = "error"
        return report

    # Cyclomatic complexity
    try:
        blocks = cc_visit(source)
        for block in blocks:
            if block.complexity >= _COMPLEXITY_THRESHOLD:
                report["issues"].append(
                    f"High complexity ({block.complexity}) in {block.name} "
                    f"at line {block.lineno} — consider refactoring"
                )
    except Exception as exc:
        report["issues"].append(f"Complexity analysis failed: {exc}")

    # Maintainability index
    try:
        mi_score = mi_visit(source, multi=True)
        if mi_score < _MI_WARNING_THRESHOLD:
            report["issues"].append(
                f"Low maintainability index ({mi_score:.1f}/100) — "
                "consider breaking the module into smaller pieces"
            )
    except Exception:
        pass

    report["status"] = "needs_optimization" if report["issues"] else "ok"
    return report


def analyze_path(target: str) -> list[dict]:
    """Analyze a file or directory and return per-file reports."""
    reports: list[dict] = []

    if os.path.isfile(target):
        reports.append(analyze_file(target))
    elif os.path.isdir(target):
        for root, _, files in os.walk(target):
            # Skip hidden / venv / cache directories
            parts = root.replace("\\", "/").split("/")
            if any(p.startswith(".") or p in _EXCLUDED_DIRS for p in parts):
                continue
            for fname in files:
                if fname.endswith(".py"):
                    reports.append(analyze_file(os.path.join(root, fname)))
    else:
        reports.append({"file": target, "issues": ["Path not found"], "status": "error"})

    return reports


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    context = context or {}
    target = context.get("path", "bots")
    results = analyze_path(target)
    total_issues = sum(len(r["issues"]) for r in results)
    return {"files": len(results), "issues": total_issues, "results": results,
            "status": "needs_optimization" if total_issues else "ok"}


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "bots"
    results = analyze_path(target)
    total_issues = sum(len(r["issues"]) for r in results)
    print(json.dumps(results, indent=2))
    print(f"\n📊 Scanned {len(results)} files — {total_issues} optimization issue(s) found.")
    if total_issues:
        sys.exit(1)
