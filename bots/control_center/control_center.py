"""Control Center — central orchestration dashboard for all Dreamcobots."""
import sys, os
from datetime import datetime, timezone
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.control_center.bot_registry import BotRegistry
from bots.control_center.heartbeat import HeartbeatMonitor
from bots.control_center.github_integration import GitHubIntegration


class ControlCenter:
    """Central control center for registering, monitoring, and orchestrating all bots."""

    def __init__(
        self,
        registry: Optional[BotRegistry] = None,
        heartbeat: Optional[HeartbeatMonitor] = None,
        github: Optional[GitHubIntegration] = None,
    ):
        self._bots: dict = {}
        self._income_log: list = []
        self._run_log: list = []
        self.registry: BotRegistry = registry or BotRegistry()
        self.heartbeat: HeartbeatMonitor = heartbeat or HeartbeatMonitor()
        self.github: GitHubIntegration = github or GitHubIntegration()

    def register_bot(self, name: str, bot_instance, repo_name: str = "") -> None:
        """Register a bot instance under the given name."""
        self._bots[name] = {
            "instance": bot_instance,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "run_count": 0,
            "last_run": None,
            "status": "idle",
        }
        # Also register in the persistent bot registry
        self.registry.register(name, repo_name=repo_name)

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
        heartbeat_summary = self.heartbeat.summary()
        registry_summary = self.registry.summary()
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
            "heartbeat": heartbeat_summary,
            "registry": registry_summary,
        }

    def ping_bot(self, bot_name: str, metadata: Optional[dict] = None) -> dict:
        """Record a heartbeat ping for *bot_name*."""
        self.registry.record_heartbeat(bot_name)
        return self.heartbeat.ping(bot_name, metadata=metadata)

    def get_github_repo_status(self, repo_name: str) -> dict:
        """Return GitHub repository status for *repo_name*."""
        return self.github.get_repo_status(repo_name)

    def deploy_bot(
        self,
        bot_name: str,
        repo_name: str = "",
        tier: str = "free",
        config: Optional[dict] = None,
    ) -> dict:
        """Register a new bot in the registry and prepare its deployment entry.

        This creates the registry entry and returns the configuration that
        can be used to provision the bot's GitHub repository and workflows.
        The actual repository creation requires a valid ``GITHUB_TOKEN``
        environment variable.
        """
        entry = self.registry.register(bot_name, repo_name=repo_name, config={
            "tier": tier,
            **(config or {}),
        })
        return {
            "bot_name": bot_name,
            "repo_name": repo_name,
            "tier": tier,
            "status": "registered",
            "entry": entry,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
