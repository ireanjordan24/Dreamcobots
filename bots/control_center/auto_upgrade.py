"""
DreamCo Control Tower — Auto-Upgrade Engine

Runs scheduled upgrade operations across all registered bots:
  1. Pull latest code from origin/main
  2. Run optional smoke tests
  3. Create auto-upgrade pull requests for tracked repos
  4. Log results in the Bot Registry

Usage (one-shot)
----------------
    python -m bots.control_tower.auto_upgrade

Usage (programmatic)
--------------------
    from bots.control_tower.auto_upgrade import AutoUpgradeEngine

    engine = AutoUpgradeEngine(registry=my_registry, github=my_gh)
    results = engine.run_all()
    print(results)

# GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import importlib
import os
import sys
from datetime import datetime, timezone
from typing import Any, Optional

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration")
)
from bots.control_center.bot_registry import BotRegistry
from bots.control_center.github_integration import GitHubIntegration
from framework import GlobalAISourcesFlow  # noqa: F401


class AutoUpgradeEngine:
    """Orchestrates upgrade operations across all registered DreamCo bots.

    Parameters
    ----------
    registry:
        :class:`BotRegistry` instance holding the list of bots to upgrade.
    github:
        :class:`GitHubIntegration` used for git operations and PR creation.
    dry_run:
        When ``True`` the engine logs what it *would* do but makes no
        git or GitHub API calls.
    """

    def __init__(
        self,
        registry: Optional[BotRegistry] = None,
        github: Optional[GitHubIntegration] = None,
        dry_run: bool = False,
    ) -> None:
        self._registry = registry or BotRegistry()
        self._github = github or GitHubIntegration()
        self._dry_run = dry_run
        self._upgrade_log: list[dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def upgrade_bot(self, bot_entry: dict) -> dict:
        """Run the upgrade flow for a single bot entry from the registry.

        Steps
        -----
        1. ``git pull --rebase origin main`` on the local repo path (if set).
        2. Create an auto-upgrade PR on the remote repo (if repo_name is set).
        3. Update the registry with the new status.

        Returns
        -------
        A result dict with ``bot_name``, ``success``, and step details.
        """
        bot_name = bot_entry.get("bot_name", "unknown")
        repo_name = bot_entry.get("repo_name", "")
        repo_path = bot_entry.get("config", {}).get("repo_path", "")
        branch = bot_entry.get("config", {}).get("branch", "auto-upgrade")

        result: dict[str, Any] = {
            "bot_name": bot_name,
            "repo_name": repo_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": self._dry_run,
            "steps": {},
        }

        # Step 1 — pull latest
        if repo_path:
            if self._dry_run:
                result["steps"]["pull"] = {"success": True, "dry_run": True}
            else:
                pull_result = self._github.pull_latest(repo_path)
                result["steps"]["pull"] = pull_result
                if not pull_result["success"]:
                    # attempt auto-merge
                    merge_result = self._github.auto_merge(repo_path)
                    result["steps"]["auto_merge"] = merge_result
        else:
            result["steps"]["pull"] = {
                "skipped": True,
                "reason": "no repo_path configured",
            }

        # Step 2 — create PR
        if repo_name:
            if self._dry_run:
                result["steps"]["pr"] = {"success": True, "dry_run": True}
            else:
                pr_result = self._github.create_pull_request(
                    repo_name=repo_name,
                    head=branch,
                    title="🤖 Auto-upgrade from DreamCo Control Tower",
                    body=(
                        "Automated upgrade triggered by the DreamCo Control Tower.\n\n"
                        f"- Bot: `{bot_name}`\n"
                        f"- Timestamp: {result['timestamp']}\n"
                        "- Source: GLOBAL AI SOURCES FLOW auto-upgrade engine"
                    ),
                )
                result["steps"]["pr"] = pr_result
        else:
            result["steps"]["pr"] = {
                "skipped": True,
                "reason": "no repo_name configured",
            }

        result["success"] = all(
            step.get("success", True) for step in result["steps"].values()
        )

        # Step 3 — update registry
        new_status = "updated" if result["success"] else "conflict_detected"
        self._registry.update_status(bot_name, new_status)

        self._upgrade_log.append(result)
        return result

    def run_all(self) -> dict:
        """Run the upgrade flow for every bot in the registry.

        Returns
        -------
        A summary dict with ``total``, ``succeeded``, ``failed``, and
        per-bot ``results``.
        """
        bots = self._registry.get_all()
        results = []
        for bot in bots:
            results.append(self.upgrade_bot(bot))

        succeeded = sum(1 for r in results if r.get("success"))
        failed = len(results) - succeeded

        summary = {
            "total": len(results),
            "succeeded": succeeded,
            "failed": failed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results,
        }
        return summary

    def test_bot(self, bot_name: str) -> dict:
        """Attempt to import and run a registered bot as a smoke test.

        Returns a result dict with ``success`` and an optional ``error``.
        """
        result: dict[str, Any] = {"bot_name": bot_name, "test": "smoke"}
        try:
            mod = importlib.import_module(f"bots.{bot_name}.{bot_name}")
            bot_cls = getattr(mod, "Bot", None)
            if bot_cls is None:
                result.update({"success": False, "error": "No Bot class found"})
            else:
                instance = bot_cls()
                run_result = instance.run() if hasattr(instance, "run") else "no run()"
                result.update({"success": True, "run_result": str(run_result)})
        except Exception as exc:
            result.update({"success": False, "error": str(exc)})
        return result

    def get_upgrade_log(self, limit: int = 100) -> list[dict]:
        """Return the most recent *limit* upgrade log entries."""
        return list(self._upgrade_log[-limit:])


__all__ = ["AutoUpgradeEngine"]
