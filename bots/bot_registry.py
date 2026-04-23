"""
Bot Registry — Central catalog and health dashboard for all system bots.

Scans the bots/ directory for available bot modules, checks their run()
availability, records metadata, and exposes a machine-readable registry
that other bots and workflows can query.

Usage
-----
    python bots/bot_registry.py [--json]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_BOTS_DIR = os.path.dirname(__file__)
_ROOT = os.path.abspath(os.path.join(_BOTS_DIR, ".."))
_REGISTRY_FILE = os.path.join(_ROOT, "knowledge", "bot_registry.json")

_SKIP_FILES = {"__init__.py", "bot_base.py", "debug.py", "lead_bot.py",
               "outreach_bot.py", "real_estate_bot.py", "sales_bot.py"}

_CATEGORIES: dict[str, str] = {
    "debug_bot": "core",
    "testing_bot": "core",
    "bot_validator": "core",
    "insight_ranker": "intelligence",
    "buddy_bot": "intelligence",
    "optimizer_bot": "analytics",
    "security_auditor_bot": "analytics",
    "pr_intelligence_bot": "intelligence",
    "deployment_review_bot": "analytics",
    "code_coverage_bot": "analytics",
    "skill_generation_bot": "factory",
    "task_execution_controller": "core",
    "proactive_task_planner": "intelligence",
    "feedback_loop_bot": "intelligence",
    "adaptive_learning_bot": "intelligence",
    "performance_monitor_bot": "analytics",
    "knowledge_sync_bot": "intelligence",
    "auto_repair_bot": "core",
    "context_pruner_bot": "intelligence",
    "parallel_execution_bot": "core",
}


def _has_run_fn(path: str) -> bool:
    """Return True if the module at *path* exposes a ``run`` callable."""
    try:
        spec = importlib.util.spec_from_file_location("_probe", path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return callable(getattr(mod, "run", None))
    except Exception:
        return False


def scan() -> list[dict]:
    """Scan bots/ and return a list of registry entries."""
    entries: list[dict] = []

    try:
        files = os.listdir(_BOTS_DIR)
    except OSError:
        return entries

    for fname in sorted(files):
        if not fname.endswith(".py"):
            continue
        if fname in _SKIP_FILES or fname.startswith("_"):
            continue

        name = fname[:-3]
        path = os.path.join(_BOTS_DIR, fname)
        has_run = _has_run_fn(path)
        category = _CATEGORIES.get(name, "custom")
        doc_path = os.path.join(_ROOT, "docs", "bots", f"{name}.md")

        entries.append(
            {
                "name": name,
                "file": f"bots/{fname}",
                "category": category,
                "has_run_fn": has_run,
                "has_docs": os.path.isfile(doc_path),
                "registered_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        )

    return entries


def save_registry(entries: list[dict]) -> None:
    os.makedirs(os.path.dirname(_REGISTRY_FILE), exist_ok=True)
    with open(_REGISTRY_FILE, "w") as fh:
        json.dump(entries, fh, indent=2)


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    entries = scan()
    save_registry(entries)
    return {"total": len(entries), "entries": entries, "status": "ok"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DreamCo Bot Registry")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    registry = scan()
    save_registry(registry)

    if args.json:
        print(json.dumps(registry, indent=2))
    else:
        print(f"{'Name':<40} {'Category':<15} {'run()':<8} {'Docs'}")
        print("-" * 72)
        for e in registry:
            run_mark = "✅" if e["has_run_fn"] else "❌"
            doc_mark = "✅" if e["has_docs"] else "❌"
            print(f"{e['name']:<40} {e['category']:<15} {run_mark:<8} {doc_mark}")
        print(f"\nTotal: {len(registry)} bots registered.")
