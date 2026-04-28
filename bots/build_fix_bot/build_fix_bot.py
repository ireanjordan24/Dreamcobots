"""
BuildFixBot — CI Missing-File Detective
=========================================
A lightweight CLI tool that parses CI/CD log output (from a file or stdin)
and detects common "missing file" error patterns.

Supported error signatures
--------------------------
- ``ENOENT: no such file or directory, open '...'``  (Node.js)
- ``ModuleNotFoundError: No module named '...'``      (Python)
- ``Cannot find module '...'``                         (Node.js)
- ``cannot find file '...'``                           (TypeScript / tsc)
- ``error: cannot open source file "..."``             (C/C++)
- ``FileNotFoundError: [Errno 2] No such file ...``   (Python)
- ``ImportError: cannot import name '...' from '...'`` (Python)
- ``No such file or directory``                        (shell / make)

Usage
-----
    # parse a saved log file
    python bots/build_fix_bot/build_fix_bot.py --log ci.log

    # pipe from stdin
    cat ci.log | python bots/build_fix_bot/build_fix_bot.py

    # emit JSON output
    python bots/build_fix_bot/build_fix_bot.py --log ci.log --json

Extending
---------
Add new patterns to the ``_PATTERNS`` list at the top of this file.
Each entry is a ``(pattern, description)`` tuple.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Error patterns
# ---------------------------------------------------------------------------

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"ENOENT[^'\"]*['\"]([^'\"]+)['\"]"), "Node.js — file not found (ENOENT)"),
    (re.compile(r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]"), "Python — missing module"),
    (re.compile(r"Cannot find module ['\"]([^'\"]+)['\"]"), "Node.js — missing module"),
    (re.compile(r"cannot find file ['\"]([^'\"]+)['\"]", re.IGNORECASE), "TypeScript — missing file"),
    (re.compile(r"error: cannot open source file \"([^\"]+)\""), "C/C++ — missing source file"),
    (re.compile(r"FileNotFoundError:.*?['\"]([^'\"]+)['\"]"), "Python — FileNotFoundError"),
    (re.compile(r"ImportError: cannot import name ['\"]([^'\"]+)['\"] from ['\"]([^'\"]+)['\"]"), "Python — bad import"),
    (re.compile(r"No such file or directory.*?['\"]([^'\"]+)['\"]"), "Shell — no such file or directory"),
    (re.compile(r"error TS2307: Cannot find module ['\"]([^'\"]+)['\"]"), "TypeScript — missing module (TS2307)"),
    (re.compile(r"open\s+['\"]([^'\"]+)['\"]:\s+no such file"), "Go — file not found"),
]


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    line_number: int
    raw_line: str
    pattern_description: str
    missing_path: str
    suggested_action: str

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Core bot logic
# ---------------------------------------------------------------------------

class BuildFixBot:
    """Parse CI log lines and return structured findings."""

    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def _suggest(self, pattern_desc: str, missing_path: str) -> str:
        if "module" in pattern_desc.lower():
            return (
                f"Add '{missing_path}' to the project (create the file or install"
                f" the package).  For Python: `pip install {missing_path}` or"
                f" create the module.  For Node.js: `npm install {missing_path}`."
            )
        return (
            f"Create the missing file/directory: '{missing_path}'.  "
            f"If it was intentionally removed, update any references to it."
        )

    def parse_lines(self, lines: list[str]) -> list[Finding]:
        self.findings = []
        for lineno, raw in enumerate(lines, start=1):
            for pattern, description in _PATTERNS:
                m = pattern.search(raw)
                if m:
                    # Use the first capture group as the missing path
                    missing = m.group(1)
                    finding = Finding(
                        line_number=lineno,
                        raw_line=raw.rstrip(),
                        pattern_description=description,
                        missing_path=missing,
                        suggested_action=self._suggest(description, missing),
                    )
                    self.findings.append(finding)
                    break  # one finding per log line
        return self.findings

    def parse_text(self, text: str) -> list[Finding]:
        return self.parse_lines(text.splitlines())

    def summary(self) -> str:
        if not self.findings:
            return "✅ No missing-file errors detected in the log."
        lines = [f"❌ {len(self.findings)} missing-file issue(s) detected:\n"]
        for f in self.findings:
            lines.append(f"  Line {f.line_number}: [{f.pattern_description}]")
            lines.append(f"    Missing : {f.missing_path}")
            lines.append(f"    Action  : {f.suggested_action}")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        help="Path to CI log file.  Reads from stdin if not provided.",
    )
    parser.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Output findings as JSON instead of human-readable text.",
    )
    args = parser.parse_args(argv)

    if args.log:
        text = args.log.read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()

    bot = BuildFixBot()
    findings = bot.parse_text(text)

    if args.output_json:
        print(json.dumps([f.to_dict() for f in findings], indent=2))
    else:
        print(bot.summary())

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
