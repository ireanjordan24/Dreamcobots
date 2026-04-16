#!/usr/bin/env python3
"""
DreamCo Bot Scanner
===================
Scans every bot directory under bots/, classifies each one, attempts a
smoke-import, and writes results to stdout as JSON.

Classification legend
---------------------
  coded       — 2+ Python source files (fully implemented)
  minimal     — exactly 1 Python source file (starter/stub)
  placeholder — no Python files found (directory only / docs only)

Smoke-test result
-----------------
  ok          — module imported without exception
  import_err  — ImportError / ModuleNotFoundError during import
  runtime_err — other exception during import
  skipped     — no main module file to import

Usage
-----
  python3 tools/bot_scanner.py [--json] [--summary]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import traceback
from dataclasses import asdict, dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOTS_DIR  = os.path.join(REPO_ROOT, "bots")
TESTS_DIR = os.path.join(REPO_ROOT, "tests")

# Prefer these filenames when looking for the main bot module
MAIN_FILE_CANDIDATES = [
    # pattern: {slug}.py  (slug = dir name with hyphens→underscores)
    "{slug}.py",
    "{slug}_bot.py",
    "bot.py",
    "main.py",
]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class BotRecord:
    dir_name:    str
    display_name: str
    py_files:    int
    main_file:   Optional[str]
    has_test:    bool
    coding_status: str       # coded / minimal / placeholder
    smoke_result:  str       # ok / import_err / runtime_err / skipped
    smoke_error:   str       # error message if smoke_result != ok
    category:    str         # inferred from dir name
    tags:        list[str] = field(default_factory=list)

    @property
    def icon(self) -> str:
        if self.coding_status == "placeholder":
            return "🔲"
        if self.smoke_result == "ok":
            return "✅"
        if self.smoke_result in ("import_err", "runtime_err"):
            return "❌"
        # skipped / minimal / coded-not-tested
        if self.coding_status == "minimal":
            return "⚠️"
        return "📦"

    @property
    def status_label(self) -> str:
        if self.coding_status == "placeholder":
            return "Placeholder"
        if self.smoke_result == "ok":
            return "Runs Smooth"
        if self.smoke_result in ("import_err", "runtime_err"):
            return "Has Bugs"
        if self.coding_status == "minimal":
            return "Minimal / Stub"
        return "Coded"

    @property
    def test_badge(self) -> str:
        return "🧪 Yes" if self.has_test else "—"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _infer_category(dir_name: str) -> str:
    name = dir_name.lower()
    mapping = {
        "real_estate": "Real Estate",
        "home_buyer": "Real Estate",
        "home_flip": "Real Estate",
        "foreclosure": "Real Estate",
        "rental": "Real Estate",
        "dream_real": "Real Estate",
        "finance": "Finance",
        "financial": "Finance",
        "wealth": "Finance",
        "money": "Finance",
        "stock": "Finance",
        "crypto": "Crypto / Trading",
        "mining": "Crypto / Trading",
        "quantum_hedge": "Crypto / Trading",
        "lead": "Lead Gen",
        "outreach": "Lead Gen",
        "buyer_network": "Lead Gen",
        "crm": "Lead Gen",
        "public_lead": "Lead Gen",
        "multi_source": "Lead Gen",
        "buddy": "AI Companion",
        "emotional": "AI Companion",
        "god": "God Mode / Power AI",
        "big_bro": "God Mode / Power AI",
        "bot_generator": "Dev Tools",
        "code": "Dev Tools",
        "ci_auto": "Dev Tools",
        "devops": "Dev Tools",
        "auto_scaler": "Dev Tools",
        "software": "Dev Tools",
        "api_kit": "Dev Tools",
        "repo": "Dev Tools",
        "app_builder": "Dev Tools",
        "bot_wars": "Dev Tools",
        "saas": "SaaS / Business",
        "business": "SaaS / Business",
        "entrepreneur": "SaaS / Business",
        "revenue": "SaaS / Business",
        "profit": "SaaS / Business",
        "shopify": "SaaS / Business",
        "marketing": "Marketing",
        "advertising": "Marketing",
        "social_media": "Marketing",
        "influencer": "Marketing",
        "email_campaign": "Marketing",
        "ad_copy": "Marketing",
        "affiliate": "Marketing",
        "multi_channel": "Marketing",
        "commercial": "Marketing",
        "cinecore": "Video / Media",
        "creative_studio": "Video / Media",
        "ai_writing": "Content Creation",
        "education": "Education",
        "ai_level_up": "Education",
        "ai_learning": "Education",
        "financial_literacy": "Education",
        "government": "Government",
        "211": "Government",
        "lawsuit": "Legal / Government",
        "legal": "Legal / Government",
        "health": "Health",
        "medical": "Health",
        "biomedical": "Health",
        "farewell": "Health",
        "job": "Jobs / HR",
        "resume": "Jobs / HR",
        "hr": "Jobs / HR",
        "selenium_job": "Jobs / HR",
        "lifestyle": "Lifestyle",
        "hustle": "Side Hustle",
        "car_flip": "Side Hustle",
        "deal_finder": "Side Hustle",
        "discount": "Side Hustle",
        "stack_and_profit": "Side Hustle",
        "alidropship": "Side Hustle",
        "fiverr": "Freelance",
        "referral": "Referral / Growth",
        "stripe": "Payments",
        "dreamco_payments": "Payments",
        "token_billing": "Payments",
        "dreamco_empire": "Payments",
    }
    for key, cat in mapping.items():
        if key in name:
            return cat
    return "General"


def _find_main_file(py_files: list[str], slug: str) -> Optional[str]:
    for pattern in MAIN_FILE_CANDIDATES:
        candidate = pattern.replace("{slug}", slug)
        if candidate in py_files:
            return candidate
    return py_files[0] if py_files else None


def _smoke_test(bot_dir: str, main_file: str) -> tuple[str, str]:
    """Try to import main_file from bot_dir. Returns (result, error_msg)."""
    module_path = os.path.join(bot_dir, main_file)
    if not os.path.isfile(module_path):
        return "skipped", ""
    try:
        spec = importlib.util.spec_from_file_location("_smoke_module", module_path)
        if spec is None:
            return "skipped", "no spec"
        mod = importlib.util.module_from_spec(spec)
        # Temporarily add bot dir and repo root to sys.path
        saved = sys.path[:]
        sys.path.insert(0, REPO_ROOT)
        sys.path.insert(0, bot_dir)
        try:
            spec.loader.exec_module(mod)
        finally:
            sys.path = saved
        return "ok", ""
    except (ImportError, ModuleNotFoundError) as exc:
        return "import_err", str(exc)
    except Exception as exc:
        return "runtime_err", str(exc)


# ---------------------------------------------------------------------------
# Main scanner
# ---------------------------------------------------------------------------

def scan_bots(run_smoke: bool = True) -> list[BotRecord]:
    test_file_names = set(os.listdir(TESTS_DIR)) if os.path.isdir(TESTS_DIR) else set()

    records: list[BotRecord] = []
    for entry in sorted(os.listdir(BOTS_DIR)):
        full_path = os.path.join(BOTS_DIR, entry)
        if not os.path.isdir(full_path):
            continue

        all_files = os.listdir(full_path)
        py_files  = [f for f in all_files if f.endswith(".py") and not f.startswith("__")]
        slug      = entry.replace("-", "_").lower()

        # Coding status
        if not py_files:
            coding_status = "placeholder"
        elif len(py_files) == 1:
            coding_status = "minimal"
        else:
            coding_status = "coded"

        # Main file
        main_file = _find_main_file(py_files, slug)

        # Has test
        has_test = (
            f"test_{slug}.py" in test_file_names
            or f"test_{entry}.py" in test_file_names
        )

        # Smoke test
        if run_smoke and main_file:
            smoke_result, smoke_error = _smoke_test(full_path, main_file)
        elif not main_file:
            smoke_result, smoke_error = "skipped", "no python files"
        else:
            smoke_result, smoke_error = "skipped", ""

        # Display name
        display_name = entry.replace("_", " ").replace("-", " ").title()

        records.append(BotRecord(
            dir_name=entry,
            display_name=display_name,
            py_files=len(py_files),
            main_file=main_file,
            has_test=has_test,
            coding_status=coding_status,
            smoke_result=smoke_result,
            smoke_error=smoke_error[:200] if smoke_error else "",
            category=_infer_category(entry),
        ))

    return records


# ---------------------------------------------------------------------------
# Reporters
# ---------------------------------------------------------------------------

def print_json(records: list[BotRecord]) -> None:
    data = [asdict(r) for r in records]
    # Add computed fields
    for d, r in zip(data, records):
        d["icon"] = r.icon
        d["status_label"] = r.status_label
        d["test_badge"] = r.test_badge
    print(json.dumps(data, indent=2))


def print_summary(records: list[BotRecord]) -> None:
    total       = len(records)
    smooth      = sum(1 for r in records if r.smoke_result == "ok")
    bugs        = sum(1 for r in records if r.smoke_result in ("import_err", "runtime_err"))
    minimal_ct  = sum(1 for r in records if r.coding_status == "minimal")
    placeholder = sum(1 for r in records if r.coding_status == "placeholder")
    coded       = sum(1 for r in records if r.coding_status == "coded")
    has_tests   = sum(1 for r in records if r.has_test)

    print("=" * 72)
    print("  DreamCo Bots — Status Dashboard")
    print("=" * 72)
    print(f"  Total bots scanned   : {total}")
    print(f"  ✅ Runs Smooth        : {smooth}")
    print(f"  ❌ Has Bugs           : {bugs}")
    print(f"  ⚠️  Minimal / Stub    : {minimal_ct}")
    print(f"  🔲 Placeholder        : {placeholder}")
    print(f"  🗂️  Coded (2+ files)   : {coded}")
    print(f"  🧪 Has Tests          : {has_tests}")
    print("=" * 72)
    print()

    # Group by category
    categories: dict[str, list[BotRecord]] = {}
    for r in records:
        categories.setdefault(r.category, []).append(r)

    for cat in sorted(categories):
        bots = categories[cat]
        print(f"  ── {cat} ({len(bots)}) ─────────────────────────────")
        for r in bots:
            test_mark = "🧪" if r.has_test else "  "
            err_snippet = f"  [{r.smoke_error[:60]}]" if r.smoke_error else ""
            print(f"    {r.icon} {r.display_name:<40s} {r.status_label:<20s} {test_mark}{err_snippet}")
        print()


def print_github_summary(records: list[BotRecord]) -> None:
    """Print GitHub-flavored markdown for GITHUB_STEP_SUMMARY."""
    total       = len(records)
    smooth      = sum(1 for r in records if r.smoke_result == "ok")
    bugs        = sum(1 for r in records if r.smoke_result in ("import_err", "runtime_err"))
    minimal_ct  = sum(1 for r in records if r.coding_status == "minimal")
    placeholder = sum(1 for r in records if r.coding_status == "placeholder")
    has_tests   = sum(1 for r in records if r.has_test)

    print("## 🤖 DreamCo Bot Status Dashboard\n")
    print(f"| Metric | Count |")
    print(f"|--------|-------|")
    print(f"| **Total bots** | {total} |")
    print(f"| ✅ Runs Smooth | {smooth} |")
    print(f"| ❌ Has Bugs (import/runtime error) | {bugs} |")
    print(f"| ⚠️ Minimal / Stub (1 file) | {minimal_ct} |")
    print(f"| 🔲 Placeholder (no code) | {placeholder} |")
    print(f"| 🧪 Has Unit Tests | {has_tests} |")
    print()

    # Group by category
    categories: dict[str, list[BotRecord]] = {}
    for r in records:
        categories.setdefault(r.category, []).append(r)

    for cat in sorted(categories):
        bots = categories[cat]
        print(f"### {cat}")
        print(f"| Bot | Status | Coded | Files | Tests | Error |")
        print(f"|-----|--------|-------|-------|-------|-------|")
        for r in bots:
            err = r.smoke_error[:80].replace("|", "\\|") if r.smoke_error else ""
            print(
                f"| {r.icon} **{r.display_name}** "
                f"| {r.status_label} "
                f"| {r.coding_status} "
                f"| {r.py_files} "
                f"| {r.test_badge} "
                f"| {err} |"
            )
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="DreamCo Bot Scanner")
    parser.add_argument("--json",    action="store_true", help="Output raw JSON")
    parser.add_argument("--summary", action="store_true", help="Print human-readable summary")
    parser.add_argument("--gh-summary", action="store_true", help="Print GitHub Step Summary markdown")
    parser.add_argument("--no-smoke", action="store_true", help="Skip smoke-import tests")
    args = parser.parse_args()

    records = scan_bots(run_smoke=not args.no_smoke)

    if args.json:
        print_json(records)
    elif args.gh_summary:
        print_github_summary(records)
    else:
        print_summary(records)


if __name__ == "__main__":
    main()
