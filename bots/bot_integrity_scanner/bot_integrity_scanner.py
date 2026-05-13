"""
DreamCo Bot Integrity Scanner

Scans every bot directory in the repository and validates:

  1. **File presence** — each bot package has ``__init__.py`` and at least one
     substantive ``.py`` implementation file.
  2. **Syntax validity** — every ``.py`` file parses without ``SyntaxError``.
  3. **Framework compliance** — implementation files reference
     ``GlobalAISourcesFlow`` (same rule enforced by
     ``tools/check_bot_framework.py``).
  4. **Class structure** — the first concrete class in an implementation file
     exposes both ``__init__`` and ``run`` methods.
  5. **Constructor safety** — ``__init__`` keyword arguments are catalogued so
     callers can verify they are not passing unsupported parameters (the root
     cause of the ``LearningLoop`` ``controller`` bug).

Run standalone::

    python bots/bot_integrity_scanner/bot_integrity_scanner.py [--path PATH]

GLOBAL AI SOURCES FLOW compliant.
"""

from __future__ import annotations

import ast
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Directories that contain bot packages (relative to repo root).
BOT_DIRS: tuple[str, ...] = (
    "bots",
    "Business_bots",
    "App_bots",
    "Marketing_bots",
    "Occupational_bots",
    "Real_Estate_bots",
    "Fiverr_bots",
)

# Files that are not bot implementations and should be skipped.
EXCLUDED_FILENAMES: frozenset[str] = frozenset(
    {
        "__init__.py",
        "tiers.py",
        "registry.py",
        "billing_system.py",
        "token_manager.py",
        "subscription_manager.py",
        "logger.py",
        "error_handler.py",
        "conftest.py",
        "setup.py",
    }
)

FRAMEWORK_MARKERS: tuple[str, ...] = (
    "GlobalAISourcesFlow",
    "global_ai_sources_flow",
    "GLOBAL AI SOURCES FLOW",
)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class IssueRecord:
    """A single integrity issue found in a bot file."""
    severity: str        # "error" | "warning" | "info"
    check: str           # short check name
    message: str         # human-readable description


@dataclass
class BotFileReport:
    """Integrity report for one Python file inside a bot package."""
    path: Path
    issues: List[IssueRecord] = field(default_factory=list)
    syntax_ok: bool = True
    framework_compliant: bool = False
    has_run_method: bool = False
    init_kwargs: List[str] = field(default_factory=list)  # kwarg names accepted by __init__

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)


@dataclass
class BotPackageReport:
    """Integrity report for one bot package (directory)."""
    package_path: Path
    name: str
    has_init: bool = False
    file_reports: List[BotFileReport] = field(default_factory=list)
    package_issues: List[IssueRecord] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return (
            any(i.severity == "error" for i in self.package_issues)
            or any(fr.has_errors for fr in self.file_reports)
        )

    @property
    def has_warnings(self) -> bool:
        return (
            any(i.severity == "warning" for i in self.package_issues)
            or any(fr.has_warnings for fr in self.file_reports)
        )

    @property
    def all_issues(self) -> List[IssueRecord]:
        issues = list(self.package_issues)
        for fr in self.file_reports:
            issues.extend(fr.issues)
        return issues


@dataclass
class ScanReport:
    """Aggregate scan report across all bot packages."""
    scanned_packages: int = 0
    scanned_files: int = 0
    packages_with_errors: int = 0
    packages_with_warnings: int = 0
    package_reports: List[BotPackageReport] = field(default_factory=list)

    @property
    def total_errors(self) -> int:
        return sum(
            sum(1 for i in pr.all_issues if i.severity == "error")
            for pr in self.package_reports
        )

    @property
    def total_warnings(self) -> int:
        return sum(
            sum(1 for i in pr.all_issues if i.severity == "warning")
            for pr in self.package_reports
        )

    @property
    def passed(self) -> bool:
        return self.packages_with_errors == 0


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _extract_class_info(tree: ast.Module) -> List[Dict]:
    """
    Return a list of dicts describing classes found in an AST.

    Each dict has:
        name        — class name
        has_init    — bool
        has_run     — bool
        init_kwargs — list of keyword-argument names (including ``**kwargs`` as
                      the literal string ``"**kwargs"``)
    """
    results = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        has_init = False
        has_run = False
        init_kwargs: List[str] = []
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            if item.name == "__init__":
                has_init = True
                args = item.args
                # Collect keyword argument names (skip 'self')
                all_args = args.args[1:]  # drop self
                init_kwargs = [a.arg for a in all_args]
                if args.kwonlyargs:
                    init_kwargs.extend(a.arg for a in args.kwonlyargs)
                if args.kwarg:
                    init_kwargs.append("**kwargs")
            elif item.name == "run":
                has_run = True
        results.append(
            {
                "name": node.name,
                "has_init": has_init,
                "has_run": has_run,
                "init_kwargs": init_kwargs,
            }
        )
    return results


# ---------------------------------------------------------------------------
# File-level checks
# ---------------------------------------------------------------------------

def _check_file(path: Path) -> BotFileReport:
    """Run all integrity checks on a single Python file."""
    report = BotFileReport(path=path)

    # 1. Read
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        report.issues.append(
            IssueRecord("error", "file_read", f"Cannot read file: {exc}")
        )
        report.syntax_ok = False
        return report

    # 2. Syntax check
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        report.syntax_ok = False
        report.issues.append(
            IssueRecord(
                "error",
                "syntax",
                f"SyntaxError at line {exc.lineno}: {exc.msg}",
            )
        )
        return report  # no point checking further

    # 3. Framework compliance
    report.framework_compliant = any(marker in source for marker in FRAMEWORK_MARKERS)
    if not report.framework_compliant:
        report.issues.append(
            IssueRecord(
                "warning",
                "framework_compliance",
                "File does not reference GlobalAISourcesFlow — add "
                "`from framework import GlobalAISourcesFlow` per CONTRIBUTING.md.",
            )
        )

    # 4. Class structure
    classes = _extract_class_info(tree)
    if classes:
        # Inspect the first concrete (non-test) class
        for cls_info in classes:
            if cls_info["name"].startswith("Test"):
                continue
            report.init_kwargs = cls_info["init_kwargs"]
            if not cls_info["has_run"]:
                report.issues.append(
                    IssueRecord(
                        "warning",
                        "missing_run_method",
                        f"Class '{cls_info['name']}' has no `run()` method. "
                        "All DreamCo bots should implement `run(task)`.",
                    )
                )
            else:
                report.has_run_method = True
            break  # only check first concrete class

    return report


# ---------------------------------------------------------------------------
# Package-level checks
# ---------------------------------------------------------------------------

def _is_implementation_file(path: Path) -> bool:
    """Return True if *path* is a bot implementation file that should be checked."""
    return (
        path.suffix == ".py"
        and path.name not in EXCLUDED_FILENAMES
        and not path.name.startswith("test_")
    )


def _check_package(package_dir: Path) -> BotPackageReport:
    """Run integrity checks on one bot package directory."""
    report = BotPackageReport(
        package_path=package_dir,
        name=package_dir.name,
    )

    # 1. __init__.py presence
    init_file = package_dir / "__init__.py"
    report.has_init = init_file.exists()
    if not report.has_init:
        report.package_issues.append(
            IssueRecord(
                "warning",
                "missing_init",
                "__init__.py not found — package may not be importable.",
            )
        )

    # 2. Collect implementation files (top-level only — no recursion into sub-packages)
    impl_files = [
        f for f in sorted(package_dir.iterdir())
        if f.is_file() and _is_implementation_file(f)
    ]
    if not impl_files:
        report.package_issues.append(
            IssueRecord(
                "warning",
                "no_implementation_file",
                "No non-test Python implementation file found in package root.",
            )
        )

    # 3. Check each implementation file
    for impl_file in impl_files:
        file_report = _check_file(impl_file)
        report.file_reports.append(file_report)

    return report


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

class BotIntegrityScanner:
    """
    Scans all bot packages in the DreamCo repository for structural and
    coding-quality issues.

    Parameters
    ----------
    repo_root : str | Path | None
        Root of the repository.  Defaults to two levels above this file.
    bot_dirs : tuple[str, ...] | None
        Iterable of directory names (relative to *repo_root*) that contain
        bot packages.  Defaults to :data:`BOT_DIRS`.
    """

    def __init__(
        self,
        repo_root: Optional[str] = None,
        bot_dirs: Optional[tuple] = None,
    ) -> None:
        if repo_root is None:
            self.repo_root = Path(__file__).resolve().parent.parent.parent
        else:
            self.repo_root = Path(repo_root).resolve()

        self.bot_dirs: tuple[str, ...] = bot_dirs if bot_dirs is not None else BOT_DIRS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan(self) -> ScanReport:
        """Scan all configured bot directories and return a :class:`ScanReport`."""
        aggregate = ScanReport()

        for dir_name in self.bot_dirs:
            parent_dir = self.repo_root / dir_name
            if not parent_dir.exists():
                continue
            for entry in sorted(parent_dir.iterdir()):
                if not entry.is_dir():
                    continue
                pkg_report = _check_package(entry)
                aggregate.scanned_packages += 1
                aggregate.scanned_files += len(pkg_report.file_reports)
                aggregate.package_reports.append(pkg_report)
                if pkg_report.has_errors:
                    aggregate.packages_with_errors += 1
                elif pkg_report.has_warnings:
                    aggregate.packages_with_warnings += 1

        return aggregate

    def run(self, task: Optional[dict] = None) -> dict:
        """
        Run the integrity scan and return a result dict.

        Compatible with the DreamCo ``BaseBot`` run interface.
        """
        report = self.scan()
        return {
            "status": "success" if report.passed else "issues_found",
            "scanned_packages": report.scanned_packages,
            "scanned_files": report.scanned_files,
            "total_errors": report.total_errors,
            "total_warnings": report.total_warnings,
            "packages_with_errors": report.packages_with_errors,
            "packages_with_warnings": report.packages_with_warnings,
            "passed": report.passed,
        }

    # ------------------------------------------------------------------
    # Reporting helpers
    # ------------------------------------------------------------------

    def print_report(self, report: ScanReport) -> None:
        """Print a human-readable report to stdout."""
        line = "=" * 70
        print(line)
        print("DreamCo Bot Integrity Scanner — Report")
        print(line)
        print(f"Repository root : {self.repo_root}")
        print(f"Packages scanned: {report.scanned_packages}")
        print(f"Files scanned   : {report.scanned_files}")
        print(f"Total errors    : {report.total_errors}")
        print(f"Total warnings  : {report.total_warnings}")
        print()

        for pkg in report.package_reports:
            if not pkg.has_errors and not pkg.has_warnings:
                continue
            status = "❌ ERROR" if pkg.has_errors else "⚠️  WARN"
            print(f"{status}  {pkg.name}/")
            for issue in pkg.all_issues:
                icon = "  ❌" if issue.severity == "error" else "  ⚠️ "
                print(f"{icon} [{issue.check}] {issue.message}")
            print()

        if report.passed:
            print("✅ All bot packages passed integrity checks.")
        else:
            print(
                f"❌ {report.packages_with_errors} package(s) have errors. "
                "Fix the issues above before deploying."
            )
        print(line)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: List[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan all DreamCo bot packages for structural and coding issues.",
    )
    parser.add_argument(
        "--path",
        default=None,
        help="Repository root (default: auto-detected).",
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        default=False,
        help="Exit 0 even when errors are found (strict mode is default).",
    )
    args = parser.parse_args(argv)

    scanner = BotIntegrityScanner(repo_root=args.path)
    report = scanner.scan()
    scanner.print_report(report)

    if args.no_strict:
        return 0
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
