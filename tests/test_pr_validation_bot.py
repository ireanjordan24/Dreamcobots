"""Tests for bots/pr_validation_bot/pr_validation_bot.py"""
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.pr_validation_bot.pr_validation_bot import (
    PRValidationBot,
    ValidationResult,
    DiscrepancyType,
    CRITICAL_FILES,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_bot(tmp_path=None, critical_files=None) -> PRValidationBot:
    log_dir = str(tmp_path) if tmp_path else tempfile.mkdtemp()
    return PRValidationBot(
        repo_root=REPO_ROOT,
        critical_files=critical_files,
        log_dir=log_dir,
    )


def make_tmp_repo(tmp_path, files: list[str]) -> PRValidationBot:
    """Create a minimal temp directory with specified files and return a bot pointing at it."""
    for rel in files:
        full = os.path.join(str(tmp_path), rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w").close()
    return PRValidationBot(
        repo_root=str(tmp_path),
        critical_files=files,
        log_dir=os.path.join(str(tmp_path), "logs"),
    )


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestInstantiation:
    def test_instantiates(self):
        bot = make_bot()
        assert bot is not None

    def test_default_critical_files(self):
        bot = PRValidationBot()
        assert bot.critical_files == CRITICAL_FILES

    def test_custom_critical_files(self):
        custom = ["file1.py", "file2.js"]
        bot = PRValidationBot(critical_files=custom)
        assert bot.critical_files == custom

    def test_default_log_dir(self):
        bot = PRValidationBot()
        assert bot.log_dir == "logs/pr-validation"

    def test_custom_log_dir(self, tmp_path):
        bot = PRValidationBot(log_dir=str(tmp_path))
        assert bot.log_dir == str(tmp_path)

    def test_has_flow_attribute(self):
        bot = make_bot()
        assert hasattr(bot, "flow")

    def test_flow_validate(self):
        bot = make_bot()
        assert bot.flow.validate() is True


# ---------------------------------------------------------------------------
# validate_critical_files
# ---------------------------------------------------------------------------

class TestValidateCriticalFiles:
    def test_all_present_passes(self, tmp_path):
        files = ["a.py", "b.json", "c.txt"]
        bot = make_tmp_repo(tmp_path, files)
        result = bot.validate_critical_files()
        assert result["passed"] is True
        assert result["missing"] == []
        assert sorted(result["present"]) == sorted(files)

    def test_missing_file_fails(self, tmp_path):
        files = ["exists.py", "missing.json"]
        # Only create one file
        full = os.path.join(str(tmp_path), "exists.py")
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w").close()
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=files,
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        result = bot.validate_critical_files()
        assert result["passed"] is False
        assert "missing.json" in result["missing"]
        assert "exists.py" in result["present"]

    def test_all_missing_fails(self, tmp_path):
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=["nope.txt", "also_nope.py"],
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        result = bot.validate_critical_files()
        assert result["passed"] is False
        assert len(result["missing"]) == 2

    def test_empty_critical_files_always_passes(self, tmp_path):
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=[],
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        result = bot.validate_critical_files()
        assert result["passed"] is True

    def test_nested_path_checked(self, tmp_path):
        nested = "subdir/deep/file.py"
        full = os.path.join(str(tmp_path), nested)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w").close()
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=[nested],
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        result = bot.validate_critical_files()
        assert result["passed"] is True

    def test_log_records_results(self, tmp_path):
        files = ["present.py"]
        bot = make_tmp_repo(tmp_path, files)
        bot.validate_critical_files()
        assert any("present.py" in line for line in bot._log)

    def test_against_real_repo(self):
        """Every critical file listed in CRITICAL_FILES must exist in the actual repo."""
        bot = PRValidationBot(repo_root=REPO_ROOT, log_dir=tempfile.mkdtemp())
        result = bot.validate_critical_files()
        assert result["passed"] is True, f"Missing: {result['missing']}"


# ---------------------------------------------------------------------------
# detect_branch_discrepancies
# ---------------------------------------------------------------------------

class TestDetectBranchDiscrepancies:
    def _make_bot_with_mock_git(self, tmp_path, git_output: str, rc: int = 0):
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=[],
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        bot._run_git = MagicMock(return_value=(rc, git_output, ""))
        return bot

    def test_no_discrepancies_passes(self, tmp_path):
        bot = self._make_bot_with_mock_git(tmp_path, "")
        result = bot.detect_branch_discrepancies("main", "feature")
        assert result["passed"] is True
        assert result["discrepancies"] == []

    def test_deleted_file_detected(self, tmp_path):
        bot = self._make_bot_with_mock_git(tmp_path, "D\tsome/file.py")
        result = bot.detect_branch_discrepancies("main", "feature")
        assert result["passed"] is False
        assert any(d["type"] == DiscrepancyType.MISSING_IN_PR for d in result["discrepancies"])

    def test_added_file_does_not_fail(self, tmp_path):
        bot = self._make_bot_with_mock_git(tmp_path, "A\tnew_file.py")
        result = bot.detect_branch_discrepancies("main", "feature")
        assert result["passed"] is True
        assert any(d["type"] == DiscrepancyType.ADDED_IN_PR for d in result["discrepancies"])

    def test_modified_file_does_not_fail(self, tmp_path):
        bot = self._make_bot_with_mock_git(tmp_path, "M\tchanged.py")
        result = bot.detect_branch_discrepancies("main", "feature")
        assert result["passed"] is True
        assert any(d["type"] == DiscrepancyType.CONTENT_CHANGED for d in result["discrepancies"])

    def test_multiple_statuses(self, tmp_path):
        git_output = "D\tdel.py\nA\tadd.py\nM\tmod.py"
        bot = self._make_bot_with_mock_git(tmp_path, git_output)
        result = bot.detect_branch_discrepancies("main", "feature")
        assert result["passed"] is False
        types = {d["type"] for d in result["discrepancies"]}
        assert DiscrepancyType.MISSING_IN_PR in types
        assert DiscrepancyType.ADDED_IN_PR in types
        assert DiscrepancyType.CONTENT_CHANGED in types

    def test_git_failure_returns_passed(self, tmp_path):
        """When git diff fails we assume no discrepancies (graceful degradation)."""
        bot = self._make_bot_with_mock_git(tmp_path, "", rc=1)
        result = bot.detect_branch_discrepancies("main", "feature")
        assert result["passed"] is True

    def test_discrepancy_contains_branch_info(self, tmp_path):
        bot = self._make_bot_with_mock_git(tmp_path, "D\tsome_file.py")
        result = bot.detect_branch_discrepancies("main", "my-feature")
        disc = result["discrepancies"][0]
        assert disc["base_branch"] == "main"
        assert disc["head_branch"] == "my-feature"
        assert disc["path"] == "some_file.py"


# ---------------------------------------------------------------------------
# auto_fix_missing_files
# ---------------------------------------------------------------------------

class TestAutoFixMissingFiles:
    def test_successful_fix(self, tmp_path):
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=[],
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        bot._run_git = MagicMock(return_value=(0, "", ""))
        result = bot.auto_fix_missing_files(["missing.py", "also_missing.js"])
        assert "missing.py" in result["fixes_applied"]
        assert "also_missing.js" in result["fixes_applied"]
        assert result["fixes_failed"] == []

    def test_failed_fix_recorded(self, tmp_path):
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=[],
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        bot._run_git = MagicMock(return_value=(1, "", "not found"))
        result = bot.auto_fix_missing_files(["cannot_restore.py"])
        assert "cannot_restore.py" in result["fixes_failed"]
        assert result["fixes_applied"] == []

    def test_partial_fix(self, tmp_path):
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=[],
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        # First call succeeds, second fails
        bot._run_git = MagicMock(side_effect=[
            (0, "", ""),
            (1, "", "error"),
        ])
        result = bot.auto_fix_missing_files(["ok.py", "fail.py"])
        assert "ok.py" in result["fixes_applied"]
        assert "fail.py" in result["fixes_failed"]

    def test_empty_list_returns_empty(self, tmp_path):
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=[],
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        result = bot.auto_fix_missing_files([])
        assert result["fixes_applied"] == []
        assert result["fixes_failed"] == []

    def test_log_records_fix(self, tmp_path):
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=[],
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        bot._run_git = MagicMock(return_value=(0, "", ""))
        bot.auto_fix_missing_files(["file.py"])
        assert any("Auto-fixed" in line or "file.py" in line for line in bot._log)


# ---------------------------------------------------------------------------
# generate_report
# ---------------------------------------------------------------------------

class TestGenerateReport:
    def _make_result(self, **kwargs) -> ValidationResult:
        defaults = dict(
            passed=True,
            missing_critical_files=[],
            discrepancies=[],
            auto_fixes_applied=[],
            auto_fix_failures=[],
            log_lines=[],
        )
        defaults.update(kwargs)
        return ValidationResult(**defaults)

    def test_passed_report_contains_pass_text(self, tmp_path):
        bot = make_bot(tmp_path)
        result = self._make_result(passed=True)
        report = bot.generate_report(result)
        assert "Passed" in report or "✅" in report

    def test_failed_report_contains_fail_text(self, tmp_path):
        bot = make_bot(tmp_path)
        result = self._make_result(passed=False, missing_critical_files=["req.txt"])
        report = bot.generate_report(result)
        assert "❌" in report or "Failed" in report

    def test_missing_files_in_report(self, tmp_path):
        bot = make_bot(tmp_path)
        result = self._make_result(passed=False, missing_critical_files=["req.txt", "pkg.json"])
        report = bot.generate_report(result)
        assert "req.txt" in report
        assert "pkg.json" in report

    def test_auto_fixes_in_report(self, tmp_path):
        bot = make_bot(tmp_path)
        result = self._make_result(passed=True, auto_fixes_applied=["fixed.py"])
        report = bot.generate_report(result)
        assert "fixed.py" in report

    def test_auto_fix_failures_in_report(self, tmp_path):
        bot = make_bot(tmp_path)
        result = self._make_result(passed=False, auto_fix_failures=["unfixable.py"])
        report = bot.generate_report(result)
        assert "unfixable.py" in report

    def test_log_lines_in_report(self, tmp_path):
        bot = make_bot(tmp_path)
        result = self._make_result(log_lines=["[2024-01-01] Some log line"])
        report = bot.generate_report(result)
        assert "Some log line" in report

    def test_report_is_string(self, tmp_path):
        bot = make_bot(tmp_path)
        result = self._make_result()
        report = bot.generate_report(result)
        assert isinstance(report, str)


# ---------------------------------------------------------------------------
# persist_log
# ---------------------------------------------------------------------------

class TestPersistLog:
    def test_creates_log_file(self, tmp_path):
        bot = make_bot(tmp_path)
        result = ValidationResult(passed=True, log_lines=["line 1", "line 2"])
        result.report = "# Report"
        log_path = bot.persist_log(result, pr_number="42")
        assert os.path.isfile(log_path)

    def test_log_file_contains_pr_number(self, tmp_path):
        bot = make_bot(tmp_path)
        result = ValidationResult(passed=True, log_lines=[])
        result.report = "report"
        log_path = bot.persist_log(result, pr_number="99")
        with open(log_path) as f:
            content = f.read()
        assert "99" in content

    def test_log_file_contains_passed_status(self, tmp_path):
        bot = make_bot(tmp_path)
        result = ValidationResult(passed=False, log_lines=[])
        result.report = "report"
        log_path = bot.persist_log(result, pr_number="1")
        with open(log_path) as f:
            content = f.read()
        assert "False" in content

    def test_log_dir_created(self, tmp_path):
        new_log_dir = os.path.join(str(tmp_path), "nested", "logs")
        bot = PRValidationBot(
            repo_root=REPO_ROOT,
            log_dir=new_log_dir,
        )
        result = ValidationResult(passed=True, log_lines=[])
        result.report = "r"
        bot.persist_log(result)
        assert os.path.isdir(new_log_dir)


# ---------------------------------------------------------------------------
# run (full pipeline)
# ---------------------------------------------------------------------------

class TestRun:
    def test_run_returns_validation_result(self, tmp_path):
        bot = make_tmp_repo(tmp_path, ["req.txt"])
        bot._run_git = MagicMock(return_value=(0, "", ""))
        result = bot.run(base_branch="main", auto_fix=False)
        assert isinstance(result, ValidationResult)

    def test_run_passes_when_all_files_present(self, tmp_path):
        files = ["a.py", "b.json"]
        bot = make_tmp_repo(tmp_path, files)
        bot._run_git = MagicMock(return_value=(0, "", ""))
        result = bot.run(base_branch="main", auto_fix=False)
        assert result.passed is True

    def test_run_fails_when_critical_file_missing(self, tmp_path):
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=["missing.py"],
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        bot._run_git = MagicMock(return_value=(0, "", ""))
        result = bot.run(base_branch="main", auto_fix=False)
        assert result.passed is False
        assert "missing.py" in result.missing_critical_files

    def test_run_auto_fix_applied(self, tmp_path):
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=["missing.py"],
            log_dir=os.path.join(str(tmp_path), "logs"),
        )
        # git diff returns nothing, git checkout succeeds and creates the file
        def mock_git(args):
            if "checkout" in args:
                # Actually create the file to simulate a restore
                full = os.path.join(str(tmp_path), "missing.py")
                open(full, "w").close()
                return (0, "", "")
            return (0, "", "")
        bot._run_git = mock_git
        result = bot.run(base_branch="main", auto_fix=True)
        assert "missing.py" in result.auto_fixes_applied

    def test_run_contains_report(self, tmp_path):
        files = ["file.py"]
        bot = make_tmp_repo(tmp_path, files)
        bot._run_git = MagicMock(return_value=(0, "", ""))
        result = bot.run(base_branch="main", auto_fix=False)
        assert isinstance(result.report, str)
        assert len(result.report) > 0

    def test_run_contains_log_lines(self, tmp_path):
        files = ["file.py"]
        bot = make_tmp_repo(tmp_path, files)
        bot._run_git = MagicMock(return_value=(0, "", ""))
        result = bot.run(base_branch="main", auto_fix=False)
        assert len(result.log_lines) > 0

    def test_run_creates_log_file(self, tmp_path):
        files = ["file.py"]
        log_dir = os.path.join(str(tmp_path), "validation-logs")
        bot = PRValidationBot(
            repo_root=str(tmp_path),
            critical_files=files,
            log_dir=log_dir,
        )
        # create the file
        open(os.path.join(str(tmp_path), "file.py"), "w").close()
        bot._run_git = MagicMock(return_value=(0, "", ""))
        bot.run(base_branch="main", pr_number="7")
        log_files = os.listdir(log_dir)
        assert any("pr-validation" in f for f in log_files)

    def test_run_discrepancy_with_deleted_file(self, tmp_path):
        files = ["present.py"]
        bot = make_tmp_repo(tmp_path, files)
        # Simulate a file deleted in PR
        bot._run_git = MagicMock(return_value=(0, "D\tdeleted.py", ""))
        result = bot.run(base_branch="main", auto_fix=False)
        assert result.passed is False
        assert any(d["type"] == DiscrepancyType.MISSING_IN_PR for d in result.discrepancies)

    def test_run_pr_number_in_result(self, tmp_path):
        files = ["file.py"]
        bot = make_tmp_repo(tmp_path, files)
        bot._run_git = MagicMock(return_value=(0, "", ""))
        result = bot.run(pr_number="123")
        assert result is not None  # PR number used in log name, not stored in result


# ---------------------------------------------------------------------------
# CRITICAL_FILES constant
# ---------------------------------------------------------------------------

class TestCriticalFilesConstant:
    def test_requirements_in_critical_files(self):
        assert "requirements.txt" in CRITICAL_FILES

    def test_package_json_in_critical_files(self):
        assert "package.json" in CRITICAL_FILES

    def test_readme_in_critical_files(self):
        assert "README.md" in CRITICAL_FILES

    def test_framework_checker_in_critical_files(self):
        assert "tools/check_bot_framework.py" in CRITICAL_FILES

    def test_framework_init_in_critical_files(self):
        assert "framework/__init__.py" in CRITICAL_FILES

    def test_ci_workflow_in_critical_files(self):
        assert ".github/workflows/ci.yml" in CRITICAL_FILES

    def test_all_critical_files_exist_in_repo(self):
        for path in CRITICAL_FILES:
            full = os.path.join(REPO_ROOT, path)
            assert os.path.isfile(full), f"Critical file missing from repo: {path}"


# ---------------------------------------------------------------------------
# DiscrepancyType enum
# ---------------------------------------------------------------------------

class TestDiscrepancyType:
    def test_values(self):
        assert DiscrepancyType.MISSING_IN_PR == "missing-in-pr"
        assert DiscrepancyType.ADDED_IN_PR == "added-in-pr"
        assert DiscrepancyType.CONTENT_CHANGED == "content-changed"
