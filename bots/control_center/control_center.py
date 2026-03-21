"""Control Center — central orchestration dashboard for all Dreamcobots."""
import sys, os
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config
from framework import GlobalAISourcesFlow  # noqa: F401


class ControlCenter:
    """Central control center for registering, monitoring, and orchestrating all bots.

    Extends the base registry with Control Tower features:
      - Heartbeat tracking per bot
      - Repository monitoring (open PRs, issues, workflow results)
      - One-click deploy coordination
      - Bot onboarding workflow
      - Conflict alerting
    """

    def __init__(self):
        self._bots: dict = {}
        self._income_log: list = []
        self._run_log: list = []
        self._repos: dict = {}
        self._heartbeat_log: list = []
        self._deploy_log: list = []

    def register_bot(self, name: str, bot_instance) -> None:
        """Register a bot instance under the given name."""
        self._bots[name] = {
            "instance": bot_instance,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "run_count": 0,
            "last_run": None,
            "status": "idle",
        }

    def get_status(self) -> dict:
        """Return status of all registered bots."""
        status = {}
        for name, meta in self._bots.items():
            bot = meta["instance"]
            tier = getattr(bot, "tier", None)
            status[name] = {
                "status": meta["status"],
                "tier": tier.value if tier else "unknown",
                "registered_at": meta["registered_at"],
                "run_count": meta["run_count"],
                "last_run": meta["last_run"],
            }
        return {
            "total_bots": len(self._bots),
            "bots": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def add_income_entry(self, source: str, amount: float) -> None:
        """Add an income tracking entry."""
        self._income_log.append({
            "source": source,
            "amount_usd": round(amount, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_income_summary(self) -> dict:
        """Return income summary across all bots and sources."""
        total = sum(e["amount_usd"] for e in self._income_log)
        by_source = {}
        for entry in self._income_log:
            src = entry["source"]
            by_source[src] = round(by_source.get(src, 0.0) + entry["amount_usd"], 2)

        return {
            "total_income_usd": round(total, 2),
            "by_source": by_source,
            "entry_count": len(self._income_log),
            "income_log": list(self._income_log),
        }

    def run_all(self) -> dict:
        """Run a status check on all registered bots and collect results."""
        results = {}
        for name, meta in self._bots.items():
            bot = meta["instance"]
            meta["run_count"] += 1
            meta["last_run"] = datetime.now(timezone.utc).isoformat()
            meta["status"] = "running"
            try:
                tier = getattr(bot, "tier", None)
                result = {
                    "bot": name,
                    "tier": tier.value if tier else "unknown",
                    "status": "ok",
                    "run_at": meta["last_run"],
                }
                if hasattr(bot, "generate_report"):
                    result["report"] = bot.generate_report()
                elif hasattr(bot, "track_profitability"):
                    result["profitability"] = bot.track_profitability()
                elif hasattr(bot, "get_status"):
                    result["bot_status"] = bot.get_status()
                results[name] = result
                meta["status"] = "idle"
            except Exception as exc:
                meta["status"] = "error"
                results[name] = {"bot": name, "status": "error", "error": str(exc)}
            self._run_log.append({"bot": name, "timestamp": meta["last_run"], "status": results[name]["status"]})
        return results

    def get_monitoring_dashboard(self) -> dict:
        """Return full monitoring dashboard with all metrics."""
        income = self.get_income_summary()
        status = self.get_status()
        return {
            "dashboard": "Dreamcobots Control Center",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "registered_bots": len(self._bots),
            "bot_status": status,
            "income_summary": income,
            "recent_runs": self._run_log[-10:],
            "health": "healthy" if all(
                m["status"] != "error" for m in self._bots.values()
            ) else "degraded",
        }

    # ------------------------------------------------------------------
    # Control Tower — heartbeat
    # ------------------------------------------------------------------

    def record_heartbeat(self, name: str) -> bool:
        """Record a heartbeat signal from a bot.

        Parameters
        ----------
        name:
            The registered bot name.

        Returns
        -------
        bool
            ``True`` if the bot was found and the heartbeat was recorded,
            ``False`` if the bot is not registered.
        """
        if name not in self._bots:
            return False
        ts = datetime.now(timezone.utc).isoformat()
        self._bots[name]["last_heartbeat"] = ts
        if self._bots[name].get("status") == "offline":
            self._bots[name]["status"] = "idle"
        self._heartbeat_log.append({"bot": name, "timestamp": ts})
        return True

    def get_heartbeat_log(self) -> list:
        """Return all recorded heartbeat events."""
        return list(self._heartbeat_log)

    # ------------------------------------------------------------------
    # Control Tower — repo monitoring
    # ------------------------------------------------------------------

    def register_repo(self, name: str, owner: str, branch: str = "main") -> None:
        """Register a GitHub repository for monitoring.

        Parameters
        ----------
        name:   Repository name (e.g. ``Dreamcobots``).
        owner:  GitHub username / org (e.g. ``ireanjordan24``).
        branch: Default branch to track (default: ``main``).
        """
        self._repos[name] = {
            "name": name,
            "owner": owner,
            "branch": branch,
            "open_prs": 0,
            "open_issues": 0,
            "last_commit": None,
            "last_workflow_result": None,
            "conflicts_detected": False,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }

    def update_repo_status(
        self,
        name: str,
        *,
        open_prs: int = 0,
        open_issues: int = 0,
        last_commit: str = "",
        last_workflow_result: str = "",
        conflicts_detected: bool = False,
    ) -> bool:
        """Update cached monitoring data for a repository.

        Returns ``True`` if the repo was found, ``False`` otherwise.
        """
        if name not in self._repos:
            return False
        repo = self._repos[name]
        repo["open_prs"] = open_prs
        repo["open_issues"] = open_issues
        if last_commit:
            repo["last_commit"] = last_commit
        if last_workflow_result:
            repo["last_workflow_result"] = last_workflow_result
        repo["conflicts_detected"] = conflicts_detected
        repo["last_synced"] = datetime.now(timezone.utc).isoformat()
        return True

    def get_repo_status(self, name: str) -> dict:
        """Return monitoring data for a single repo, or an empty dict if unknown."""
        return dict(self._repos.get(name, {}))

    def get_all_repo_status(self) -> dict:
        """Return monitoring data for all registered repos."""
        return {
            "total_repos": len(self._repos),
            "repos": {k: dict(v) for k, v in self._repos.items()},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_conflict_alerts(self) -> list:
        """Return names of repos or bots that have conflicts detected."""
        alerts = []
        for name, repo in self._repos.items():
            if repo.get("conflicts_detected"):
                alerts.append({"type": "repo", "name": name})
        for name, meta in self._bots.items():
            if meta.get("status") == "error":
                alerts.append({"type": "bot", "name": name})
        return alerts

    # ------------------------------------------------------------------
    # Control Tower — deploy
    # ------------------------------------------------------------------

    def deploy_bot(self, name: str, target: str = "production") -> dict:
        """Coordinate a one-click deploy for a registered bot.

        Records a deploy event and marks the bot status as ``deploying``.
        In a production setup this would trigger a CI/CD pipeline or call
        a cloud API.

        Parameters
        ----------
        name:   Registered bot name.
        target: Deployment target label (default: ``production``).

        Returns
        -------
        dict
            ``{"bot": name, "status": "deploying"|"error", "deploy_id": ..., ...}``
        """
        if name not in self._bots:
            return {"bot": name, "status": "error", "detail": "Bot not registered."}

        ts = datetime.now(timezone.utc).isoformat()
        deploy_id = f"deploy-{name}-{ts}"
        self._bots[name]["status"] = "deploying"
        event = {
            "deploy_id": deploy_id,
            "bot": name,
            "target": target,
            "status": "deploying",
            "initiated_at": ts,
        }
        self._deploy_log.append(event)
        return event

    def deploy_all(self, target: str = "production") -> dict:
        """Trigger deploy for every registered bot.

        Returns a dict mapping bot name → deploy result.
        """
        return {name: self.deploy_bot(name, target) for name in self._bots}

    def get_deploy_log(self) -> list:
        """Return the history of all deploy events in this session."""
        return list(self._deploy_log)

    # ------------------------------------------------------------------
    # Control Tower — onboarding
    # ------------------------------------------------------------------

    def onboard_bot(self, name: str, bot_instance, tier: Tier = Tier.FREE) -> dict:
        """Onboard a new bot: register it and run a self-test.

        Parameters
        ----------
        name:         Unique name for the bot.
        bot_instance: The bot object (must have a ``run()`` method or similar).
        tier:         Subscription tier to assign.

        Returns
        -------
        dict
            ``{"bot": name, "onboarding_status": "ok"|"error", ...}``
        """
        self.register_bot(name, bot_instance)
        tier_value = tier.value if isinstance(tier, Tier) else str(tier)
        self._bots[name]["tier_assigned"] = tier_value

        # Attempt a quick smoke-test
        onboarding_status = "ok"
        detail = ""
        try:
            if hasattr(bot_instance, "run"):
                bot_instance.run()
        except Exception as exc:
            onboarding_status = "error"
            detail = str(exc)
            self._bots[name]["status"] = "error"

        result = {
            "bot": name,
            "onboarding_status": onboarding_status,
            "tier": tier.value,
            "registered_at": self._bots[name]["registered_at"],
        }
        if detail:
            result["detail"] = detail
        return result
