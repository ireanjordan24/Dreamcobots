"""
DreamSalesPro Division — Production-Ready Module

Provides the DreamSalesPro division explorer with:
  - Structured bot catalog loaded from JSON data
  - Division/category/bot browsing
  - Tier-aware feature access
  - Bot task execution hooks
  - Monetization helpers (purchase, subscribe, demo)
  - Filtering by tier, category, and pricing type

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

# GLOBAL AI SOURCES FLOW
import copy
import sys
import os
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.dream_sales_pro.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_PRO_BOTS,
    FEATURE_ENTERPRISE_BOTS,
    FEATURE_DIVISION_EXPLORER,
    FEATURE_BOT_EXECUTOR,
    FEATURE_ANALYTICS_DASHBOARD,
    FEATURE_MONETIZATION,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_TASK_AUTOMATION,
    FEATURE_OUTREACH_TOOLS,
    FEATURE_PIPELINE_TOOLS,
    FEATURE_ENTERPRISE_REPORTING,
)

try:
    from framework import GlobalAISourcesFlow  # noqa: F401
except ImportError:
    pass

logger = logging.getLogger(__name__)

_DATA_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "dream_sales_pro.json"
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class DreamSalesProTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class DreamSalesProBotNotFoundError(Exception):
    """Raised when a requested bot is not found in the catalog."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class BotRecord:
    """Represents a single bot entry from the DreamSalesPro catalog."""

    division: str
    category: str
    bot_name: str
    bot_id: str
    tier: str
    description: str
    pricing_type: str
    audience: str
    price: str
    features: list[str]

    @classmethod
    def from_dict(cls, data: dict) -> "BotRecord":
        return cls(
            division=data["division"],
            category=data["category"],
            bot_name=data["botName"],
            bot_id=data["botId"],
            tier=data["tier"],
            description=data["description"],
            pricing_type=data["pricingType"],
            audience=data["audience"],
            price=data["price"],
            features=data.get("features", []),
        )

    def to_dict(self) -> dict:
        return {
            "division": self.division,
            "category": self.category,
            "botName": self.bot_name,
            "botId": self.bot_id,
            "tier": self.tier,
            "description": self.description,
            "pricingType": self.pricing_type,
            "audience": self.audience,
            "price": self.price,
            "features": self.features,
        }


@dataclass
class TaskResult:
    """Result returned from a bot task execution."""

    bot_id: str
    task: str
    status: str
    output: dict = field(default_factory=dict)
    executed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    error: Optional[str] = None


@dataclass
class MonetizationOption:
    """Represents a monetization action for a bot."""

    bot_id: str
    action: str          # "purchase" | "subscribe" | "demo"
    pricing_type: str
    price: str
    payment_url: str


# ---------------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------------

class DreamSalesPro:
    """
    DreamSalesPro division explorer and bot executor.

    Parameters
    ----------
    tier : Tier
        The subscription tier (PRO or ENTERPRISE).
    operator_name : str
        Name of the operator/user running the division.
    """

    DIVISION_NAME = "DreamSalesPro"
    PAYMENT_BASE_URL = "https://dreamco.io/pay/sales-pro"

    def __init__(self, tier: Tier = Tier.PRO, operator_name: str = "DreamCo Operator") -> None:
        self.tier = tier
        self.operator_name = operator_name
        self.config: TierConfig = copy.deepcopy(get_tier_config(tier))
        self._catalog: list[BotRecord] = self._load_catalog()
        self._active_bots: list[str] = []
        self._task_log: list[TaskResult] = []
        logger.info(
            "DreamSalesPro division initialised. Tier=%s, Bots=%d",
            tier.value,
            len(self._catalog),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_catalog(self) -> list[BotRecord]:
        """Load bot catalog from the JSON data file."""
        try:
            with open(_DATA_FILE, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            return [BotRecord.from_dict(item) for item in raw]
        except FileNotFoundError:
            logger.error("Catalog file not found: %s", _DATA_FILE)
            return []
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("Failed to parse catalog: %s", exc)
            return []

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            msg = (
                f"Feature '{feature}' is not available on the {self.tier.value!r} tier. "
                + (f"Upgrade to {upgrade.value!r}." if upgrade else "No upgrade available.")
            )
            raise DreamSalesProTierError(msg)

    def _require_bot_access(self, bot: BotRecord) -> None:
        """Check tier allows access to the given bot's tier level."""
        if bot.tier.lower() == "enterprise":
            self._require_feature(FEATURE_ENTERPRISE_BOTS)
        else:
            self._require_feature(FEATURE_PRO_BOTS)

    def _get_bot(self, bot_id: str) -> BotRecord:
        for bot in self._catalog:
            if bot.bot_id == bot_id:
                return bot
        raise DreamSalesProBotNotFoundError(f"Bot '{bot_id}' not found in DreamSalesPro catalog.")

    # ------------------------------------------------------------------
    # Division Explorer
    # ------------------------------------------------------------------

    def list_categories(self) -> list[str]:
        """Return all unique categories in the division."""
        self._require_feature(FEATURE_DIVISION_EXPLORER)
        seen: set[str] = set()
        result: list[str] = []
        for bot in self._catalog:
            if bot.category not in seen:
                seen.add(bot.category)
                result.append(bot.category)
        return result

    def list_bots(
        self,
        category: Optional[str] = None,
        tier_filter: Optional[str] = None,
        pricing_type_filter: Optional[str] = None,
    ) -> list[BotRecord]:
        """
        List bots with optional filtering.

        Parameters
        ----------
        category : str, optional
            Filter by category name (case-insensitive).
        tier_filter : str, optional
            Filter by tier ("Pro" or "Enterprise").
        pricing_type_filter : str, optional
            Filter by pricing type substring.

        Returns
        -------
        list[BotRecord]
        """
        self._require_feature(FEATURE_DIVISION_EXPLORER)
        results = self._catalog
        if category:
            results = [b for b in results if b.category.lower() == category.lower()]
        if tier_filter:
            results = [b for b in results if b.tier.lower() == tier_filter.lower()]
        if pricing_type_filter:
            results = [
                b for b in results
                if pricing_type_filter.lower() in b.pricing_type.lower()
            ]
        return results

    def get_bot(self, bot_id: str) -> BotRecord:
        """Retrieve a specific bot by ID."""
        self._require_feature(FEATURE_DIVISION_EXPLORER)
        return self._get_bot(bot_id)

    def search_bots(self, query: str) -> list[BotRecord]:
        """Full-text search across bot names, descriptions, and features."""
        self._require_feature(FEATURE_DIVISION_EXPLORER)
        q = query.lower()
        return [
            b for b in self._catalog
            if q in b.bot_name.lower()
            or q in b.description.lower()
            or any(q in f.lower() for f in b.features)
        ]

    def get_division_summary(self) -> dict:
        """Return a summary of the division including bot and category counts."""
        self._require_feature(FEATURE_DIVISION_EXPLORER)
        categories = self.list_categories()
        tier_counts = {"Pro": 0, "Enterprise": 0}
        for b in self._catalog:
            key = "Enterprise" if b.tier.lower() == "enterprise" else "Pro"
            tier_counts[key] += 1
        return {
            "division": self.DIVISION_NAME,
            "total_bots": len(self._catalog),
            "total_categories": len(categories),
            "categories": categories,
            "tier_counts": tier_counts,
        }

    # ------------------------------------------------------------------
    # Bot activation
    # ------------------------------------------------------------------

    def activate_bot(self, bot_id: str) -> dict:
        """Activate a bot for use (checks tier and capacity limits)."""
        self._require_feature(FEATURE_BOT_EXECUTOR)
        bot = self._get_bot(bot_id)
        self._require_bot_access(bot)

        max_bots = self.config.max_active_bots
        if max_bots is not None and len(self._active_bots) >= max_bots:
            upgrade = get_upgrade_path(self.tier)
            msg = (
                f"Active bot limit ({max_bots}) reached on {self.tier.value!r} tier. "
                + (f"Upgrade to {upgrade.value!r} for unlimited bots." if upgrade else "")
            )
            raise DreamSalesProTierError(msg)

        if bot_id not in self._active_bots:
            self._active_bots.append(bot_id)
            logger.info("Bot activated: %s", bot_id)
        return {"bot_id": bot_id, "status": "active", "bot_name": bot.bot_name}

    def deactivate_bot(self, bot_id: str) -> dict:
        """Deactivate a bot."""
        if bot_id in self._active_bots:
            self._active_bots.remove(bot_id)
            logger.info("Bot deactivated: %s", bot_id)
        return {"bot_id": bot_id, "status": "inactive"}

    def list_active_bots(self) -> list[str]:
        """Return IDs of all currently active bots."""
        return list(self._active_bots)

    # ------------------------------------------------------------------
    # Task execution hooks
    # ------------------------------------------------------------------

    def execute_task(self, bot_id: str, task: str, params: Optional[dict] = None) -> TaskResult:
        """
        Execute a task on a specific bot.

        Parameters
        ----------
        bot_id : str
            The bot to execute the task on.
        task : str
            The task name (e.g. "analyze_campaign_roi", "scrape_leads").
        params : dict, optional
            Task-specific parameters.

        Returns
        -------
        TaskResult
        """
        self._require_feature(FEATURE_TASK_AUTOMATION)
        bot = self._get_bot(bot_id)
        self._require_bot_access(bot)

        params = params or {}
        result = self._dispatch_task(bot, task, params)
        self._task_log.append(result)
        logger.info("Task executed: bot=%s task=%s status=%s", bot_id, task, result.status)
        return result

    def _dispatch_task(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        """Route task to appropriate handler based on category."""
        handlers = {
            "Analytics": self._task_analytics,
            "Autonomy": self._task_autonomy,
            "Billing": self._task_billing,
            "Conversion": self._task_conversion,
            "Intelligence": self._task_intelligence,
            "Leads": self._task_leads,
            "Outreach": self._task_outreach,
            "Pipeline": self._task_pipeline,
            "White-Label": self._task_white_label,
        }
        handler = handlers.get(bot.category, self._task_generic)
        return handler(bot, task, params)

    def _make_result(self, bot: BotRecord, task: str, output: dict) -> TaskResult:
        return TaskResult(bot_id=bot.bot_id, task=task, status="success", output=output)

    def _task_analytics(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "roi": params.get("roi", 0.0),
            "revenue_per_email": params.get("revenue_per_email", 0.0),
            "win_rate": params.get("win_rate", 0.0),
            "forecast": params.get("forecast", {}),
            "message": f"{bot.bot_name} completed analytics task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_autonomy(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "autonomy_level": params.get("autonomy_level", "manual"),
            "budget_cap": params.get("budget_cap", 0.0),
            "campaign_status": params.get("campaign_status", "active"),
            "message": f"{bot.bot_name} completed autonomy task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_billing(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "invoice_created": params.get("invoice_created", False),
            "mrr": params.get("mrr", 0.0),
            "revenue_tracked": params.get("revenue_tracked", 0.0),
            "message": f"{bot.bot_name} completed billing task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_conversion(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "conversion_rate": params.get("conversion_rate", 0.0),
            "funnel_drop_off": params.get("funnel_drop_off", {}),
            "ab_test_winner": params.get("ab_test_winner", ""),
            "message": f"{bot.bot_name} completed conversion task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_intelligence(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "objections_handled": params.get("objections_handled", 0),
            "pitch_generated": params.get("pitch_generated", False),
            "win_probability": params.get("win_probability", 0.0),
            "message": f"{bot.bot_name} completed intelligence task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_leads(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "leads_scraped": params.get("leads_scraped", 0),
            "leads_validated": params.get("leads_validated", 0),
            "icp_matches": params.get("icp_matches", 0),
            "message": f"{bot.bot_name} completed leads task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_outreach(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "emails_sent": params.get("emails_sent", 0),
            "open_rate": params.get("open_rate", 0.0),
            "reply_rate": params.get("reply_rate", 0.0),
            "deliverability_score": params.get("deliverability_score", 0.0),
            "message": f"{bot.bot_name} completed outreach task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_pipeline(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "appointments_booked": params.get("appointments_booked", 0),
            "pipeline_value": params.get("pipeline_value", 0.0),
            "close_rate": params.get("close_rate", 0.0),
            "message": f"{bot.bot_name} completed pipeline task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_white_label(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "clients_onboarded": params.get("clients_onboarded", 0),
            "white_label_domains": params.get("white_label_domains", []),
            "health_score": params.get("health_score", 0.0),
            "message": f"{bot.bot_name} completed white-label task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_generic(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "params": params,
            "message": f"{bot.bot_name} completed task: {task}",
        }
        return self._make_result(bot, task, output)

    def get_task_log(self) -> list[TaskResult]:
        """Return the full task execution log."""
        return list(self._task_log)

    # ------------------------------------------------------------------
    # Monetization
    # ------------------------------------------------------------------

    def get_monetization_options(self, bot_id: str) -> list[MonetizationOption]:
        """Return available monetization actions for a given bot."""
        self._require_feature(FEATURE_MONETIZATION)
        bot = self._get_bot(bot_id)
        options = [
            MonetizationOption(
                bot_id=bot_id,
                action="demo",
                pricing_type=bot.pricing_type,
                price="Free trial",
                payment_url=f"{self.PAYMENT_BASE_URL}/demo/{bot_id}",
            ),
            MonetizationOption(
                bot_id=bot_id,
                action="subscribe",
                pricing_type=bot.pricing_type,
                price=bot.price,
                payment_url=f"{self.PAYMENT_BASE_URL}/subscribe/{bot_id}",
            ),
        ]
        if "Enterprise" in bot.pricing_type or bot.tier.lower() == "enterprise":
            options.append(
                MonetizationOption(
                    bot_id=bot_id,
                    action="enterprise_license",
                    pricing_type="Enterprise license",
                    price="Custom pricing",
                    payment_url=f"{self.PAYMENT_BASE_URL}/enterprise/{bot_id}",
                )
            )
        return options

    def get_bundle_options(self) -> list[dict]:
        """Return available bundle packages for monetization."""
        self._require_feature(FEATURE_MONETIZATION)
        return [
            {
                "bundle_id": "starter_plus",
                "name": "Starter+",
                "description": "5 Pro-tier bots for essential sales operations.",
                "price": "$299/mo",
                "bot_count": 5,
                "tier": "Pro",
            },
            {
                "bundle_id": "growth_plus",
                "name": "Growth+",
                "description": "15 Pro & Enterprise bots for scaling revenue teams.",
                "price": "$799/mo",
                "bot_count": 15,
                "tier": "Pro + Enterprise",
            },
            {
                "bundle_id": "empire",
                "name": "Empire",
                "description": "Full DreamSalesPro catalog — all 25 bots unlimited.",
                "price": "$1,499/mo",
                "bot_count": 25,
                "tier": "Enterprise",
            },
        ]

    # ------------------------------------------------------------------
    # Analytics dashboard
    # ------------------------------------------------------------------

    def get_analytics_summary(self) -> dict:
        """Return analytics data for the division dashboard."""
        self._require_feature(FEATURE_ANALYTICS_DASHBOARD)
        total_tasks = len(self._task_log)
        success_count = sum(1 for t in self._task_log if t.status == "success")
        return {
            "division": self.DIVISION_NAME,
            "operator": self.operator_name,
            "tier": self.tier.value,
            "total_bots_in_catalog": len(self._catalog),
            "active_bots": len(self._active_bots),
            "tasks_executed": total_tasks,
            "tasks_succeeded": success_count,
            "success_rate_pct": round(success_count / total_tasks * 100, 2) if total_tasks else 0.0,
        }

    # ------------------------------------------------------------------
    # Outreach tools
    # ------------------------------------------------------------------

    def get_outreach_tools(self) -> list[str]:
        """Return available outreach tool names."""
        self._require_feature(FEATURE_OUTREACH_TOOLS)
        outreach_bots = self.list_bots(category="Outreach")
        return [b.bot_name for b in outreach_bots]

    # ------------------------------------------------------------------
    # Pipeline tools
    # ------------------------------------------------------------------

    def get_pipeline_tools(self) -> list[str]:
        """Return available pipeline tool names."""
        self._require_feature(FEATURE_PIPELINE_TOOLS)
        pipeline_bots = self.list_bots(category="Pipeline")
        return [b.bot_name for b in pipeline_bots]

    # ------------------------------------------------------------------
    # Enterprise reporting
    # ------------------------------------------------------------------

    def generate_enterprise_report(self) -> dict:
        """Generate an enterprise-level division report."""
        self._require_feature(FEATURE_ENTERPRISE_REPORTING)
        summary = self.get_division_summary()
        analytics = self.get_analytics_summary()
        return {
            "report_type": "enterprise_division_report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "division_summary": summary,
            "analytics": analytics,
            "active_bots": self._active_bots,
            "tier": self.tier.value,
            "operator": self.operator_name,
        }

    # ------------------------------------------------------------------
    # Tier info
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Return a human-readable description of the current tier."""
        info = self.config
        lines = [
            f"=== {info.name} DreamSalesPro Tier ===",
            f"Price: ${info.price_usd_monthly:.2f}/month",
            f"Max Active Bots: {'Unlimited' if info.max_active_bots is None else info.max_active_bots}",
            f"Support: {info.support_level}",
            "Features:",
        ]
        for feat in info.features:
            lines.append(f"  ✓ {feat}")
        return "\n".join(lines)

    def run(self) -> str:
        """Run the DreamSalesPro division and return status."""
        summary = self.get_division_summary()
        return (
            f"DreamSalesPro division active. "
            f"Tier: {self.tier.value}. "
            f"Bots: {summary['total_bots']}. "
            f"Categories: {summary['total_categories']}."
        )


# Alias for framework compatibility
Bot = DreamSalesPro
