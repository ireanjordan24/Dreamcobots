"""
PR Validation Bot — validates pull requests, auto-restores deleted critical files,
enforces revenue readiness, scans for placeholder code, validates file structure,
and generates Markdown reports.

Key behaviors:
  - Only restores files with git status 'D' (deleted).  Files with status 'M'
    (modified) or 'R' (renamed) are intentional changes and must NOT be touched.
  - Validates that every bot directory contains the revenue-readiness files.
  - Scans changed files for placeholder text (TODO, FIXME, PLACEHOLDER, etc.).
  - Validates that all expected top-level files and directories are present.
  - Outputs a detailed Markdown report for the PR comment.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

CRITICAL_FILES = [
    "index.js",
    "package.json",
    "README.md",
    "requirements.txt",
    "framework/__init__.py",
    "tools/check_bot_framework.py",
]

REVENUE_REQUIRED_FILES = [
    "payments.js",
    "logger.js",
    "index.js",
]

# Patterns that indicate incomplete / placeholder code
PLACEHOLDER_PATTERNS: List[re.Pattern] = [
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bFIXME\b", re.IGNORECASE),
    re.compile(r"\bHACK\b", re.IGNORECASE),
    re.compile(r"\bXXX\b"),
    re.compile(r"\bPLACEHOLDER\b", re.IGNORECASE),
    re.compile(r"\bNOT IMPLEMENTED\b", re.IGNORECASE),
    re.compile(r"\bSTUB\b", re.IGNORECASE),
]

# File extensions to scan for placeholder text
SCANNABLE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".sh", ".yml", ".yaml", ".json", ".md",
    ".html", ".css", ".env",
}

# Expected top-level structure (files and directories that must be present)
EXPECTED_STRUCTURE: List[str] = [
    "index.js",
    "package.json",
    "README.md",
    "requirements.txt",
    "framework/__init__.py",
    "tools/check_bot_framework.py",
    "bots",
    "tests",
    ".github",
]


@dataclass
class PlaceholderMatch:
    """Represents a single placeholder found in a file."""
    path: str
    line_number: int
    line_text: str
    pattern: str

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "line_number": self.line_number,
            "line_text": self.line_text,
            "pattern": self.pattern,
        }


@dataclass
class FileStatus:
    path: str
    status: str  # 'D', 'M', 'R', 'A', 'U', …


@dataclass
class RevenueCheck:
    bot_path: str
    has_payment: bool
    has_logger: bool
    has_offer: bool

    @property
    def is_ready(self) -> bool:
        return self.has_payment and self.has_logger and self.has_offer

    def to_dict(self) -> dict:
        return {
            "bot_path": self.bot_path,
            "has_payment": self.has_payment,
            "has_logger": self.has_logger,
            "has_offer": self.has_offer,
            "is_ready": self.is_ready,
        }


@dataclass
class ValidationResult:
    passed: bool
    critical_files_ok: bool
    restored_files: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)
    revenue_checks: List[RevenueCheck] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    placeholder_matches: List[PlaceholderMatch] = field(default_factory=list)
    missing_structure: List[str] = field(default_factory=list)
    report_md: str = ""


# ---------------------------------------------------------------------------
# PRValidationBot
# ---------------------------------------------------------------------------

class PRValidationBot:
    """Validates PRs, auto-restores deleted critical files, and checks revenue readiness."""

    def __init__(self, repo_root: str = ".", base_branch: str = "main"):
        self.repo_root = os.path.abspath(repo_root)
        self.base_branch = base_branch

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self) -> ValidationResult:
        """Run full PR validation and return a ValidationResult."""
        changed = self._get_changed_files()
        deleted, skipped = self._classify_files(changed)
        restored = self._restore_deleted_critical_files(deleted)
        revenue_checks = self._validate_revenue_bots()
        placeholder_matches = self._scan_placeholders(changed)
        missing_structure = self._validate_file_structure()
        errors = self._collect_errors(restored, revenue_checks, placeholder_matches, missing_structure)
        critical_ok = self._check_critical_files_exist()
        passed = critical_ok and not errors
        result = ValidationResult(
            passed=passed,
            critical_files_ok=critical_ok,
            restored_files=restored,
            skipped_files=skipped,
            revenue_checks=revenue_checks,
            errors=errors,
            placeholder_matches=placeholder_matches,
            missing_structure=missing_structure,
        )
        result.report_md = self._build_report(result)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=check,
        )

    def _get_changed_files(self) -> List[FileStatus]:
        """Return list of FileStatus objects for files changed relative to base branch."""
        try:
            result = self._run(
                ["git", "diff", "--name-status", f"{self.base_branch}...HEAD"], check=False
            )
            statuses: List[FileStatus] = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    status_code = parts[0][0]  # first char: D, M, R, A, …
                    path = parts[1]
                    statuses.append(FileStatus(path=path, status=status_code))
            return statuses
        except Exception:
            return []

    def _classify_files(
        self, changed: List[FileStatus]
    ) -> tuple[List[FileStatus], List[str]]:
        """Split changed files into truly-deleted vs intentionally-modified.

        Only files with status 'D' (deleted) are eligible for auto-restore.
        Files with status 'M' (modified) or 'R' (renamed) represent intentional
        changes and must NOT be overwritten.
        """
        deleted: List[FileStatus] = []
        skipped: List[str] = []
        for fs in changed:
            if fs.status == "D":
                deleted.append(fs)
            elif fs.status in ("M", "R"):
                # Intentional change — skip to avoid overwriting developer work
                skipped.append(fs.path)
        return deleted, skipped

    def _restore_deleted_critical_files(self, deleted: List[FileStatus]) -> List[str]:
        """Restore critical files that were deleted, from the base branch."""
        restored: List[str] = []
        critical_set = set(CRITICAL_FILES)
        for fs in deleted:
            if fs.path not in critical_set:
                continue
            try:
                self._run(["git", "checkout", self.base_branch, "--", fs.path])
                restored.append(fs.path)
            except subprocess.CalledProcessError:
                pass
        return restored

    def _check_critical_files_exist(self) -> bool:
        """Verify all critical files are present in the working tree."""
        for f in CRITICAL_FILES:
            full_path = os.path.join(self.repo_root, f)
            if not os.path.exists(full_path):
                return False
        return True

    def _validate_revenue_bots(self) -> List[RevenueCheck]:
        """Check every bot directory for revenue-readiness files."""
        checks: List[RevenueCheck] = []
        bots_dir = os.path.join(self.repo_root, "bots")
        if not os.path.isdir(bots_dir):
            return checks
        for entry in sorted(os.listdir(bots_dir)):
            bot_path = os.path.join(bots_dir, entry)
            if not os.path.isdir(bot_path):
                continue
            check = RevenueCheck(
                bot_path=entry,
                has_payment=os.path.isfile(os.path.join(bot_path, "payments.js")),
                has_logger=os.path.isfile(os.path.join(bot_path, "logger.js")),
                has_offer=os.path.isfile(os.path.join(bot_path, "index.js")),
            )
            checks.append(check)
        return checks

    def _collect_errors(
        self,
        restored: List[str],
        revenue_checks: List[RevenueCheck],
        placeholder_matches: Optional[List[PlaceholderMatch]] = None,
        missing_structure: Optional[List[str]] = None,
    ) -> List[str]:
        errors: List[str] = []
        for rc in revenue_checks:
            if not rc.is_ready:
                missing = []
                if not rc.has_payment:
                    missing.append("payments.js")
                if not rc.has_logger:
                    missing.append("logger.js")
                if not rc.has_offer:
                    missing.append("index.js")
                errors.append(
                    f"Bot '{rc.bot_path}' missing revenue files: {', '.join(missing)}"
                )
        if placeholder_matches:
            for pm in placeholder_matches:
                errors.append(
                    f"Placeholder '{pm.pattern}' found in {pm.path}:{pm.line_number}"
                )
        if missing_structure:
            for item in missing_structure:
                errors.append(f"Expected repository item missing: {item}")
        return errors

    def _scan_placeholders(self, changed: List[FileStatus]) -> List[PlaceholderMatch]:
        """Scan changed files for placeholder text patterns."""
        matches: List[PlaceholderMatch] = []
        for fs in changed:
            if fs.status == "D":
                continue  # Skip deleted files
            ext = os.path.splitext(fs.path)[1].lower()
            if ext not in SCANNABLE_EXTENSIONS:
                continue
            full_path = os.path.join(self.repo_root, fs.path)
            if not os.path.isfile(full_path):
                continue
            try:
                with open(full_path, encoding="utf-8", errors="replace") as fh:
                    for lineno, line in enumerate(fh, start=1):
                        for pattern in PLACEHOLDER_PATTERNS:
                            if pattern.search(line):
                                matches.append(
                                    PlaceholderMatch(
                                        path=fs.path,
                                        line_number=lineno,
                                        line_text=line.rstrip(),
                                        pattern=pattern.pattern,
                                    )
                                )
                                break  # one hit per line is enough
            except OSError:
                pass
        return matches

    def _validate_file_structure(self) -> List[str]:
        """Check that all expected top-level items are present in the repository."""
        missing: List[str] = []
        for item in EXPECTED_STRUCTURE:
            full_path = os.path.join(self.repo_root, item)
            if not os.path.exists(full_path):
                missing.append(item)
        return missing

    def _build_report(self, result: ValidationResult) -> str:
        """Generate a Markdown summary report for the PR comment."""
        lines: List[str] = [
            "## 🤖 PR Validation Report",
            "",
            f"**Overall Status:** {'✅ PASSED' if result.passed else '❌ FAILED'}",
            f"**Critical Files:** {'✅ All present' if result.critical_files_ok else '❌ Some missing'}",
            f"**File Structure:** {'✅ Complete' if not result.missing_structure else '❌ Items missing'}",
            f"**Placeholder Code:** {'✅ None found' if not result.placeholder_matches else f'❌ {len(result.placeholder_matches)} occurrence(s) found'}",
            "",
        ]

        if result.restored_files:
            lines.append("### 🔧 Auto-Restored Deleted Files")
            for f in result.restored_files:
                lines.append(f"- `{f}` — restored from `{self.base_branch}`")
            lines.append("")

        if result.skipped_files:
            lines.append("### ⏭️ Skipped (Intentional Changes — Not Overwritten)")
            for f in result.skipped_files:
                lines.append(f"- `{f}`")
            lines.append("")

        if result.missing_structure:
            lines.append("### 🗂️ Missing Expected Repository Items")
            for item in result.missing_structure:
                lines.append(f"- `{item}`")
            lines.append("")

        if result.placeholder_matches:
            lines.append("### 🚧 Placeholder Code Detected")
            lines.append("")
            lines.append("The following files contain placeholder text that must be replaced with production code:")
            lines.append("")
            lines.append("| File | Line | Pattern | Content |")
            lines.append("|------|------|---------|---------|")
            for pm in result.placeholder_matches:
                snippet = pm.line_text.strip()[:80].replace("|", "\\|")
                lines.append(f"| `{pm.path}` | {pm.line_number} | `{pm.pattern}` | `{snippet}` |")
            lines.append("")

        # Revenue readiness table
        lines.append("### 💰 Revenue Readiness")
        lines.append("")
        lines.append("| Bot | payments.js | logger.js | index.js | Ready |")
        lines.append("|-----|-------------|-----------|----------|-------|")
        for rc in result.revenue_checks:
            p = "✅" if rc.has_payment else "❌"
            lg = "✅" if rc.has_logger else "❌"
            o = "✅" if rc.has_offer else "❌"
            r = "✅" if rc.is_ready else "❌"
            lines.append(f"| `{rc.bot_path}` | {p} | {lg} | {o} | {r} |")
        lines.append("")

        if result.errors:
            lines.append("### ⚠️ Errors")
            for e in result.errors:
                lines.append(f"- {e}")
            lines.append("")

        return "\n".join(lines)
