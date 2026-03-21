"""
DreamRealEstate Division — Production-Ready Module

Provides the DreamRealEstate division explorer with:
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

from bots.dream_real_estate.tiers import (
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
    FEATURE_PORTFOLIO_TOOLS,
    FEATURE_ENTERPRISE_REPORTING,
)

try:
    from framework import GlobalAISourcesFlow  # noqa: F401
except ImportError:
    pass

logger = logging.getLogger(__name__)

_DATA_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "dream_real_estate.json"
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class DreamRealEstateTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class DreamRealEstateBotNotFoundError(Exception):
    """Raised when a requested bot is not found in the catalog."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class BotRecord:
    """Represents a single bot entry from the DreamRealEstate catalog."""

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

class DreamRealEstate:
    """
    DreamRealEstate division explorer and bot executor.

    Parameters
    ----------
    tier : Tier
        The subscription tier (PRO or ENTERPRISE).
    operator_name : str
        Name of the operator/user running the division.
    """

    DIVISION_NAME = "DreamRealEstate"
    PAYMENT_BASE_URL = "https://dreamco.io/pay/real-estate"

    def __init__(self, tier: Tier = Tier.PRO, operator_name: str = "DreamCo Operator") -> None:
        self.tier = tier
        self.operator_name = operator_name
        self.config: TierConfig = copy.deepcopy(get_tier_config(tier))
        self._catalog: list[BotRecord] = self._load_catalog()
        self._active_bots: list[str] = []
        self._task_log: list[TaskResult] = []
        logger.info(
            "DreamRealEstate division initialised. Tier=%s, Bots=%d",
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
            raise DreamRealEstateTierError(msg)

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
        raise DreamRealEstateBotNotFoundError(f"Bot '{bot_id}' not found in DreamRealEstate catalog.")

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
            raise DreamRealEstateTierError(msg)

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
            The task name (e.g. "scan_properties", "analyze_lease").
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
            "Acquisition": self._task_acquisition,
            "Analytics": self._task_analytics,
            "Construction": self._task_construction,
            "Crowdfunding": self._task_crowdfunding,
            "Distressed-Assets": self._task_distressed_assets,
            "Energy-Optimization": self._task_energy_optimization,
            "Investor-Reporting": self._task_investor_reporting,
            "Land-Banking": self._task_land_banking,
            "Lease-Analysis": self._task_lease_analysis,
            "Portfolio": self._task_portfolio,
            "Predictive-Maintenance": self._task_predictive_maintenance,
            "Property-Management": self._task_property_management,
            "Reit-Analysis": self._task_reit_analysis,
            "Residential-Investing": self._task_residential_investing,
            "Risk-Simulation": self._task_risk_simulation,
            "Smart-Buildings": self._task_smart_buildings,
            "Syndication": self._task_syndication,
            "Tax": self._task_tax,
            "Valuation": self._task_valuation,
            "Zoning-Compliance": self._task_zoning_compliance,
        }
        handler = handlers.get(bot.category, self._task_generic)
        return handler(bot, task, params)

    def _make_result(self, bot: BotRecord, task: str, output: dict) -> TaskResult:
        return TaskResult(bot_id=bot.bot_id, task=task, status="success", output=output)

    def _task_acquisition(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "scan_results": params.get("scan_results", []),
            "deals_found": params.get("deals_found", 0),
            "cap_rate": params.get("cap_rate", 0.0),
            "message": f"{bot.bot_name} completed acquisition task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_analytics(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "heatmap_data": params.get("heatmap_data", {}),
            "forecast": params.get("forecast", {}),
            "message": f"{bot.bot_name} completed analytics task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_construction(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "budget_variance": params.get("budget_variance", 0.0),
            "change_orders": params.get("change_orders", []),
            "message": f"{bot.bot_name} completed construction task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_crowdfunding(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "ranked_deals": params.get("ranked_deals", []),
            "message": f"{bot.bot_name} completed crowdfunding task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_distressed_assets(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "foreclosures_found": params.get("foreclosures_found", 0),
            "arv_estimate": params.get("arv_estimate", 0.0),
            "message": f"{bot.bot_name} completed distressed assets task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_energy_optimization(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "energy_savings_pct": params.get("energy_savings_pct", 0.0),
            "solar_roi": params.get("solar_roi", 0.0),
            "message": f"{bot.bot_name} completed energy optimization task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_investor_reporting(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "report_generated": True,
            "irr": params.get("irr", 0.0),
            "equity_multiple": params.get("equity_multiple", 0.0),
            "message": f"{bot.bot_name} completed investor reporting task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_land_banking(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "parcels_scored": params.get("parcels_scored", 0),
            "top_growth_score": params.get("top_growth_score", 0.0),
            "message": f"{bot.bot_name} completed land banking task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_lease_analysis(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "optimized_rent": params.get("optimized_rent", 0.0),
            "lease_abstractions": params.get("lease_abstractions", []),
            "message": f"{bot.bot_name} completed lease analysis task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_portfolio(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "rebalance_actions": params.get("rebalance_actions", []),
            "allocation_drift": params.get("allocation_drift", 0.0),
            "message": f"{bot.bot_name} completed portfolio task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_predictive_maintenance(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "failures_predicted": params.get("failures_predicted", []),
            "maintenance_schedule": params.get("maintenance_schedule", []),
            "message": f"{bot.bot_name} completed predictive maintenance task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_property_management(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "tenants_screened": params.get("tenants_screened", 0),
            "rent_collected": params.get("rent_collected", 0.0),
            "message": f"{bot.bot_name} completed property management task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_reit_analysis(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "ffo_forecast": params.get("ffo_forecast", 0.0),
            "dividend_yield": params.get("dividend_yield", 0.0),
            "message": f"{bot.bot_name} completed REIT analysis task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_residential_investing(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "deals_found": params.get("deals_found", 0),
            "arv": params.get("arv", 0.0),
            "flip_roi_pct": params.get("flip_roi_pct", 0.0),
            "message": f"{bot.bot_name} completed residential investing task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_risk_simulation(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "monte_carlo_runs": params.get("monte_carlo_runs", 1000),
            "portfolio_var": params.get("portfolio_var", 0.0),
            "stress_test_result": params.get("stress_test_result", {}),
            "message": f"{bot.bot_name} completed risk simulation task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_smart_buildings(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "hvac_optimized": params.get("hvac_optimized", False),
            "occupancy_score": params.get("occupancy_score", 0.0),
            "energy_saved_kwh": params.get("energy_saved_kwh", 0.0),
            "message": f"{bot.bot_name} completed smart buildings task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_syndication(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "capital_raised": params.get("capital_raised", 0.0),
            "investor_count": params.get("investor_count", 0),
            "message": f"{bot.bot_name} completed syndication task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_tax(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "tax_savings": params.get("tax_savings", 0.0),
            "incentives_found": params.get("incentives_found", []),
            "message": f"{bot.bot_name} completed tax task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_valuation(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "estimated_value": params.get("estimated_value", 0.0),
            "confidence_interval": params.get("confidence_interval", [0.0, 0.0]),
            "message": f"{bot.bot_name} completed valuation task: {task}",
        }
        return self._make_result(bot, task, output)

    def _task_zoning_compliance(self, bot: BotRecord, task: str, params: dict) -> TaskResult:
        output = {
            "task": task,
            "bot": bot.bot_name,
            "zoning_code": params.get("zoning_code", ""),
            "compliant": params.get("compliant", True),
            "permit_requirements": params.get("permit_requirements", []),
            "message": f"{bot.bot_name} completed zoning compliance task: {task}",
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
                "description": "5 Pro-tier bots for essential real estate operations.",
                "price": "$299/mo",
                "bot_count": 5,
                "tier": "Pro",
            },
            {
                "bundle_id": "growth_plus",
                "name": "Growth+",
                "description": "15 Pro & Enterprise bots for scaling investors.",
                "price": "$799/mo",
                "bot_count": 15,
                "tier": "Pro + Enterprise",
            },
            {
                "bundle_id": "empire",
                "name": "Empire",
                "description": "Full DreamRealEstate catalog — all 25 bots unlimited.",
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
    # Portfolio tools
    # ------------------------------------------------------------------

    def get_portfolio_tools(self) -> list[str]:
        """Return available portfolio tool names."""
        self._require_feature(FEATURE_PORTFOLIO_TOOLS)
        portfolio_bots = self.list_bots(category="Portfolio")
        return [b.bot_name for b in portfolio_bots]

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
            f"=== {info.name} DreamRealEstate Tier ===",
            f"Price: ${info.price_usd_monthly:.2f}/month",
            f"Max Active Bots: {'Unlimited' if info.max_active_bots is None else info.max_active_bots}",
            f"Support: {info.support_level}",
            "Features:",
        ]
        for feat in info.features:
            lines.append(f"  ✓ {feat}")
        return "\n".join(lines)

    def run(self) -> str:
        """Run the DreamRealEstate division and return status."""
        summary = self.get_division_summary()
        return (
            f"DreamRealEstate division active. "
            f"Tier: {self.tier.value}. "
            f"Bots: {summary['total_bots']}. "
            f"Categories: {summary['total_categories']}."
        )


# Alias for framework compatibility
Bot = DreamRealEstate
