"""
BuddyOrchestrator — Centralized operational hub for all DreamCobots bots and systems.

Buddy orchestrates:
  • Core functions     — register, run, and monitor every bot
  • Data aggregation   — collect and unify data from all active bots
  • Revenue tracking   — aggregate revenue across the bot network
  • GitHub Actions     — read-only monitoring of workflow run status
  • Scrape lifecycle   — enforce the June 22, 2026 data-scraping deadline

Design
------
BuddyOrchestrator intentionally avoids hard runtime imports of every bot
module so that it can be used even when optional bot dependencies are absent.
Bots are described via lightweight ``BotSpec`` descriptors and instantiated
lazily on demand.

Build-a-Bot marketplace support
--------------------------------
``list_catalog()`` returns every registered spec with pricing and feature
metadata so it can be rendered by the React Marketplace UI, compared
side-by-side, and sold via the billing layer.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.buddy_orchestrator import BuddyOrchestrator

    orch = BuddyOrchestrator()
    orch.register_bot("buddy_bot",    tier="PRO",        category="ai",       price_usd=49.0)
    orch.register_bot("sales_bot",    tier="ENTERPRISE", category="sales",    price_usd=99.0)

    result = orch.run_bot("buddy_bot", task="generate leads")
    summary = orch.aggregate_data()
    health  = orch.github_actions_status()
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.buddy_orchestrator.data_scrape_lifecycle import DataScrapeLifecycle

try:
    from framework import GlobalAISourcesFlow  # noqa: F401
    _FLOW_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FLOW_AVAILABLE = False


# ---------------------------------------------------------------------------
# Bot specification descriptor (lightweight, no heavy imports)
# ---------------------------------------------------------------------------

@dataclass
class BotSpec:
    """
    Describes a bot available in the DreamCobots ecosystem.

    Used by the marketplace UI for comparison, marketing, and selling.
    """

    bot_id: str
    display_name: str
    category: str
    tier: str
    description: str = ""
    price_usd: float = 0.0
    features: list[str] = field(default_factory=list)
    module_path: str = ""
    is_live: bool = False


# ---------------------------------------------------------------------------
# Internal run record
# ---------------------------------------------------------------------------

@dataclass
class BotRunRecord:
    """Records the outcome of a single bot execution."""

    bot_id: str
    task: str
    result: Any
    revenue_usd: float
    ran_at: str
    success: bool


# ---------------------------------------------------------------------------
# Lightweight GitHub Actions helper (no external deps required)
# ---------------------------------------------------------------------------

def _fetch_workflow_runs(
    repo: str,
    token: Optional[str] = None,
    per_page: int = 10,
) -> list[dict]:
    """
    Fetch recent GitHub Actions workflow runs for *repo*.

    Falls back gracefully to an empty list when the ``requests`` library
    is unavailable or the API call fails.
    """
    try:
        import requests as _req
    except ImportError:
        return []

    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = _req.get(
            f"https://api.github.com/repos/{repo}/actions/runs",
            headers=headers,
            params={"per_page": min(100, max(1, per_page))},
            timeout=5,
        )
        if resp.status_code == 200:
            return [
                {
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "status": r.get("status"),
                    "conclusion": r.get("conclusion"),
                    "branch": r.get("head_branch"),
                    "event": r.get("event"),
                    "run_started_at": r.get("run_started_at"),
                    "url": r.get("html_url"),
                }
                for r in resp.json().get("workflow_runs", [])
            ]
    except Exception:  # noqa: BLE001
        pass
    return []


# ---------------------------------------------------------------------------
# BuddyOrchestrator
# ---------------------------------------------------------------------------

class OrchestratorError(Exception):
    """Raised when an orchestration operation cannot be completed."""


class BuddyOrchestrator:
    """
    Central operational hub — integrates every bot and system.

    Parameters
    ----------
    github_repo : str
        ``owner/repo`` slug for GitHub Actions monitoring.
    github_token : str | None
        Optional GitHub personal access token for authenticated API calls.
    scrape_deadline : date | None
        Override the default scraping deadline (June 22, 2026).
    """

    def __init__(
        self,
        github_repo: str = "DreamCo-Technologies/Dreamcobots",
        github_token: Optional[str] = None,
        scrape_deadline=None,
    ) -> None:
        self.github_repo = github_repo
        self._github_token = github_token or os.environ.get("GITHUB_TOKEN")

        # Registered bot catalog
        self._catalog: dict[str, BotSpec] = {}

        # Run history
        self._run_history: list[BotRunRecord] = []

        # Revenue totals per bot
        self._revenue: dict[str, float] = {}

        # Aggregated data store (key → value)
        self._data_store: dict[str, Any] = {}

        # Scraping lifecycle
        self.scrape_lifecycle = (
            DataScrapeLifecycle(deadline=scrape_deadline)
            if scrape_deadline
            else DataScrapeLifecycle()
        )

    # ------------------------------------------------------------------
    # Bot registration (build-a-bot catalog)
    # ------------------------------------------------------------------

    def register_bot(
        self,
        bot_id: str,
        display_name: str = "",
        tier: str = "FREE",
        category: str = "other",
        description: str = "",
        price_usd: float = 0.0,
        features: Optional[list[str]] = None,
        module_path: str = "",
    ) -> BotSpec:
        """
        Register a bot in the centralized catalog.

        Idempotent — calling again updates the existing spec.

        Returns
        -------
        BotSpec
        """
        spec = BotSpec(
            bot_id=bot_id,
            display_name=display_name or bot_id.replace("_", " ").title(),
            category=category,
            tier=tier,
            description=description,
            price_usd=price_usd,
            features=features or [],
            module_path=module_path,
        )
        self._catalog[bot_id] = spec
        self.scrape_lifecycle.register_bot(bot_id)
        return spec

    def unregister_bot(self, bot_id: str) -> bool:
        """Remove a bot from the catalog.  Returns True if it existed."""
        if bot_id in self._catalog:
            del self._catalog[bot_id]
            return True
        return False

    def get_bot(self, bot_id: str) -> Optional[BotSpec]:
        """Return the BotSpec for *bot_id*, or None."""
        return self._catalog.get(bot_id)

    def list_catalog(self) -> list[dict]:
        """
        Return the full bot catalog as a list of dicts.

        Suitable for rendering the build-a-bot marketplace UI and driving
        comparisons, pricing pages, and sales flows.
        """
        return [
            {
                "bot_id": spec.bot_id,
                "display_name": spec.display_name,
                "category": spec.category,
                "tier": spec.tier,
                "description": spec.description,
                "price_usd": spec.price_usd,
                "features": spec.features,
                "is_live": spec.is_live,
                "module_path": spec.module_path,
            }
            for spec in self._catalog.values()
        ]

    # ------------------------------------------------------------------
    # Bot execution
    # ------------------------------------------------------------------

    def run_bot(
        self,
        bot_id: str,
        task: str = "",
        runner: Optional[Callable[[str, str], Any]] = None,
        revenue_usd: float = 0.0,
    ) -> dict:
        """
        Execute a bot task and record the result.

        Parameters
        ----------
        bot_id : str
            The identifier of the bot to run.
        task : str
            Description of the task to perform.
        runner : callable | None
            Optional ``(bot_id, task) → result`` callable.  If None, a
            stub result is generated.
        revenue_usd : float
            Revenue attributed to this run (for tracking purposes).

        Returns
        -------
        dict with keys: ``bot_id``, ``task``, ``result``, ``revenue_usd``,
        ``ran_at``, ``success``.
        """
        if bot_id not in self._catalog:
            raise OrchestratorError(f"Bot '{bot_id}' is not registered.")

        try:
            result = runner(bot_id, task) if runner else {"status": "stub_run", "task": task}
            success = True
        except Exception as exc:  # noqa: BLE001
            result = {"error": str(exc)}
            success = False

        ran_at = datetime.now(tz=timezone.utc).isoformat()
        record = BotRunRecord(
            bot_id=bot_id,
            task=task,
            result=result,
            revenue_usd=revenue_usd,
            ran_at=ran_at,
            success=success,
        )
        self._run_history.append(record)

        # Revenue tracking
        self._revenue[bot_id] = self._revenue.get(bot_id, 0.0) + revenue_usd

        # Record scrape activity
        if success:
            self.scrape_lifecycle.record_scrape(bot_id)

        return {
            "bot_id": bot_id,
            "task": task,
            "result": result,
            "revenue_usd": revenue_usd,
            "ran_at": ran_at,
            "success": success,
        }

    def run_all(self, runner: Optional[Callable[[str, str], Any]] = None) -> list[dict]:
        """Run every registered bot with no specific task.  Returns a list of results."""
        return [self.run_bot(bot_id, runner=runner) for bot_id in list(self._catalog)]

    # ------------------------------------------------------------------
    # Data aggregation
    # ------------------------------------------------------------------

    def ingest(self, key: str, value: Any) -> None:
        """Store an arbitrary data point in the central data store."""
        self._data_store[key] = value

    def aggregate_data(self) -> dict:
        """
        Return a unified data snapshot across all systems.

        Includes:
          - Bot catalog size and live count
          - Run history summary
          - Revenue totals
          - Scraping lifecycle status
          - Arbitrary ingested data
        """
        total_runs = len(self._run_history)
        successful_runs = sum(1 for r in self._run_history if r.success)
        total_revenue = sum(self._revenue.values())
        live_bots = sum(1 for s in self._catalog.values() if s.is_live)

        return {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "bots": {
                "registered": len(self._catalog),
                "live": live_bots,
            },
            "runs": {
                "total": total_runs,
                "successful": successful_runs,
                "failed": total_runs - successful_runs,
            },
            "revenue": {
                "total_usd": round(total_revenue, 2),
                "by_bot": {k: round(v, 2) for k, v in self._revenue.items()},
            },
            "scraping": self.scrape_lifecycle.summary(),
            "data_store": dict(self._data_store),
        }

    # ------------------------------------------------------------------
    # Revenue optimisation
    # ------------------------------------------------------------------

    def top_revenue_bots(self, n: int = 5) -> list[dict]:
        """Return the *n* bots with the highest total revenue, descending."""
        ranked = sorted(self._revenue.items(), key=lambda kv: kv[1], reverse=True)
        return [
            {"bot_id": bot_id, "revenue_usd": round(rev, 2)}
            for bot_id, rev in ranked[:n]
        ]

    def optimise_revenue(self) -> dict:
        """
        Analyse revenue data and return actionable optimisation suggestions.

        Returns
        -------
        dict with keys: ``top_bots``, ``suggestions``, ``total_revenue_usd``.
        """
        top = self.top_revenue_bots()
        total = round(sum(self._revenue.values()), 2)
        zero_revenue = [bid for bid, rev in self._revenue.items() if rev == 0]
        inactive = [bid for bid, spec in self._catalog.items() if not spec.is_live]

        suggestions = []
        if top:
            suggestions.append(
                f"Double down on '{top[0]['bot_id']}' — highest revenue generator."
            )
        if zero_revenue:
            suggestions.append(
                f"{len(zero_revenue)} bot(s) have zero revenue — review their configurations."
            )
        if inactive:
            suggestions.append(
                f"{len(inactive)} bot(s) are not live — deploy them to start earning."
            )
        if not suggestions:
            suggestions.append("All bots are performing well — consider adding new bots.")

        return {
            "total_revenue_usd": total,
            "top_bots": top,
            "suggestions": suggestions,
        }

    # ------------------------------------------------------------------
    # GitHub Actions monitoring
    # ------------------------------------------------------------------

    def github_actions_status(self, per_page: int = 10) -> dict:
        """
        Return recent GitHub Actions workflow runs for the configured repo.

        Read-only — never triggers or modifies any workflow.

        Returns
        -------
        dict with keys: ``repo``, ``runs`` (list), ``source``.
        """
        runs = _fetch_workflow_runs(
            repo=self.github_repo,
            token=self._github_token,
            per_page=per_page,
        )
        source = "github_api" if runs else "unavailable"
        return {
            "repo": self.github_repo,
            "runs": runs,
            "source": source,
            "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Activate / deactivate bots (go-live)
    # ------------------------------------------------------------------

    def go_live(self, bot_id: str) -> dict:
        """Mark a bot as live (deployed and earning)."""
        if bot_id not in self._catalog:
            raise OrchestratorError(f"Bot '{bot_id}' is not registered.")
        self._catalog[bot_id].is_live = True
        return {"bot_id": bot_id, "is_live": True}

    def deactivate(self, bot_id: str) -> dict:
        """Mark a bot as not live."""
        if bot_id not in self._catalog:
            raise OrchestratorError(f"Bot '{bot_id}' is not registered.")
        self._catalog[bot_id].is_live = False
        return {"bot_id": bot_id, "is_live": False}

    # ------------------------------------------------------------------
    # Status snapshot
    # ------------------------------------------------------------------

    def status(self) -> dict:
        """Return a high-level orchestrator health snapshot."""
        return {
            "orchestrator": "BuddyOrchestrator",
            "github_repo": self.github_repo,
            "catalog_size": len(self._catalog),
            "scraping_active": self.scrape_lifecycle.scraping_active(),
            "scrape_deadline": self.scrape_lifecycle.deadline_iso(),
            "days_until_deadline": self.scrape_lifecycle.days_remaining(),
            "total_runs": len(self._run_history),
            "total_revenue_usd": round(sum(self._revenue.values()), 2),
        }
