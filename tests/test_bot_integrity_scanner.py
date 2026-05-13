"""Tests for bots/bot_integrity_scanner/bot_integrity_scanner.py"""
import os
import sys
import textwrap
from pathlib import Path

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.bot_integrity_scanner.bot_integrity_scanner import (
    BotIntegrityScanner,
    BotFileReport,
    BotPackageReport,
    IssueRecord,
    ScanReport,
    _check_file,
    _check_package,
    _extract_class_info,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_file(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


def make_good_bot_file(path: Path) -> Path:
    """Write a minimal compliant bot file."""
    return write_file(
        path,
        """\
        # GLOBAL AI SOURCES FLOW
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from framework import GlobalAISourcesFlow  # noqa: F401

        class MyBot:
            def __init__(self, name=None):
                self.name = name

            def run(self, task=None):
                return {"status": "ok"}
        """,
    )


# ---------------------------------------------------------------------------
# IssueRecord
# ---------------------------------------------------------------------------

class TestIssueRecord:
    def test_fields(self):
        issue = IssueRecord("error", "syntax", "bad code")
        assert issue.severity == "error"
        assert issue.check == "syntax"
        assert issue.message == "bad code"


# ---------------------------------------------------------------------------
# BotFileReport
# ---------------------------------------------------------------------------

class TestBotFileReport:
    def test_has_errors_false_when_empty(self):
        r = BotFileReport(path=Path("x.py"))
        assert not r.has_errors

    def test_has_errors_true_with_error_issue(self):
        r = BotFileReport(path=Path("x.py"))
        r.issues.append(IssueRecord("error", "syntax", "oops"))
        assert r.has_errors

    def test_has_warnings_true_with_warning_issue(self):
        r = BotFileReport(path=Path("x.py"))
        r.issues.append(IssueRecord("warning", "check", "hmm"))
        assert r.has_warnings

    def test_has_warnings_false_for_info(self):
        r = BotFileReport(path=Path("x.py"))
        r.issues.append(IssueRecord("info", "check", "fyi"))
        assert not r.has_warnings


# ---------------------------------------------------------------------------
# _extract_class_info
# ---------------------------------------------------------------------------

class TestExtractClassInfo:
    def _parse(self, source: str):
        import ast
        return ast.parse(textwrap.dedent(source))

    def test_finds_class_with_run(self):
        tree = self._parse(
            """\
            class Foo:
                def __init__(self, a, b=1): pass
                def run(self, task=None): pass
            """
        )
        info = _extract_class_info(tree)
        assert len(info) == 1
        assert info[0]["name"] == "Foo"
        assert info[0]["has_run"]
        assert info[0]["has_init"]
        assert "a" in info[0]["init_kwargs"]
        assert "b" in info[0]["init_kwargs"]

    def test_finds_class_without_run(self):
        tree = self._parse(
            """\
            class Bar:
                def __init__(self): pass
            """
        )
        info = _extract_class_info(tree)
        assert not info[0]["has_run"]

    def test_kwargs_star_star(self):
        tree = self._parse(
            """\
            class Baz:
                def __init__(self, **kwargs): pass
                def run(self): pass
            """
        )
        info = _extract_class_info(tree)
        assert "**kwargs" in info[0]["init_kwargs"]

    def test_multiple_classes(self):
        tree = self._parse(
            """\
            class A:
                def run(self): pass
            class B:
                def run(self): pass
            """
        )
        info = _extract_class_info(tree)
        assert len(info) == 2


# ---------------------------------------------------------------------------
# _check_file
# ---------------------------------------------------------------------------

class TestCheckFile:
    def test_compliant_good_file(self, tmp_path):
        f = make_good_bot_file(tmp_path / "bot.py")
        report = _check_file(f)
        assert report.syntax_ok
        assert report.framework_compliant
        assert report.has_run_method
        assert not report.has_errors

    def test_syntax_error_detected(self, tmp_path):
        f = write_file(tmp_path / "bad.py", "def foo(:\n")
        report = _check_file(f)
        assert not report.syntax_ok
        assert report.has_errors
        checks = [i.check for i in report.issues]
        assert "syntax" in checks

    def test_missing_framework_is_warning(self, tmp_path):
        f = write_file(
            tmp_path / "no_fw.py",
            """\
            class Bot:
                def run(self): pass
            """,
        )
        report = _check_file(f)
        assert report.syntax_ok
        assert not report.framework_compliant
        warnings = [i for i in report.issues if i.check == "framework_compliance"]
        assert warnings

    def test_missing_run_is_warning(self, tmp_path):
        f = write_file(
            tmp_path / "no_run.py",
            """\
            # GLOBAL AI SOURCES FLOW
            class Bot:
                def __init__(self): pass
            """,
        )
        report = _check_file(f)
        assert not report.has_run_method
        warns = [i for i in report.issues if i.check == "missing_run_method"]
        assert warns

    def test_init_kwargs_extracted(self, tmp_path):
        f = make_good_bot_file(tmp_path / "bot.py")
        report = _check_file(f)
        assert "name" in report.init_kwargs

    def test_unreadable_file_is_error(self, tmp_path):
        """Non-existent file path triggers a read error."""
        report = _check_file(tmp_path / "ghost.py")
        assert report.has_errors
        assert any(i.check == "file_read" for i in report.issues)

    def test_framework_marker_in_comment(self, tmp_path):
        """A comment containing the marker is sufficient for compliance."""
        f = write_file(
            tmp_path / "comment.py",
            """\
            # GLOBAL AI SOURCES FLOW
            class Bot:
                def run(self): pass
            """,
        )
        report = _check_file(f)
        assert report.framework_compliant

    def test_test_class_not_checked_for_run(self, tmp_path):
        """A file whose only class starts with 'Test' should not trigger a missing-run warning."""
        f = write_file(
            tmp_path / "test_bot.py",
            """\
            # GLOBAL AI SOURCES FLOW
            class TestSomething:
                def test_it(self): pass
            """,
        )
        report = _check_file(f)
        assert not any(i.check == "missing_run_method" for i in report.issues)


# ---------------------------------------------------------------------------
# _check_package
# ---------------------------------------------------------------------------

class TestCheckPackage:
    def _make_package(self, tmp_path: Path, with_init: bool = True) -> Path:
        pkg = tmp_path / "mybot"
        pkg.mkdir()
        if with_init:
            (pkg / "__init__.py").write_text(
                "# GLOBAL AI SOURCES FLOW\n", encoding="utf-8"
            )
        return pkg

    def test_package_with_good_file_has_no_errors(self, tmp_path):
        pkg = self._make_package(tmp_path)
        make_good_bot_file(pkg / "mybot.py")
        report = _check_package(pkg)
        assert report.has_init
        assert not report.has_errors

    def test_missing_init_is_warning(self, tmp_path):
        pkg = self._make_package(tmp_path, with_init=False)
        make_good_bot_file(pkg / "mybot.py")
        report = _check_package(pkg)
        assert not report.has_init
        issues = [i.check for i in report.package_issues]
        assert "missing_init" in issues

    def test_no_impl_file_is_warning(self, tmp_path):
        pkg = self._make_package(tmp_path)
        report = _check_package(pkg)
        issues = [i.check for i in report.package_issues]
        assert "no_implementation_file" in issues

    def test_syntax_error_in_impl_file_is_error(self, tmp_path):
        pkg = self._make_package(tmp_path)
        write_file(pkg / "bad.py", "def (:\n")
        report = _check_package(pkg)
        assert report.has_errors

    def test_test_files_excluded(self, tmp_path):
        pkg = self._make_package(tmp_path)
        # Only a test file — should trigger no_implementation_file warning
        write_file(pkg / "test_mybot.py", "class TestBot: pass\n")
        report = _check_package(pkg)
        issues = [i.check for i in report.package_issues]
        assert "no_implementation_file" in issues


# ---------------------------------------------------------------------------
# ScanReport
# ---------------------------------------------------------------------------

class TestScanReport:
    def test_passed_when_no_errors(self):
        r = ScanReport()
        assert r.passed

    def test_not_passed_when_errors(self):
        r = ScanReport(packages_with_errors=1)
        assert not r.passed

    def test_total_errors_aggregates(self):
        r = ScanReport()
        pkg = BotPackageReport(package_path=Path("."), name="x")
        pkg.package_issues.append(IssueRecord("error", "check", "bad"))
        r.package_reports.append(pkg)
        assert r.total_errors == 1

    def test_total_warnings_aggregates(self):
        r = ScanReport()
        pkg = BotPackageReport(package_path=Path("."), name="x")
        pkg.package_issues.append(IssueRecord("warning", "check", "hmm"))
        r.package_reports.append(pkg)
        assert r.total_warnings == 1


# ---------------------------------------------------------------------------
# BotIntegrityScanner
# ---------------------------------------------------------------------------

class TestBotIntegrityScanner:
    def _make_scanner(self, tmp_path: Path) -> BotIntegrityScanner:
        """Create a scanner scoped to a temp repo with a single 'bots' dir."""
        return BotIntegrityScanner(repo_root=str(tmp_path), bot_dirs=("bots",))

    def _make_good_package(self, bots_dir: Path, name: str) -> Path:
        pkg = bots_dir / name
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("# GLOBAL AI SOURCES FLOW\n", encoding="utf-8")
        make_good_bot_file(pkg / f"{name}.py")
        return pkg

    def test_instantiates_with_defaults(self):
        scanner = BotIntegrityScanner()
        assert scanner.repo_root.exists()

    def test_instantiates_with_custom_root(self, tmp_path):
        scanner = BotIntegrityScanner(repo_root=str(tmp_path))
        assert scanner.repo_root == tmp_path.resolve()

    def test_scan_empty_dir_returns_zero(self, tmp_path):
        scanner = self._make_scanner(tmp_path)
        report = scanner.scan()
        assert report.scanned_packages == 0

    def test_scan_good_package_passes(self, tmp_path):
        bots_dir = tmp_path / "bots"
        bots_dir.mkdir()
        self._make_good_package(bots_dir, "alpha_bot")
        scanner = self._make_scanner(tmp_path)
        report = scanner.scan()
        assert report.scanned_packages == 1
        assert report.passed

    def test_scan_package_with_syntax_error(self, tmp_path):
        bots_dir = tmp_path / "bots"
        bots_dir.mkdir()
        pkg = bots_dir / "broken_bot"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("# GLOBAL AI SOURCES FLOW\n", encoding="utf-8")
        write_file(pkg / "broken_bot.py", "def (\n")
        scanner = self._make_scanner(tmp_path)
        report = scanner.scan()
        assert report.packages_with_errors >= 1
        assert not report.passed

    def test_scan_multiple_packages(self, tmp_path):
        bots_dir = tmp_path / "bots"
        bots_dir.mkdir()
        self._make_good_package(bots_dir, "alpha_bot")
        self._make_good_package(bots_dir, "beta_bot")
        scanner = self._make_scanner(tmp_path)
        report = scanner.scan()
        assert report.scanned_packages == 2

    def test_missing_bot_dirs_ignored(self, tmp_path):
        scanner = BotIntegrityScanner(
            repo_root=str(tmp_path), bot_dirs=("nonexistent_dir",)
        )
        report = scanner.scan()
        assert report.scanned_packages == 0

    def test_run_returns_dict(self, tmp_path):
        bots_dir = tmp_path / "bots"
        bots_dir.mkdir()
        self._make_good_package(bots_dir, "gamma_bot")
        scanner = self._make_scanner(tmp_path)
        result = scanner.run()
        assert isinstance(result, dict)
        assert "status" in result
        assert "scanned_packages" in result
        assert "passed" in result

    def test_run_status_success_when_no_errors(self, tmp_path):
        bots_dir = tmp_path / "bots"
        bots_dir.mkdir()
        self._make_good_package(bots_dir, "delta_bot")
        scanner = self._make_scanner(tmp_path)
        result = scanner.run()
        assert result["status"] == "success"
        assert result["passed"] is True

    def test_run_status_issues_found_when_errors(self, tmp_path):
        bots_dir = tmp_path / "bots"
        bots_dir.mkdir()
        pkg = bots_dir / "bad_bot"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("# GLOBAL AI SOURCES FLOW\n", encoding="utf-8")
        write_file(pkg / "bad_bot.py", "def (\n")
        scanner = self._make_scanner(tmp_path)
        result = scanner.run()
        assert result["status"] == "issues_found"
        assert result["passed"] is False

    def test_print_report_runs_without_error(self, tmp_path, capsys):
        bots_dir = tmp_path / "bots"
        bots_dir.mkdir()
        self._make_good_package(bots_dir, "echo_bot")
        scanner = self._make_scanner(tmp_path)
        report = scanner.scan()
        scanner.print_report(report)
        captured = capsys.readouterr()
        assert "DreamCo Bot Integrity Scanner" in captured.out

    def test_non_dir_entries_in_bots_dir_skipped(self, tmp_path):
        bots_dir = tmp_path / "bots"
        bots_dir.mkdir()
        # A file (not a directory) at the top level of bots/
        (bots_dir / "some_file.py").write_text("x = 1\n", encoding="utf-8")
        self._make_good_package(bots_dir, "zeta_bot")
        scanner = self._make_scanner(tmp_path)
        report = scanner.scan()
        # Only the package directory should be counted
        assert report.scanned_packages == 1

    def test_custom_bot_dirs(self, tmp_path):
        custom = tmp_path / "custom_bots"
        custom.mkdir()
        pkg = custom / "my_custom_bot"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("# GLOBAL AI SOURCES FLOW\n", encoding="utf-8")
        make_good_bot_file(pkg / "my_custom_bot.py")
        scanner = BotIntegrityScanner(
            repo_root=str(tmp_path), bot_dirs=("custom_bots",)
        )
        report = scanner.scan()
        assert report.scanned_packages == 1
        assert report.passed
