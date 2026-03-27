"""DreamCo PR Validation Bot.

Autonomously validates pull requests by:
- Checking that all critical repository files are present.
- Detecting cross-branch file discrepancies between a PR branch and main.
- Recommending (and optionally applying) auto-fixes for resolvable issues.
- Generating structured reports with detailed logs for maintainers.

All DreamCo bots must integrate with the GLOBAL AI SOURCES FLOW framework.
"""
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'framework'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

# Framework compliance — required by all DreamCo bots.
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Constants — files the repository must always contain
# ---------------------------------------------------------------------------

#: Paths (relative to repo root) that every PR branch must preserve.
CRITICAL_FILES: list[str] = [
    "requirements.txt",
    "package.json",
    "README.md",
    "tools/check_bot_framework.py",
    "framework/__init__.py",
    "framework/global_ai_sources_flow.py",
    "bots/ai-models-integration/ai_models_integration.py",
    ".github/workflows/ci.yml",
    ".github/workflows/bot-ci.yml",
    ".github/workflows/auto-recovery.yml",
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class DiscrepancyType(str, Enum):
    """Types of discrepancy a PR branch can introduce."""
    MISSING_IN_PR = "missing-in-pr"       # File present on main, gone in PR branch
    ADDED_IN_PR = "added-in-pr"           # File added by PR (informational, not an error)
    CONTENT_CHANGED = "content-changed"   # File exists in both but differs


@dataclass
class ValidationResult:
    """Full result of a PR validation run."""
    passed: bool
    missing_critical_files: list[str] = field(default_factory=list)
    discrepancies: list[dict] = field(default_factory=list)
    auto_fixes_applied: list[str] = field(default_factory=list)
    auto_fix_failures: list[str] = field(default_factory=list)
    log_lines: list[str] = field(default_factory=list)
    report: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Bot
# ---------------------------------------------------------------------------

class PRValidationBot:
    """Autonomous pull-request validation bot for DreamCo repositories.

    Usage::

        bot = PRValidationBot(repo_root="/path/to/repo")
        result = bot.run(base_branch="main", head_branch="feature/my-pr")
        print(result.report)
    """

    def __init__(
        self,
        repo_root: Optional[str] = None,
        critical_files: Optional[list[str]] = None,
        log_dir: str = "logs/pr-validation",
    ):
        self.repo_root = repo_root or os.getcwd()
        self.critical_files = critical_files if critical_files is not None else CRITICAL_FILES
        self.log_dir = log_dir
        self._log: list[str] = []

        # Framework compliance
        self.flow = GlobalAISourcesFlow(bot_name="PRValidationBot")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _log_line(self, message: str) -> None:
        """Append a timestamped message to the in-memory log."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"[{timestamp}] {message}"
        self._log.append(line)

    def _file_exists(self, relative_path: str) -> bool:
        """Return True if *relative_path* exists under *repo_root*."""
        return os.path.isfile(os.path.join(self.repo_root, relative_path))

    def _run_git(self, args: list[str]) -> tuple[int, str, str]:
        """Run a git command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_root] + args,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            return 1, "", str(exc)

    # ------------------------------------------------------------------
    # Critical-file validation
    # ------------------------------------------------------------------

    def validate_critical_files(self) -> dict:
        """Check that every critical file is present in the working tree.

        Returns a dict with keys:
        - ``passed`` (bool)
        - ``missing`` (list[str]) — relative paths of absent files
        - ``present`` (list[str]) — relative paths of found files
        """
        missing: list[str] = []
        present: list[str] = []
        for rel_path in self.critical_files:
            if self._file_exists(rel_path):
                present.append(rel_path)
                self._log_line(f"✅ Critical file present: {rel_path}")
            else:
                missing.append(rel_path)
                self._log_line(f"❌ Critical file MISSING: {rel_path}")
        return {
            "passed": len(missing) == 0,
            "missing": missing,
            "present": present,
        }

    # ------------------------------------------------------------------
    # Cross-branch discrepancy detection
    # ------------------------------------------------------------------

    def detect_branch_discrepancies(
        self,
        base_branch: str = "main",
        head_branch: Optional[str] = None,
    ) -> dict:
        """Compare *head_branch* against *base_branch* and list file discrepancies.

        When *head_branch* is None the current working-tree state is compared.

        Returns a dict with keys:
        - ``passed`` (bool) — True when no MISSING_IN_PR discrepancies exist
        - ``discrepancies`` (list[dict]) — each entry has ``type``, ``path``,
          ``base_branch``, and ``head_branch`` keys
        """
        discrepancies: list[dict] = []

        # Files deleted in PR branch that existed on base
        rc, stdout, _ = self._run_git(["diff", "--name-status", f"{base_branch}...{head_branch or 'HEAD'}"])
        if rc != 0:
            self._log_line(f"⚠️  Could not diff branches ({base_branch} → {head_branch}): git returned {rc}")
            return {"passed": True, "discrepancies": []}

        for line in stdout.splitlines():
            if not line.strip():
                continue
            parts = line.split("\t", 1)
            if len(parts) < 2:
                continue
            status, path = parts[0].strip(), parts[1].strip()
            if status.startswith("D"):
                discrepancies.append({
                    "type": DiscrepancyType.MISSING_IN_PR,
                    "path": path,
                    "base_branch": base_branch,
                    "head_branch": head_branch or "HEAD",
                })
                self._log_line(f"⚠️  File deleted in PR: {path} (was on {base_branch})")
            elif status.startswith("A"):
                discrepancies.append({
                    "type": DiscrepancyType.ADDED_IN_PR,
                    "path": path,
                    "base_branch": base_branch,
                    "head_branch": head_branch or "HEAD",
                })
                self._log_line(f"ℹ️  New file added in PR: {path}")
            elif status.startswith("M"):
                discrepancies.append({
                    "type": DiscrepancyType.CONTENT_CHANGED,
                    "path": path,
                    "base_branch": base_branch,
                    "head_branch": head_branch or "HEAD",
                })
                self._log_line(f"ℹ️  File modified in PR: {path}")

        missing_in_pr = [d for d in discrepancies if d["type"] == DiscrepancyType.MISSING_IN_PR]
        return {
            "passed": len(missing_in_pr) == 0,
            "discrepancies": discrepancies,
        }

    # ------------------------------------------------------------------
    # Auto-fix
    # ------------------------------------------------------------------

    def auto_fix_missing_files(
        self,
        missing_paths: list[str],
        source_branch: str = "main",
    ) -> dict:
        """Attempt to restore *missing_paths* from *source_branch*.

        For each path, uses ``git checkout <source_branch> -- <path>`` to
        restore the file if it exists on the source branch.

        Returns a dict with:
        - ``fixes_applied`` (list[str]) — paths successfully restored
        - ``fixes_failed`` (list[str]) — paths that could not be restored
        """
        fixes_applied: list[str] = []
        fixes_failed: list[str] = []
        for path in missing_paths:
            rc, _, err = self._run_git(["checkout", source_branch, "--", path])
            if rc == 0:
                fixes_applied.append(path)
                self._log_line(f"🔧 Auto-fixed: restored {path} from {source_branch}")
            else:
                fixes_failed.append(path)
                self._log_line(f"🚫 Auto-fix failed for {path}: {err}")
        return {
            "fixes_applied": fixes_applied,
            "fixes_failed": fixes_failed,
        }

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def generate_report(self, result: ValidationResult) -> str:
        """Produce a human-readable Markdown report for maintainers."""
        status_icon = "✅" if result.passed else "❌"
        lines = [
            f"## {status_icon} DreamCo PR Validation Report",
            f"**Generated:** {result.timestamp}",
            "",
        ]

        # Critical files
        if result.missing_critical_files:
            lines.append("### ❌ Missing Critical Files")
            for f in result.missing_critical_files:
                lines.append(f"- `{f}`")
            lines.append("")
        else:
            lines.append("### ✅ All Critical Files Present\n")

        # Discrepancies
        missing_disc = [
            d for d in result.discrepancies
            if d.get("type") == DiscrepancyType.MISSING_IN_PR
        ]
        if missing_disc:
            lines.append("### ⚠️  Files Deleted in This PR (were on main)")
            for d in missing_disc:
                lines.append(f"- `{d['path']}`")
            lines.append("")

        added_disc = [
            d for d in result.discrepancies
            if d.get("type") == DiscrepancyType.ADDED_IN_PR
        ]
        if added_disc:
            lines.append("### ℹ️  New Files Added in This PR")
            for d in added_disc:
                lines.append(f"- `{d['path']}`")
            lines.append("")

        # Auto-fixes
        if result.auto_fixes_applied:
            lines.append("### 🔧 Auto-Fixes Applied")
            for fix in result.auto_fixes_applied:
                lines.append(f"- Restored `{fix}` from `main`")
            lines.append("")

        if result.auto_fix_failures:
            lines.append("### 🚫 Auto-Fix Failures (Manual Action Required)")
            for fail in result.auto_fix_failures:
                lines.append(f"- Could not restore `{fail}` — please add it manually")
            lines.append("")

        # Validation result
        if result.passed:
            lines.append("### ✅ Validation Passed — PR is merge-ready.")
        else:
            lines.append(
                "### ❌ Validation Failed — resolve the issues above before merging."
            )

        lines.append("")
        lines.append("<details>")
        lines.append("<summary>📋 Full Validation Log</summary>")
        lines.append("")
        lines.append("```")
        lines.extend(result.log_lines)
        lines.append("```")
        lines.append("</details>")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def persist_log(self, result: ValidationResult, pr_number: str = "") -> str:
        """Write the validation log to disk and return the file path."""
        os.makedirs(self.log_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"pr-validation-{pr_number or 'unknown'}-{ts}.log"
        log_path = os.path.join(self.log_dir, filename)
        with open(log_path, "w", encoding="utf-8") as fh:
            fh.write(f"PR Validation Log — PR #{pr_number}\n")
            fh.write(f"Timestamp: {result.timestamp}\n")
            fh.write(f"Passed: {result.passed}\n\n")
            fh.write("\n".join(result.log_lines))
            fh.write("\n\n--- REPORT ---\n")
            fh.write(result.report)
        return log_path

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def run(
        self,
        base_branch: str = "main",
        head_branch: Optional[str] = None,
        auto_fix: bool = True,
        pr_number: str = "",
    ) -> ValidationResult:
        """Run the complete PR validation pipeline.

        Steps:
        1. Validate all critical files are present.
        2. Detect cross-branch discrepancies.
        3. Optionally auto-fix missing critical files from *base_branch*.
        4. Build a structured ValidationResult with a Markdown report.
        5. Persist the log to disk.

        Args:
            base_branch: The branch to compare against (default ``"main"``).
            head_branch: The PR branch to validate (default: current HEAD).
            auto_fix: When True, attempt to restore missing critical files
                      from *base_branch* using ``git checkout``.
            pr_number: Optional PR identifier used in the log filename.

        Returns:
            A :class:`ValidationResult` describing the outcome.
        """
        self._log = []
        self._log_line(f"🚀 Starting PR validation (base={base_branch}, head={head_branch or 'HEAD'})")

        # 1. Critical file check
        self._log_line("--- Step 1: Critical File Validation ---")
        crit = self.validate_critical_files()
        missing_critical = crit["missing"]

        # 2. Branch discrepancy check
        self._log_line("--- Step 2: Cross-Branch Discrepancy Detection ---")
        disc = self.detect_branch_discrepancies(
            base_branch=base_branch,
            head_branch=head_branch,
        )

        # 3. Auto-fix
        fixes_applied: list[str] = []
        fixes_failed: list[str] = []
        if auto_fix and missing_critical:
            self._log_line("--- Step 3: Auto-Fix Attempt ---")
            fix_result = self.auto_fix_missing_files(missing_critical, source_branch=base_branch)
            fixes_applied = fix_result["fixes_applied"]
            fixes_failed = fix_result["fixes_failed"]
            # Re-validate after fixes
            if fixes_applied:
                self._log_line("🔄 Re-validating after auto-fix...")
                crit = self.validate_critical_files()
                missing_critical = crit["missing"]

        # 4. Determine overall pass/fail
        passed = (
            len(missing_critical) == 0
            and disc["passed"]
            and len(fixes_failed) == 0
        )

        if passed:
            self._log_line("✅ Validation complete — all checks passed.")
        else:
            self._log_line("❌ Validation complete — one or more checks failed.")

        result = ValidationResult(
            passed=passed,
            missing_critical_files=missing_critical,
            discrepancies=disc["discrepancies"],
            auto_fixes_applied=fixes_applied,
            auto_fix_failures=fixes_failed,
            log_lines=list(self._log),
        )
        result.report = self.generate_report(result)

        # 5. Persist log
        self.persist_log(result, pr_number=pr_number)

        # Framework pipeline compliance
        self.flow.run_pipeline(raw_data={"pr_number": pr_number, "passed": passed})

        return result
