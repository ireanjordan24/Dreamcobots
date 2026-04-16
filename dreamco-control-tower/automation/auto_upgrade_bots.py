"""
DreamCo Control Tower — Auto-Upgrade Automation Script
========================================================
Entry-point automation script that wires together the full Control Tower
upgrade pipeline:

  1. Load bots and repos from config.
  2. Sync each repo with GitHub (fetch PR counts, issue counts, workflow status).
  3. Run the auto-upgrader on every registered bot.
  4. Print a summary report.

Usage
-----
    python automation/auto_upgrade_bots.py

Environment Variables
---------------------
    GITHUB_TOKEN   — Personal access token (required for GitHub API calls).
    REPO_ROOT      — Filesystem root of the cloned Dreamcobots repo
                     (defaults to the parent of this script's directory).
    RUN_TESTS      — Set to ``"0"`` to skip test execution.
    DRY_RUN        — Set to ``"1"`` to skip git and PR operations.
"""

from __future__ import annotations

import os
import sys

# Make sibling modules importable when run as a script
_BACKEND = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, _BACKEND)

from auto_upgrader import AutoUpgrader
from bot_manager import BotManager
from repo_manager import GitHubClient, RepoManager


def main() -> None:
    """Run the full auto-upgrade pipeline."""
    # ------------------------------------------------------------------ config
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    bots_config = os.path.join(config_dir, "bots.json")
    repos_config = os.path.join(config_dir, "repos.json")

    repo_root = os.environ.get(
        "REPO_ROOT", os.path.join(os.path.dirname(__file__), "..", "..")
    )
    run_tests = os.environ.get("RUN_TESTS", "1") != "0"
    dry_run = os.environ.get("DRY_RUN", "0") == "1"

    print("=" * 60)
    print("DreamCo Control Tower — Auto-Upgrade Pipeline")
    print("=" * 60)
    print(f"  Repo root : {repo_root}")
    print(f"  Run tests : {run_tests}")
    print(f"  Dry run   : {dry_run}")
    print()

    # ----------------------------------------------------------------- managers
    bm = BotManager(config_path=bots_config)
    client = GitHubClient()
    rm = RepoManager(config_path=repos_config, github_client=client)

    print(f"Registered bots  : {bm.total_bots()}")
    print(f"Monitored repos  : {len(rm.list_repos())}")
    print()

    # ------------------------------------------------------------------ sync repos
    print("Syncing repositories with GitHub…")
    sync_results = rm.sync_all()
    for name, result in sync_results.items():
        if "error" in result:
            print(f"  ⚠️  {name}: {result['error']}")
        else:
            prs = result.get("openPRs", "?")
            issues = result.get("openIssues", "?")
            print(f"  ✅  {name}: {prs} open PRs, {issues} open issues")
    print()

    # ----------------------------------------------------------------- upgrade bots
    if dry_run:
        print("DRY RUN — skipping git pull / PR creation.")
        bots = bm.list_bots()
        for bot in bots:
            print(f"  🤖  Would upgrade: {bot['name']} ({bot.get('repoPath', '?')})")
        print()
        print("Dry-run complete.  No changes were made.")
        return

    upgrader = AutoUpgrader(
        bot_manager=bm,
        repo_manager=rm,
        repo_root=repo_root,
        run_tests=run_tests,
    )

    print("Running auto-upgrade on all bots…")
    results = upgrader.upgrade_all()

    ok = 0
    resolved = 0
    errors = 0
    for name, result in results.items():
        status = result.get("status", "error")
        if status == "ok":
            ok += 1
            print(f"  ✅  {name}: updated successfully")
        elif status == "conflict_resolved":
            resolved += 1
            print(f"  🔧  {name}: conflict auto-resolved")
        else:
            errors += 1
            detail = result.get("detail") or result.get("pull", {}).get("stderr", "")
            print(f"  ❌  {name}: error — {detail[:80] if detail else 'unknown'}")
    print()

    # ------------------------------------------------------------------- summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Bots upgraded      : {ok}")
    print(f"  Conflicts resolved : {resolved}")
    print(f"  Errors             : {errors}")
    print()
    print("Upgrade pipeline complete.")


if __name__ == "__main__":
    main()
