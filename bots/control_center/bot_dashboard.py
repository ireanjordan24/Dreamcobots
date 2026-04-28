"""
Dreamcobots Bot Dashboard
=========================
Command-line dashboard that scans all bot directories, reports health status,
detects duplicates, and integrates with the ControlCenter / BotRegistry.

Usage:
    python bots/control_center/bot_dashboard.py [--json] [--category CATEGORY]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

# Allow running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

BOT_ROOTS = [
    "bots",
    "Business_bots",
    "App_bots",
    "Occupational_bots",
    "Marketing_bots",
    "Real_Estate_bots",
    "Side_Hustle_bots",
    "Fiverr_bots",
    "Government_Contract_bots",
]

_STUB_RE = re.compile(
    r"raise\s+NotImplementedError|#\s*TODO|#\s*FIXME|#\s*STUB|#\s*PLACEHOLDER",
    re.IGNORECASE,
)


# ─────────────────────────────────────────────────────────────────────────────
# Bot scanning helpers
# ─────────────────────────────────────────────────────────────────────────────


def scan_bot(bot_path: str) -> dict:
    """Return health metadata for a single bot directory."""
    py_files = [f for f in os.listdir(bot_path) if f.endswith(".py")]
    has_run = False
    has_stub = False
    syntax_errors: list[str] = []

    for fname in py_files:
        fpath = os.path.join(bot_path, fname)
        try:
            source = open(fpath, encoding="utf-8", errors="replace").read()
        except OSError as exc:
            syntax_errors.append(f"{fname}: {exc}")
            continue

        try:
            compile(source, fpath, "exec")
        except SyntaxError as exc:
            syntax_errors.append(f"{fname}: SyntaxError at line {exc.lineno}")

        if re.search(r"def run\(", source):
            has_run = True
        if _STUB_RE.search(source):
            has_stub = True

    if syntax_errors:
        status = "error"
    elif not has_run:
        status = "stub"
    elif has_stub:
        status = "partial"
    else:
        status = "ok"

    return {
        "path": bot_path,
        "name": os.path.basename(bot_path),
        "category": os.path.dirname(bot_path),
        "py_files": len(py_files),
        "has_run_method": has_run,
        "has_stub_patterns": has_stub,
        "syntax_errors": syntax_errors,
        "status": status,
    }


def scan_all_bots(category_filter: str = "") -> list[dict]:
    """Scan all bot roots and return a list of bot health records."""
    results: list[dict] = []
    for root in BOT_ROOTS:
        if category_filter and root != category_filter:
            continue
        if not os.path.isdir(root):
            continue
        for entry in sorted(os.listdir(root)):
            bot_path = os.path.join(root, entry)
            if not os.path.isdir(bot_path):
                continue
            py_files = [f for f in os.listdir(bot_path) if f.endswith(".py")]
            if not py_files:
                continue
            results.append(scan_bot(bot_path))
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Duplicate detection
# ─────────────────────────────────────────────────────────────────────────────


def _bot_fingerprint(bot_path: str) -> str:
    """Content fingerprint for a bot directory (normalised Python source)."""
    chunks: list[str] = []
    for fname in sorted(os.listdir(bot_path)):
        if not fname.endswith(".py"):
            continue
        fpath = os.path.join(bot_path, fname)
        try:
            source = open(fpath, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        source = re.sub(r'""".*?"""', "", source, flags=re.DOTALL)
        source = re.sub(r"'''.*?'''", "", source, flags=re.DOTALL)
        source = re.sub(r"#.*", "", source)
        source = "\n".join(ln.strip() for ln in source.splitlines() if ln.strip())
        chunks.append(source)
    return "\n".join(chunks)


def find_duplicate_bots(bots: list[dict], threshold: float = 0.80) -> list[dict]:
    """Return pairs of bots whose content similarity exceeds *threshold*."""
    import difflib

    duplicates: list[dict] = []
    fps = [(b, _bot_fingerprint(b["path"])) for b in bots]

    for i, (a, fp_a) in enumerate(fps):
        for j, (b, fp_b) in enumerate(fps):
            if j <= i or not fp_a or not fp_b:
                continue
            ratio = difflib.SequenceMatcher(None, fp_a, fp_b).quick_ratio()
            if ratio >= threshold:
                duplicates.append({
                    "bot_a": a["path"],
                    "bot_b": b["path"],
                    "similarity_pct": round(ratio * 100, 1),
                })
    return duplicates


def find_duplicate_workflows(wf_dir: str = ".github/workflows") -> dict:
    """Return duplicate workflow names and identical-content groups."""
    if not os.path.isdir(wf_dir):
        return {"name_duplicates": {}, "content_duplicates": {}}

    name_map: dict[str, list[str]] = {}
    hash_map: dict[str, list[str]] = {}

    for fname in sorted(os.listdir(wf_dir)):
        if not fname.endswith((".yml", ".yaml")):
            continue
        fpath = os.path.join(wf_dir, fname)
        content = open(fpath, encoding="utf-8", errors="replace").read()

        m = re.search(r"^name:\s*(.+)", content, re.MULTILINE)
        wf_name = m.group(1).strip() if m else "(unnamed)"
        name_map.setdefault(wf_name, []).append(fname)

        lines = [ln for ln in content.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        digest = hashlib.sha256("\n".join(lines).encode()).hexdigest()[:12]
        hash_map.setdefault(digest, []).append(fname)

    return {
        "name_duplicates": {n: fs for n, fs in name_map.items() if len(fs) > 1},
        "content_duplicates": {h: fs for h, fs in hash_map.items() if len(fs) > 1},
    }


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard rendering
# ─────────────────────────────────────────────────────────────────────────────


def _status_icon(status: str) -> str:
    return {"ok": "✅", "stub": "⚠️", "partial": "⚠️", "error": "❌"}.get(status, "❓")


def render_text_dashboard(bots: list[dict], workflow_dups: dict) -> None:
    """Print a human-readable dashboard to stdout."""
    total = len(bots)
    ok    = sum(1 for b in bots if b["status"] == "ok")
    stub  = sum(1 for b in bots if b["status"] in ("stub", "partial"))
    err   = sum(1 for b in bots if b["status"] == "error")
    ts    = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    print("=" * 65)
    print("  🤖  Dreamcobots Bot Dashboard")
    print(f"  Generated: {ts}")
    print("=" * 65)
    print(f"  Total bots   : {total}")
    print(f"  ✅ Healthy   : {ok}")
    print(f"  ⚠️  Stub/partial: {stub}")
    print(f"  ❌ Error     : {err}")
    print("-" * 65)

    # Per-category summary
    categories: dict[str, list[dict]] = {}
    for b in bots:
        categories.setdefault(b["category"], []).append(b)

    print("  Category breakdown:")
    for cat, cat_bots in sorted(categories.items()):
        c_ok   = sum(1 for b in cat_bots if b["status"] == "ok")
        c_stub = sum(1 for b in cat_bots if b["status"] in ("stub", "partial"))
        c_err  = sum(1 for b in cat_bots if b["status"] == "error")
        print(f"    {cat:<35} {len(cat_bots):>3} total  {c_ok} ok  {c_stub} stub  {c_err} err")

    print("-" * 65)

    # Problem bots
    problem_bots = [b for b in bots if b["status"] != "ok"]
    if problem_bots:
        print(f"  ⚠️  Problem bots ({len(problem_bots)}):")
        for b in problem_bots[:20]:
            icon = _status_icon(b["status"])
            errs = f" — errors: {', '.join(b['syntax_errors'][:1])}" if b["syntax_errors"] else ""
            print(f"    {icon} {b['path']}{errs}")
        if len(problem_bots) > 20:
            print(f"    … and {len(problem_bots) - 20} more")
        print("-" * 65)

    # Workflow duplicates
    name_dups = workflow_dups.get("name_duplicates", {})
    cont_dups = workflow_dups.get("content_duplicates", {})
    if name_dups or cont_dups:
        print(f"  🔁 Workflow duplicates:")
        for name, files in name_dups.items():
            print(f"    Name '{name}': {', '.join(files)}")
        for h, files in cont_dups.items():
            print(f"    Identical content ({h}): {', '.join(files)}")
        print("-" * 65)

    print("  ✅ Dashboard complete.")
    print("=" * 65)


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dreamcobots Bot Dashboard")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
    parser.add_argument("--category", default="", help="Filter by bot category (e.g. Business_bots)")
    parser.add_argument(
        "--threshold", type=float, default=0.80,
        help="Duplicate similarity threshold (0.0–1.0, default 0.80)",
    )
    args = parser.parse_args(argv)

    bots = scan_all_bots(category_filter=args.category)
    workflow_dups = find_duplicate_workflows()
    bot_dups = find_duplicate_bots(bots, threshold=args.threshold)

    if args.json:
        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "bots": bots,
            "duplicate_bots": bot_dups,
            "duplicate_workflows": workflow_dups,
            "summary": {
                "total_bots": len(bots),
                "ok": sum(1 for b in bots if b["status"] == "ok"),
                "stub": sum(1 for b in bots if b["status"] in ("stub", "partial")),
                "error": sum(1 for b in bots if b["status"] == "error"),
                "duplicate_bot_pairs": len(bot_dups),
                "duplicate_workflow_names": len(workflow_dups.get("name_duplicates", {})),
                "duplicate_workflow_content": len(workflow_dups.get("content_duplicates", {})),
            },
        }
        print(json.dumps(output, indent=2))
    else:
        render_text_dashboard(bots, workflow_dups)

    return 0


if __name__ == "__main__":
    sys.exit(main())
