"""Tests for bots/pr_validation_bot/pr_validation_bot.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from unittest.mock import patch, MagicMock
from bots.pr_validation_bot.pr_validation_bot import (
    PRValidationBot,
    ValidationResult,
    RevenueCheck,
    FileStatus,
    PlaceholderMatch,
    CRITICAL_FILES,
    PLACEHOLDER_PATTERNS,
    EXPECTED_STRUCTURE,
    SCANNABLE_EXTENSIONS,
)


# ---------------------------------------------------------------------------
# FileStatus and classification tests
# ---------------------------------------------------------------------------


class TestFileStatusClassification:
    def setup_method(self):
        self.bot = PRValidationBot(repo_root=REPO_ROOT)

    def test_deleted_file_goes_to_deleted_list(self):
        files = [FileStatus(path="index.js", status="D")]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 1
        assert deleted[0].path == "index.js"
        assert len(skipped) == 0

    def test_modified_file_goes_to_skipped(self):
        files = [FileStatus(path="index.js", status="M")]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 0
        assert "index.js" in skipped

    def test_renamed_file_goes_to_skipped(self):
        files = [FileStatus(path="README.md", status="R")]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 0
        assert "README.md" in skipped

    def test_added_file_not_in_either_list(self):
        files = [FileStatus(path="new_bot.py", status="A")]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 0
        assert len(skipped) == 0

    def test_mixed_statuses_correctly_classified(self):
        files = [
            FileStatus(path="index.js", status="D"),
            FileStatus(path="package.json", status="M"),
            FileStatus(path="README.md", status="R"),
            FileStatus(path="new_file.py", status="A"),
        ]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 1
        assert deleted[0].path == "index.js"
        assert "package.json" in skipped
        assert "README.md" in skipped
        assert "new_file.py" not in skipped

    def test_multiple_deleted_files(self):
        files = [
            FileStatus(path="index.js", status="D"),
            FileStatus(path="package.json", status="D"),
        ]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 2
        assert len(skipped) == 0

    def test_modified_critical_file_not_restored(self):
        """Modified critical files must NOT be auto-restored."""
        files = [FileStatus(path="framework/__init__.py", status="M")]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 0
        assert "framework/__init__.py" in skipped


# ---------------------------------------------------------------------------
# Revenue check tests
# ---------------------------------------------------------------------------


class TestRevenueCheck:
    def test_fully_ready_bot(self, tmp_path):
        bot_dir = tmp_path / "my_bot"
        bot_dir.mkdir()
        (bot_dir / "payments.js").write_text("{}")
        (bot_dir / "logger.js").write_text("{}")
        (bot_dir / "index.js").write_text("{}")
        rc = RevenueCheck(
            bot_path="my_bot",
            has_payment=True,
            has_logger=True,
            has_offer=True,
        )
        assert rc.is_ready is True

    def test_missing_payment_not_ready(self):
        rc = RevenueCheck(
            bot_path="bot_x", has_payment=False, has_logger=True, has_offer=True
        )
        assert rc.is_ready is False

    def test_missing_logger_not_ready(self):
        rc = RevenueCheck(
            bot_path="bot_y", has_payment=True, has_logger=False, has_offer=True
        )
        assert rc.is_ready is False

    def test_missing_offer_not_ready(self):
        rc = RevenueCheck(
            bot_path="bot_z", has_payment=True, has_logger=True, has_offer=False
        )
        assert rc.is_ready is False

    def test_to_dict_contains_expected_keys(self):
        rc = RevenueCheck(
            bot_path="bot_a", has_payment=True, has_logger=True, has_offer=True
        )
        d = rc.to_dict()
        assert "bot_path" in d
        assert "has_payment" in d
        assert "has_logger" in d
        assert "has_offer" in d
        assert "is_ready" in d


# ---------------------------------------------------------------------------
# Critical file existence check
# ---------------------------------------------------------------------------


class TestCriticalFilesExist:
    def test_missing_critical_file_returns_false(self, tmp_path):
        bot = PRValidationBot(repo_root=str(tmp_path))
        assert bot._check_critical_files_exist() is False

    def test_all_critical_files_present(self, tmp_path):
        for f in CRITICAL_FILES:
            full = tmp_path / f
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text("")
        bot = PRValidationBot(repo_root=str(tmp_path))
        assert bot._check_critical_files_exist() is True


# ---------------------------------------------------------------------------
# Revenue bot validation
# ---------------------------------------------------------------------------


class TestValidateRevenueBots:
    def test_no_bots_dir_returns_empty(self, tmp_path):
        bot = PRValidationBot(repo_root=str(tmp_path))
        checks = bot._validate_revenue_bots()
        assert checks == []

    def test_bot_with_all_files_is_ready(self, tmp_path):
        bots_dir = tmp_path / "bots"
        my_bot = bots_dir / "my_bot"
        my_bot.mkdir(parents=True)
        (my_bot / "payments.js").write_text("{}")
        (my_bot / "logger.js").write_text("{}")
        (my_bot / "index.js").write_text("{}")
        bot = PRValidationBot(repo_root=str(tmp_path))
        checks = bot._validate_revenue_bots()
        assert len(checks) == 1
        assert checks[0].is_ready is True

    def test_bot_missing_payments_not_ready(self, tmp_path):
        bots_dir = tmp_path / "bots"
        my_bot = bots_dir / "my_bot"
        my_bot.mkdir(parents=True)
        (my_bot / "logger.js").write_text("{}")
        (my_bot / "index.js").write_text("{}")
        bot = PRValidationBot(repo_root=str(tmp_path))
        checks = bot._validate_revenue_bots()
        assert not checks[0].has_payment
        assert checks[0].is_ready is False

    def test_multiple_bots_scanned(self, tmp_path):
        bots_dir = tmp_path / "bots"
        for name in ["bot_a", "bot_b", "bot_c"]:
            (bots_dir / name).mkdir(parents=True)
        bot = PRValidationBot(repo_root=str(tmp_path))
        checks = bot._validate_revenue_bots()
        assert len(checks) == 3


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


class TestBuildReport:
    def test_report_contains_passed_status(self):
        bot = PRValidationBot()
        result = ValidationResult(passed=True, critical_files_ok=True)
        result.report_md = bot._build_report(result)
        assert "PASSED" in result.report_md

    def test_report_contains_failed_status(self):
        bot = PRValidationBot()
        result = ValidationResult(passed=False, critical_files_ok=False)
        result.report_md = bot._build_report(result)
        assert "FAILED" in result.report_md

    def test_report_lists_restored_files(self):
        bot = PRValidationBot()
        result = ValidationResult(
            passed=True,
            critical_files_ok=True,
            restored_files=["index.js"],
        )
        result.report_md = bot._build_report(result)
        assert "index.js" in result.report_md
        assert "Auto-Restored" in result.report_md

    def test_report_lists_skipped_files(self):
        bot = PRValidationBot()
        result = ValidationResult(
            passed=True,
            critical_files_ok=True,
            skipped_files=["package.json"],
        )
        result.report_md = bot._build_report(result)
        assert "package.json" in result.report_md
        assert "Skipped" in result.report_md

    def test_report_has_revenue_table(self):
        bot = PRValidationBot()
        result = ValidationResult(
            passed=True,
            critical_files_ok=True,
            revenue_checks=[
                RevenueCheck("my_bot", has_payment=True, has_logger=True, has_offer=True)
            ],
        )
        result.report_md = bot._build_report(result)
        assert "Revenue Readiness" in result.report_md
        assert "my_bot" in result.report_md

    def test_report_is_string(self):
        bot = PRValidationBot()
        result = ValidationResult(passed=True, critical_files_ok=True)
        md = bot._build_report(result)
        assert isinstance(md, str)

    def test_report_contains_pr_validation_header(self):
        bot = PRValidationBot()
        result = ValidationResult(passed=True, critical_files_ok=True)
        md = bot._build_report(result)
        assert "PR Validation Report" in md


# ---------------------------------------------------------------------------
# ValidationResult dataclass
# ---------------------------------------------------------------------------


class TestValidationResult:
    def test_default_values(self):
        r = ValidationResult(passed=True, critical_files_ok=True)
        assert r.restored_files == []
        assert r.skipped_files == []
        assert r.revenue_checks == []
        assert r.errors == []
        assert r.report_md == ""

    def test_passed_false_when_errors(self):
        r = ValidationResult(
            passed=False,
            critical_files_ok=True,
            errors=["something wrong"],
        )
        assert not r.passed

# ---------------------------------------------------------------------------
# PlaceholderMatch dataclass
# ---------------------------------------------------------------------------


class TestPlaceholderMatch:
    def test_to_dict_contains_all_keys(self):
        pm = PlaceholderMatch(
            path="bots/my_bot/bot.py",
            line_number=42,
            line_text="    # TODO: implement this",
            pattern=r"\bTODO\b",
        )
        d = pm.to_dict()
        assert d["path"] == "bots/my_bot/bot.py"
        assert d["line_number"] == 42
        assert d["line_text"] == "    # TODO: implement this"
        assert d["pattern"] == r"\bTODO\b"

    def test_placeholder_match_fields(self):
        pm = PlaceholderMatch(path="a.py", line_number=1, line_text="TODO", pattern="TODO")
        assert pm.path == "a.py"
        assert pm.line_number == 1


# ---------------------------------------------------------------------------
# Placeholder pattern constants
# ---------------------------------------------------------------------------


class TestPlaceholderPatterns:
    def test_todo_pattern_matches(self):
        import re
        pattern = next(p for p in PLACEHOLDER_PATTERNS if "TODO" in p.pattern)
        assert pattern.search("# TODO: fix this")

    def test_todo_pattern_case_insensitive(self):
        import re
        pattern = next(p for p in PLACEHOLDER_PATTERNS if "TODO" in p.pattern)
        assert pattern.search("# todo: fix this")

    def test_placeholder_pattern_matches(self):
        import re
        pattern = next(p for p in PLACEHOLDER_PATTERNS if "PLACEHOLDER" in p.pattern)
        assert pattern.search("value = PLACEHOLDER")

    def test_fixme_pattern_matches(self):
        import re
        pattern = next(p for p in PLACEHOLDER_PATTERNS if "FIXME" in p.pattern)
        assert pattern.search("# FIXME: broken")

    def test_hack_pattern_matches(self):
        import re
        pattern = next(p for p in PLACEHOLDER_PATTERNS if "HACK" in p.pattern)
        assert pattern.search("# HACK: workaround")

    def test_stub_pattern_matches(self):
        import re
        pattern = next(p for p in PLACEHOLDER_PATTERNS if "STUB" in p.pattern)
        assert pattern.search("# STUB function")

    def test_xxx_pattern_matches(self):
        import re
        pattern = next(p for p in PLACEHOLDER_PATTERNS if p.pattern == r"\bXXX\b")
        assert pattern.search("# XXX dangerous")

    def test_not_implemented_pattern_matches(self):
        import re
        pattern = next(p for p in PLACEHOLDER_PATTERNS if "NOT IMPLEMENTED" in p.pattern)
        assert pattern.search("raise NotImplementedError  # NOT IMPLEMENTED")


# ---------------------------------------------------------------------------
# Placeholder scanning
# ---------------------------------------------------------------------------


class TestScanPlaceholders:
    def _make_bot(self, tmp_path):
        return PRValidationBot(repo_root=str(tmp_path))

    def test_no_changed_files_returns_empty(self, tmp_path):
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([])
        assert result == []

    def test_deleted_files_are_skipped(self, tmp_path):
        f = tmp_path / "script.py"
        f.write_text("# TODO: implement\n")
        bot = self._make_bot(tmp_path)
        # Status 'D' means deleted — should be ignored even if file exists on disk
        result = bot._scan_placeholders([FileStatus(path="script.py", status="D")])
        assert result == []

    def test_todo_in_python_file_detected(self, tmp_path):
        f = tmp_path / "bot.py"
        f.write_text("def run():\n    pass  # TODO: implement\n")
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([FileStatus(path="bot.py", status="A")])
        assert len(result) == 1
        assert result[0].path == "bot.py"
        assert result[0].line_number == 2

    def test_placeholder_in_js_file_detected(self, tmp_path):
        f = tmp_path / "index.js"
        f.write_text("const x = 'PLACEHOLDER';\n")
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([FileStatus(path="index.js", status="M")])
        assert len(result) == 1
        assert result[0].path == "index.js"

    def test_fixme_in_ts_file_detected(self, tmp_path):
        f = tmp_path / "app.ts"
        f.write_text("// FIXME: remove this\nconst a = 1;\n")
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([FileStatus(path="app.ts", status="A")])
        assert len(result) == 1
        assert result[0].line_number == 1

    def test_unscannable_extension_skipped(self, tmp_path):
        f = tmp_path / "image.png"
        f.write_bytes(b"TODO binary content")
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([FileStatus(path="image.png", status="A")])
        assert result == []

    def test_multiple_placeholders_in_one_file(self, tmp_path):
        f = tmp_path / "bot.py"
        f.write_text("# TODO: line1\n# FIXME: line2\nclean_line = 1\n# PLACEHOLDER\n")
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([FileStatus(path="bot.py", status="A")])
        assert len(result) == 3

    def test_clean_file_returns_no_matches(self, tmp_path):
        f = tmp_path / "clean.py"
        f.write_text("def add(a, b):\n    return a + b\n")
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([FileStatus(path="clean.py", status="A")])
        assert result == []

    def test_nonexistent_file_skipped_gracefully(self, tmp_path):
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([FileStatus(path="ghost.py", status="A")])
        assert result == []

    def test_yaml_file_scanned(self, tmp_path):
        f = tmp_path / "config.yml"
        f.write_text("key: value\n# TODO: add more keys\n")
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([FileStatus(path="config.yml", status="A")])
        assert len(result) == 1

    def test_markdown_file_scanned(self, tmp_path):
        f = tmp_path / "README.md"
        f.write_text("# My Bot\n\nTODO: write docs\n")
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([FileStatus(path="README.md", status="M")])
        assert len(result) == 1

    def test_only_one_match_per_line(self, tmp_path):
        # A line matching two patterns should only produce one PlaceholderMatch
        f = tmp_path / "bot.py"
        f.write_text("# TODO FIXME: do both\n")
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([FileStatus(path="bot.py", status="A")])
        assert len(result) == 1

    def test_case_insensitive_todo(self, tmp_path):
        f = tmp_path / "bot.py"
        f.write_text("# todo: lowercase\n")
        bot = self._make_bot(tmp_path)
        result = bot._scan_placeholders([FileStatus(path="bot.py", status="A")])
        assert len(result) == 1


# ---------------------------------------------------------------------------
# File structure validation
# ---------------------------------------------------------------------------


class TestValidateFileStructure:
    def _create_structure(self, tmp_path, items):
        for item in items:
            p = tmp_path / item
            if p.suffix:  # has a file extension — treat as a file
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("")
            else:
                p.mkdir(parents=True, exist_ok=True)

    def test_all_expected_items_present(self, tmp_path):
        self._create_structure(tmp_path, EXPECTED_STRUCTURE)
        bot = PRValidationBot(repo_root=str(tmp_path))
        missing = bot._validate_file_structure()
        assert missing == []

    def test_missing_item_detected(self, tmp_path):
        # Create all but the first item
        self._create_structure(tmp_path, EXPECTED_STRUCTURE[1:])
        bot = PRValidationBot(repo_root=str(tmp_path))
        missing = bot._validate_file_structure()
        assert EXPECTED_STRUCTURE[0] in missing

    def test_empty_repo_missing_all(self, tmp_path):
        bot = PRValidationBot(repo_root=str(tmp_path))
        missing = bot._validate_file_structure()
        assert len(missing) == len(EXPECTED_STRUCTURE)

    def test_expected_structure_contains_required_items(self):
        # Sanity check that EXPECTED_STRUCTURE has the key repo items
        assert "README.md" in EXPECTED_STRUCTURE
        assert "package.json" in EXPECTED_STRUCTURE
        assert "bots" in EXPECTED_STRUCTURE
        assert "tests" in EXPECTED_STRUCTURE
        assert ".github" in EXPECTED_STRUCTURE

    def test_extra_files_not_penalised(self, tmp_path):
        # All expected items present + an extra file — should still pass
        self._create_structure(tmp_path, EXPECTED_STRUCTURE)
        (tmp_path / "extra_file.py").write_text("extra = True\n")
        bot = PRValidationBot(repo_root=str(tmp_path))
        missing = bot._validate_file_structure()
        assert missing == []


# ---------------------------------------------------------------------------
# collect_errors with placeholder/structure args
# ---------------------------------------------------------------------------


class TestCollectErrorsExtended:
    def setup_method(self):
        self.bot = PRValidationBot(repo_root=REPO_ROOT)

    def test_placeholder_matches_add_errors(self):
        pm = PlaceholderMatch(path="bot.py", line_number=5, line_text="# TODO", pattern=r"\bTODO\b")
        errors = self.bot._collect_errors([], [], placeholder_matches=[pm])
        assert any("Placeholder" in e for e in errors)
        assert any("bot.py:5" in e for e in errors)

    def test_missing_structure_adds_errors(self):
        errors = self.bot._collect_errors([], [], missing_structure=["README.md"])
        assert any("README.md" in e for e in errors)

    def test_no_placeholder_no_error(self):
        errors = self.bot._collect_errors([], [], placeholder_matches=[])
        assert not any("Placeholder" in e for e in errors)

    def test_no_missing_structure_no_error(self):
        errors = self.bot._collect_errors([], [], missing_structure=[])
        assert not any("missing" in e.lower() for e in errors)

    def test_combined_errors_reported(self):
        pm = PlaceholderMatch(path="x.py", line_number=1, line_text="TODO", pattern=r"\bTODO\b")
        errors = self.bot._collect_errors(
            [],
            [],
            placeholder_matches=[pm],
            missing_structure=["bots"],
        )
        assert len(errors) == 2


# ---------------------------------------------------------------------------
# Report includes placeholder and structure sections
# ---------------------------------------------------------------------------


class TestBuildReportExtended:
    def test_report_shows_placeholder_section(self):
        bot = PRValidationBot()
        pm = PlaceholderMatch(path="bot.py", line_number=3, line_text="# TODO", pattern=r"\bTODO\b")
        result = ValidationResult(
            passed=False,
            critical_files_ok=True,
            placeholder_matches=[pm],
        )
        md = bot._build_report(result)
        assert "Placeholder Code Detected" in md
        assert "bot.py" in md

    def test_report_shows_structure_section(self):
        bot = PRValidationBot()
        result = ValidationResult(
            passed=False,
            critical_files_ok=True,
            missing_structure=["bots", "tests"],
        )
        md = bot._build_report(result)
        assert "Missing Expected Repository Items" in md
        assert "bots" in md
        assert "tests" in md

    def test_report_no_placeholder_section_when_clean(self):
        bot = PRValidationBot()
        result = ValidationResult(passed=True, critical_files_ok=True)
        md = bot._build_report(result)
        assert "Placeholder Code Detected" not in md

    def test_report_no_structure_section_when_complete(self):
        bot = PRValidationBot()
        result = ValidationResult(passed=True, critical_files_ok=True)
        md = bot._build_report(result)
        assert "Missing Expected Repository Items" not in md

    def test_report_placeholder_status_in_header(self):
        bot = PRValidationBot()
        pm = PlaceholderMatch(path="a.py", line_number=1, line_text="TODO", pattern="TODO")
        result = ValidationResult(
            passed=False, critical_files_ok=True, placeholder_matches=[pm]
        )
        md = bot._build_report(result)
        assert "1 occurrence" in md

    def test_report_placeholder_none_found_in_header(self):
        bot = PRValidationBot()
        result = ValidationResult(passed=True, critical_files_ok=True)
        md = bot._build_report(result)
        assert "None found" in md


# ---------------------------------------------------------------------------
# ValidationResult dataclass — new fields
# ---------------------------------------------------------------------------


class TestValidationResultExtended:
    def test_default_placeholder_matches_empty(self):
        r = ValidationResult(passed=True, critical_files_ok=True)
        assert r.placeholder_matches == []

    def test_default_missing_structure_empty(self):
        r = ValidationResult(passed=True, critical_files_ok=True)
        assert r.missing_structure == []

    def test_placeholder_matches_stored(self):
        pm = PlaceholderMatch(path="a.py", line_number=1, line_text="TODO", pattern="TODO")
        r = ValidationResult(passed=False, critical_files_ok=True, placeholder_matches=[pm])
        assert len(r.placeholder_matches) == 1

    def test_missing_structure_stored(self):
        r = ValidationResult(passed=False, critical_files_ok=True, missing_structure=["bots"])
        assert "bots" in r.missing_structure
